from aalpy.utils import load_automaton_from_file, save_automaton_to_file
from aalpy.automata import MealyMachine, MealyState
from aalpy.SULs import MealySUL
from aalpy.base.SUL import CacheSUL
from ExactWpMethod import RandomWpMethodEqOracle
from aalpy.oracles import PerfectKnowledgeEqOracle
from aalpy.base import Oracle, SUL, DeterministicAutomaton, Automaton
from aalpy.learning_algs import run_Lsharp
from aalpy.utils.ModelChecking import bisimilar

import random
import os
import glob

def randomly_choose_state(mealy_states, sink, new):
    random_int = random.randint(0,mealy_states*3)
    state = None
    if random_int <= mealy_states:
        return random_int
    elif random_int <= mealy_states*2:
        return sink
    else:
        return new

def add_state(mealy, alphabet, outputs, sink):
    states = [MealyState(f"s{i}") for i in range(0, len(mealy.states)+1)]
    for state_id in range(0, len(mealy.states)):
        for i in alphabet:
            states[state_id].output_fun[i] = mealy.states[state_id].output_fun[i]
            states[state_id].transitions[i] = states[mealy.states.index(mealy.states[state_id].transitions[i])]
    new_id = len(mealy.states)
    for i in alphabet:
        states[new_id].output_fun[i] = random.choice(outputs)
        states[new_id].transitions[i] = states[randomly_choose_state(len(states)-1, sink, new_id)]
    for _ in range(3):
        states[random.randint(0,len(mealy.states))].transitions[random.choice(alphabet)] = states[new_id]
    mealy_machine = MealyMachine(states[0], states)
    return minimize_mealy(mealy_machine)

def remove_state(mealy, alphabet, sink):
    states = [MealyState(f"s{i}") for i in range(0, len(mealy.states))]
    if len(mealy.states) < 10:
        return mealy
    to_remove = random.randint(1,len(mealy.states)-1)
    while to_remove == sink:
        to_remove = random.randint(0,len(mealy.states))
    good_states = [i for i in range(0, len(mealy.states)) if i != to_remove]
    for state_id in range(0, len(mealy.states)):
        if state_id != to_remove:
            for i in alphabet:
                states[state_id].output_fun[i] = mealy.states[state_id].output_fun[i]
                dest = mealy.states.index(mealy.states[state_id].transitions[i])
                if dest == to_remove:
                    states[state_id].transitions[i] = states[random.choice(good_states)]
                else:
                    states[state_id].transitions[i] = states[mealy.states.index(mealy.states[state_id].transitions[i])]
    mealy_machine = MealyMachine(states[0], states)
    mealy_machine.states.remove(states[to_remove])
    print(mealy_machine)
    return minimize_mealy(mealy_machine)

def divert_transition(mealy, alphabet):
    if len(mealy.states) < 10:
        return mealy
    states = [MealyState(f"s{i}") for i in range(0, len(mealy.states))]
    for state_id in range(0, len(mealy.states)):
        for i in alphabet:
            states[state_id].output_fun[i] = mealy.states[state_id].output_fun[i]
            states[state_id].transitions[i] = states[mealy.states.index(mealy.states[state_id].transitions[i])]
    inp = random.choice(alphabet)
    orig = random.choice(states)
    dest = random.choice(states)
    orig.transitions[inp] = dest
    mealy_machine = MealyMachine(states[0], states)
    return minimize_mealy(mealy_machine)

def change_output(mealy, alphabet, outputs):
    if len(mealy.states) < 10:
        return mealy
    states = [MealyState(f"s{i}") for i in range(0, len(mealy.states))]
    for state_id in range(0, len(mealy.states)):
        for i in alphabet:
            states[state_id].output_fun[i] = mealy.states[state_id].output_fun[i]
            states[state_id].transitions[i] = states[mealy.states.index(mealy.states[state_id].transitions[i])]
    inp = random.choice(alphabet)
    orig = random.choice(states)
    outp = random.choice(outputs)
    orig.output_fun[inp] = outp
    mealy_machine = MealyMachine(states[0], states)
    return minimize_mealy(mealy_machine)

def minimize_mealy(mealy):
    mealy.minimize()
    while True:
        to_remove = []
        for s in mealy.states:
            if s.prefix == None:
                to_remove.append(s)
        if len(to_remove) == 0:
            return mealy
        for s in to_remove:
            mealy.states.remove(s)
        mealy.minimize()


names = ['DropBearOrig','BitViseOrig','OpenSSHOrig']
alphabet = ['UA_PK_NOK ', 'KEX30 ', 'SERVICE_REQUEST_AUTH ', 'SERVICE_REQUEST_CONN ', 'NEWKEYS ', 'CH_REQUEST_PTY ', 'CH_OPEN ', 'CH_DATA ', 'UA_PK_OK ', 'KEXINIT_PROCEED ', 'CH_CLOSE ', 'KEXINIT ', 'CH_EOF ']
outputs = set()
for i in names:
    mealy_machine = load_automaton_from_file(f'./SSH/{i}.dot', automaton_type='mealy')
    for st in mealy_machine.states:
        for inp in alphabet:
            outputs.add(st.output_fun[inp])
outputs = list(outputs)
tests = 500000
sink = 1
for s in range(10):
    random.seed(s+7713)
    model = load_automaton_from_file(f'./SSH/DropBearOrig.dot', automaton_type='mealy')
    new_name = f"DropBear_mut{s}"

    new_mm = add_state(model, alphabet, outputs, sink)
    new_mm = add_state(new_mm, alphabet, outputs, sink)
    new_mm = remove_state(new_mm, alphabet, sink)
    new_mm = divert_transition(new_mm, alphabet)
    new_mm = change_output(new_mm, alphabet, outputs)
    new_mm = change_output(new_mm, alphabet, outputs)


    sul = MealySUL(new_mm)
    eq_oracle = RandomWpMethodEqOracle(alphabet, sul, len(new_mm.states), num_tests=tests)
    # eq_oracle = PerfectKnowledgeEqOracle(alphabet, sul, new_mm)
    learned_mealy, info = run_Lsharp(alphabet, sul, eq_oracle, automaton_type='mealy',
                            extension_rule="SepSeq", separation_rule="ADS", return_data=True, max_learning_rounds=50, print_level=1)
    save_automaton_to_file(learned_mealy,f"{new_name}.dot")      



