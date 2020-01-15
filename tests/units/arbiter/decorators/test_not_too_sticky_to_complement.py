import unittest

from arbiter.base import Arbiter
from arbiter.decorators import not_too_sticky_to_complement

class FakeOracle():
    def __init__(self):
        self.affinity = 0.0

    def binding_affinity(self, seq1, seq2):
        return self.affinity

class TestNotTooStickyToComplementDecorator(unittest.TestCase):
    def setUp(self):
        self.threshold = 8.0
        self.oracle = FakeOracle()
        self.collection = set()
        base_arbiter = Arbiter(self.oracle, self.collection)
        self.arbiter = not_too_sticky_to_complement.Decorator(base_arbiter, self.threshold)

    def test_too_high(self):
        self.oracle.affinity = self.threshold + 1.0
        with self.assertRaises(self.arbiter.Rejection):
            self.arbiter.consider("AAAA")

    def test_too_low(self):
        self.oracle.affinity = self.threshold - 1.0
        accept = self.arbiter.consider("AAAA")
        self.assertTrue(accept)
