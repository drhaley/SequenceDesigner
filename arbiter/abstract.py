import abc   #abstract classes

from util.constants import \
    MAX_FITNESS, \
    MIN_AFFINITY_TO_SELF, \
    MAX_AFFINITY_TO_OTHER_SINGLE, \
    MAX_AFFINITY_TO_OTHER_PAIR
from util import common

class AbstractArbiter(abc.ABC):
###################################################
    @abc.abstractmethod
    def _conditions_to_check(self):
        return [
            self._sticky_to_complement,
            self._not_sticky_to_others,
            self._not_sticky_to_pairs,
            self._not_sticky_with_adjacent,
        ]

###################################################

    def __init__(self, oracle = None, initial_sequences = [], save_filename = None, verbose = False):
        if oracle is None:
            raise AssertionError("Must supply the arbiter with access to a valid oracle")
        else:
            self._oracle = oracle
        self._accepted_sequences = initial_sequences
        self._verbose = verbose
        self._save_filename = save_filename

    def consider(self, sequence):
        conditions_to_check = self._conditions_to_check()

        results = [
            check_condition(sequence)
            for check_condition in conditions_to_check
        ]

        accept = all([check_result for check_result,_ in results])
        overall_fitness = (
            sum([fitness**2 for _,fitness in results])
            // ((MAX_FITNESS**2)*len(conditions_to_check))
        )

        if accept:
            self._accept(sequence)
        else:
            self._reject(sequence)

        return overall_fitness

    def get_sequences(self):
        return self._accepted_sequences

    def load_from_file(self, filename):
        self._accepted_sequences = []
        self.append_from_file(filename)

    def append_from_file(self, filename):
        with open(filename, "r") as inFile:
            sequence = inFile.readline().strip()
            while sequence:
                if sequence not in self._accepted_sequences:
                    self._accepted_sequences.append(sequence)
                sequence = inFile.readline().strip()
                
    def _accept(self, sequence):
        self._accepted_sequences.append(sequence)
        if self._verbose: print(f"Accepted {sequence}")
        self._save()

    def _reject(self, sequence):
        if self._verbose: print(f"Rejected {sequence}")

    def _save(self):
        if self._save_filename:
            with open(self._save_filename, "w") as outFile:
                for accepted_sequence in self._accepted_sequences:
                    outFile.write(f"{accepted_sequence}\n")

    def _proportion_exceeding_target(self, value, target):
        fitness = MAX_FITNESS * (value - target) / target
        fitness = min(fitness, MAX_FITNESS)
        return fitness

    def _proportion_of_target(self, value, target):
        fitness = MAX_FITNESS * (target - value) / target
        fitness = min(fitness, MAX_FITNESS)
        return fitness

    def _sticky_to_complement(self, sequence):
        affinity_to_self = self._oracle.binding_affinity(sequence, common.wc(sequence))
        sticky_to_complement = affinity_to_self >= MIN_AFFINITY_TO_SELF

        if self._verbose: print(f"\tself affinity: {affinity_to_self}")

        fitness = self._proportion_of_target(affinity_to_self, MIN_AFFINITY_TO_SELF)
        return sticky_to_complement, fitness

    def _not_sticky_to_others(self, sequence):
        if not self._accepted_sequences:
            not_sticky_to_other_singles = True
            fitness = MAX_FITNESS
        else:
            affinity_to_other_singles = [
                self._oracle.binding_affinity(seq1, seq2)
                for found_sequence in self._accepted_sequences
                for seq1 in [sequence, common.wc(sequence)]
                for seq2 in [found_sequence, common.wc(found_sequence)]
            ]

            not_sticky_to_other_singles = all([
                affinity <= MAX_AFFINITY_TO_OTHER_SINGLE
                for affinity in affinity_to_other_singles
            ])

            max_affinity = max(affinity_to_other_singles)
            fitness = self._proportion_exceeding_target(max_affinity, MAX_AFFINITY_TO_OTHER_SINGLE)

            if self._verbose and self._accepted_sequences:
                print(f"\tmax affinity to other singles: {max_affinity}")

        return not_sticky_to_other_singles, fitness


    def _not_sticky_to_pairs(self, sequence):
        if not self._accepted_sequences:
            not_sticky_to_other_pairs = True
            fitness = MAX_FITNESS
        else:
            affinity_to_other_pairs = [
                self._oracle.binding_affinity(joined_sequence, common.wc(sequence))
                for joined_sequence in
                    [seq1 + seq2
                        for seq1 in self._accepted_sequences
                        for seq2 in self._accepted_sequences
                    ]
            ]
            not_sticky_to_other_pairs = all([
                affinity <= MAX_AFFINITY_TO_OTHER_PAIR
                for affinity in affinity_to_other_pairs
            ])
            
            max_affinity = max(affinity_to_other_pairs)
            fitness = self._proportion_exceeding_target(max_affinity, MAX_AFFINITY_TO_OTHER_PAIR)

            if self._verbose and self._accepted_sequences:
                print(f"\tmax affinity to other pairs: {max_affinity}")

        return not_sticky_to_other_pairs, fitness


    def _not_sticky_with_adjacent(self, sequence):
        if not self._accepted_sequences:
            not_sticky_when_with_adjacent_domain = True
            fitness = MAX_FITNESS
        else:
            mid_domain_affinities = [
                self._oracle.binding_affinity(joined_sequence, common.wc(starred_domain))
                for adjacent_domain in self._accepted_sequences + [sequence]
                for starred_domain in self._accepted_sequences
                for joined_sequence in [adjacent_domain + sequence, sequence + adjacent_domain]
                if adjacent_domain != starred_domain
            ]
            not_sticky_when_with_adjacent_domain = all([
                affinity <= MAX_AFFINITY_TO_OTHER_PAIR
                for affinity in mid_domain_affinities
            ])
            
            max_affinity = max(mid_domain_affinities)
            fitness = self._proportion_exceeding_target(max_affinity, MAX_AFFINITY_TO_OTHER_PAIR)

            if self._verbose and self._accepted_sequences:
                print(f"\tmax mid-domain affinity: {max(mid_domain_affinities)}")

        return not_sticky_when_with_adjacent_domain, fitness
