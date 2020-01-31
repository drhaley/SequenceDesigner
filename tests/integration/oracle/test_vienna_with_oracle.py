import unittest

from oracle import vienna

def fixed_place_round(number, DECIMAL_PLACES = 20):
    return round(number, DECIMAL_PLACES)

class TestViennaWithOracle(unittest.TestCase):
    TEMPERATURE = 25.0

    def setUp(self):
        self.mfe_oracle = vienna.Oracle(self.TEMPERATURE, partition_function = False)
        self.partition_oracle = vienna.Oracle(self.TEMPERATURE, partition_function = True)

    def test_low_mfe_self_affinity(self):
        affinity = self.mfe_oracle.self_affinity("CACCCTAATCATCATC")
        self.assertEqual(fixed_place_round(0.0), fixed_place_round(affinity))  #value by regression

    def test_low_partition_self_affinity(self):
        affinity = self.partition_oracle.self_affinity("CACCCTAATCATCATC")
        self.assertEqual(fixed_place_round(0.10048452019691467), fixed_place_round(affinity))  # value by regression

    def test_high_mfe_self_affinity(self):
        affinity = self.mfe_oracle.self_affinity("CCCTCCCTCCCTTTTTGGGTGGGTGGG")
        self.assertEqual(fixed_place_round(9.5600004196167), fixed_place_round(affinity))  # value by regression

    def test_high_partition_self_affinity(self):
        affinity = self.partition_oracle.self_affinity("CCCTCCCTCCCTTTTTGGGTGGGTGGG")
        self.assertEqual(fixed_place_round(9.607780456542969), fixed_place_round(affinity))  # value by regression

    def test_low_mfe_binding_affinity(self):
        affinity = self.mfe_oracle.binding_affinity("TCTACCTCTTTCCCACCTCC", "CAAACAACACAATACACTCA")
        self.assertEqual(fixed_place_round(1.8600000143051147), fixed_place_round(affinity))  # value by regression

    def test_low_partition_binding_affinity(self):
        affinity = self.partition_oracle.binding_affinity("TCTACCTCTTTCCCACCTCC", "CAAACAACACAATACACTCA")
        self.assertEqual(fixed_place_round(2.825085401535034), fixed_place_round(affinity))  # value by regression

    def test_high_mfe_binding_affinity(self):
        affinity = self.mfe_oracle.binding_affinity("CCTCTCTTACCATAAC", "GAGAGG")
        self.assertEqual(fixed_place_round(8.329999923706055), fixed_place_round(affinity))  # value by regression

    def test_high_partition_binding_affinity(self):
        affinity = self.partition_oracle.binding_affinity("CCTCTCTTACCATAAC", "GAGAGG")
        self.assertEqual(fixed_place_round(8.54045581817627), fixed_place_round(affinity))  # value by regression
