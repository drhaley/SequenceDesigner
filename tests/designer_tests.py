import itertools
import unittest
import os
import abc
import importlib
import re
import random
import tempfile
from util import common

#add the project dir to the python path
import sys
import os
sys.path.append(
	os.path.abspath(
		os.path.join(os.path.dirname(__file__),"..")
	)
)

	
class OracleTests(unittest.TestCase):
	_TEMPERATURE = 40.0
	_MANUALLY_INSTANTIATED_ORACLES = ['vienna']

	def __init__(self, *args):
		#instantiate all of the different oracles and iterators
		super().__init__(*args)

		#_equivalent_oracles := list of pairs of oracles that return identical results
		self._equivalent_oracles = self._get_vienna_equivalent_oracles()
		self._oracle_list = [
			oracle
			for oracle_pair in self._equivalent_oracles
			for oracle in oracle_pair
		]
		for oracle_name in oracle_names():
			if oracle_name.lower() not in self._MANUALLY_INSTANTIATED_ORACLES:
				oracle_library = import_oracle_by_name(oracle_name)
				self._oracle_list.append(
					oracle_library.Oracle(self._TEMPERATURE)
				)
	
	def _get_vienna_equivalent_oracles(self):
		vienna_library = import_oracle_by_name('vienna')
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

	def test_hairpin(self):
		for oracle in self._oracle_list:
			with self.subTest(oracle = oracle):
				strong_binding_affinity = oracle.self_affinity(
					"GGGGGGGGGGGGGGGGGGGGGGGGGAAATCCCCCCCCCCCCC"
				)
				self.assertTrue(strong_binding_affinity > 0.0)
				weak_binding_affinity = oracle.self_affinity(
					"GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
				)
				self.assertTrue(weak_binding_affinity <= 0.0)

	def test_binding(self):
		for oracle in self._oracle_list:
			with self.subTest(oracle = oracle):
				polyC = "CCCCCCCCCCCCCCC"
				polyG = "GGGGGGGGGGGGGGG"
				almost_polyC = "CCCCCCCCCCCCCCA"

				strong_binding_affinity = oracle.binding_affinity(polyC, polyG)
				self.assertTrue(strong_binding_affinity > 0.0)

				weak_binding_affinity = oracle.binding_affinity(polyC, almost_polyC)
				self.assertTrue(weak_binding_affinity <= 0.0)

	def test_equivalent_oracles(self):
		TOLERANCE = 0.01

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

