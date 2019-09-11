from sequence_iterator.abstract import AbstractSequenceIterator
import util.common as common
import lib.dsd as dsd

class SequenceIterator(AbstractSequenceIterator):
    def __init__(self, *args, domain_length=None, **kargs):
        super().__init__(*args, domain_length=domain_length, **kargs)

        if self._domain_length > 12:
            print(f"WARNING: Instantiated exhaustive sequence iterator with long domain length ({domain_length})")

        ALPHABET = "ATC"
        
        FORBIDDEN_SUBSTRINGS_LENGTH_4 = ['CCCC','AAAA','TTTT']
        FORBIDDEN_SUBSTRINGS_LENGTH_5 = common.product_strings(5,'AT')

        self._sequence_list = dsd.DNASeqList(self._domain_length,alphabet=tuple(char for char in ALPHABET))
        #self._sequence_list = self._sequence_list.filter_base_nowhere('G')    #remove all G's
        #k=1;self._sequence_list = self._sequence_list.filter_base_count('G', 0, k) #no more than k G's
        self._sequence_list = self._sequence_list.filter_substring(list(FORBIDDEN_SUBSTRINGS_LENGTH_4))
        self._sequence_list = self._sequence_list.filter_substring(list(FORBIDDEN_SUBSTRINGS_LENGTH_5))
        self._sequence_list.shuffle()

    def __next__(self):
        return self._sequence_list.pop()

    def feedback(self, fitness):
        pass #this iterator does not learn from feedback

