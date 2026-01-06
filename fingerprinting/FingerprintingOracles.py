from itertools import chain, product

from aalpy.base.Oracle import Oracle
from aalpy.base.SUL import SUL
import random
from random import shuffle, randint, choice


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


class WpMethodEqOracle(Oracle):
    """
    Implements the Wp-method equivalence oracle.
    """

    def __init__(self, alphabet: list, sul: SUL, max_number_of_states=4):
        super().__init__(alphabet, sul)
        self.m = max_number_of_states
        self.cache = []

    def find_cex(self, hypothesis, cache=False):
        if not hypothesis.characterization_set:
            hypothesis.characterization_set = hypothesis.compute_characterization_set()

        transition_cover = set(
            state.prefix + (letter,)
            for state in hypothesis.states
            for letter in self.alphabet
        )

        state_cover = set(state.prefix for state in hypothesis.states)
        difference = transition_cover.difference(state_cover)
        depth = self.m + 1 - len(hypothesis.states)
        # first phase State Cover * Middle * Characterization Set
        first_phase = first_phase_it(self.alphabet, state_cover, depth, hypothesis.characterization_set)

        # second phase (Transition Cover - State Cover) * Middle * Characterization Set
        # of the state that the prefix leads to
        second_phase = second_phase_it(hypothesis, self.alphabet, difference, depth)
        test_suite = chain(first_phase, second_phase)

        for seq in test_suite:
            if len(seq) > 0:
                sul_out = self.sul.query(seq)
                hyp_out = hypothesis.execute_sequence(hypothesis.initial_state,seq)
                if cache:
                    self.cache.append((seq, sul_out))
                if tuple(sul_out) != tuple(hyp_out):
                    return seq

        return None


class WpMethodEqOracleK(Oracle):
    """
    Implements the Wp-method equivalence oracle.
    """

    def __init__(self, alphabet: list, sul: SUL, k=2):
        super().__init__(alphabet, sul)
        self.k = k
        self.cache = []

    def find_cex(self, hypothesis, cache=False):
        if not hypothesis.characterization_set:
            hypothesis.characterization_set = hypothesis.compute_characterization_set()

        transition_cover = set(
            state.prefix + (letter,)
            for state in hypothesis.states
            for letter in self.alphabet
        )

        state_cover = set(state.prefix for state in hypothesis.states)
        difference = transition_cover.difference(state_cover)
        depth = self.k + 1
        # first phase State Cover * Middle * Characterization Set
        first_phase = first_phase_it(self.alphabet, state_cover, depth, hypothesis.characterization_set)

        # second phase (Transition Cover - State Cover) * Middle * Characterization Set
        # of the state that the prefix leads to
        second_phase = second_phase_it(hypothesis, self.alphabet, difference, depth)
        test_suite = chain(first_phase, second_phase)

        for seq in test_suite:
            if len(seq) > 0:
                sul_out = self.sul.query(seq)
                hyp_out = hypothesis.execute_sequence(hypothesis.initial_state,seq)
                if cache:
                    self.cache.append((seq, sul_out))
                if tuple(sul_out) != tuple(hyp_out):
                    return seq

        return None

class BudgetRandomWpMethodEqOracle(Oracle):
    """
    Randomized version of the Wp-Method equivalence oracle.
    Random walks stem from fixed prefix (path to the state). At the end of the random
    walk an element from the characterization set is added to the test case.
    """

    def __init__(self, alphabet: list, sul: SUL, target, budget, min_length=3, expected_length=8):
        """
        Args:

            alphabet: input alphabet

            sul: system under learning

            walks_per_state: number of random walks that should start from each state

            walk_len: length of random walk
        """

        super().__init__(alphabet, sul)
        self.expected_length = expected_length
        self.min_length = min_length
        self.target = target
        print(f'initial budget {budget}')
        self.budget = budget
        self.cache = []

    def find_cex(self, hypothesis, cache = False):
        if hypothesis == self.target:
            self.sul.num_steps += (self.budget - (self.sul.num_queries + self.sul.num_steps))
            print(f' Hyp correct, avoid doing tests {self.sul.num_steps}')
            return None

        if not hypothesis.characterization_set:
            hypothesis.characterization_set = hypothesis.compute_characterization_set()
            # fix for non-minimal intermediate hypothesis that can occur in KV
            if not hypothesis.characterization_set:
                hypothesis.characterization_set = [(a,) for a in hypothesis.get_input_alphabet()]

        states_to_cover = []
        for state in hypothesis.states:
            if state.prefix is None:
                state.prefix = hypothesis.get_shortest_path(hypothesis.initial_state, state)

        print(f'{self.sul.num_queries + self.sul.num_steps} < {self.budget}')
        while self.sul.num_queries + self.sul.num_steps < self.budget: 
            state = random.choice(hypothesis.states)
            input = state.prefix

            limit = self.min_length
            while limit > 0 or random.random() > 1 / (self.expected_length + 1):
                letter = random.choice(self.alphabet)
                input += (letter,)
                limit -= 1
            # global suffix
            input += choice(hypothesis.characterization_set)

            sul_out = self.sul.query(input)
            hyp_out = hypothesis.execute_sequence(hypothesis.initial_state,input)
            if cache:
                self.cache.append((input, sul_out))
            if tuple(sul_out) != tuple(hyp_out):
                print(f'cex found {self.sul.num_queries + self.sul.num_steps} < {self.budget}')
                return input

        return None

