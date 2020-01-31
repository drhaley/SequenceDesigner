import unittest

from oracle import viennaCLI as full_vienna_CLI

#TODO: ViennaRNA presents different outputs based upon whether it is called
# as a subprocess or used in a live terminal session
# (e.g. ensemble energy in brackets and mfe in parentheses)

class FakeProcess():
    def __init__(self, arg_list):
        self.arg_list = arg_list
        self.fake_mfe_energy = 742
        self.fake_partition_energy = 973
        self.fake_stderr = ""

    def __update__(self, arg_list):
        self.arg_list = arg_list

    def communicate(self, user_input):
        self.user_input = user_input

        if self.arg_list[0] == "RNAfold":
            fake_output = self._fake_fold_output(float(self.fake_mfe_energy), float(self.fake_partition_energy))
        elif self.arg_list[0] == "RNAduplex":
            fake_output = self._fake_duplex_output(float(self.fake_mfe_energy))
        elif self.arg_list[0] == "RNAcofold":
            fake_output = self._fake_cofold_output(float(self.fake_mfe_energy), float(self.fake_partition_energy))

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

    def _fake_cofold_output(self, mfe_energy, pf_energy):
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
            minimum free energy =   {mfe_energy} kcal/mol

            free energy of ensemble =  {pf_energy} kcal/mol

            frequency of mfe structure in ensemble 1; delta G binding=999.00
            Use '&' to connect 2 sequences that shall form a complex.

            Input string (upper or lower case); @ to quit
            ....,....1....,....2....,....3....,....4....,....5....,....6....,....7....,....8
            @
            """

    def _fake_fold_output(self, mfe_energy, pf_energy):
        return \
            f"""
            Input string (upper or lower case); @ to quit
            ....,....1....,....2....,....3....,....4....,....5....,....6....,....7....,....8
            AAAAA
            length = 5

            AAAAA
            .....
            minimum free energy =   {mfe_energy} kcal/mol
            .....

            free energy of ensemble =  {pf_energy} kcal/mol

            ..... {{  0.00 d=0.00}}
            frequency of mfe structure in ensemble 1; ensemble diversity 0.00

            Input string (upper or lower case); @ to quit
            ....,....1....,....2....,....3....,....4....,....5....,....6....,....7....,....8
            @
            """

    def kill(self):
        pass

class SensingViennaCLI(full_vienna_CLI.Oracle):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.fake_process = FakeProcess([])

    def _open_subprocess(self, arg_list):
        self.fake_process.__update__(arg_list)
        return self.fake_process

class TestViennaCLI(unittest.TestCase):
    TEMPERATURE = 41.2

    def setUp(self):
        self.oracle = SensingViennaCLI(self.TEMPERATURE, partition_function = False)
        self.partition_oracle = SensingViennaCLI(self.TEMPERATURE, partition_function = True)

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
        self.oracle.binding_affinity("CCCC","CCCC")
        arg_list = self.oracle.fake_process.arg_list
        self.assertEqual(arg_list[0], "RNAduplex")
        self.assertTrue("-p" not in arg_list and "-p0" not in arg_list)

    def test_uses_cofold(self):
        self.partition_oracle.binding_affinity("GGGG","GGGG")
        arg_list = self.partition_oracle.fake_process.arg_list
        self.assertEqual(arg_list[0], "RNAcofold")
        self.assertTrue("-p" in arg_list or "-p0" in arg_list)

    def test_uses_fold(self):
        for oracle in [self.oracle, self.partition_oracle]:
            oracle.self_affinity("ATCG")
            arg_list = oracle.fake_process.arg_list
            self.assertEqual(arg_list[0], "RNAfold")
        self.assertTrue("-p" in self.partition_oracle.fake_process.arg_list)

    def test_set_temperature(self):
        ALTERNATE_TEMPERATURE = 52.7
        self.oracle.set_temperature(ALTERNATE_TEMPERATURE)
        self.oracle.self_affinity("AAAAAAA")
        arg_list = self.oracle.fake_process.arg_list
        temperature_index = arg_list.index("-T") + 1
        self.assertEqual(float(arg_list[temperature_index]), ALTERNATE_TEMPERATURE)

    def test_self_affinity_user_input(self):
        TEST_SEQUENCE = "AATTCCGG"
        self.oracle.self_affinity(TEST_SEQUENCE)
        user_input = self.oracle.fake_process.user_input
        self.assertEqual(
            user_input,
            (TEST_SEQUENCE + "\n@\n").encode('utf-8')
        )

    def test_binding_affinity_user_input_with_duplex(self):
        TEST_SEQUENCES = ["ATTCCG", "AATCGG"]
        self.oracle.binding_affinity(*TEST_SEQUENCES)
        user_input = self.oracle.fake_process.user_input
        self.assertEqual(
            user_input,
            ('\n'.join(TEST_SEQUENCES) + "\n@\n").encode('utf-8')
        )

    def test_binding_affinity_user_input_with_cofold(self):
        TEST_SEQUENCES = ["ATTCCGGGG", "AATCGGGGG"]
        self.partition_oracle.binding_affinity(*TEST_SEQUENCES)
        user_input = self.partition_oracle.fake_process.user_input
        self.assertEqual(
            user_input,
            ('&'.join(TEST_SEQUENCES) + "\n@\n").encode('utf-8')
        )

    def test_self_affinity_is_negative_energy_with_partition(self):
        ENERGY = -101
        self.partition_oracle.fake_process.fake_partition_energy = ENERGY
        affinity = self.partition_oracle.self_affinity("A")
        self.assertEqual(affinity, -ENERGY)

    def test_self_affinity_is_negative_energy_with_mfe(self):
        ENERGY = -101
        self.oracle.fake_process.fake_mfe_energy = ENERGY
        affinity = self.oracle.self_affinity("A")
        self.assertEqual(affinity, -ENERGY)

    def test_binding_affinity_is_negative_energy_with_duplex(self):
        ENERGY = -102
        self.oracle.fake_process.fake_mfe_energy = ENERGY
        affinity = self.oracle.binding_affinity("A", "T")
        self.assertEqual(affinity, -ENERGY)

    def test_binding_affinity_is_negative_energy_with_cofold(self):
        ENERGY = -103
        self.partition_oracle.fake_process.fake_partition_energy = ENERGY
        affinity = self.partition_oracle.binding_affinity("C", "G")
        self.assertEqual(affinity, -ENERGY)
