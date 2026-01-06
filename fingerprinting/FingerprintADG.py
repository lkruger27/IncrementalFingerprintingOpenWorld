from collections import defaultdict
from aalpy.utils.ModelChecking import bisimilar


class AdgNode:
    __slots__ = ['sep_seq', 'children', 'score', 'current_block']

    def __init__(self, sep_seq_val=None, children=None, score=0, current_block=None):
        self.sep_seq = sep_seq_val
        self.children = children if children else {}
        self.score = score
        self.current_block = current_block

    @staticmethod
    def create_leaf(current_block):
        return AdgNode(current_block=current_block)

    def get_sep_seq(self):
        return self.sep_seq

    def get_child_node(self, outputs):
        if outputs in self.children:
            return self.children[outputs]
        return None

    def get_score(self):
        return self.score

    def get_current_block(self):
        return self.current_block


class Adg:
    def __init__(self, alphabet, current_block):
        self.initial_node = self.construct_adg(alphabet, current_block)
        self.current_node = self.initial_node

    def get_score(self):
        return self.initial_node.get_score()

    def get_all_separating_sequences(self, current_block):
        all_sep_seqs = set()
        for x in range(0,len(current_block)):
            for y in range(x+1,len(current_block)):
                sep_seq = tuple(bisimilar(current_block[x][1], current_block[y][1], return_cex=True))
                all_sep_seqs.add(sep_seq)
        return all_sep_seqs

    def construct_adg(self, alphabet, current_block):
        # Builds the ADG tree recursively by selecting optimal sep_seqs for splitting models
        if len(current_block) == 1:
            return AdgNode.create_leaf(current_block)

        best_sep_seq, best_score = None, 0 #self.maximal_base_sep_seq(alphabet, current_block)
        best_children = None

        # The maximal apartness pairs is len(current block) - 1, for any current block, immediately return
        if best_score == len(current_block) - 1:
            return AdgNode(best_sep_seq, best_children, best_score, current_block)

        all_sep_seqs = self.get_all_separating_sequences(current_block)
        for sep_seq_val in all_sep_seqs:
            sep_seq_partitions = self.partition_on_sepseq(current_block, sep_seq_val)
            u_i = sum(len(part) for part in sep_seq_partitions.values())
            sep_seq_score = 0
            children = {}

            for output, partition in sep_seq_partitions.items():
                output_score, subtree = self.compute_output_subtree(alphabet, partition, u_i) 
                sep_seq_score += output_score
                children[output] = subtree

            if sep_seq_score > best_score:
                best_score = sep_seq_score
                best_sep_seq = sep_seq_val
                best_children = children
            if best_score == len(current_block) - 1:
                return AdgNode(best_sep_seq, best_children, best_score)

        if best_sep_seq is None:
            raise RuntimeError("Error during ADG construction")

        return AdgNode(best_sep_seq, best_children, best_score)

    def compute_output_subtree(self, alphabet, partition, u_i):
        # Computes and scores a subtree for a specific output partition
        output_subtree = self.construct_adg(alphabet, partition)
        output_score = self.compute_score(len(partition), u_i, output_subtree.get_score())
        return output_score, output_subtree

    def compute_score(self, u_io, u_i, child_score):
        # Calculates a score based on partition size and subtree characteristics
        return (u_io * (u_i - u_io + child_score)) / u_i

    def partition_on_sepseq(self, block, sep_seq_val):
        # Partitions states in the block based on their output for a given sep_seq
        partition = defaultdict(list)
        for model in block:
            output = tuple(model[1].compute_output_seq(model[1].initial_state, sep_seq_val))
            if output is not None:
                partition[output].append(model)
        return partition

    def next_sep_seq(self, prev_outputs):
        # Returns the next sep_seq based on the previous output and updates the current node
        if prev_outputs is not None:
            child = self.current_node.get_child_node(prev_outputs)
            if child is None:
                return None
            self.current_node = child
        return self.current_node.get_sep_seq()

    def reset_to_root(self):
        # Resets the current ADG node to the initial root node
        self.current_node = self.initial_node