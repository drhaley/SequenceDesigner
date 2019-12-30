import subprocess   #calls out to nupack
import math
import re

from oracle.abstract import AbstractOracle


class Oracle(AbstractOracle):
    def __init__(self, temperature):
        self.set_temperature(temperature)

    def set_temperature(self, temperature):
        self._temperature = temperature

    def self_affinity(self, sequence):
        return -self._pfunc(sequence)

    def binding_affinity(self, sequence1, sequence2):
        return -self._pfunc(sequence1,sequence2)

    _R = 0.0019872041 # Boltzmann's constant in kcal/mol/K
    
    def _dGadjust(self, temperature, sequence_length):
        water_concentration = 55.14 # molar concentration of water at 37 C; ignore temperature dependence, ~5%
        _K = temperature + 273.15 # Kelvin
        adjusting_factor = (self._R)*(_K)*math.log(water_concentration) # converts from NUPACK mole fraction units to molar units, per association
        return adjusting_factor*(sequence_length-1)

    def _open_subprocess(self, arg_list):
        return subprocess.Popen(
            arg_list,
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
        )

    def _pfunc(self, *sequences):
        user_input = str(len(sequences)) + '\n' + '\n'.join(sequences) + '\n' + ' '.join(map(str,list(range(1,len(sequences)+1))))

        nupack_process = self._open_subprocess(['pfunc','-T',str(self._temperature),'-multi','-material','dna'])

        try:
            output = nupack_process.communicate(user_input.encode('utf-8'))[0]
            output = output.decode('utf-8')
        except BaseException as error:
            nupack_process.kill()
            raise error

        FLOAT_REGEX = r"[-+]?[0-9]*\.?[0-9]+"
        SCIENTIFIC_NUMBER_REGEX = r"\s*(" + f"{FLOAT_REGEX}e{FLOAT_REGEX}" + r"|inf)\s*"

        FREE_ENERGY_REGEX = "".join([
            r"Free energy \(kcal\/mol\) and partition function:",
            SCIENTIFIC_NUMBER_REGEX
        ])

        search_result = re.search(f"{FREE_ENERGY_REGEX}", output)

        raw_energy = search_result.group(1)
        if raw_energy == "inf":
            #this can occur when two strands have MFE completely unpaired; should be 0 energy
            energy = 0.0
        else:
            energy = float(raw_energy)

        energy += self._dGadjust(self._temperature,len(sequences))  #TODO: should this be applied to inf case?

        return energy

