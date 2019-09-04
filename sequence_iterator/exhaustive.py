import itertools

from sequence_iterator.abstract import AbstractSequenceIterator

import lib.dsd as dsd

class SequenceIterator(AbstractSequenceIterator):
    def __init__(self, *args):
        super().__init__(*args)

        DOMAIN_LENGTH = 10
        ALPHABET = "ATC"
        
        FORBIDDEN_SUBSTRINGS_LENGTH_4 = ['CCCC','AAAA','TTTT']
        FORBIDDEN_SUBSTRINGS_LENGTH_5 = self.__product_strings(5,'AT')

        self.__sequence_list = dsd.DNASeqList(DOMAIN_LENGTH,alphabet=tuple(char for char in ALPHABET))
        #self.__sequence_list = self.__sequence_list.filter_base_nowhere('G')    #remove all G's
        #k=1;self.__sequence_list = self.__sequence_list.filter_base_count('G', 0, k) #no more than k G's
        self.__sequence_list = self.__sequence_list.filter_substring(list(FORBIDDEN_SUBSTRINGS_LENGTH_4))
        self.__sequence_list = self.__sequence_list.filter_substring(list(FORBIDDEN_SUBSTRINGS_LENGTH_5))
        self.__sequence_list.shuffle()
        

    def next(self):
        return self.__sequence_list.pop()

    def feedback(self, fitness):
        raise NotImplementedError()

    def __product_strings(self,length,alphabet):
        return [''.join(character_list) for character_list in itertools.product(alphabet,repeat=length)]
