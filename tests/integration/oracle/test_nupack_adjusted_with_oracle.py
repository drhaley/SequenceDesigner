import unittest

from oracle import nupack_adjusted as nupack

def fixed_place_round(number, DECIMAL_PLACES = 6):
    return round(number, DECIMAL_PLACES)

class TestNupackAdjustedWithOracle(unittest.TestCase):
    TEMPERATURE = 25.0

    def setUp(self):
        self.mfe_oracle = nupack.Oracle(self.TEMPERATURE)
        self.partition_oracle = nupack.Oracle(self.TEMPERATURE, partition_function = True)

    def test_low_mfe_self_affinity(self):
        affinity = self.mfe_oracle.self_affinity("CACCCTAATCATCATC")
        self.assertEqual(fixed_place_round(0.111844329), fixed_place_round(affinity))  #value by regression

    def test_low_partition_self_affinity(self):
        affinity = self.partition_oracle.self_affinity("CACCCTAATCATCATC")
        self.assertEqual(fixed_place_round(0.111853183), fixed_place_round(affinity))  # value by regression

    def test_high_mfe_self_affinity(self):
        affinity = self.mfe_oracle.self_affinity("CCCTCCCTCCCTTTTTGGGTGGGTGGG")
        self.assertEqual(fixed_place_round(10.6524319), fixed_place_round(affinity))  # value by regression

    def test_high_partition_self_affinity(self):
        affinity = self.partition_oracle.self_affinity("CCCTCCCTCCCTTTTTGGGTGGGTGGG")
        self.assertEqual(fixed_place_round(10.6527791), fixed_place_round(affinity))  # value by regression

    def test_low_mfe_binding_affinity(self):
        affinity = self.mfe_oracle.binding_affinity("TCTACCTCTTTCCCACCTCC", "CAAACAACACAATACACTCA")
        self.assertEqual(fixed_place_round(1.682482), fixed_place_round(affinity))  # value by regression

    def test_low_partition_binding_affinity(self):
        affinity = self.partition_oracle.binding_affinity("TCTACCTCTTTCCCACCTCC", "CAAAC")
        self.assertEqual(fixed_place_round(1.164256), fixed_place_round(affinity))  # value by regression

    def test_high_mfe_binding_affinity(self):
        affinity = self.mfe_oracle.binding_affinity("CCTCTCTTACCATAAC", "GAGAGG")
        self.assertEqual(fixed_place_round(7.454112), fixed_place_round(affinity))  # value by regression

    def test_high_partition_binding_affinity(self):
        affinity = self.mfe_oracle.binding_affinity("CCTCTCTTACCATAAC", "GAGAGG")
        self.assertEqual(fixed_place_round(7.454112), fixed_place_round(affinity))  # value by regression
