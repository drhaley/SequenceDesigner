import abc   #abstract classes

class AbstractOracle(abc.ABC):
    @abc.abstractmethod
    def self_affinity(self, sequence, temperature):
        pass

    @abc.abstractmethod
    def binding_affinity(self, sequence1, sequence2, temperature):
        pass