class SequenceIteratorTests(unittest.TestCase):
	_DOMAIN_LENGTH = 8
	_NUMBER_OF_GRABS = 20
	_FORBIDDEN_STRINGS = [r"$A", r"A^", r"[CG]{5}"]
	_TEST_GENERATORS = [  #as generator, regex_to_test_against, intended_bool_result
		(lambda: "A"*10,
			"^A{10}$", True),
		(lambda: "G"*10,
			"^G{10}$", True),
		(lambda: ''.join([random.choice(list("AT")) for _ in range(10)]),
			r"^[AT]{8}$", False),
		(lambda: ''.join([random.choice(list("AT")) for _ in range(10)]),
			r"^[TCG]{10}$", False),
		(lambda: ''.join([random.choice(list("ATCG")) for _ in range(random.choice([5,6,7]))]),
			r"^[ATCG]{5}(|[ATCG]{1}|[ATCG]{2})$", True),
	]

	def __init__(self, *args):
		super().__init__(*args)

		self._iterator_list = []
		self._iterator_library_list = []
		for iterator_name in iterator_names():
			iterator_library = import_iterator_by_name(iterator_name)
			self._iterator_list.append(
				iterator_library.SequenceIterator(domain_length=self._DOMAIN_LENGTH)
			)
			self._iterator_library_list.append(iterator_library)

	def test_sequence_length(self):
		for domain_length in range(1, 1+self._DOMAIN_LENGTH):
			for iterator_library in self._iterator_library_list:
				iterator = iterator_library.SequenceIterator(domain_length = domain_length)
				with self.subTest(iterator = iterator, domain_length = domain_length):
					self.assertEqual(
						len(next(iterator)),
						domain_length
					)
				
	def test_alphabet(self):
		for char_list in common.powerset(list("ATCG")):
			alphabet = ''.join(char_list)
			if alphabet:
				for iterator_library in self._iterator_library_list:
					iterator = iterator_library.SequenceIterator(
								domain_length = self._DOMAIN_LENGTH,
								alphabet = alphabet)
					with self.subTest(iterator = iterator, alphabet = alphabet):
						total_grabs = self._NUMBER_OF_GRABS if len(alphabet) > 1 else 1
						for _ in range(total_grabs):
							sequence = next(iterator)
							self.assertEqual(
								"", 
								re.sub(f"[{alphabet}]","", sequence)
							)

	def test_forbidden_strings(self):
		for iterator_library in self._iterator_library_list:
			iterator = iterator_library.SequenceIterator(
				domain_length = self._DOMAIN_LENGTH,
				forbidden_substrings = self._FORBIDDEN_STRINGS
			)
			with self.subTest(iterator = iterator):
				for _ in range(self._NUMBER_OF_GRABS):
					sequence = next(iterator)
					for forbidden_string in self._FORBIDDEN_STRINGS:
						self.assertTrue(
							re.search(forbidden_string, sequence) is None
						)

	def test_works_as_iterator(self):
		for iterator_library in self._iterator_library_list:
			iterator = iterator_library.SequenceIterator()
			with self.subTest(iterator = iterator):
				grabs = 0
				for _ in iterator:
					grabs += 1
					if grabs >= self._NUMBER_OF_GRABS:
						break

	def test_max_G(self):
		for max_G in range(1, 1+self._DOMAIN_LENGTH):
			for iterator_library in self._iterator_library_list:
				iterator = iterator_library.SequenceIterator(max_G = max_G)
				with self.subTest(iterator = iterator, max_G = max_G):
					for _ in range(self._NUMBER_OF_GRABS):
						sequence = next(iterator)
						self.assertTrue(sequence.count("G") <= max_G)
            
	def test_custom_iterator(self):
		custom_iterator_library = import_iterator_by_name("custom")
		for generator, regex_match, intended_test_result in self._TEST_GENERATORS:
			with self.subTest(regex_match = regex_match):
				iterator = custom_iterator_library.SequenceIterator(generator = generator)
				sequences = [next(iterator) for _ in range(self._NUMBER_OF_GRABS)]
				all_sequences_pass = all([re.match(regex_match, sequence) for sequence in sequences])
				if intended_test_result == True:
					self.assertTrue(all_sequences_pass)
				else:
					self.assertFalse(all_sequences_pass)


