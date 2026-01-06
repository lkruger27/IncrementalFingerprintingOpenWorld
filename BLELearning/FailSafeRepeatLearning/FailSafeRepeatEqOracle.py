from aalpy.base.Oracle import Oracle
from pathlib import Path
import time
from aalpy.utils import save_automaton_to_file
from aalpy.oracles.WpMethodEqOracle import RandomWpMethodEqOracle


class FailSafeRepeatEqOracle(Oracle):
    """
    Implements a fail safe equivalence oracle by repeating queries
    """

    def __init__(self, eq_oracle: RandomWpMethodEqOracle, hypotheses_path: Path = None):
        super().__init__(eq_oracle.alphabet, eq_oracle.sul)
        self.eq_oracle = eq_oracle
        self.hypotheses_path = hypotheses_path
        self.learning_rounds = 0
        self.bound = eq_oracle.bound
        self.eq_query_time = 0

    def repeat_cex(self, cex, hypothesis):
        try:
            # fetch metrics from sul
            queries_before = self.sul.num_queries
            steps_before = self.sul.num_steps

            out_sul = self.sul.query(cex)

            # adapt metric of equivalence oracle
            self.num_queries +=  self.sul.num_queries - queries_before 
            self.num_steps += self.sul.num_steps - steps_before

            # reset metrics of sul
            self.sul.num_queries = queries_before
            self.sul.num_steps = steps_before
        except (SystemExit, Exception) as e:
            print("non-deterministic error in repetition of query in equivalence query")
            raise e


        out_hypothesis = hypothesis.execute_sequence(
            hypothesis.initial_state, cex)
        if out_sul[-1] != out_hypothesis[-1]:
            return cex
        else:
            return None
        
    def find_cex_extended(self, hypothesis):
        num_queries_before = self.eq_oracle.num_queries
        num_steps_before = self.eq_oracle.num_steps
        cex = self.eq_oracle.find_cex(hypothesis)
        print(f"equivalence queries before {self.num_queries}")
        self.num_queries += self.eq_oracle.num_queries - num_queries_before
        print(f"equivalence queries after {self.num_queries}")
        self.num_steps += self.eq_oracle.num_steps - num_steps_before
        if cex:
            cex = self.repeat_cex(cex, hypothesis)
            # counterexample could not be reproduced, continue searching
            if cex is None:
                queries_performed = self.eq_oracle.num_queries - num_queries_before
                self.eq_oracle.bound = self.eq_oracle.bound - queries_performed
                return self.find_cex_extended(hypothesis)
            return cex
        else:
            return None

    def find_cex(self, hypothesis):

        if self.hypotheses_path:
            # save intermediate hypotheses
            hypothesis_file = Path(self.hypotheses_path, f"hypothesis_{self.learning_rounds}").absolute().as_posix()
            save_automaton_to_file(hypothesis, path=hypothesis_file)
        self.learning_rounds += 1
        self.eq_oracle.bound = self.bound
        eq_start_time = time.time()
        cex = self.find_cex_extended(hypothesis)
        self.eq_query_time += round(time.time() - eq_start_time, 2)

        return cex

