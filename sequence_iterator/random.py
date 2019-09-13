from sequence_iterator.abstract import AbstractSequenceIterator

import random

class SequenceIterator(AbstractSequenceIterator):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        
    def get(self):
        return ''.join([
            random.choice(self._alphabet)
            for _ in range(self._domain_length)
        ])

    def feedback(self, fitness):
        pass #this iterator does not learn from feedback
