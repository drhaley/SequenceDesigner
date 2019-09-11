import abc   #abstract classes
import itertools

class AbstractSequenceIterator(abc.ABC):
    _DEFAULT_DOMAIN_LENGTH = 10

    def __init__(self, *args, domain_length=None):
        super().__init__(*args)
        self._domain_length = \
            domain_length if domain_length \
            else self._DEFAULT_DOMAIN_LENGTH

    def __iter__(self):
        return self

    @abc.abstractmethod
    def __next__(self):
        pass

    @abc.abstractmethod
    def feedback(self, fitness):
        """Method by which to give a measure of fitness of the previous sequence
        which can then be used by the class to learn"""
        pass

    def _product_strings(self,length,alphabet):
        return [''.join(character_list) for character_list in itertools.product(alphabet,repeat=length)]
