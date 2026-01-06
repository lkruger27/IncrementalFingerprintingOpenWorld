from BLESUL import BLESUL
import os
from FailSafeLearning.FailSafeCacheSUL import FailSafeCacheSUL
from FailSafeLearning.StatePrefixEqOracleFailSafe import StatePrefixOracleFailSafe
from FailSafeRepeatLearning import FailSafeRepeatCacheSUL, FailSafeRepeatEqOracle
from aalpy.utils import load_automaton_from_file


def load_references(path : str):
    references = []
    for file in os.listdir(path):
         if file.endswith(".dot"):
             file_path = os.path.join(path, file)
             references.append(load_automaton_from_file(file_path, automaton_type='mealy'))
    return references

def print_intermediate_learning_info(sul : FailSafeRepeatCacheSUL, eq_oracle: FailSafeRepeatEqOracle, total_time):
    info = {
        'queries_learning': sul.num_queries,
        'steps_learning': sul.num_steps,
        'queries_eq_oracle': eq_oracle.num_queries,
        'steps_eq_oracle': eq_oracle.num_steps,
        'learning_rounds': eq_oracle.learning_rounds,
        'total_time': total_time,
        'cache_saved': sul.num_cached_queries,
        'eq_oracle_time' : eq_oracle.eq_query_time,
        'learning_time' : round(total_time - eq_oracle.eq_query_time, 2) 
    }

    print('-----------------------------------')
    print('Learning stopped unexpectedly.')
    print('Learning rounds        : {}'.format(info['learning_rounds']))
    print('Time (in seconds)')
    print('  Total                : {}'.format(info['total_time']))
    print('  Learning algorithm   : {}'.format(info['learning_time']))
    print('  Conformance checking : {}'.format(info['eq_oracle_time']))
    print('Learning Algorithm')
    print(' # Membership Queries  : {}'.format(info['queries_learning']))
    if 'cache_saved' in info.keys():
        print(' # MQ Saved by Caching : {}'.format(info['cache_saved']))
    print(' # Steps               : {}'.format(info['steps_learning']))
    print('Equivalence Query')
    print(' # Membership Queries  : {}'.format(info['queries_eq_oracle']))
    print(' # Steps               : {}'.format(info['steps_eq_oracle']))
    print('-----------------------------------')
    

def get_error_info(ble: BLESUL, cache: FailSafeCacheSUL, eq_oracle: StatePrefixOracleFailSafe):
    """
    Create error statistics.
    """

    error_info = {
        'replaced_values' : cache.cache.values_updated,
        'repeated_cached_queries': cache.cache.cached_non_deterministic_query,
        'non_det_output': cache.cache.non_corresponding_outputs,
        'non_det_query': cache.non_det_query_counter,
        'non_det_step': cache.non_det_step_counter,
        'connection_error': ble.connection_error_counter,
        'mq_reset_time': cache.reset_time,
        'cq_reset_time': eq_oracle.reset_time,
        'mq_physical_resets': cache.physical_reset,
        'cq_physical_resets': eq_oracle.physical_reset,

    }
    return error_info


def print_error_info(ble: BLESUL, cache: FailSafeCacheSUL, eq_oracle: StatePrefixOracleFailSafe):
    """
    Print error statistics.
    """
    error_info = get_error_info(ble,cache, eq_oracle)
  
    print('-----------------------------------')
    print('Connection errors:  {}'.format(error_info['connection_error']))
    print('Cached values updated: {}'.format(error_info['replaced_values']))
    print('Queries performed to determine correct output (before update): {}'.format(error_info['repeated_cached_queries']))
    print('Non-determinism in learning (before update): {}'.format(error_info['non_det_output']))
    print('Non-determinism in learning (after update): {}'.format(error_info['non_det_query']))
    print('Non-determinism in equivalence check (after update): {}'.format(error_info['non_det_step']))
    print('Physical resets during membership queries: {}'.format(error_info['mq_physical_resets']))
    print('Physical resets during conformance queries: {}'.format(error_info['cq_physical_resets']))
    print('Reset time during membership queries: {}'.format(error_info['mq_reset_time']))
    print('Reset time  during conformance queries: {}'.format(error_info['cq_reset_time']))
    print('-----------------------------------')


def print_error_info(ble: BLESUL):
    print('-----------------------------------')
    print('Connection errors:  {}'.format(ble.connection_error_counter))

def print_error_waiting_time(waiting_time: float):
    print('-----------------------------------')
    print('Connection errors:  {}'.format(waiting_time))
    
    