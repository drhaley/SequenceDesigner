import unittest

from util import common

class TestUtil(unittest.TestCase):
	def test_product_strings(self):
		self.assertEqual(
			set(common.product_strings(1, "AT")),
            {"A", "T"}
		)
		self.assertEqual(
			set(common.product_strings(2, "AT")),
			{"AA", "AT", "TA", "TT"}
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
