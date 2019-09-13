from sequence_iterator.abstract import AbstractSequenceIterator

import lib.dsd as dsd

class SequenceIterator(AbstractSequenceIterator):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

        if self._domain_length > 12:
            print(f"WARNING: Instantiated exhaustive sequence iterator with long domain length ({self._domain_length})")
        
        self._sequence_list = dsd.DNASeqList(
            self._domain_length,
            alphabet=tuple(char for char in self._alphabet)
        )
        self._sequence_list.shuffle()

    def get(self):
        return self._sequence_list.pop()


    def feedback(self, fitness):
        pass #this iterator does not learn from feedback
