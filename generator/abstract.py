import abc

#TODO: add method to filter via decorator pattern

class AbstractGenerator(abc.ABC):
    """
    The Generator is responsible for producing a stream of
    potential sequences to consider
    """
###################################################
    @abc.abstractmethod
    def __next__(self):
        pass
###################################################
    
    def __iter__(self):
        return self
