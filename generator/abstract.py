import abc

#TODO: Decouple forbid_substring()

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

    @abc.abstractmethod
    def forbid_substring(self, forbidden_regex):
        """
        Forbid the provided substring (must accept regular expressions)
        May be helpful to use the method regex_search() from util.common
        """
        pass

###################################################

    def __iter__(self):
        return self

