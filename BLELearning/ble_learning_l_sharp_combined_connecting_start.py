import sys
import constant
import time
from pathlib import Path
from BLESULConnectingStart import BLESULConnectingStart
from FailSafeRepeatLearning.FailSafeRepeatCacheSUL import FailSafeRepeatCacheSUL
from FailSafeRepeatLearning.FailSafeRepeatEqOracle import FailSafeRepeatEqOracle
from aalpy.oracles.WpMethodEqOracle import RandomWpMethodEqOracle
from aalpy.learning_algs import run_Lsharp
from aalpy.utils import save_automaton_to_file
from util import print_error_info, print_error_waiting_time, print_intermediate_learning_info


def print_additional_error_info(ble_sul: BLESULConnectingStart):
    # prints number of connection and non-deterministic errors
    print_error_info(ble_sul)

    if constant.PHYSICAL_RESET:
        print_error_waiting_time(ble_sul.waiting_time)

# rsrc = resource.RLIMIT_DATA
# soft, hard = resource.getrlimit(rsrc)
# resource.setrlimit(rsrc, (1024 * 1024 * 1024 * 12, hard))

"""
this script uses the learning interface that start learning after establishing a connection. Therefore, also the input alphabet is reduced.
"""

args_len = len(sys.argv) - 1

if args_len < 2:
    sys.exit("Too few arguments provided.\nUsage: python3 ble_learning.py 'serial_port' 'advertiser_address', ['result path']")

serial_port = sys.argv[1]
advertiser_address = sys.argv[2]

results_path = None
file_prefix = f"{int(time.time())}"

learned_model_name = 'learned_model'
if args_len == 3:
    results_path = Path(f"{file_prefix}_{sys.argv[3]}")

else:
    results_path = Path(f"{file_prefix}_learning_results")

results_path.mkdir(parents=True, exist_ok=True)
pcap_filename = Path(results_path, "learning_log").absolute().as_posix()
learned_model_name = Path(results_path, "learned_model").absolute().as_posix()

ble_sul = BLESULConnectingStart(serial_port, advertiser_address)

# enable our fail safe caching
# sul = FailSafeCacheSUL(ble_sul)
sul = FailSafeRepeatCacheSUL(ble_sul)

# define the input alphabet
alphabet = ['length_req', 'length_rsp',  'feature_rsp', 'feature_req', 'version_req', 'mtu_req', 'pairing_req']


# define a equivalence oracle
eq_oracle = RandomWpMethodEqOracle(alphabet, sul, num_tests=100)

eq_oracle_fail_safe = FailSafeRepeatEqOracle(eq_oracle, results_path)

# run the learning algorithm
# internal caching is disabled, since we require an error handling for possible non-deterministic behavior
# learned_model = run_Lstar(alphabet, sul, eq_oracle, automaton_type='mealy',cache_and_non_det_check=False, print_level=3)

total_time_start = time.time()

try: 
    learned_model = run_Lsharp(alphabet, sul, eq_oracle_fail_safe, cache_and_non_det_check=False, automaton_type='mealy', print_level=3)
except Exception as e:
    print_intermediate_learning_info(sul, eq_oracle_fail_safe,  time.time() - total_time_start)
    print_additional_error_info(ble_sul)
    raise e

save_automaton_to_file(learned_model, path=learned_model_name, file_type='dot')
print_additional_error_info(ble_sul)


#save pcap file of sent and received packages during learning
if constant.LOG_PCAP:
    ble_sul.save_pcap(pcap_filename + '.pcap')

# visualize the automaton
