import abc   #abstract classes

class AbstractOracle(abc.ABC):
    def __init__(self, temperature):
        self.set_temperature(temperature)

    def set_temperature(self, temperature):
        self._temperature = temperature
    
    @abc.abstractmethod
    def self_affinity(self, sequence):
        pass

    @abc.abstractmethod
    def binding_affinity(self, sequence1, sequence2):
        pass
