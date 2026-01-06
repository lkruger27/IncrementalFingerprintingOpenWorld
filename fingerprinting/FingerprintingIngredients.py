from aalpy.utils import load_automaton_from_file
from aalpy.automata import MealyMachine, MealyState
from aalpy.SULs import MealySUL
from aalpy.base.SUL import CacheSUL
from aalpy.oracles import PerfectKnowledgeEqOracle
from aalpy.base import Oracle, SUL, DeterministicAutomaton
from FingerprintingOracles import WpMethodEqOracle, WpMethodEqOracleK, BudgetRandomWpMethodEqOracle, RandomWpMethodEqOracle, StatePrefixEqOracle, RandomWordEqOracle
from FingerprintingAdaptiveLSharp import run_adaptive_Lsharp
from FingerprintingLSharp import run_Lsharp
from FingerprintADG import Adg
from aalpy.utils.ModelChecking import bisimilar

import random
import os
import glob
import re

def get_oracle(target, sul, oracle_type, m, budget=None):
    # Retrieves an oracle based on a string input oracle type
    val = None
    if len(re.findall(r'\d+', oracle_type)) > 0:
        val = int(re.findall(r'\d+', oracle_type)[0])

    if oracle_type == 'RandomWpBudget':
        return BudgetRandomWpMethodEqOracle(target.get_input_alphabet(), sul, target, budget, min_length=5, expected_length=8)
    elif "RandomWord" in oracle_type:
        return RandomWordEqOracle(target.get_input_alphabet(), sul, num_walks=val)
    elif "RandomWp" in oracle_type:
        return RandomWpMethodEqOracle(target.get_input_alphabet(), sul, walks_per_state=val, walk_len=5)
    elif oracle_type == 'StatePrefix100':
        return StatePrefixEqOracle(target.get_input_alphabet(), sul, walks_per_state=100)
    elif oracle_type == 'PerfectKnowledge':
        return PerfectKnowledgeEqOracle(target.get_input_alphabet(), sul, target)
    elif oracle_type == 'Wp':
        return WpMethodEqOracle(target.get_input_alphabet(), sul, m)
    elif oracle_type == 'WpK':
        return WpMethodEqOracleK(target.get_input_alphabet(), sul, 2)

def ADG_fingerprinting(sul, specifications):
    # Apply Adaptive Distinguishing Graph to the sul until sul is consistent with 1 or none of the specifications
    adg = Adg(specifications[0][1].get_input_alphabet(), specifications)
    samples = []
    last_outputs = None

    while True:
        next_sep_seq = adg.next_sep_seq(last_outputs)
        if next_sep_seq is None:
            break
        else:
            outputs = tuple(sul.query(next_sep_seq)) 
            samples.append((next_sep_seq, outputs))
            last_outputs = outputs

    valid_models = adg.current_node.current_block
    if valid_models is None:
        return None, samples
    if len(valid_models) == 1:
        return valid_models[0][1], samples


def separating_sequence_fingerprinting(sul, specifications):
    # Apply separating sequences to the sul until sul is consistent with 1 or none of the specifications
    samples = []
    valid_models = [s for (c, s) in specifications]
    for si in range(0, len(specifications)):
        for sj in range(si+1, len(specifications)):
            (_, spec1) = specifications[si]
            (_, spec2) = specifications[sj]
            if spec1 not in valid_models or spec2 not in valid_models:
                continue

            separating_sequence = bisimilar(spec1, spec2, return_cex=True)
            if not separating_sequence:
                raise RuntimeError(
                    "No separating sequence found between specifications")

            sep_outputs = tuple(sul.query(separating_sequence))
            if (separating_sequence, sep_outputs) not in samples:
                samples.append((separating_sequence, sep_outputs))

            if sep_outputs != tuple(spec1.compute_output_seq(spec1.initial_state, separating_sequence)):
                valid_models.remove(spec1)
            if sep_outputs != tuple(spec2.compute_output_seq(spec2.initial_state, separating_sequence)):
                valid_models.remove(spec2)

            if len(valid_models) == 1:
                return valid_models[0], samples
            if len(valid_models) == 0:
                return None, samples
    raise RuntimeError("Multiple models are valid after fingerprinting")


def conformance_check(sul, implementation, specification, oracle_type, budget):
    # Conformance test, return whether the model passes or not and the samples
    rebuild_oracle = get_oracle(
        implementation, sul, oracle_type, specification.size, budget)
    if oracle_type != 'PerfectKnowledge':
        cex = rebuild_oracle.find_cex(specification, cache=True)
    else:
        cex = rebuild_oracle.find_cex(specification)
    return cex == None, rebuild_oracle


