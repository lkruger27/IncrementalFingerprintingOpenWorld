from aalpy.utils import load_automaton_from_file
from aalpy.utils.ModelChecking import bisimilar

from FingerprintingIngredients import algorithm, shallow_fingerprint, shallow_fingerprint_if
from multiprocessing import Process, Pool
import time

import sys
import random
import os
import glob
import argparse

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

            # check if implementation is specifications or not
            similar = False
            for (c, x) in specifications:
                if bisimilar(x, new_automaton):
                    similar = True
                    classification[c].add(counter)
                    break
            if not similar:
                classification[counter] = {counter}
                specifications.append((counter, new_automaton))

            implementations.append((counter, new_automaton))
            counter += 1
    for (repr_id, impl_class) in classification.items():
        print(f"impl class {repr_id} {impl_class}")
    return implementations, specifications, classification

def get_SSH_models(copies = 4):
    # Reading in the models and figuring out which are specifications
    implementations = []
    specifications = []
    classification = dict()
    counter = 0
    folder_path = './SSH/'
    for filename in glob.iglob(folder_path + '/*.dot', recursive=True):
        with open(filename, 'r') as f:
            new_automaton = load_automaton_from_file(
                filename, automaton_type='mealy')
            specifications.append((counter, new_automaton))
            implementations.append((counter, new_automaton))
            spec_count = counter
            classification[counter] = {counter}

            # This 4 indicates that we make 4 copies of each .dot file in the directory
            # We add them to the 'implementations' set but not the 'specifications' set
            for _ in range(copies):
                counter += 1
                classification[spec_count].add(counter)
                implementations.append((counter, new_automaton))
            counter += 1
    for (repr_id, impl_class) in classification.items():
        print(f"impl class {repr_id} {impl_class}")
    return implementations, specifications, classification

def get_MQTT_models(copies = 4):
    # Reading in the models and figuring out which are specifications
    implementations = []
    specifications = []
    classification = dict()
    counter = 0
    folder_path = 'mqtt/out/'
    for filename in glob.iglob(folder_path + '/*.dot', recursive=True):
        with open(filename, 'r') as f:
            new_automaton = load_automaton_from_file(
                filename, automaton_type='mealy')
            specifications.append((counter, new_automaton))
            implementations.append((counter, new_automaton))
            spec_count = counter
            classification[counter] = {counter}

            # This 4 indicates that we make 4 copies of each .dot file in the directory
            # We add them to the 'implementations' set but not the 'specifications' set
            for _ in range(copies):
                counter += 1
                classification[spec_count].add(counter)
                implementations.append((counter, new_automaton))
            counter += 1
    for (repr_id, impl_class) in classification.items():
        print(f"impl class {repr_id} {impl_class}")
    return implementations, specifications, classification

def get_BLE_models(copies = 4):
    # Reading in the models and figuring out which are specifications
    implementations = []
    specifications = []
    classification = dict()
    counter = 0
    folder_path = 'BLELearning/out/'
    for filename in glob.iglob(folder_path + '/*.dot', recursive=True):
        with open(filename, 'r') as f:
            new_automaton = load_automaton_from_file(
                filename, automaton_type='mealy')
            specifications.append((counter, new_automaton))
            implementations.append((counter, new_automaton))
            spec_count = counter
            classification[counter] = {counter}
            print(f'file {filename} new automaton {len(new_automaton.states)} inp {len(new_automaton.get_input_alphabet())}')

            # This 4 indicates that we make 4 copies of each .dot file in the directory
            # We add them to the 'implementations' set but not the 'specifications' set
            for _ in range(copies):
                counter += 1
                classification[spec_count].add(counter)
                implementations.append((counter, new_automaton))
            counter += 1
    for (repr_id, impl_class) in classification.items():
        print(f"impl class {repr_id} {impl_class}")
    return implementations, specifications, classification

def get_BLEDiff_models(copies = 4):
    # Reading in the models and figuring out which are specifications
    implementations = []
    specifications = []
    classification = dict()
    counter = 0
    folder_path = 'BLEDiff_Models/'
    for filename in glob.iglob(folder_path + '/*.dot', recursive=True):
        with open(filename, 'r') as f:
            new_automaton = load_automaton_from_file(
                filename, automaton_type='mealy')
            new_automaton.make_input_complete()
            specifications.append((counter, new_automaton))
            implementations.append((counter, new_automaton))
            spec_count = counter
            classification[counter] = {counter}
            print(f'file {filename} new automaton {len(new_automaton.states)} inp {len(new_automaton.get_input_alphabet())}')

            # This 4 indicates that we make 4 copies of each .dot file in the directory
            # We add them to the 'implementations' set but not the 'specifications' set
            for _ in range(copies):
                counter += 1
                classification[spec_count].add(counter)
                implementations.append((counter, new_automaton))
            counter += 1
    for (repr_id, impl_class) in classification.items():
        print(f"impl class {repr_id} {impl_class}")
    if len(implementations) == 0:
        raise Exception("BLEDiff models are not publicly available") 
    return implementations, specifications, classification

