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
            partition_function=False, params_filename=DEFAULT_PARAMS_FILE):
        self._use_partition_function = partition_function
        self._params_filename = params_filename
        self.set_temperature(temperature)
        RNA.cvar.noGU = True      #legacy code did not allow GU pairs
        RNA.params_load(self._params_filename)

    def set_temperature(self, temperature):
        RNA.cvar.temperature = temperature

    def self_affinity(self, sequence):
        if self._use_partition_function:
            folded_compound = RNA.fold_compound(sequence)
            _, free_energy = folded_compound.pf()
        else:
            _, free_energy = RNA.fold(sequence)
        return -free_energy

    def binding_affinity(self, sequence1, sequence2):
        if self._use_partition_function:
            energy_list = RNA.co_pf_fold('&'.join([sequence1, sequence2]))
            free_energy = energy_list[-1]  #ensemble energy is the last in a list of structure-specific energies
        else:
            free_energy = RNA.duplexfold(sequence1, sequence2).energy
        return -free_energy
