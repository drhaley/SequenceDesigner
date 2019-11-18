import RNA
import re

from oracle.abstract import AbstractOracle

#TODO: Try to make the system path and python path as smart as possible
# but right now some of the following commands may be helpful:
# - export PATH=$PATH:vienna_install_dir/bin
# - export PYTHONPATH=$PYTHONPATH:vienna_source_dir/interfaces/Python3

DEFAULT_PARAMS_FILE = "lib/dna_mathews2004.par"

class Oracle(AbstractOracle):
    def __init__(self, temperature,
            use_duplex=True, params_filename=DEFAULT_PARAMS_FILE, **kargs):
        self._use_duplex = use_duplex
        self._params_filename = params_filename
        self.set_temperature(temperature)
        RNA.cvar.noGU = True      #legacy code did not allow GU pairs
        RNA.params_load(self._params_filename)

    def set_temperature(self, temperature):
        RNA.cvar.temperature = temperature

    def self_affinity(self, sequence):
        _, minimum_free_energy = RNA.fold(sequence)
        return -minimum_free_energy

    def binding_affinity(self, sequence1, sequence2):
        if self._use_duplex:
            minimum_free_energy = RNA.duplexfold(sequence1, sequence2).energy
        else:
            _, minimum_free_energy = RNA.cofold('&'.join([sequence1, sequence2]))
        return -minimum_free_energy
