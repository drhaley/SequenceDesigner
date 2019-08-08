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
	def test_hairpin(self):
		strong_binding_energy = sst_dsd.hairpin(
			"GGGGGGGGGGGGGGGGGGGGGGGGGAAATCCCCCCCCCCCCC",
			37.0
		)
		self.assertTrue(strong_binding_energy < 0)
		weak_binding_energy = sst_dsd.hairpin(
			"GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
			37.0
		)
		self.assertTrue(weak_binding_energy >= 0.0)

class python_syntax_checks(unittest.TestCase):
	def test_f_strings(self):
		self.assertEqual(f"{3}", "3")
		self.assertNotEqual(f"{4}", "3")

if __name__ == "__main__":
	unittest.main()