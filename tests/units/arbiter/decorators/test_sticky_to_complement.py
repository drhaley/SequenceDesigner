import unittest

from arbiter.base import Arbiter
from arbiter.decorators import sticky_to_complement

class FakeOracle():
    def __init__(self):
        self.affinity = 0.0

    def binding_affinity(self, seq1, seq2):
        return self.affinity

class TestStickyToComplementDecorator(unittest.TestCase):
    def setUp(self):
        self.threshold = 8.0
        self.oracle = FakeOracle()
        self.collection = set()
        base_arbiter = Arbiter(self.oracle, self.collection)
        self.arbiter = sticky_to_complement.Decorator(base_arbiter, self.threshold)

    def test_too_low(self):
        self.oracle.affinity = self.threshold - 1.0
        accept = self.arbiter.consider("AAAA")
        self.assertFalse(accept)

    def test_too_high(self):
        self.oracle.affinity = self.threshold + 1.0
        accept = self.arbiter.consider("AAAA")
        self.assertTrue(accept)
