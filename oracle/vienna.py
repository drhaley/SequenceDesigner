import RNA

from oracle.abstract import AbstractOracle

#TODO: Try to make the system path and python path as smart as possible
# but right now some of the following commands may be helpful:
# - export PATH=$PATH:vienna_install_dir/bin
# - export PYTHONPATH=$PYTHONPATH:vienna_source_dir/interfaces/Python3

class Oracle(AbstractOracle):
    __USE_DUPLEX = False

    def set_temperature(self, temperature):
        super().set_temperature(temperature)
        RNA.cvar.temperature = temperature
        #TODO: params file
        #TODO: --noGU  (no GU interaction)
        #TODO: --noconv  (no auto-conversion of U and T)

    def self_affinity(self, sequence):
        _, minimum_free_energy = RNA.fold(sequence)
        return minimum_free_energy

    def binding_affinity(self, sequence1, sequence2):
        if self.__USE_DUPLEX:
            raise NotImplementedError()
            #the following line is not calling a valid API function (yet)
            _, minimum_free_energy = RNA.duplex(sequence1, sequence2)
        else:
            _, minimum_free_energy = RNA.cofold(sequence1, sequence2)
        return minimum_free_energy
