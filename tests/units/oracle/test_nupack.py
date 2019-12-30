import unittest

from oracle import nupack as full_nupack

class FakeProcess():
    def __init__(self, arg_list):
        self.arg_list = arg_list
        self.fake_energy = 643
        self.fake_stderr = ""

    def __update__(self, arg_list):
        self.arg_list = arg_list

    def communicate(self, user_input):
        self.user_input = user_input

        number_of_strands = int(user_input.decode('utf-8').split('\n')[0])

        if number_of_strands == 1:
            fake_output = self._fake_one_strand_output(self.fake_energy)
        elif number_of_strands == 2:
            fake_output = self._fake_two_strand_output(self.fake_energy)
        else:
            raise AssertionError(f"received call to nupack process for number of strands = {number_of_strands}")

        return (
            fake_output.encode('utf-8'),
            self.fake_stderr.encode('utf-8')
        )

    def _fake_one_strand_output(self, energy):
        if not isinstance(energy,str):
            energy = format(energy, "e")
        return \
            f"""
            No input file specified.
            Requesting input manually.
            % NUPACK 3.2.2
            % Program: pfunc
            % Start time: Mon Dec 30 11:58:16 2019
            % Command: pfunc -T 40 -multi -material dna 
            Enter number of strands: 1
            Enter sequence for strand type 1: 
            ATCG
            Enter strand permutation (e.g. 1 2 4 3 2): 
            1 2   
            % Sequence:  ATCG
            % v(pi): 1
            % Parameters: DNA, 1998
            % Dangles setting: 1
            % Temperature (C): 40.0
            % Sodium concentration: 1.0000 M
            % Magnesium concentration: 0.0000 M
            %
            % Free energy (kcal/mol) and partition function:
            {energy}
            1.00000000000000e+00
            """

    def _fake_two_strand_output(self, energy):
        if not isinstance(energy,str):
            energy = format(energy, "e")
        return \
            f"""
            No input file specified.
            Requesting input manually.
            % NUPACK 3.2.2
            % Program: pfunc
            % Start time: Mon Dec 30 12:02:40 2019
            % Command: pfunc -T 40 -multi -material dna 
            Enter number of strands: 2
            Enter sequence for strand type 1: 
            ATCG
            Enter sequence for strand type 2: 
            AATTCCGG
            Enter strand permutation (e.g. 1 2 4 3 2): 
            1 2 3
            % Sequence:  ATCG+AATTCCGG
            % v(pi): 1
            % Parameters: DNA, 1998
            % Dangles setting: 1
            % Temperature (C): 40.0
            % Sodium concentration: 1.0000 M
            % Magnesium concentration: 0.0000 M
            %
            % Free energy (kcal/mol) and partition function:
            {energy}
            7.86918961547281e+02
            """

    def kill(self):
        pass

class SensingNupackCLI(full_nupack.Oracle):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.fake_process = FakeProcess([])

    def _open_subprocess(self, arg_list):
        self.fake_process.__update__(arg_list)
        return self.fake_process

class TestNupackCLI(unittest.TestCase):
    TEMPERATURE = 41.2

    def setUp(self):
        self.oracle = SensingNupackCLI(self.TEMPERATURE)

    def test_init_temperature(self):
        self.oracle.self_affinity("AAAA")
        arg_list = self.oracle.fake_process.arg_list
        temperature_index = arg_list.index("-T") + 1
        self.assertEqual(float(arg_list[temperature_index]), self.TEMPERATURE)

    def test_uses_dna_argument(self):
        self.oracle.binding_affinity("CCCC","CCCC")
        arg_list = self.oracle.fake_process.arg_list
        self.assertTrue("dna" in arg_list)

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
            (f'1\n{TEST_SEQUENCE}\n1').encode('utf-8')
        )

    def test_binding_affinity_user_input(self):
        TEST_SEQUENCES = ["ATTCCG", "AATCGG"]
        self.oracle.binding_affinity(*TEST_SEQUENCES)
        user_input = self.oracle.fake_process.user_input
        self.assertEqual(
            user_input,
            ('2\n' + '\n'.join(TEST_SEQUENCES) + '\n1 2').encode('utf-8')
        )

    def test_self_affinity_is_negative_energy(self):
        ENERGY = -101
        self.oracle.fake_process.fake_energy = ENERGY
        affinity = self.oracle.self_affinity("A")
        self.assertTrue(affinity > 0)

    def test_binding_affinity_is_negative_energy(self):
        ENERGY = -102
        self.oracle.fake_process.fake_energy = ENERGY
        affinity = self.oracle.binding_affinity("A", "T")
        self.assertTrue(affinity > 0)

    def test_infinite_energy_should_be_zero(self):
        self.oracle.fake_process.fake_energy = "inf"
        inf_affinity = self.oracle.binding_affinity("A", "T")
        self.oracle.fake_process.fake_energy = 0.0
        zero_affinity = self.oracle.binding_affinity("A", "T")
        self.assertEqual(inf_affinity, zero_affinity)

