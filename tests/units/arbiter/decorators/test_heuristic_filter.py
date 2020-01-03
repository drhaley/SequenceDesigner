import unittest

from arbiter.base import Arbiter
from arbiter.decorators import heuristic_filter

class TestStickyToComplementDecorator(unittest.TestCase):
    forbidden_substrings = [
        r"[CG]{4}",
        r"[AT]{5}",
        r"^[AT]{3}",
        r"[AT]{3}$",
        r"AAAA",
        r"TTTT",
    ]

    def setUp(self):
        self.oracle = None
        self.collection = set()
        base_arbiter = Arbiter(self.oracle, self.collection)
        self.arbiter = heuristic_filter.Decorator(base_arbiter, self.forbidden_substrings)

    def test_filtered_out(self):
        forbidden_sequences = [
            "ACGCGA",
            "CAATATG",
            "ATACC",
            "CCATA",
            "CAAAAC",
            "GTTTTG",
        ]
        for sequence in forbidden_sequences:
            with self.subTest(sequence=sequence):
                self.assertFalse(self.arbiter.consider(sequence))

    def test_not_filtered(self):
        permitted_sequences = [
           "CCCACCC",
           "GAATTG",
           "GAAAG",
           "GTTTG",
        ]
        for sequence in permitted_sequences:
            with self.subTest(sequence=sequence):
                self.assertTrue(self.arbiter.consider(sequence))
