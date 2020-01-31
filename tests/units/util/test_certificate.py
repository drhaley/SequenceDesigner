import unittest

from util.certificate import Certificate

class TestCertificate(unittest.TestCase):
	def setUp(self):
		self.certificate = Certificate()

	def test_empty(self):
		self.assertEqual(self.certificate.get_singles(), {})
		self.assertEqual(self.certificate.get_pairs(), {})

	def test_add_single(self):
		self.certificate.add_single("ATCG", 5.0)
		self.assertEqual(self.certificate.get_singles(), {"ATCG": 5.0})

	def test_add_pair(self):
		self.certificate.add_pair("ATCG", "TTTT", 2.0)
		self.assertEqual(self.certificate.get_pairs(), {("ATCG", "TTTT"): 2.0})

	def test_aliases(self):
		self.certificate.define_alias("TTTT", "a")
		self.certificate.define_alias("AAAA", "a*")
		self.certificate.add_single("TTTT", 3.7)
		self.assertEqual(self.certificate.get_singles(), {"a": 3.7})
		self.certificate.add_pair("TTTT", "AAAA", 3.8)
		self.assertEqual(self.certificate.get_pairs(), {("a", "a*"): 3.8})
