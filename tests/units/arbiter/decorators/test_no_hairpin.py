import unittest

from arbiter.base import Arbiter
from arbiter.decorators import no_hairpin

class FakeOracle():
    def __init__(self):
        self.affinity = 0.0

    def self_affinity(self, seq1, seq2):
        return self.affinity

class TestStickyToComplementDecorator(unittest.TestCase):
    def setUp(self):
        self.threshold = 8.0
        self.oracle = FakeOracle()
        self.collection = set()
        base_arbiter = Arbiter(self.oracle, self.collection)
        self.arbiter = no_hairpin.Decorator(base_arbiter, self.threshold)

    def test_no_hairpin(self):
        self.oracle.affinity = self.threshold - 1.0
        accept = self.arbiter.consider("AAAA")
        self.assertTrue(accept)

    def test_hairpin(self):
        self.oracle.affinity = self.threshold + 1.0
        with self.assertRaises(self.arbiter.Rejection):
            self.arbiter.consider("AAAA")