class RandomWpMethodEqOracle(Oracle):
    """
    Randomized version of the Wp-Method equivalence oracle.
    Random walks stem from fixed prefix (path to the state). At the end of the random
    walk an element from the characterization set is added to the test case.
    """

    def __init__(self, alphabet: list, sul: SUL, walks_per_state=12, walk_len=12):
        """
        Args:

            alphabet: input alphabet

            sul: system under learning

            walks_per_state: number of random walks that should start from each state

            walk_len: length of random walk
        """

        super().__init__(alphabet, sul)
        self.walks_per_state = walks_per_state
        self.random_walk_len = walk_len
        self.freq_dict = dict()
        self.cache = []

    def find_cex(self, hypothesis, cache = False):

        if not hypothesis.characterization_set:
            hypothesis.characterization_set = hypothesis.compute_characterization_set()
            # fix for non-minimal intermediate hypothesis that can occur in KV
            if not hypothesis.characterization_set:
                hypothesis.characterization_set = [(a,) for a in hypothesis.get_input_alphabet()]

        states_to_cover = []
        for state in hypothesis.states:
            if state.prefix is None:
                state.prefix = hypothesis.get_shortest_path(hypothesis.initial_state, state)
            if state.prefix not in self.freq_dict.keys():
                self.freq_dict[state.prefix] = 0

            states_to_cover.extend([state] * (self.walks_per_state - self.freq_dict[state.prefix]))

        shuffle(states_to_cover)

        for state in states_to_cover:
            self.freq_dict[state.prefix] = self.freq_dict[state.prefix] + 1

            prefix = state.prefix
            random_walk = tuple(choice(self.alphabet) for _ in range(randint(1, self.random_walk_len)))
            seq = prefix + random_walk + choice(hypothesis.characterization_set)

            sul_out = self.sul.query(seq)
            hyp_out = hypothesis.execute_sequence(hypothesis.initial_state,seq)
            if cache:
                self.cache.append((seq, sul_out))
            if tuple(sul_out) != tuple(hyp_out):
                return seq

        return None

class RandomWordEqOracle(Oracle):
    """
    Equivalence oracle where queries are of random length in a predefined range.
    """

    def __init__(self, alphabet: list, sul: SUL, num_walks=500, min_walk_len=10, max_walk_len=30,
                 reset_after_cex=True):
        """
        Args:
            alphabet: input alphabet

            sul: system under learning

            num_walks: number of walks to perform during search for cex

            min_walk_len: minimum length of each walk

            max_walk_len: maximum length of each walk

            reset_after_cex: if True, num_walks will be preformed after every counter example, else the total number
                or walks will equal to num_walks
        """

        super().__init__(alphabet, sul)
        self.num_walks = num_walks
        self.min_walk_len = min_walk_len
        self.max_walk_len = max_walk_len
        self.reset_after_cex = reset_after_cex
        self.num_walks_done = 0
        self.automata_type = None

        self.walk_lengths = [randint(min_walk_len, max_walk_len) for _ in range(num_walks)]
        self.cache = []

    def find_cex(self, hypothesis, cache=False):
        while self.num_walks_done < self.num_walks:
            seq = []
            self.reset_hyp_and_sul(hypothesis)
            self.num_walks_done += 1

            num_steps = self.walk_lengths.pop(0)

            for _ in range(num_steps):
                seq.append(choice(self.alphabet))

            sul_out = self.sul.query(seq)
            hyp_out = hypothesis.execute_sequence(hypothesis.initial_state,seq)
            if cache:
                self.cache.append((seq, sul_out))
            if sul_out != hyp_out:
                return seq

        return None

    def reset_counter(self):
        if self.reset_after_cex:
            self.num_walks_done = 0


class StatePrefixEqOracle(Oracle):
    """
    Equivalence oracle that achieves guided exploration by starting random walks from each state a walk_per_state
    times. Starting the random walk ensures that all states are reached at least walk_per_state times and that their
    surrounding is randomly explored. Note that each state serves as a root of random exploration of maximum length
    rand_walk_len exactly walk_per_state times during learning. Therefore excessive testing of initial states is
    avoided.
    """
    def __init__(self, alphabet: list, sul: SUL, walks_per_state=10, walk_len=12, depth_first=False):
        """
        Args:

            alphabet: input alphabet

            sul: system under learning

            walks_per_state:individual walks per state of the automaton over the whole learning process

            walk_len:length of random walk

            depth_first:first explore newest states
        """

        super().__init__(alphabet, sul)
        self.walks_per_state = walks_per_state
        self.steps_per_walk = walk_len
        self.depth_first = depth_first

        self.freq_dict = dict()
        self.cache = []

    def find_cex(self, hypothesis, cache=False):

        states_to_cover = []
        for state in hypothesis.states:
            if state.prefix is None:
                state.prefix = hypothesis.get_shortest_path(hypothesis.initial_state, state)
            if state.prefix not in self.freq_dict.keys():
                self.freq_dict[state.prefix] = 0

            states_to_cover.extend([state] * (self.walks_per_state - self.freq_dict[state.prefix]))

        if self.depth_first:
            # reverse sort the states by length of their access sequences
            # first do the random walk on the state with longest access sequence
            states_to_cover.sort(key=lambda x: len(x.prefix), reverse=True)
        else:
            random.shuffle(states_to_cover)

        for state in states_to_cover:
            self.freq_dict[state.prefix] = self.freq_dict[state.prefix] + 1

            seq = state.prefix

            for _ in range(self.steps_per_walk):
                seq += (random.choice(self.alphabet),)

            sul_out = self.sul.query(seq)
            hyp_out = hypothesis.execute_sequence(hypothesis.initial_state,seq)
            if cache:
                self.cache.append((seq, sul_out))
            if tuple(sul_out) != tuple(hyp_out):
                return seq

        return None
