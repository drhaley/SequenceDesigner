import itertools

from sequence_iterator.abstract import AbstractSequenceIterator

import lib.dsd as dsd

class SequenceIterator(AbstractSequenceIterator):
    def __init__(self, *args):
        super().__init__(*args)

        DOMAIN_LENGTH = 10
        ALPHABET = "ATC"
        
        FORBIDDEN_SUBSTRINGS_LENGTH_4 = ['CCCC','AAAA','TTTT']
        FORBIDDEN_SUBSTRINGS_LENGTH_5 = self._product_strings(5,'AT')

        self._sequence_list = dsd.DNASeqList(DOMAIN_LENGTH,alphabet=tuple(char for char in ALPHABET))
        #self._sequence_list = self._sequence_list.filter_base_nowhere('G')    #remove all G's
        #k=1;self._sequence_list = self._sequence_list.filter_base_count('G', 0, k) #no more than k G's
        self._sequence_list = self._sequence_list.filter_substring(list(FORBIDDEN_SUBSTRINGS_LENGTH_4))
        self._sequence_list = self._sequence_list.filter_substring(list(FORBIDDEN_SUBSTRINGS_LENGTH_5))
        self._sequence_list.shuffle()
        

    def next(self):
        return self._sequence_list.pop()

    def feedback(self, fitness):
        raise NotImplementedError()

    def _product_strings(self,length,alphabet):
        return [''.join(character_list) for character_list in itertools.product(alphabet,repeat=length)]
