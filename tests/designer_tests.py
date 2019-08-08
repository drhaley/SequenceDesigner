import itertools
import unittest

#add the project dir to the python path
import sys
import os
sys.path.append(
	os.path.abspath(
		os.path.join(os.path.dirname(__file__),"..")
	)
)

#project imports
import dsd
import sst_dsd

class legacy_code_tests(unittest.TestCase):
	TEST_TEMPERATURE = 50.0
	BINDING_STRENGTH_BOUND = 10000.0

	def test_wc(self):
		seq = "ATCG"
		complement_seq = "CGAT"
		self.assertEqual(complement_seq, sst_dsd.wc(seq))

	def test_domain_equal_strength(self):
		seq = "AAAAAAACCCCCCCC"
		seq_is_strongly_bound_to_complement = sst_dsd.domain_equal_strength(
			seq, self.TEST_TEMPERATURE, 0, self.BINDING_STRENGTH_BOUND
		)
		self.assertTrue(seq_is_strongly_bound_to_complement)

	def test_hairpin(self):
		strong_binding_energy = sst_dsd.hairpin(
			"GGGGGGGGGGGGGGGGGGGGGGGGGAAATCCCCCCCCCCCCC",
			self.TEST_TEMPERATURE
		)
		self.assertTrue(strong_binding_energy < 0.0)
		weak_binding_energy = sst_dsd.hairpin(
			"GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
			self.TEST_TEMPERATURE
		)
		self.assertTrue(weak_binding_energy >= 0.0)

	def test_binding(self):
		seq1 = "CCCC"
		seq2 = sst_dsd.wc(seq1)
		strong_binding_energy = sst_dsd.binding(seq1, seq2, self.TEST_TEMPERATURE)
		self.assertTrue(strong_binding_energy < 0.0)

		weak_binding_energy = sst_dsd.binding(seq1, seq1, self.TEST_TEMPERATURE)
		self.assertTrue(weak_binding_energy > 0.0)

	def test_duplex(self):
		seq1 = "AAAAAACCCCCCCT"
		seq2 = sst_dsd.wc(seq1)
		duplex_binding_energy = sst_dsd.duplex(seq1, self.TEST_TEMPERATURE)
		duplex_binding_energy_using_binding_method = sst_dsd.binding(seq1, seq2, self.TEST_TEMPERATURE)
		self.assertEqual(duplex_binding_energy, duplex_binding_energy_using_binding_method)

	def test_randomseq(self):
		sst_dsd.randomseq(10)

	
	
class python_syntax_checks(unittest.TestCase):
	def test_f_strings(self):
		self.assertEqual(f"{3}", "3")
		self.assertNotEqual(f"{4}", "3")

if __name__ == "__main__":
	unittest.main()