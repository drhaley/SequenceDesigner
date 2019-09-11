from sequence_iterator.abstract import AbstractSequenceIterator
import util.common as common

import random

class SequenceIterator(AbstractSequenceIterator):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

        self._ALPHABET = "ATC"
        self._MAX_ATTEMPTS_BEFORE_WARNING = 1000
        
        self._FORBIDDEN_SUBSTRINGS = ['CCCC','AAAA','TTTT'] + common.product_strings(5,'AT')

    def __next__(self):
        while(True):
            for _ in range(self._MAX_ATTEMPTS_BEFORE_WARNING):
                potential_sequence = ''.join([
                    random.choice(self._ALPHABET)
                    for _ in range(self._domain_length)
                ])

                if all(
                    potential_sequence.find(forbidden_substring) == -1  #not found
                    for forbidden_substring in self._FORBIDDEN_SUBSTRINGS
                ):
                    return potential_sequence
            else:
                print(f"WARNING: Did not yet find a random sequence in {self._MAX_ATTEMPTS_BEFORE_WARNING} attempts")

    def feedback(self, fitness):
        pass #this iterator does not learn from feedback
