import sys
from pathlib import Path
from aalpy.SULs import MealySUL
from aalpy.learning_algs import run_Lsharp
from aalpy.utils import save_automaton_to_file, load_automaton_from_file
from aalpy.oracles import RandomWpMethodEqOracle
from aalpy.base import SUL


class ConnectionStartSUL(SUL):
    def __init__(self, mealySUL :MealySUL):
        super().__init__()
        self.sul = mealySUL

    def pre(self):
        self.sul.automaton.reset_to_initial()
        self.sul.step("scan_req")
        self.sul.step("connection_req")

    def post(self):
        pass

    def step(self, letter):
        return self.sul.step(letter)


"""
this script uses the learning interface that start learning after establishing a connection. Therefore, also the input alphabet is reduced.
"""

args_len = len(sys.argv) - 1

if args_len < 2:
    sys.exit("Too few arguments provided.\nUsage: python3 ble_learning_reference.py 'reference_path' 'connection_enabled'")

path = sys.argv[1]
connection_enabled = sys.argv[2]

print(path)


reference_path = Path(path, "reference.dot").absolute().as_posix()


reference = load_automaton_from_file(reference_path, 'mealy')

sul = MealySUL(reference)

if connection_enabled == "true":

    sul = ConnectionStartSUL(sul)

# # define the input alphabet
alphabet = ['length_req', 'length_rsp',  'feature_rsp', 'feature_req', 'version_req', 'mtu_req', 'pairing_req']
eq_oracle = RandomWpMethodEqOracle(alphabet, sul, num_tests=100)


learned_model = run_Lsharp(alphabet, sul, eq_oracle, cache_and_non_det_check=True, automaton_type='mealy', print_level=3)

learned_model_name = Path(path, "learned_model").absolute().as_posix()

# export automaton to file
save_automaton_to_file(learned_model, path=learned_model_name, file_type='dot')


