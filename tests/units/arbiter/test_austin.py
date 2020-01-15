import unittest

from arbiter.austin import Arbiter

class FakeOracle():
    lookups = {
        ("AACC", "GGTT"): 10.0,
        ("AACC", "ATCG"): 0.0,
        ("AACC", "CGAT"): 0.0,
        ("GGTT", "ATCG"): 0.0,
        ("GGTT", "CGAT"): 0.0,
        ("GGTT", "ATCGATCG"): 0.0,
        ("CGAT", "AACCAACC"): 0.0,
    }

    def binding_affinity(self, seq1, seq2):
        for key in [(seq1, seq2), (seq2, seq1)]:
            if key in self.lookups:
                return self.lookups[key]
        else:
            raise AssertionError(f"Austin test referenced missing key in lookup table: {key}")

    def self_affinity(self, seq1):
        return 0.0

class TestAustinArbiter(unittest.TestCase):
    def setUp(self):
        self.oracle = FakeOracle()
        self.collection = {"ATCG"}

        stickiness = 8.0
        single_domain_threshold = 4.0
        double_domain_threshold = 5.0

        self.arbiter = Arbiter(
            self.oracle,
            self.collection,
            stickiness,
            single_domain_threshold,
            double_domain_threshold
        )

    def test_austin_good_consider(self):
        accept = self.arbiter.consider("AACC")
        self.assertTrue(accept)

    def test_austin_weak_sticky_to_self(self):
        self.oracle.lookups[("AACC", "GGTT")] = 0.0
        with self.assertRaises(self.arbiter.Rejection):
            self.arbiter.consider("AACC")

    def test_austin_sticky_to_other(self):
        self.oracle.lookups[("AACC", "ATCG")] = 10.0
        with self.assertRaises(self.arbiter.Rejection):
            self.arbiter.consider("AACC")

    def test_austin_sticky_to_pair(self):
        self.oracle.lookups[("CGAT", "AACCAACC")] = 10.0
        with self.assertRaises(self.arbiter.Rejection):
            accept = self.arbiter.consider("AACC")

    def test_austin_filters(self):
        #these should be filtered immediately without attempting to call the oracle
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
                with self.assertRaises(self.arbiter.Rejection):
                    self.arbiter.consider(sequence)
