from aalpy.utils import load_automaton_from_file
from aalpy.utils.ModelChecking import bisimilar
from FingerprintingIngredients import identify_and_learn, adaptive_lsharp_learning, lsharp_learning

from pathlib import Path
import sys
import os
import glob
import argparse
import random

def incremental_fingerprinting(dirt, implementations, specifications, algorithm, fingerprint_type, oracle_type_fingerprint, oracle_type_conformance, learning_algorithm, print_mapping):
    """ 
    General algorithm that runs IF, RAL# or RL# and keeps track of the specifications
    """
    info_dict = dict()
    info_dict['total_separating_queries'] = 0
    info_dict['total_separating_symbols'] = 0
    info_dict['total_conformance_queries'] = 0
    info_dict['total_conformance_symbols'] = 0
    info_dict['total_learning_queries'] = 0
    info_dict['total_learning_symbols'] = 0
    mapping = dict()

    for (s_n, s) in specifications:
        mapping[s_n] = set()

    info_dict['learned_models'] = 0
    for n, i in implementations:
        if algorithm == 'IF':
            s, separating_queries, separating_symbols, conformance_queries, conformance_symbols, learning_queries, learning_symbols = identify_and_learn(
                i, specifications, fingerprint_type, oracle_type_fingerprint, oracle_type_conformance, learning_algorithm, budget=None)
        elif method == 'AL#':
            s, learning_queries, learning_symbols = adaptive_lsharp_learning(
                i, specifications, oracle_type_conformance, budget)
        else:
            s, learning_queries, learning_symbols = lsharp_learning(
                i, oracle_type_conformance, budget)

        if algorithm == 'IF':
            info_dict['total_separating_queries'] += separating_queries
            info_dict['total_separating_symbols'] += separating_symbols
            info_dict['total_conformance_queries'] += conformance_queries
            info_dict['total_conformance_symbols'] += conformance_symbols
        info_dict['total_learning_queries'] += learning_queries
        info_dict['total_learning_symbols'] += learning_symbols
        info_dict['learned_models'] += (bisimilar(i, s) == True)

        s_n = next(
            (s_n for (s_n, spec) in specifications if spec == s), None)
        if s_n:
            mapping[s_n].add(n)
        else:
            specifications.append((n, s))
            mapping[n] = set()

    if algorithm == "IF":
        print_learning_info_if(info_dict, dirt, implementations, specifications, algorithm, fingerprint_type,
                               oracle_type_fingerprint, oracle_type_conformance, learning_algorithm)
    else:
        print_learning_info_not_if(info_dict, dirt, implementations,
                                   specifications, algorithm, oracle_type_conformance)

    if print_mapping:
        print_constructed_mapping(mapping)



def get_models_in_dir(dir, specs=False):
    models = []
    for filename in glob.iglob(dir + '**/*.dot', recursive=True):
        with open(filename, 'r') as f:
            new_automaton = load_automaton_from_file(
                filename, automaton_type='mealy')
            if specs == False or not any([True for (name,automaton) in models if automaton == new_automaton]):
                models.append((filename, new_automaton))
    return models


def print_learning_info_if(info: dict, dirt, implementations, specifications, algorithm, fingerprint_type, oracle_type_fingerprint, oracle_type_conformance, learning_algorithm):
    """
    Print learning statistics when using the IF algorithm.
    """
    print('-----------------------------------')
    print(f'Learning Finished of {dirt} using {algorithm} with:')
    print(f'  - Fingerprint Algorithm: {fingerprint_type},\n  - Fingerprint Conformance Check: {oracle_type_fingerprint},\n  - Learning Algorithm: {learning_algorithm},\n  - Learning Conformance Check: {oracle_type_conformance}.')
    print('-----------------------------------')
    print('Accuracy')
    print(' # Number of Implementations          : {}'.format(len(implementations)))
    print(' # Found Specifications               : {}'.format(len(specifications)))
    print(' # Correctly Learned Implementations  : {}%'.format(
        round(100*info['learned_models']/len(implementations), 1)))
    print('-----------------------------------')
    print('Fingerprinting')
    print(' # Queries  : {}'.format(info['total_separating_queries']))
    print(' # Steps    : {}'.format(info['total_separating_symbols']))
    print('Fingerprint Conformance Check')
    print(' # Queries  : {}'.format(info['total_conformance_queries']))
    print(' # Steps    : {}'.format(info['total_conformance_symbols']))
    print('Learning')
    print(' # Queries  : {}'.format(info['total_learning_queries']))
    print(' # Steps    : {}'.format(info['total_learning_symbols']))
    print('-----------------------------------')