###########################################################################################################

def experiment_perfect_knowledge(implementations, specifications, classification, runs, processes, result_file):
    """ 
    Runs Experiment 1a which compares IF, RAL# and RL# when using a perfect teacher.
    """
    pool = Pool(processes=processes)
    results = []
    for x in range(runs):
        if x > 0:
            random.seed(x)
            random.shuffle(implementations)
        for oracle_type in ['PerfectKnowledge']:
            for method in ['IF-AL#', 'IF-L#', 'AL#', 'L#']:
                random.seed(x)
                if method == 'IF-AL#':
                    results.append(pool.apply_async(algorithm, args=(implementations, [], 'IF-AL#', 'adg', oracle_type, oracle_type, classification, result_file)))
                elif method == 'IF-L#':
                    results.append(pool.apply_async(algorithm, args=(implementations, [], 'IF-L#', 'adg', oracle_type, oracle_type, classification, result_file)))
                else:
                    results.append(pool.apply_async(algorithm, args=(implementations, [], method, None, oracle_type, oracle_type, classification, result_file)))
    pool.close()
    pool.join()
    with open(result_file, 'a') as file:
        for p in results:
            file.write(p.get())


def experiment_budget(implementations, specifications, classification, runs, processes, result_file, budget):
    """ 
    Runs Experiment 1b which compares IF, RAL# and RL# when using a maximum budget.
    """
    pool = Pool(processes=processes)
    results = []
    for x in range(runs):
        if x > 0:
            random.seed(x)
            random.shuffle(implementations)
        for method in ['IF-AL#', 'IF-L#', 'L#', 'AL#',]:
            random.seed(x)
            if method == 'IF-AL#':
                # algorithm(implementations, [], 'IF-AL#', 'adg', 'RandomWpBudget', 'RandomWpBudget', classification, result_file, 0, budget)
                results.append(pool.apply_async(algorithm, args=(implementations, [], 'IF-AL#', 'adg', 'RandomWpBudget', 'RandomWpBudget', classification, result_file, 0, budget)))
            elif method == 'IF-L#':
                results.append(pool.apply_async(algorithm, args=(implementations, [], 'IF-L#', 'adg', 'RandomWpBudget', 'RandomWpBudget', classification, result_file, 0, budget)))
            else:
                results.append(pool.apply_async(algorithm, args=(implementations, [], method, None, 'RandomWpBudget', 'RandomWpBudget', classification, result_file, 0, budget)))
    pool.close()
    pool.join()
    with open(result_file, 'a') as file:
        for p in results:
            file.write(p.get())

def experiment_RQ0_closed_world_fingerprint(implementations, specifications, classification, result_file):
    """ 
    Runs the motivation Experiment from Section 2 (Overview).
    It performs fingerprinting when starting with 11, 21 or 22 specifications of the 22 of TLS.
    """
    runs = 10
    for start_spec in [11, 21, 22]:
        for x in range(runs):
            random.seed(x)
            random.shuffle(specifications)
            specs = specifications[:start_spec]
            shallow_fingerprint(implementations, list(specs), classification, result_file, 'sep_seq', None, len(specs))

def experiment_RQ0_IF(implementations, specifications, classification, result_file):
    """ 
    Runs the motivation Experiment from Section 2 (Overview).
    It performs IF without learning but with conformance testing when starting with 11, 21 or 22 specifications of the 22 of TLS.
    """
    runs = 10
    pool = Pool(processes=4)
    results = []
    for start_spec in [11, 21, 22]:
        for x in range(runs):
            random.seed(x)
            random.shuffle(specifications)
            random.shuffle(implementations)
            specs = specifications[:start_spec]
            results.append(pool.apply_async(shallow_fingerprint_if, args=(implementations, list(specs), classification, result_file, 'adg', start_spec, 'RandomWp100')))
    pool.close()
    pool.join()
    with open(result_file, 'a') as file:
        for p in results:
            file.write(p.get())

