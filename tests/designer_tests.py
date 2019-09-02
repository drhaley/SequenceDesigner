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


###############################################
#TODO: Iterate over all oracles
import oracle.nupack as oracle_lib
#import oracle.debug as oracle_lib
###############################################
#choose which sequence iterator to use here.  TODO: tie this option to the command-line
import sequence_iterator.exhaustive as sequence_iterator_lib
###############################################

class oracle_tests(unittest.TestCase):
	__TEMPERATURE = 40.0

	def __init__(self, *args):
		self.__oracle = oracle_lib.Oracle()
		super().__init__(*args)

	def test_hairpin(self):
		strong_binding_energy = self.__oracle.self_affinity(
			"GGGGGGGGGGGGGGGGGGGGGGGGGAAATCCCCCCCCCCCCC",
			self.__TEMPERATURE
		)
		self.assertTrue(strong_binding_energy < 0.0)
		weak_binding_energy = self.__oracle.self_affinity(
			"GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
			self.__TEMPERATURE
		)
		self.assertTrue(weak_binding_energy >= 0.0)

	def test_binding(self):
		seq1 = "CCCC"
		seq2 = "GGGG"

		strong_binding_energy = self.__oracle.binding_affinity(seq1, seq2, self.__TEMPERATURE)
		self.assertTrue(strong_binding_energy < 0.0)

		weak_binding_energy = self.__oracle.binding_affinity(seq1, seq1, self.__TEMPERATURE)
		self.assertTrue(weak_binding_energy > 0.0)


class sequence_iterator_checks(unittest.TestCase):
	def __init__(self, *args):
		self.__sequence_iterator = sequence_iterator_lib.SequenceIterator()
		super().__init__(*args)

	def test_grab_many_sequences(self):
		NUMBER_OF_GRABS = 100
		for _ in range(NUMBER_OF_GRABS):
			seq = self.__sequence_iterator.next()
	
	
class python_syntax_checks(unittest.TestCase):
	def test_f_strings(self):
		self.assertEqual(f"{3}", "3")
		self.assertNotEqual(f"{4}", "3")


if __name__ == "__main__":
	unittest.main()