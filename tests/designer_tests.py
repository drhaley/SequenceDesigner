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
	_TEMPERATURE = 40.0
	_MANUALLY_INSTANTIATED_ORACLES = ['vienna']

	def __init__(self, *args):
		#instantiate all of the different oracles
		super().__init__(*args)

		#_equivalent_oracles := list of pairs of oracles that return identical results
		self._equivalent_oracles = self._get_vienna_equivalent_oracles()
		
		self._oracle_list = [
			oracle
			for oracle_pair in self._equivalent_oracles
			for oracle in oracle_pair
		]

		for oracle_name in self._oracle_names():
			if oracle_name.lower() not in self._MANUALLY_INSTANTIATED_ORACLES:
				oracle_library = self._import_oracle_by_name(oracle_name)
				self._oracle_list.append(
					oracle_library.Oracle(self._TEMPERATURE)
				)

	def _import_oracle_by_name(self, oracle_name):
		return importlib.import_module(f"oracle.{oracle_name}")
	
	def _get_vienna_equivalent_oracles(self):
		vienna_library = self._import_oracle_by_name('vienna')
		equivalent_oracles = []
		for use_duplex in [True, False]:
			equivalent_oracles.append(
				[
					vienna_library.Oracle(
						self._TEMPERATURE, use_duplex=use_duplex, use_subprocess=use_subprocess
					)
					for use_subprocess in [True,False]
				]
			)
		return equivalent_oracles
			

	def _oracle_names(self):
		oracle_names = []
		for file in os.listdir("oracle"):
			if file.endswith(".py"):
				oracle_name = os.path.splitext(file)[0]
				if oracle_name.lower() != "abstract":
					oracle_names.append(oracle_name)
		return oracle_names

	def test_hairpin(self):
		for oracle in self._oracle_list:
			with self.subTest(oracle = oracle):
				strong_binding_energy = oracle.self_affinity(
					"GGGGGGGGGGGGGGGGGGGGGGGGGAAATCCCCCCCCCCCCC"
				)
				self.assertTrue(strong_binding_energy < 0.0)
				weak_binding_energy = oracle.self_affinity(
					"GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
				)
				self.assertTrue(weak_binding_energy >= 0.0)

	def test_binding(self):
		for oracle in self._oracle_list:
			with self.subTest(oracle = oracle):
				polyC = "CCCCCCCCCCCCCCC"
				polyG = "GGGGGGGGGGGGGGG"
				almost_polyC = "CCCCCCCCCCCCCCA"

				strong_binding_energy = oracle.binding_affinity(polyC, polyG)
				self.assertTrue(strong_binding_energy < 0.0)

				weak_binding_energy = oracle.binding_affinity(polyC, almost_polyC)
				self.assertTrue(weak_binding_energy >= 0.0)

	def test_equivalent_oracles(self):
		TOLERANCE = 0.50  #TODO: Why is Vienna not agreeing strongly with itself!?!

		SELF_AFFINITY_TEST_SET = [
			"AAAATTTTTCCCCCGGGGGGG",
			"CCCCCCGGGGGGAAAATTT",
			"ATCGATCGATCGATCG",
			"AAAAAAAAAAAAAAAAA",
			"ATCATCATCATCATCA",
			"ATC",
		]
		BINDING_AFFINITY_TEST_SET = [
			("AAAATTTTTCCCCCGGGGGGG", "CCCCCCGGGGGGAAAATTT"),
			("ATCGATCGATCGATCG", "AAAAAAAAAAAAAA"),
			("AAAAAAAAAAAAAAAAA", "AAAAAAAAAAAAAA"),
			("ATCATCATCATCATCA", "ATC"),
		]
		for oracle1, oracle2 in self._equivalent_oracles:
			for test_case in SELF_AFFINITY_TEST_SET:
				value1 = oracle1.self_affinity(test_case)
				value2 = oracle2.self_affinity(test_case)
				with self.subTest(oracle1=oracle1, oracle2=oracle2, test_case=test_case,
						value1=value1, value2=value2):
					self.assertTrue(abs(value1 - value2) < TOLERANCE)
			for test_case in BINDING_AFFINITY_TEST_SET:
				value1 = oracle1.binding_affinity(*test_case)
				value2 = oracle2.binding_affinity(*test_case)
				with self.subTest(oracle1=oracle1, oracle2=oracle2, test_case=test_case,
						value1=value1, value2=value2):	
					self.assertTrue(abs(value1 - value2) < TOLERANCE)

class SequenceIteratorChecks(unittest.TestCase):
	def __init__(self, *args):
		self.__sequence_iterator = sequence_iterator_lib.SequenceIterator()
		super().__init__(*args)

	def test_grab_many_sequences(self):
		NUMBER_OF_GRABS = 100
		for _ in range(NUMBER_OF_GRABS):
			_ = self.__sequence_iterator.next()
	
	
class PythonSyntaxChecks(unittest.TestCase):
	def test_f_strings(self):
		self.assertEqual(f"{3}", "3")
		self.assertNotEqual(f"{4}", "3")


if __name__ == "__main__":
	unittest.main()