def identify_and_learn(implementation, specifications, fingerprint_type, oracle_type1, oracle_type2, internal_method, budget):
    # 1. Perform fingerprinting
    # 2. Conformance test the fingerprinted model
    #       If 'pass': terminate
    #       Else: run adaptive learning with all specifications so far and initialize with OQs so far
    # Everything uses the same cachedSUL
    sul = CacheSUL(MealySUL(implementation))

    separating_queries = 0
    separating_symbols = 0
    conformance_queries = 0
    conformance_symbols = 0
    learning_queries = 0
    learning_symbols = 0

    if len(specifications) == 0:
        eq_oracle = get_oracle(implementation, sul,
                           oracle_type2, implementation.size, budget)
        s, data = run_Lsharp(implementation.get_input_alphabet(), sul, eq_oracle,
                             extension_rule=None, separation_rule="SepSeq", return_data=True, cache_and_non_det_check=False, print_level=0, budget=budget)
        learning_queries += count_and_reset_queries(sul)
        learning_symbols += count_and_reset_symbols(sul)
    else:
        s = None
        samples = []
        if len(specifications) == 1:
            (_, s) = specifications[0]
        elif len(specifications) > 1:
            if fingerprint_type == 'sep_seq':
                s, samples = separating_sequence_fingerprinting(
                    sul, specifications)
            else:
                s, samples = ADG_fingerprinting(
                    sul, specifications)
            separating_queries += count_and_reset_queries(sul)
            separating_symbols += count_and_reset_symbols(sul)
            if budget is not None:
                budget = budget - separating_queries - separating_symbols
        equiv = False
        if s:
            equiv, rebuild_oracle = conformance_check(
                sul, implementation, s, oracle_type1, budget)
            conformance_queries += count_and_reset_queries(sul)
            conformance_symbols += count_and_reset_symbols(sul)
            if oracle_type1 != 'PerfectKnowledge':
                samples += rebuild_oracle.cache
            if budget is not None:
                budget = budget - conformance_queries - conformance_symbols
        if equiv == False:
            eq_oracle = get_oracle(implementation, sul,
                           oracle_type2, implementation.size, budget)
            if internal_method == 'AL#':
                s, data = run_adaptive_Lsharp(implementation.get_input_alphabet(), sul, [s for (_, s) in specifications], 
                eq_oracle, extension_rule=None, separation_rule="SepSeq",
                                              rebuilding=True, state_matching="Approximate", samples=samples, cache_and_non_det_check=False, return_data=True, print_level=0, budget=budget)
            else:
                s, data = run_Lsharp(implementation.get_input_alphabet(), sul, eq_oracle, extension_rule=None, separation_rule="SepSeq",
                                     samples=samples, cache_and_non_det_check=False, return_data=True, print_level=0, budget=budget)
            learning_queries += count_and_reset_queries(sul)
            learning_symbols += count_and_reset_symbols(sul)
    return s, separating_queries, separating_symbols, conformance_queries, conformance_symbols, learning_queries, learning_symbols


def adaptive_lsharp_learning(implementation, specifications, oracle_type, budget):
    # Run adaptive L# with all specifications so far
    sul = CacheSUL(MealySUL(implementation))
    eq_oracle = get_oracle(implementation, sul,
                           oracle_type, implementation.size, budget)
    learned_mealy, data = run_adaptive_Lsharp(implementation.get_input_alphabet(), sul, [s for (_, s) in specifications], eq_oracle, extension_rule=None, separation_rule="SepSeq",rebuilding=True, state_matching="Approximate", samples=None, cache_and_non_det_check=False, return_data=True, print_level=0, budget=budget)
    return learned_mealy, sul.num_queries, sul.num_steps


def lsharp_learning(implementation, oracle_type, budget):
    # Run L#
    sul = CacheSUL(MealySUL(implementation))
    eq_oracle = get_oracle(implementation, sul,
                           oracle_type, implementation.size, budget)
    learned_mealy, data = run_Lsharp(implementation.get_input_alphabet(), sul, eq_oracle,
                                     extension_rule=None, separation_rule="SepSeq", cache_and_non_det_check=False, return_data=True, print_level=0, budget=budget)

    return learned_mealy, sul.num_queries, sul.num_steps


