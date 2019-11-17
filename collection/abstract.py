import abc

#TODO: add file I/O methods

class AbstractCollection(abc.ABC):
    """
    The Collection is responsible for maintaining a record of the
    'accepted' sequences, and must handle file I/O related to that data
    """
###################################################
    @abc.abstractmethod
    def add(self, sequence):
        pass

    @abc.abstractmethod
    def discard(self, sequence):
        pass

    @abc.abstractmethod
    def __contains__(self, sequence):
        pass

    @abc.abstractmethod
    def __len__(self):
        pass

    @abc.abstractmethod
    def __iter__(self):
        pass
###################################################

    def remove(self, sequence):
        if sequence in self:
            self.discard(sequence)
        else:
            raise KeyError(f"'{sequence}' is not in collection {self}")
