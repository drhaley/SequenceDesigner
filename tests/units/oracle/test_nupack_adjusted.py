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
    TEMPERATURE = 40.7

    def setUp(self):
        self.oracle = SensingNupackCLI(self.TEMPERATURE)

    def test_self_affinity_is_positive(self):
        ENERGY = -101
        self.oracle.fake_process.fake_energy = ENERGY
        affinity = self.oracle.self_affinity("A")
        self.assertTrue(affinity > 0)

    def test_binding_affinity_is_positive(self):
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

