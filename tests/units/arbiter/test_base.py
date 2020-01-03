import unittest

from arbiter.base import Arbiter

class TestBaseArbiter(unittest.TestCase):
    def setUp(self):
        self.oracle = None
        self.collection = set()
        self.base_arbiter = Arbiter(self.oracle, self.collection)

    def test_base_consider(self):
        accept = self.base_arbiter.consider("AAAA")
        self.assertEqual(accept, True)
