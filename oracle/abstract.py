import abc

class AbstractOracle(abc.ABC):
    """
    Adapter for the various DNA folding oracles available (e.g. nupack, viennaRNA)
    """
    def __init__(self, temperature):
        self.set_temperature(temperature)

    @abc.abstractmethod
    def set_temperature(self, temperature):
        """set temperature to be used (in Celsius)"""
        pass
    
    @abc.abstractmethod
    def self_affinity(self, sequence):
        """Returns a POSITIVE value correlated with self affinity (e.g. hairpin affinity)"""
        pass

    @abc.abstractmethod
    def binding_affinity(self, sequence1, sequence2):
        """Returns a POSITIVE value correlated with duplex/cofold affinity"""
        pass
