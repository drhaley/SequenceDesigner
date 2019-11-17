import abc

#TODO: add method to implement new tests via decorator pattern

class AbstractArbiter(abc.ABC):
    """
    The Arbiter is responsible for performing acceptance tests
    on prospective sequences
    """
###################################################
    @abc.abstractmethod
    def __init__(self, oracle, collection):
        pass

    @abc.abstractmethod
    def consider(self, sequence):
        """
        returns True if sequence is to be 'accepted'
        """
        pass
###################################################