class ArbiterTests(unittest.TestCase):
	_TEMPERATURE = 40.0

	def __init__(self, *args):
		super().__init__(*args)

		self._oracle = import_oracle_by_name('vienna').Oracle(self._TEMPERATURE)

		self._arbiter_list = []
		self._arbiter_library_list = []
		for arbiter_name in arbiter_names():
			arbiter_library = import_arbiter_by_name(arbiter_name)
			self._arbiter_list.append(
				arbiter_library.Arbiter(oracle = self._oracle)
			)
			self._arbiter_library_list.append(arbiter_library)

	def test_oracle_exists_assertion(self):
		for arbiter_library in self._arbiter_library_list:
			with self.subTest(arbiter_library = arbiter_library):
				with self.assertRaises(AssertionError):
					arbiter_library.Arbiter()  #no oracle provided

	def test_initial_sequences_are_accepted(self):
		TEST_LIST = common.product_strings(3, "ATCG")
		for arbiter_library in self._arbiter_library_list:
			with self.subTest(arbiter_library = arbiter_library):
				arbiter = arbiter_library.Arbiter(
					oracle = self._oracle,
					initial_sequences = TEST_LIST
				)
				self.assertEqual(TEST_LIST, arbiter.get_sequences())

	def test_file_read_and_write(self):
		TEST_SEQUENCES = ["ATCG", "AATT"]
		EXTRA_SEQUENCES = ["AAAA", "AATT"] #intentional overlap with TEST_SEQUENCES

		for arbiter_library in self._arbiter_library_list:
			with self.subTest(arbiter_library = arbiter_library):
				_, temporary_filename = tempfile.mkstemp()
		
				arbiter = arbiter_library.Arbiter(
					oracle = self._oracle,
					initial_sequences = TEST_SEQUENCES,
					save_filename = temporary_filename
				)

				arbiter._save()

				loaded_arbiter = arbiter_library.Arbiter(oracle = self._oracle)
				loaded_arbiter.load_from_file(temporary_filename)

				self.assertEqual(TEST_SEQUENCES, loaded_arbiter.get_sequences())

				appended_arbiter = arbiter_library.Arbiter(
					oracle = self._oracle,
					initial_sequences = EXTRA_SEQUENCES
				)
				appended_arbiter.append_from_file(temporary_filename)

				self.assertTrue(
					all([
						appended_arbiter.get_sequences().count(sequence) == 1
						for sequence in TEST_SEQUENCES + EXTRA_SEQUENCES
					])
				)

	def test_checks_exist(self):
		#Test to be sure that the functions listed in _conditions_to_check() actually exist
		for arbiter in self._arbiter_list:
			for condition in arbiter._conditions_to_check():
				with self.subTest(arbiter = arbiter, condition = condition):
					condition("ATCG")
					with self.assertRaises(TypeError):
						condition()

	def test_fitness(self):
		#TODO
		pass

	def test_sticky_to_complement(self):
		#test self._sticky_to_complement()
		#TODO
		pass

	def test_not_sticky_to_others(self):
		#test self._not_sticky_to_others()
		#TODO
		pass

	def test_not_sticky_to_pairs(self):
		#test self._not_sticky_to_pairs()
		#TODO
		pass
	
	def test_not_sticky_to_adjacent(self):
		#test self._not_sticky_to_adjacent()
		#TODO
		pass			


class UtilTests(unittest.TestCase):
	def test_wc(self):
		TEST_CASES = [
			("AATT", "AATT"),
			("ATCG", "CGAT"),
			("ACTG", "CAGT"),
			("AAAAA", "TTTTT"),
			("TTTTT", "AAAAA"),
			("CCCCC", "GGGGG"),
			("GGGGG", "CCCCC"),
		]
		for sequence, wc_sequence in TEST_CASES:
			self.assertEqual(
				common.wc(sequence),
				wc_sequence
			)

	def test_product_strings(self):
		self.assertEqual(
			set(common.product_strings(1, "AT")),
			set(["A", "T"])
		)
		self.assertEqual(
			set(common.product_strings(2, "AT")),
			set(["AA", "AT", "TA", "TT"])
		)

	def test_powerset(self):
		self.assertEqual(
			list(common.powerset([0])),
			[(), (0,)]
		)
		self.assertEqual(
			list(common.powerset([0,1])),
			[(), (0,), (1,), (0,1)]
		)


class PythonSyntaxTests(unittest.TestCase):
	def test_f_strings(self):
		self.assertEqual(f"{3}", "3")
		self.assertNotEqual(f"{4}", "3")


def import_oracle_by_name(oracle_name):
	return importlib.import_module(f"oracle.{oracle_name}")

def import_iterator_by_name(iterator_name):
	return importlib.import_module(f"sequence_iterator.{iterator_name}")

def import_arbiter_by_name(arbiter_name):
	return importlib.import_module(f"arbiter.{arbiter_name}")

def oracle_names():
	return get_py_filename_list("oracle")
	
def iterator_names():
	return get_py_filename_list("sequence_iterator")

def arbiter_names():
	return get_py_filename_list("arbiter")

def get_py_filename_list(directory):
	filenames = []
	for file in os.listdir(directory):
		if file.endswith(".py"):
			filename = os.path.splitext(file)[0]
			if filename.lower() not in ["abstract", "__init__"]:
				filenames.append(filename)
	return filenames


if __name__ == "__main__":
	unittest.main()