def print_learning_info_not_if(info: dict, dirt, implementations, specifications, algorithm, oracle_type_conformance):
    """
    Print learning statistics when using the RL# or RAL# algorithm.
    """
    print('-----------------------------------')
    print(
        f'Learning Finished of {dirt} using {algorithm} with Conformance Check {oracle_type_conformance}.')
    print('-----------------------------------')
    print('Accuracy')
    print(' # Number of Implementations          : {}'.format(len(implementations)))
    print(' # Found Specifications               : {}'.format(len(specifications)))
    print(' # Correctly Learned Implementations  : {}%'.format(
        round(100*info['learned_models']/len(implementations), 1)))
    print('-----------------------------------')
    print('Learning')
    print(' # Queries  : {}'.format(info['total_learning_queries']))
    print(' # Steps    : {}'.format(info['total_learning_symbols']))
    print('-----------------------------------')

def print_constructed_mapping(mapping):
    print('Mapping:')
    for n_s in mapping.keys():
        print(f"Specifications {n_s}:")
        for n_i in mapping[n_s]:
            print(f" - {n_i}")


def check_args(args):
    assert args.algorithm in [
        'IF', 'RL#', 'RAL#'], f"Algorithm should be one of ('IF', 'RL#', 'RAL#')"
    assert os.path.isdir(Path(args.implementations_directory)
                         ), f"{args.implementations_directory} is not a directory"
    assert args.fcq and args.fcq in ['PerfectKnowledge', 'RandomWord1000',
                                     'RandomWp100'], f"Fingerprinting conformance check should be one of ('PerfectKnowledge', 'RandomWord1000', 'RandomWp100')"
    assert args.lcq and args.lcq in ['PerfectKnowledge', 'RandomWord1000',
                                     'RandomWp100'], f"Learning conformance check should be one of ('PerfectKnowledge', 'RandomWord1000', 'RandomWp100')"
    assert args.fingerprint and args.fingerprint in [
        'SepSeq', 'ADG'], f"Fingerprinting algorithm should be one of ('SepSeq', 'ADG')"
    assert args.learning and args.learning in [
        'AL#', 'L#'], f"Learning algorithm should be one of ('AL#', 'L#')"
    if args.algorithm != 'IF' and args.fcq is not None and args.fingerprint is not None and args.learning is not None:
        print(
            "Arguments 'fcq', 'fingerprint' and 'learning' are ignored when not using IF.")
    if args.specifications_directory is not None:
        assert os.path.isdir(Path(args.specifications_directory)
                             ), f"{args.specifications_directory} is not a directory"


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Example")
    parser.add_argument("implementations_directory",
                        help="Directory with the implementations.", type=str)
    parser.add_argument(
        "algorithm", help="Algorithm to use ('IF', 'RL#', 'RAL#').", type=str)
    parser.add_argument("-specifications_directory",
                        help="Directory with the specifications.", type=str)
    parser.add_argument(
        "-fcq", help="Conformance checking algorithm to use after fingerprinting ('PerfectKnowledge', 'RandomWord1000', 'RandomWp100').", type=str, default='RandomWp100')
    parser.add_argument(
        "-lcq", help="Conformance checking algorithm to use after learning ('PerfectKnowledge', 'RandomWord1000', 'RandomWp100').", type=str, default='RandomWp100')
    parser.add_argument(
        "-fingerprint", help="Fingerprinting algorithm ('SepSeq', 'ADG').", type=str, default='ADG')
    parser.add_argument(
        "-learning", help="Learning algorithm ('AL#', 'L#').", type=str, default="AL#")
    parser.add_argument(
        "-print_mapping", help="Boolean to indicate whether the mapping should be printed.", type=str, default="False")
    parser.add_argument(
        "-x", help="Seed.", type=int, default=0)
    args = parser.parse_args()

    check_args(args)
    impls = get_models_in_dir(args.implementations_directory)

    specs = []
    if args.specifications_directory:
        specs = get_models_in_dir(args.specifications_directory, specs=True)
        print(f"Starting with {len(specs)} specifications from {args.specifications_directory}")

    print_mapping = args.print_mapping == "True"
    random.seed(args.x)
    incremental_fingerprinting(args.implementations_directory, impls, specs,
                               args.algorithm, args.fingerprint, args.fcq, args.lcq, args.learning, print_mapping)
