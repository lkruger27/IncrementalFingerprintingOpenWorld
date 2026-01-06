from aalpy.utils import load_automaton_from_file
from aalpy.utils.ModelChecking import bisimilar
from aalpy.utils import load_automaton_from_file, save_automaton_to_file
from aalpy.automata import MealyMachine, MealyState
from aalpy.SULs import MealySUL
from aalpy.base.SUL import CacheSUL
from ExactWpMethod import RandomWpMethodEqOracle
from aalpy.base import Oracle, SUL, DeterministicAutomaton
from aalpy.learning_algs import run_Lsharp
import time
import sys
import random
import os
import glob
import argparse

def state_characterization_set(hypothesis, alphabet, state):
    """
    Return a list of sequences that distinguish the given state from all other states in the hypothesis.
    Args:
        hypothesis: hypothesis automaton
        alphabet: input alphabet
        state: state for which to find distinguishing sequences
    """
    result = []
    for i in range(len(hypothesis.states)):
        if hypothesis.states[i] == state:
            continue
        seq = hypothesis.find_distinguishing_seq(state, hypothesis.states[i], alphabet)
        if seq:
            result.append(tuple(seq))
    return result


def first_phase_it(alphabet, state_cover, depth, char_set):
    """
    Return an iterator that generates all possible sequences for the first phase of the Wp-method.
    Args:
        alphabet: input alphabet
        state_cover: list of states to cover
        depth: maximum length of middle part
        char_set: characterization set
    """
    char_set = char_set or [()]
    for d in range(depth):
        middle = product(alphabet, repeat=d)
        for m in middle:
            for s in state_cover:
                for c in char_set:
                    yield s + m + c


def second_phase_it(hyp, alphabet, difference, depth):
    """
    Return an iterator that generates all possible sequences for the second phase of the Wp-method.
    Args:
        hyp: hypothesis automaton
        alphabet: input alphabet
        difference: set of sequences that are in the transition cover but not in the state cover
        depth: maximum length of middle part
    """
    state_mapping = {}
    for d in range(depth):
        middle = product(alphabet, repeat=d)
        for mid in middle:
            for t in difference:
                _ = hyp.execute_sequence(hyp.initial_state, t + mid)
                state = hyp.current_state
                if state not in state_mapping:
                    state_mapping[state] = state_characterization_set(hyp, alphabet, state)

                for sm in state_mapping[state]:
                    yield t + mid + sm


class RandomWpMethodEqOracle(Oracle):
    """
    Randomized version of the Wp-Method equivalence oracle.
    Random walks stem from fixed prefix (path to the state). At the end of the random
    walk an element from the characterization set is added to the test case.
    """

    def __init__(self, alphabet: list, sul: SUL, expected_states, min_length=1, expected_length=5, num_tests=5000000):
        """
        Args:

            alphabet: input alphabet

            sul: system under learning

            walks_per_state: number of random walks that should start from each state

            walk_len: length of random walk
        """

        super().__init__(alphabet, sul)
        self.min_length = min_length
        self.expected_length = expected_length
        self.bound = num_tests
        self.expected_states = expected_states

    def find_cex(self, hypothesis, cache = False):
        if len(hypothesis.states) == self.expected_states:
            print("Early Stopping!")
            return None
        # fix for non-minimal intermediate hypothesis that can occur in KV
        hypothesis.characterization_set = hypothesis.compute_characterization_set()
        if not hypothesis.characterization_set:
            hypothesis.characterization_set = [(a,) for a in hypothesis.get_input_alphabet()]

        state_mapping = {s : state_characterization_set(hypothesis, self.alphabet, s) for s in hypothesis.states}

        for _ in range(self.bound):
            state = random.choice(hypothesis.states)
            input = state.prefix
            limit = self.min_length
            while limit > 0 or random.random() > 1 / (self.expected_length + 1):
                letter = random.choice(self.alphabet)
                input += (letter,)
                limit -= 1
            if random.random() > 0.5:
                # global suffix with characterization_set
                input += random.choice(hypothesis.characterization_set)
            else:
                # local suffix
                _ = hypothesis.execute_sequence(hypothesis.initial_state, input)
                if state_mapping[hypothesis.current_state]:
                    input += random.choice(state_mapping[hypothesis.current_state])
                else:
                    continue

            self.reset_hyp_and_sul(hypothesis)
            for ind, letter in enumerate(input):
                out_hyp = hypothesis.step(letter)
                out_sul = self.sul.step(letter)
                self.num_steps += 1

                if out_hyp != out_sul:
                    self.sul.post()
                    return input[: ind + 1]
        return None

def get_TLS_models():
    # Reading in the models and figuring out which are specifications
    implementations = []
    specifications = []
    classification = dict()
    counter = 0
    folder_path = './TLS/'
    for filename in glob.iglob(folder_path + '**/*.dot', recursive=True):
        with open(filename, 'r') as f:
            new_automaton = load_automaton_from_file(
                filename, automaton_type='mealy')
            if counter == 0:
                alphabet = new_automaton.get_input_alphabet()

            # check if implementation is specifications or not
            similar = False
            for (c, x, n) in specifications:
                if bisimilar(x, new_automaton):
                    similar = True
                    classification[c].add(counter)
                    break
            if not similar:
                classification[counter] = {counter}
                specifications.append((counter, new_automaton, filename))

            implementations.append((counter, new_automaton))
            counter += 1
    for (repr_id, impl_class) in classification.items():
        print(f"impl class {repr_id} {impl_class}")
    return implementations, specifications, classification, alphabet

def experiment():
    with open('./TLS/L#_results.csv','a') as f:
        f.write(f"model,eq_oracle,cop,tests,states,equivalent,learning_queries,learning_steps,eq_queries,eq_steps\n")
    implementations, specifications, classification, alphabet = get_TLS_models()
    tests = 500000
    for s in range(30):
        random.seed(s)
        for (c,m,name) in specifications:
            sul = MealySUL(m)
            eq_oracle = RandomWpMethodEqOracle(alphabet, sul, len(m.states), num_tests=tests)

            learned_mealy, info = run_Lsharp(alphabet, sul, eq_oracle, automaton_type='mealy',
                                    extension_rule="SepSeq", separation_rule="ADS", return_data=True, max_learning_rounds=50, print_level=1)
            with open('./TLS/L#_results.csv','a') as f:
                f.write(f"{name},randomWp,{len(classification[c])},{tests},{info['automaton_size']},{len(m.states)==info['automaton_size']},{info['queries_learning']},{info['steps_learning']},{info['queries_eq_oracle']},{info['steps_eq_oracle']}\n")

def evaluation():
    df = pd.read_csv("./TLS/L#_results.csv")
    df['modelname'] = df['model'].apply(lambda x: x[6:-17])
    df['Inputs'] = 11
    df['Copies'] = df['cop']
    df['Learning Symbols'] = df['learning_queries'] + df['learning_steps']
    df['Testing Symbols'] = df['eq_queries'] + df['eq_steps']
    df = df.groupby(['modelname']).mean(numeric_only=True)
    print(df.to_latex(columns=['modelname', 'states', 'Inputs', 'Copies', 'Learning Symbols', 'Testing Symbols'],float_format="%.0f" ))

experiment()
evaluation()
