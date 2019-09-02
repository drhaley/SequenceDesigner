import abc   #abstract classes

class AbstractSequenceIterator(abc.ABC):
    @abc.abstractmethod
    def next(self):
        pass

    @abc.abstractmethod
    def feedback(self, fitness):
        """Method by which to give a measure of fitness of the previous sequence
        which can then be used by the class to learn"""
        pass
