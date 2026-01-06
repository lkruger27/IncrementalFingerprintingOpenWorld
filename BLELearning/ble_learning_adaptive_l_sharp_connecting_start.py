import sys
import constant
import time
from BLESULConnectingStart import BLESULConnectingStart
from FailSafeRepeatLearning.FailSafeRepeatCacheSUL import FailSafeRepeatCacheSUL
from FailSafeRepeatLearning.FailSafeRepeatEqOracle import FailSafeRepeatEqOracle
from aalpy.oracles.WpMethodEqOracle import RandomWpMethodEqOracle
from aalpy.learning_algs import run_Lsharp, run_adaptive_Lsharp
from aalpy.utils import save_automaton_to_file, load_automaton_from_file
from util import print_error_info, print_intermediate_learning_info, load_references

# rsrc = resource.RLIMIT_DATA
# soft, hard = resource.getrlimit(rsrc)
# resource.setrlimit(rsrc, (1024 * 1024 * 1024 * 12, hard))

"""
this script uses the learning interface that start learning after establishing a connection. Therefore, also the input alphabet is reduced.
"""

args_len = len(sys.argv) - 1

if args_len < 3:
    sys.exit("Too few arguments provided.\nUsage: python3 ble_learning_adaptive_l_sharp_connecting_start.py 'serial_port' 'advertiser_address', 'reference_path' , ['pcap- & model-filename']")

serial_port = sys.argv[1]
advertiser_address = sys.argv[2]
reference_path = sys.argv[3]
learned_model_name = 'learned_model'
if args_len == 4:
    pcap_filename = sys.argv[4]
    learned_model_name = sys.argv[4]
else:
    pcap_filename = 'learning_data'

ble_sul = BLESULConnectingStart(serial_port, advertiser_address)

# enable our fail safe caching
# sul = FailSafeCacheSUL(ble_sul)
sul = FailSafeRepeatCacheSUL(ble_sul)

# define the input alphabet
alphabet = ['length_req', 'length_rsp',  'feature_rsp', 'feature_req', 'version_req', 'mtu_req', 'pairing_req']


# define a equivalence oracle
eq_oracle = RandomWpMethodEqOracle(alphabet, sul, num_tests=100)

eq_oracle_fail_safe = FailSafeRepeatEqOracle(eq_oracle)

# run the learning algorithm
# internal caching is disabled, since we require an error handling for possible non-deterministic behavior
# learned_model = run_Lstar(alphabet, sul, eq_oracle, automaton_type='mealy',cache_and_non_det_check=False, print_level=3)

# ref_0 = load_automaton_from_file("raspberry_pi_references/reference_0.dot", 'mealy')
# ref_1 = load_automaton_from_file("raspberry_pi_references/reference_1.dot", 'mealy')

references = load_references(reference_path)

total_time_start = time.time()

try: 
    learned_model = run_adaptive_Lsharp(alphabet, sul, references, eq_oracle_fail_safe, cache_and_non_det_check=False, automaton_type='mealy', print_level=3)
    # learned_model = run_Lsharp(alphabet, sul, eq_oracle_fail_safe, cache_and_non_det_check=False, automaton_type='mealy', print_level=3)
except Exception as e:
    print_intermediate_learning_info(sul, eq_oracle_fail_safe,  time.time() - total_time_start)
    raise e

save_automaton_to_file(learned_model, path=learned_model_name, file_type='dot')

# prints number of connection and non-deterministic errors
print_error_info(ble_sul)

print('-----------------------------------')
print('Reset hold time: {}'.format(round(ble_sul.waiting_time,2)))
print('-----------------------------------')

#save pcap file of sent and received packages during learning
if constant.LOG_PCAP:
    ble_sul.save_pcap(pcap_filename + '.pcap')

# visualize the automaton