def experiment_RQ0_LSharp(implementations, specifications, classification, result_file):
    """ 
    Runs the motivation Experiment from Section 2 (Overview).
    It performs R-L# with more conformance testing.
    """
    runs = 10
    pool = Pool(processes=4)
    results = []
    for x in range(runs):
        random.seed(x)
        random.shuffle(implementations)
        results.append(pool.apply_async(algorithm, args=(implementations, [], 'L#', 'adg', 'RandomWp100', 'RandomWp100', classification, result_file)))
        results.append(pool.apply_async(algorithm, args=(implementations, [], 'L#', 'adg', 'RandomWp500', 'RandomWp500', classification, result_file)))
    pool.close()
    pool.join()
    with open(result_file, 'a') as file:
        for p in results:
            file.write(p.get())

def experiment_RQ1_RQ2(implementations, specifications, classification, runs, processes, result_file):
    """ 
    Runs Experiment 2 which encompasses Experiment 1c. 
    The experiment compares IF, RAL# and RL# when using different fingerprinting, conformance testing and learning algorithms for IF.
    """
    pool = Pool(processes=processes)
    results = []
    for x in range(runs):
        if x > 0:
            random.seed(x)
            random.shuffle(implementations)
        for oracle_type in ['WpK', 'RandomWp100', 'RandomWord1000']:
            for method in ['AL#', 'IF-AL#', 'IF-L#', 'L#']:
                random.seed(x)
                if method in ['IF-AL#', 'IF-L#']:
                    for fingerprint_type in ['sep_seq', 'adg']:
                        results.append(pool.apply_async(algorithm, args=(implementations, [], method, fingerprint_type, oracle_type, oracle_type, classification, result_file)))
                else:
                    results.append(pool.apply_async(algorithm, args=(implementations, [], method, None, oracle_type, oracle_type, classification, result_file)))
    pool.close()
    pool.join()
    with open(result_file, 'a') as file:
        for p in results:
            file.write(p.get())

def experiment_RQ1_additional(implementations, specifications, classification, runs, processes, result_file):
    """ 
    Runs additional experiments related to Experiment 1.
    It compares IF, RAL# and RL# when using different conformance testing techniques.
    """
    pool = Pool(processes=processes)
    results = []
    for x in range(runs):
        if x > 0:
            random.seed(x)
            random.shuffle(implementations)
            for oracle_type in ['RandomWp25', 'RandomWp50','RandomWp100', 'RandomWp200', 'RandomWp500']:
                results.append(pool.apply_async(algorithm, args=(implementations, [], 'AL#', 'adg', oracle_type, oracle_type, classification, result_file)))
                results.append(pool.apply_async(algorithm, args=(implementations, [], 'IF-AL#', 'adg', oracle_type, oracle_type, classification, result_file)))
    pool.close()
    pool.join()
    with open(result_file, 'a') as file:
        for p in results:
            file.write(p.get())

def experiment_RQ2_additional(implementations, specifications, classification, runs, processes, result_file):
    """ 
    Runs additional experiments related to Experiment 2.
    It compares IF when using different combinations of conformance testing techniques for the learning and fingerprinting CQ.
    """
    pool = Pool(processes=processes)
    results = []
    for x in range(runs):
        if x > 0:
            random.seed(x)
            random.shuffle(implementations)
        for oracle_type1 in ['RandomWp25', 'RandomWp50', 'RandomWp100']:
            for oracle_type2 in ['RandomWp25', 'RandomWp50', 'RandomWp100']:
                random.seed(x)
                results.append(pool.apply_async(algorithm, args=(implementations, [], 'IF-AL#', 'adg', oracle_type1, oracle_type2, classification, result_file)))
    pool.close()
    pool.join()
    with open(result_file, 'a') as file:
        for p in results:
            file.write(p.get())

def experiment_RQ3(implementations, specifications, classification, runs, processes, result_file):
    """ 
    Runs Experiment 3 which investigates the influence of learning misclassifications on fingerprinting misclassifications.
    """
    pool = Pool(processes=processes)
    results = []
    for x in range(runs):
        if x > 0:
            random.seed(x)
            random.shuffle(implementations)
        for oracle_type1 in ['RandomWp25', 'RandomWp50', 'RandomWp100']:
            random.seed(x)
            results.append(pool.apply_async(algorithm, args=(implementations, [], 'IF-AL#', 'adg', 'RandomWp100', oracle_type1, classification, result_file)))
    pool.close()
    pool.join()
    with open(result_file, 'a') as file:
        for p in results:
            file.write(p.get())

