from aalpy.base import SUL
from aalpy.base.CacheTree import CacheTree, CacheDict
from constant import QUERY_STEP_REPEAT, MAX_QUERY_STEP_REPEAT
from FailSafeLearning import Errors

class FailSafeRepeatCacheSUL(SUL):
    """
    System under learning that keeps a multiset of all queries in memory.
    This multiset/cache is encoded as a tree.
    """

    def __init__(self, sul: SUL, cache_type='tree'):
        super().__init__()
        self.sul = sul
        self.cache = CacheTree() if cache_type == 'tree' else CacheDict()

    def majority_vote_output(self, outputs):
        return max(set(outputs), key=outputs.count)
    
    def longest_prefix_output(self, input, outputs):
        trace_length = len(input)

        if trace_length == 1: 
            return self.majority_vote_output(outputs)
        
        output_prefix_in_cache = None
        for i in reversed(range(1, trace_length)):
            prefix = input[:i]
            cached_query = self.cache.in_cache(prefix)
            if cached_query:
                output_prefix_in_cache = cached_query
                break
        
        if output_prefix_in_cache:
            output_sequences_in_cache = []
            for output in outputs:
                prefix = output[:len(output_prefix_in_cache)]
                if prefix == output_prefix_in_cache:
                    output_sequences_in_cache.append(output)

            if len(output_sequences_in_cache) <= 1:
                raise Errors.NonDeterministicError

            return self.majority_vote_output(output_sequences_in_cache)
        else:
            return self.majority_vote_output(outputs)
    
    def repeat_query(self, word):
        # repeat query several times due to non-deterministic behavior
        outputs = []
        repeats = min(len(word) * QUERY_STEP_REPEAT, MAX_QUERY_STEP_REPEAT)

        for _ in range(repeats):
            # get outputs using default query method
            queries_before = self.sul.num_queries
            steps_before = self.sul.num_steps
            out = self.sul.query(word)
            outputs.append(tuple(out))
            self.num_queries +=  self.sul.num_queries - queries_before 
            self.num_steps += self.sul.num_steps - steps_before
        return outputs

    def query(self, word):
        """
        Performs a membership query on the SUL if and only if `word` is not a prefix of any trace in the cache.
        Before the query, pre() method is called and after the query post()
        method is called. Each letter in the word (input in the input sequence) is executed using the step method.

        Args:

            word: membership query (word consisting of letters/inputs)

        Returns:

            list of outputs, where the i-th output corresponds to the output of the system after the i-th input

        """
        cached_query = self.cache.in_cache(word)
        if cached_query:
            self.num_cached_queries += 1
            return cached_query

        outputs = self.repeat_query(word)

        out = None
        try: 
            out = self.longest_prefix_output(word, outputs)
        except Errors.NonDeterministicError as e:
            print("repeat query once due non-determinism")
            outputs = self.repeat_query(word)
            out = self.longest_prefix_output(word, outputs)
            print(f"received outputs: {outputs}")

        # add input/outputs to tree
        self.cache.reset()
        for i, o in zip(word, out):
            try: 
                self.cache.step_in_cache(i, o)
            except (SystemExit, Exception) as e:
                print(f"received outputs: {outputs}")
                print(f"picked output: {out}")
                raise e


            # self.num_queries += 1
            # self.num_steps += len(word)
        return out


    def pre(self):
        """
        Reset the system under learning and current node in the cache tree.
        """
        self.cache.reset()
        self.sul.pre()

    def post(self):
        self.sul.post()

    def step(self, letter):
        """
        Executes an action on the system under learning, adds it to the cache and returns its result.

        Args:

           letter: Single input that is executed on the SUL.

        Returns:

           Output received after executing the input.

        """
        out = self.sul.step(letter)

        # self.cache.step_in_cache(letter, out)
        return out