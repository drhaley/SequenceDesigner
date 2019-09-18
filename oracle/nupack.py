import subprocess   #calls out to nupack
import math

from oracle.abstract import AbstractOracle


class Oracle(AbstractOracle):
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

    def _pfunc(self, *sequences):
        """Calls NUPACK's pfunc on a complex consisting of the unique strands in
        sequences, returns dG.  temperature is in Celsius."""
        user_input = str(len(sequences)) + '\n' + '\n'.join(sequences) + '\n' + ' '.join(map(str,list(range(1,len(sequences)+1))))

        p=subprocess.Popen(['pfunc','-T',str(self._temperature),'-multi','-material','dna'],
                    stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)             

        try:
            #output = p.communicate(user_input)[0]
            output = p.communicate(user_input.encode())[0]
            output = output.decode()
        except BaseException as error:
            p.kill()
            raise error
        
        #lines = output.split('\n')
        lines = output.split('\n')
        
        if lines[-4] != "% Free energy (kcal/mol) and partition function:" :
            raise NameError('NUPACK output parsing problem')
        
        dG_str = lines[-3].strip()
        if dG_str.lower() == 'inf':
            # this can occur when two strands have MFE completely unpaired; should be 0 energy
            dG = 0.0
        else:
            dG = float(dG_str)
        
        dG += self._dGadjust(self._temperature,len(sequences))
        return dG