def experiment_duplicates(func, runs, processes, result_file):
    """ 
    Runs an Experiment mentioned in the discussion.
    """
    pool = Pool(processes=processes)
    results = []
    for copies in [0, 4, 9, 14, 19, 24]:
        implementations, specifications, classification = func(copies)
        for x in range(runs):
            random.seed(x)
            random.shuffle(implementations)
            for method in ['AL#', 'IF-AL#', 'L#']:
                random.seed(x)
                results.append(pool.apply_async(algorithm, args=(implementations, [], method, 'adg', 'RandomWp100', 'RandomWp100', classification, result_file, copies)))
    pool.close()
    pool.join()
    with open(result_file, 'a') as file:
        for p in results:
            file.write(p.get())

if __name__ == "__main__":
    parser = argparse.ArgumentParser("simple_example")
    parser.add_argument("experiment", help="Experiment to run ('RQ0_closed_world_fingerprint', 'RQ0_IF', 'RQ0_LSharp', 'RQ1_perfect_knowledge', 'RQ1_Budget', 'RQ1_RQ2', 'RQ1_additional', 'RQ2_additional', 'RQ3', 'duplicates').", type=str)
    parser.add_argument("benchmark", help="Benchmark to use ('TLS', 'SSH', 'MQTT', 'BLE', 'BLEDiff).", type=str)
    parser.add_argument("-r", "--runs", help="Runs to execute, default = 20.", type=int, default=20)
    parser.add_argument("-p", "--processes", help="Processes to use, default = 2.", type=int, default=2)
    args = parser.parse_args()
    
    experiment = args.experiment 
    benchmark = args.benchmark 
    runs = args.runs
    processes = args.processes
             
    budget = None
    if benchmark == "TLS":
        implementations, specifications, classification = get_TLS_models()
        func = get_TLS_models
        budget = 100000
    elif benchmark == "SSH":
        implementations, specifications, classification = get_SSH_models()
        func = get_SSH_models
        budget = 750000
    elif benchmark == "MQTT":
        implementations, specifications, classification = get_MQTT_models()
        func = get_MQTT_models
        budget = 100000
    elif benchmark == "BLE":
        implementations, specifications, classification = get_BLE_models()
        func = get_BLE_models
        budget = 2500
    elif benchmark == "BLEDiff":
        implementations, specifications, classification = get_BLEDiff_models()
        func = get_BLEDiff_models
        budget = 10000
    
    result_file = f'./fingerprinting/results/{experiment}_new_{benchmark}.csv'
    if not os.path.isfile(result_file): # Create the file 
        with open(result_file, mode="w", newline="", encoding="utf-8") as f: 
            if "RQ0" in experiment and "RQ0_LSharp" not in experiment:
                f.write("algorithm,oracle_type,fingerprint_type,fingerprint_queries,fingerprint_symbols,conformance_queries,conformance_symbols,learning_queries,learning_symbols,correctly_learned_models,found_specifications,no_fingerprint,start_specs\n") 
            else:
                f.write("method,oracle_type1,oracle_type2,fingerprint_type,total_separating_queries,total_separating_symbols,total_conformance_queries,total_conformance_symbols,total_learning_queries,total_learning_symbols,learned_models,len(specifications),start_specs,budget\n")

    if experiment == "RQ0_closed_world_fingerprint":
        if benchmark != "TLS":
            raise Exception("This experiment is only defined for TLS")
        experiment_RQ0_closed_world_fingerprint(implementations, specifications, classification, result_file)
    elif experiment == "RQ0_IF":
        if benchmark != "TLS":
            raise Exception("This experiment is only defined for TLS")
        experiment_RQ0_IF(implementations, specifications, classification, result_file)
    elif experiment == "RQ0_LSharp":
        experiment_RQ0_LSharp(implementations, specifications, classification, result_file)
    elif experiment == "RQ1_perfect_knowledge":
        experiment_perfect_knowledge(implementations, specifications, classification, runs, processes, result_file)
    elif experiment == "RQ1_Budget":
        experiment_budget(implementations, specifications, classification, runs, processes, result_file, budget)
    elif experiment == "RQ1_RQ2":
        experiment_RQ1_RQ2(implementations, specifications, classification, runs, processes, result_file)
    elif experiment == "RQ1_additional":
        if benchmark != "TLS" or benchmark != "SSH":
            raise Exception("This experiment is only defined for TLS and SSH")
        experiment_RQ1_additional(implementations, specifications, classification, runs, processes, result_file)
    elif experiment == "RQ2_additional":
        experiment_RQ2_additional(implementations, specifications, classification, runs, processes, result_file)
    elif experiment == "RQ3":
        experiment_RQ3(implementations, specifications, classification, runs, processes, result_file)
    elif experiment == "duplicates":
        if benchmark != "MQTT":
            raise Exception("This experiment is only defined for MQTT")
        experiment_duplicates(runs, processes, result_file)
