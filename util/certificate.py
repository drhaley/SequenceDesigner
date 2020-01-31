#used to store energy information about single and pairwise energy relationships between domains

class Certificate():
    def __init__(self):
        self._self_affinities = {}
        self._pairwise_affinities = {}
        self._aliases = {}

    def add_single(self, sequence, energy):
        self._self_affinities[sequence] = energy

    def add_pair(self, sequence1, sequence2, energy):
        self._pairwise_affinities[(sequence1, sequence2)] = energy

    def define_alias(self, sequence, alias):
        self._aliases[sequence] = alias

    def get_singles(self):
        aliased_energies = {
            self._alias(sequence): energy
                for sequence, energy in self._self_affinities.items()
        }
        return aliased_energies

    def get_pairs(self):
        aliased_energies = {
            (self._alias(sequence1), self._alias(sequence2)): energy
                for (sequence1, sequence2), energy in self._pairwise_affinities.items()
        }
        return aliased_energies

    def _alias(self, sequence):
        if sequence in self._aliases:
            return self._aliases[sequence]
        else:
            return sequence

    def export(self):
        return {
            "Self_affinities": self.get_singles(),
            "pairwise_affinities": self.get_pairs(),
        }
