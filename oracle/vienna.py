import RNA
import subprocess  #to call out to ViennaRNA
import re

from oracle.abstract import AbstractOracle

#TODO: Try to make the system path and python path as smart as possible
# but right now some of the following commands may be helpful:
# - export PATH=$PATH:vienna_install_dir/bin
# - export PYTHONPATH=$PYTHONPATH:vienna_source_dir/interfaces/Python3

#TODO: Will the Python wrapper work from Windows?

DEFAULT_PARAMS_FILE = "lib/dna_mathews2004.par"

class Oracle(AbstractOracle):
    def __init__(self, *args, 
            use_duplex=True, use_subprocess=False, params_filename=DEFAULT_PARAMS_FILE, **kargs):
        self._use_duplex = use_duplex
        self._use_subprocess = use_subprocess
        self._params_filename = params_filename
        super().__init__(*args, **kargs)
        RNA.cvar.noGU = True      #legacy code did not allow GU pairs

    def set_temperature(self, temperature):
        super().set_temperature(temperature)
        RNA.cvar.temperature = temperature
        RNA.params_load(self._params_filename)  #generates warnings about asymmetries

    def self_affinity(self, sequence):
        if self._use_subprocess:
            minimum_free_energy = self._subprocess_self_affinity(sequence)
        else:
            _, minimum_free_energy = RNA.fold(sequence)
        return minimum_free_energy

    def binding_affinity(self, sequence1, sequence2):
        if self._use_subprocess:
            minimum_free_energy = self._subprocess_binding_affinity(sequence1, sequence2)
        elif self._use_duplex:
            minimum_free_energy = RNA.duplexfold(sequence1, sequence2).energy
        else:
            _, minimum_free_energy = RNA.cofold('&'.join([sequence1, sequence2]))
        return minimum_free_energy

    ################################################################################
    # below this line, code is only relevant to the oracle with "use_subprocess" enabled
    ################################################################################

    _VIENNA_QUIT_STRING = "@\n"
    _IGNORED_ERRORS = [
        'WARNING: stacking enthalpies not symmetric',
    ]
    
    def _subprocess_self_affinity(self, sequence):
        user_input = sequence + self._VIENNA_QUIT_STRING
        return self._get_energy_from_subprocess('RNAfold', user_input)

    def _subprocess_binding_affinity(self, sequence1, sequence2):
        """Calls RNAduplex or RNAcofold on a pair of strings using 'ATCG'"""

        #comment ported from legacy code:
        # NB: the string NA_parameter_set needs to be exactly the intended filename; 
        #  e.g. any extra whitespace characters causes RNAduplex to
        #  default to RNA parameter set without warning the user!
    
        if self._use_duplex:
            executable_name = 'RNAduplex'
            user_input = '\n'.join([sequence1,sequence2]) + self._VIENNA_QUIT_STRING
        else:
            executable_name = 'RNAcofold'
            user_input = '&'.join([sequence1,sequence2]) + self._VIENNA_QUIT_STRING

        return self._get_energy_from_subprocess(executable_name, user_input)
        
    def _get_energy_from_subprocess(self, executable_name, user_input):
        vienna_process = subprocess.Popen(
            [
                executable_name,
                '-P', self._params_filename,
                '-T', str(self._temperature),
                '--noGU',
                '--noconv',
            ],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
        )  

        try: 
            output, stderr = vienna_process.communicate(user_input.encode('utf-8'))
            output = output.decode('utf-8')
            stderr = stderr.decode('utf-8')
        except BaseException as error:
            vienna_process.kill()
            raise error
        
        if stderr.strip() != '': # an error from RNAduplex
            if stderr.split('\n')[0] not in self._IGNORED_ERRORS:
                print('Warning or error from RNAduplex: ', stderr)
                raise ValueError('RNAduplex error')

        FLOATING_POINT_NUMBER_REGEX = r"\(\s*([-+]?[0-9]*\.?[0-9]+)\)"  #looks for number in parens e.g. (-41.70) or (  0.00)
        energy = float(
            re.search(FLOATING_POINT_NUMBER_REGEX, output).group(1) #just get middle part (no parens)
        )
        return energy

