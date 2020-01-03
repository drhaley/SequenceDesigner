import unittest

from arbiter.base import Arbiter
from arbiter.decorators import not_sticky_to_others

class FakeOracle():
    def __init__(self):
        self.affinity = 0.0
        self.number_of_calls = 0

    def binding_affinity(self, seq1, seq2):
        self.number_of_calls += 1
        return self.affinity

class TestNotStickyToOthersDecorator(unittest.TestCase):
    def setUp(self):
        self.threshold = 8.0
        self.oracle = FakeOracle()
        self.collection = ["ATCG", "GGGAAAA", "CCCCC"]
        base_arbiter = Arbiter(self.oracle, self.collection)
        self.arbiter = not_sticky_to_others.Decorator(base_arbiter, self.threshold)

    def test_low_affinity(self):
        self.oracle.affinity = self.threshold - 1.0
        accept = self.arbiter.consider("AAAA")
        self.assertTrue(accept)

    def test_high_affinity(self):
        self.oracle.affinity = self.threshold + 1.0
        accept = self.arbiter.consider("AAAA")
        self.assertFalse(accept)

    def test_number_of_calls(self):
        self.arbiter.consider("AAAA")
        self.assertEqual(self.oracle.number_of_calls, 4*len(self.collection))
