import unittest

from arbiter.austin import Arbiter

class FakeOracle():
    lookups = {
        ("AAAA", "TTTT"): 10.0,
        ("AAAA", "CCCC"): 0.0,
        ("AAAA", "GGGG"): 0.0,
        ("TTTT", "CCCC"): 0.0,
        ("TTTT", "GGGG"): 0.0,
        ("TTTT", "CCCCCCCC"): 0.0,
        ("GGGG", "AAAAAAAA"): 0.0,
    }

    def binding_affinity(self, seq1, seq2):
        for key in [(seq1, seq2), (seq2, seq1)]:
            if key in self.lookups:
                return self.lookups[key]
        else:
            raise AssertionError(f"Austin test referenced missing key in lookup table: {key}")

class TestAustinArbiter(unittest.TestCase):
    def setUp(self):
        self.oracle = FakeOracle()
        self.collection = {"CCCC"}

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
        accept = self.arbiter.consider("AAAA")
        self.assertTrue(accept)

    def test_austin_weak_sticky_to_self(self):
        self.oracle.lookups[("AAAA", "TTTT")] = 0.0
        accept = self.arbiter.consider("AAAA")
        self.assertFalse(accept)

    def test_austin_sticky_to_other(self):
        self.oracle.lookups[("AAAA", "CCCC")] = 10.0
        accept = self.arbiter.consider("AAAA")
        self.assertFalse(accept)

    def test_austin_sticky_to_pair(self):
        self.oracle.lookups[("GGGG", "AAAAAAAA")] = 10.0
        accept = self.arbiter.consider("AAAA")
        self.assertFalse(accept)
