import unittest
import importlib

from oracle import viennaCLI as full_vienna_CLI

class FakeProcess():
    def __init__(self, arg_list):
        self.arg_list = arg_list
        self.fake_energy = 742
        self.fake_stderr = ""

    def communicate(self, user_input):
        self.user_input = user_input

        if self.arg_list[0] == "RNAfold":
            fake_output = self._fake_fold_output(float(self.fake_energy))
        elif self.arg_list[0] == "RNAduplex":
            fake_output = self._fake_duplex_output(float(self.fake_energy))
        elif self.arg_list[0] == "RNAcofold":
            fake_output = self._fake_cofold_output(float(self.fake_energy))

        return (
            fake_output.encode('utf-8'),
            self.fake_stderr.encode('utf-8')
        )

    def _fake_duplex_output(self, energy):
        return \
            f"""
            Input two sequences (one line each); @ to quit
            ....,....1....,....2....,....3....,....4....,....5....,....6....,....7....,....8
            AAAAA
            AAAAA
            lengths = 5,5
            
            .&.   1,1   :   0,0   ({energy})
            
            Input two sequences (one line each); @ to quit
            ....,....1....,....2....,....3....,....4....,....5....,....6....,....7....,....8
            @
            """

    def _fake_cofold_output(self, energy):
        return \
            f"""
            Use '&' to connect 2 sequences that shall form a complex.; @ to quit
            ....,....1....,....2....,....3....,....4....,....5....,....6....,....7....,....8
            AAAAA&AAAAA
            length1 = 5
            length2 = 5
            WARNING: Both input strands are identical, thus inducing rotationally symmetry! Symmetry correction might be required to compute actual MFE!
            AAAAA&AAAAA
            .....&.....
            minimum free energy =   0.00 kcal/mol
            
            free energy of ensemble =  {energy} kcal/mol
            
            frequency of mfe structure in ensemble 1; delta G binding=999.00
            Use '&' to connect 2 sequences that shall form a complex.

            Input string (upper or lower case); @ to quit
            ....,....1....,....2....,....3....,....4....,....5....,....6....,....7....,....8
            @
            """

    def _fake_fold_output(self, energy):
        return \
            f"""
            Input string (upper or lower case); @ to quit
            ....,....1....,....2....,....3....,....4....,....5....,....6....,....7....,....8
            AAAAA
            length = 5

            AAAAA
            .....
            minimum free energy =   0.00 kcal/mol
            .....
            
            free energy of ensemble =  {energy} kcal/mol
            
            ..... {{  0.00 d=0.00}}
            frequency of mfe structure in ensemble 1; ensemble diversity 0.00

            Input string (upper or lower case); @ to quit
            ....,....1....,....2....,....3....,....4....,....5....,....6....,....7....,....8
            @
            """                                     

    def kill(self):
        pass

class SensingViennaCLI(full_vienna_CLI.Oracle):
    def _open_subprocess(self, arg_list):
        self.fake_process = FakeProcess(arg_list)
        return self.fake_process

class TestViennaCLI(unittest.TestCase):
    TEMPERATURE = 41.2

    def setUp(self):
        self.oracle = SensingViennaCLI(self.TEMPERATURE)

    def test_init_temperature(self):
        self.oracle.self_affinity("AAAA")
        arg_list = self.oracle.fake_process.arg_list
        temperature_index = arg_list.index("-T") + 1
        self.assertEqual(float(arg_list[temperature_index]), self.TEMPERATURE)

    def test_init_params_filename(self):
        TEST_FILENAME = "test.file"
        self.oracle = SensingViennaCLI(self.TEMPERATURE, params_filename = TEST_FILENAME)
        self.oracle.self_affinity("TTTT")
        arg_list = self.oracle.fake_process.arg_list
        filename_index = arg_list.index("-P") + 1
        self.assertEqual(arg_list[filename_index], TEST_FILENAME)

    def test_uses_duplex(self):
        pass

    def test_uses_cofold(self):
        pass

    def test_set_temperature(self):
        pass

    def test_self_affinity(self):
        pass

    def test_binding_affinity(self):
        pass

    def test_get_energy_from_subprocess(self):
        pass
