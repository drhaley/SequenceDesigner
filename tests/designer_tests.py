import itertools
import unittest
import os
import abc
import importlib

#add the project dir to the python path
import sys
import os
sys.path.append(
	os.path.abspath(
		os.path.join(os.path.dirname(__file__),"..")
	)
)



###############################################
#choose which sequence iterator to use here.
import sequence_iterator.exhaustive as sequence_iterator_lib
###############################################

class OracleTests(unittest.TestCase):
	__TEMPERATURE = 40.0

	def __init__(self, *args):
		self.__oracle_list = [
			importlib.import_module(f"oracle.{oracle_name}").Oracle()
			for oracle_name in self.__oracle_names()
		]
		super().__init__(*args)

	def __oracle_names(self):
		oracle_names = []
		for file in os.listdir("oracle"):
			if file.endswith(".py"):
				oracle_name = os.path.splitext(file)[0]
				if oracle_name.lower() != "abstract":
					oracle_names.append(oracle_name)
		return oracle_names

	def test_hairpin(self):
		for oracle in self.__oracle_list:
			with self.subTest(oracle = oracle):
				strong_binding_energy = oracle.self_affinity(
					"GGGGGGGGGGGGGGGGGGGGGGGGGAAATCCCCCCCCCCCCC",
					self.__TEMPERATURE
				)
				self.assertTrue(strong_binding_energy < 0.0)
				weak_binding_energy = oracle.self_affinity(
					"GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
					self.__TEMPERATURE
				)
				self.assertTrue(weak_binding_energy >= 0.0)

	def test_binding(self):
		for oracle in self.__oracle_list:
			with self.subTest(oracle = oracle):
				seq1 = "CCCC"
				seq2 = "GGGG"

				strong_binding_energy = oracle.binding_affinity(seq1, seq2, self.__TEMPERATURE)
				self.assertTrue(strong_binding_energy < 0.0)

				weak_binding_energy = oracle.binding_affinity(seq1, seq1, self.__TEMPERATURE)
				self.assertTrue(weak_binding_energy >= 0.0)

class SequenceIteratorChecks(unittest.TestCase):
	def __init__(self, *args):
		self.__sequence_iterator = sequence_iterator_lib.SequenceIterator()
		super().__init__(*args)

	def test_grab_many_sequences(self):
		NUMBER_OF_GRABS = 100
		for _ in range(NUMBER_OF_GRABS):
			seq = self.__sequence_iterator.next()
	
	
class PythonSyntaxChecks(unittest.TestCase):
	def test_f_strings(self):
		self.assertEqual(f"{3}", "3")
		self.assertNotEqual(f"{4}", "3")


if __name__ == "__main__":
	unittest.main()
