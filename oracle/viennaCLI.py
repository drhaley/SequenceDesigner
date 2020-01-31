import subprocess  #to call out to ViennaRNA
import re

from oracle.abstract import AbstractOracle

class Oracle(AbstractOracle):
    _DEFAULT_PARAMS_FILENAME = "lib/dna_mathews2004.par"
    _VIENNA_QUIT_STRING = "\n@\n"
    _IGNORED_ERRORS = [
        'WARNING: stacking enthalpies not symmetric',
    ]

    def __init__(self, temperature, 
            partition_function = False, params_filename = None):
        if not params_filename:
            params_filename = self._DEFAULT_PARAMS_FILENAME
        self._params_filename = params_filename
        self._use_partition_function = partition_function
        self.set_temperature(temperature)

    def set_temperature(self, temperature):
        self._temperature = temperature

    def self_affinity(self, sequence):
        minimum_free_energy = self._subprocess_self_binding_energy(sequence)
        return -minimum_free_energy

    def binding_affinity(self, sequence1, sequence2):
        minimum_free_energy = self._subprocess_binding_energy(sequence1, sequence2)
        return -minimum_free_energy
    
    def _subprocess_self_binding_energy(self, sequence):
        user_input = sequence + self._VIENNA_QUIT_STRING
        if self._use_partition_function:
            params = '-p'
        else:
            params = None
        return self._get_energy_from_subprocess('RNAfold', params, user_input)

    def _subprocess_binding_energy(self, sequence1, sequence2):
        """Calls RNAduplex or RNAcofold on a pair of strings using 'ATCG'"""

        #comment ported from legacy code:
        # NB: the string NA_parameter_set needs to be exactly the intended filename; 
        #  e.g. any extra whitespace characters causes RNAduplex to
        #  default to RNA parameter set without warning the user!
    
        if self._use_partition_function:
            executable_name = 'RNAcofold'
            additional_parameters = '-p0'  #'-p0' is more efficient than '-p'
            user_input = '&'.join([sequence1,sequence2]) + self._VIENNA_QUIT_STRING
        else:
            executable_name = 'RNAduplex'
            additional_parameters = ''
            user_input = '\n'.join([sequence1,sequence2]) + self._VIENNA_QUIT_STRING

        return self._get_energy_from_subprocess(executable_name, additional_parameters, user_input)

    def _open_subprocess(self, command_line_string_list):
        return subprocess.Popen(
            command_line_string_list,
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
        )
        
    def _get_energy_from_subprocess(self, executable_name, additional_parameters, user_input):
        command_line_string_list = [
                executable_name,
                '-P', self._params_filename,
                '-T', str(self._temperature),
                '--noGU',
                '--noconv',
        ]
        if additional_parameters:
            command_line_string_list.append(additional_parameters)

        vienna_process = self._open_subprocess(command_line_string_list)

        energy_regex = self._get_energy_regex()

        try:
            output, stderr = vienna_process.communicate(user_input.encode('utf-8'))
            output = output.decode('utf-8')
            stderr = stderr.decode('utf-8')
        except BaseException as error:
            vienna_process.kill()
            raise error

        if stderr.strip() != '': # an error from RNAduplex (or RNAcofold)
            if stderr.split('\n')[0] not in self._IGNORED_ERRORS:
                print('Warning or error from RNAduplex/RNAcofold: ', stderr)
                raise ValueError('RNAduplex/RNAcofold error')

        search_result = re.search(energy_regex, output)

        if search_result:
            energy = search_result.group(1)
            if energy is None:  #try the second recognition string
                energy = search_result.group(2)
        else:
            raise AssertionError(f"Could not locate energy in ViennaRNA output:\n{output}\n")

        return float(energy)

    def _get_energy_regex(self):
        FLOATING_POINT_NUMBER_REGEX = r"\s*([-+]?[0-9]*\.?[0-9]+)\s*"

        if self._use_partition_function:
            ENSEMBLE_ENERGY_REGEX = "".join([
                r"free energy of ensemble =",
                FLOATING_POINT_NUMBER_REGEX,
                r"kcal\/mol"
            ])
            BRACKETS_NUMBER_REGEX = "".join([
                r"\[",
                FLOATING_POINT_NUMBER_REGEX,
                r"\]"
            ])

            energy_regex = f"{ENSEMBLE_ENERGY_REGEX}|{BRACKETS_NUMBER_REGEX}"
        else:
            MFE_REGEX = "".join([
                r"minimum free energy =",
                FLOATING_POINT_NUMBER_REGEX,
                r"kcal\/mol"
            ])
            PARENS_NUMBER_REGEX = "".join([
                r"\(",
                FLOATING_POINT_NUMBER_REGEX,
                r"\)"
            ])
            energy_regex = f"{MFE_REGEX}|{PARENS_NUMBER_REGEX}"

        return energy_regex