def shallow_fingerprint_if(implementations, specifications, classification, result_file, fingerprint_type, start_spec, oracle):
    # Algorithm for performing shallow fingerprinting (only use sepseqs with an inmutable set of specifications)
    learned_models = 0
    not_found = 0
    separating_queries = 0
    separating_symbols = 0
    learning_queries = 0
    learning_symbols = 0
    conformance_queries = 0
    conformance_symbols = 0
    for (i_id, i) in implementations:

        sul = CacheSUL(MealySUL(i))
        eq_oracle = get_oracle(i, sul,
                           oracle, i.size)

        if fingerprint_type == "sep_seq":
            s, samples = separating_sequence_fingerprinting(sul, specifications)
        else:
            s, samples = ADG_fingerprinting(sul, specifications)
        separating_queries += count_and_reset_queries(sul)
        separating_symbols += count_and_reset_symbols(sul)
        equiv = False
        if s:
            equiv, rebuild_oracle = conformance_check(sul, i, s, oracle, budget=None)
        if equiv == False or s is None:
            s, data = run_adaptive_Lsharp(i.get_input_alphabet(), sul, [s for (_, s) in specifications], eq_oracle, extension_rule=None, separation_rule="SepSeq",
                                              rebuilding=True, state_matching="Approximate", samples=samples, budget=None,  cache_and_non_det_check=False, return_data=True, print_level=0)
            learning_queries += count_and_reset_queries(sul)
            learning_symbols += count_and_reset_symbols(sul)
        conformance_queries += count_and_reset_queries(sul)
        conformance_symbols += count_and_reset_symbols(sul)

        if s:
            learned_models += (bisimilar(i, s) == True)
            if s not in [spec for (count, spec) in specifications]:
                specifications.append((i_id, s))
        else:
            not_found += 1
    print(f"finished {start_spec}")
    return f"IF,{oracle},{fingerprint_type},{separating_queries},{separating_symbols},{conformance_queries},{conformance_symbols},{learning_queries},{learning_symbols},{learned_models},{len(specifications)},{not_found},{start_spec}\n"


def shallow_fingerprint(implementations, specifications, classification, result_file, fingerprint_type, oracle_type,start_specs):
    # Algorithm for performing shallow fingerprinting (only use sepseqs with an inmutable set of specifications)
    learned_models = 0
    not_found = 0
    separating_queries = 0
    separating_symbols = 0
    conformance_queries = 0
    conformance_symbols = 0
    for (i_id, i) in implementations:

        sul = CacheSUL(MealySUL(i))
        if fingerprint_type == "sep_seq":
            s, _ = separating_sequence_fingerprinting(sul, specifications)
        else:
            s, _ = ADG_fingerprinting(sul, specifications)
        separating_queries += count_and_reset_queries(sul)
        separating_symbols += count_and_reset_symbols(sul)
        if oracle_type and s:
            equiv, rebuild_oracle = conformance_check(sul, i, s, oracle_type)
            if equiv == False:
                s = None
        conformance_queries += count_and_reset_queries(sul)
        conformance_symbols += count_and_reset_symbols(sul)

        if s:
            learned_models += (bisimilar(i, s) == True)
            if s not in [spec for (count, spec) in specifications]:
                print(f"Adding {i_id} to the specifications")
                specifications.append((i_id, s))
        else:
            not_found += 1

    with open(result_file, 'a') as file:
        file.write(f"SepSeq,{oracle_type},{fingerprint_type},{separating_queries},{separating_symbols},{conformance_queries},{conformance_symbols},0,0,{learned_models},{len(specifications)},{not_found},{start_specs}\n")


def algorithm(implementations, specifications, method, fingerprint_type, oracle_type1, oracle_type2, classification, result_file, copies=None, budget=None):
    # General algorithm that runs IF, RAL# or RL# and keeps track of the specifications and misclassifications
    total_separating_queries = 0
    total_separating_symbols = 0
    total_conformance_queries = 0
    total_conformance_symbols = 0
    total_learning_queries = 0
    total_learning_symbols = 0

    learned_models = 0
    for (i_id, i) in implementations:
        if method == 'IF-AL#':
            s, separating_queries, separating_symbols, conformance_queries, conformance_symbols, learning_queries, learning_symbols = identify_and_learn(
                i, specifications, fingerprint_type, oracle_type1, oracle_type2, 'AL#', budget)
        elif method == 'IF-L#':
            s, separating_queries, separating_symbols, conformance_queries, conformance_symbols, learning_queries, learning_symbols = identify_and_learn(
                i, specifications, fingerprint_type, oracle_type1, oracle_type2, 'L#', budget)
        elif method == 'AL#':
            s, learning_queries, learning_symbols = adaptive_lsharp_learning(
                i, specifications, oracle_type2, budget)
        else:
            s, learning_queries, learning_symbols = lsharp_learning(
                i, oracle_type2, budget)

        if 'IF' in method:
            total_separating_queries += separating_queries
            total_separating_symbols += separating_symbols
            total_conformance_queries += conformance_queries
            total_conformance_symbols += conformance_symbols
        total_learning_queries += learning_queries
        total_learning_symbols += learning_symbols
        learned_models += (bisimilar(i, s) == True)

        if s not in [spec for (count, spec) in specifications]:
            specifications.append((i_id, s))

    return f"{method},{oracle_type1},{oracle_type2},{fingerprint_type},{total_separating_queries},{total_separating_symbols},{total_conformance_queries},{total_conformance_symbols},{total_learning_queries},{total_learning_symbols},{learned_models},{len(specifications)},{copies},{budget}\n"


def count_and_reset_queries(sul):
    temp_queries = sul.num_queries
    sul.num_queries = 0
    return temp_queries

def count_and_reset_symbols(sul):
    temp_symbols = sul.num_steps
    sul.num_steps = 0
    return temp_symbols





