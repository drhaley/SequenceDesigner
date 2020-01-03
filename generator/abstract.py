import abc

class AbstractGenerator(abc.ABC):
    """
    The Generator is responsible for producing a stream of
    potential sequences to consider
    """
###################################################
    @abc.abstractmethod
    def __next__(self):
        """
        Produce and return a new sequence
        """
        pass
###################################################

    def __iter__(self):
        return self

