import unittest

from arbiter.base import Arbiter
from arbiter.decorators import not_sticky_to_pairs_lite

class FakeOracle():
    def __init__(self):
        self.affinity = 0.0
        self.number_of_calls = 0

    def binding_affinity(self, seq1, seq2):
        self.number_of_calls += 1
        return self.affinity

class TestNotStickyToPairsLiteDecorator(unittest.TestCase):
    def setUp(self):
        self.threshold = 8.0
        self.oracle = FakeOracle()
        self.collection = ["ATCG", "GGGAAAA", "CCCCC"]
        base_arbiter = Arbiter(self.oracle, self.collection)
        self.arbiter = not_sticky_to_pairs_lite.Decorator(base_arbiter, self.threshold)

    def test_low_affinity(self):
        self.oracle.affinity = self.threshold - 1.0
        accept = self.arbiter.consider("AAAA")
        self.assertTrue(accept)

    def test_high_affinity(self):
        self.oracle.affinity = self.threshold + 1.0
        with self.assertRaises(self.arbiter.Rejection):
            self.arbiter.consider("AAAA")

    def test_number_of_calls(self):
        n = len(self.collection)
        self.arbiter.consider("AAAA")
        self.assertEqual(self.oracle.number_of_calls, 2*n + 3*n*(n-1))
