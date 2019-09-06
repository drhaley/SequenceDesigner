from oracle.abstract import AbstractOracle

#TODO: Try to make the system path and python path as smart as possible
# but right now some of the following commands may be helpful:
# - export PATH=$PATH:vienna_install_dir/bin
# - export PYTHONPATH=$PYTHONPATH:vienna_source_dir/interfaces/Python3

#TODO: Will the Python wrapper work from Windows?

#TODO: combine the two version of this class into one class
# with a parameter to choose between them
USE_PYTHON_WRAPPER_LIBRARY = False

################################################################################
if USE_PYTHON_WRAPPER_LIBRARY:
    import RNA

    class Oracle(AbstractOracle):
        def __init__(self, *args, use_duplex=True):
            super().__init__(*args)
            self._use_duplex = use_duplex

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
            if self._use_duplex:
                minimum_free_energy = RNA.duplexfold(sequence1, sequence2).energy
            else:
                _, minimum_free_energy = RNA.cofold('&'.join([sequence1, sequence2]))
            return minimum_free_energy

################################################################################
else: #do not use Python wrapper library, instead call ViennRNA as a subprocess
    import subprocess  #to call out to ViennaRNA
    import re

    class Oracle(AbstractOracle):
        _VIENNA_QUIT_STRING = "@\n"
        _IGNORED_ERRORS = [
            'WARNING: stacking enthalpies not symmetric',
        ]

        def __init__(self, *args, use_duplex=False):
            super().__init__(*args)
            self._use_duplex = use_duplex
    
        def self_affinity(self, sequence):
            user_input = sequence + self._VIENNA_QUIT_STRING
            return self._get_energy_from_subprocess('RNAfold', user_input)

        def binding_affinity(self, sequence1, sequence2):
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
                    #'-P', NA_parameter_set,   #TODO
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
                print('Warning or error from RNAduplex: ', stderr)
                if stderr.split('\n')[0] not in self._IGNORED_ERRORS:
                    print('RNAduplex says:' + str(stderr.split('\n')[0]))
                    raise ValueError('RNAduplex error')

            FLOATING_POINT_NUMBER_REGEX = r"\(\s*([-+]?[0-9]*\.?[0-9]+)\)"  #looks for number in parens e.g. (-41.70) or (  0.00)
            energy = float(
                re.search(FLOATING_POINT_NUMBER_REGEX, output).group(1) #just get middle part (no parens)
            )
            return energy

