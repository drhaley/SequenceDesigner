#the legacy code adjusted free energy to account for number of strands
#and so that adjustment is provided in this inherited class

import math

from oracle.nupack import Oracle as NupackOracle

class Oracle(NupackOracle):
    _R = 0.0019872041 # Boltzmann's constant in kcal/mol/K
    
    def _dGadjust(self, temperature, sequence_length):
        water_concentration = 55.14 # molar concentration of water at 37 C; ignore temperature dependence, ~5%
        _K = temperature + 273.15 # Kelvin
        adjusting_factor = (self._R)*(_K)*math.log(water_concentration) # converts from NUPACK mole fraction units to molar units, per association
        return adjusting_factor*(sequence_length-1)

    def _pfunc(self, *sequences):
        energy = super()._pfunc(*sequences)

        energy += self._dGadjust(self._temperature,len(sequences))

        return energy

