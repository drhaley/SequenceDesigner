import unittest
import tempfile
import os

from util import common
from collection.abstract import AbstractCollection

class FakeOracle():
    accepted_sequences = {"ATCG", "TTTT", common.wc("ATCG"), common.wc("TTTT")}

    def binding_affinity(self, seq1, seq2):
        if seq1 in self.accepted_sequences:
            if seq2 in self.accepted_sequences:
                return 1.0
            else:
                bad_seq = seq2
        else:
            bad_seq = seq1

        raise AssertionError(f"Abstract collection test referenced missing key in lookup table: {bad_seq}")

    def self_affinity(self, seq1):
        return 0.0

class FakeCollection(AbstractCollection):
    def __init__(self):
        self.sequences = set()

    def add(self, sequence):
        self.sequences.add(sequence)

    def discard(self, sequence):
        self.sequences.discard(sequence)

    def __contains__(self, sequence):
        return sequence in self.sequences

    def __len__(self):
        return len(self.sequences)

    def __iter__(self):
        return iter(self.sequences)

class TestAbstractCollection(unittest.TestCase):
    def setUp(self):
        self.collection = FakeCollection()

    def test_remove(self):
        test_sequence = "ATCGGG"
        self.collection.add(test_sequence)
        self.collection.remove(test_sequence)
        self.assertFalse(test_sequence in self.collection)

    def test_remove_when_empty(self):
        with self.assertRaises(KeyError):
            self.collection.remove("ATCG")

    def test_wipe(self):
        dummy_sequences = {"AA", "TT", "CC"}
        for sequence in dummy_sequences:
            self.collection.add(sequence)
            self.assertTrue(sequence in self.collection)
        self.collection._wipe()
        for sequence in dummy_sequences:
            self.assertFalse(sequence in self.collection)

    def test_save_then_load(self):
        dummy_sequences = {"AA", "TT", "CC"}
        _, filename = tempfile.mkstemp()
        for sequence in dummy_sequences:
            self.collection.add(sequence)
        self.collection.save(filename)
        self.collection._wipe()
        self.collection.load(filename)
        self.assertTrue(dummy_sequences == set(self.collection))

    def test_load_with_append(self):
        dummy_sequences1 = {"AA", "TT", "CC"}
        dummy_sequences2 = {"AAA", "TTT", "GGG"}
        _, filename = tempfile.mkstemp()
        for sequence in dummy_sequences1:
            self.collection.add(sequence)
        self.collection.save(filename)
        self.collection._wipe()
        for sequence in dummy_sequences2:
            self.collection.add(sequence)
        self.collection.load(filename, append = True)
        self.assertTrue(dummy_sequences1.union(dummy_sequences2) == set(self.collection))

    def test_load_legacy_1_0(self):
        legacy_sequences = {"TCTACCTCTTTCCCACCTCC","CAAACAACACAATACACTCA"}
        self.collection.load(os.path.join('tests','resources','legacy_sequences_1_0.json'))
        self.assertTrue(legacy_sequences == set(self.collection))

    def test_load_legacy_1_1(self):
        legacy_sequences = {"CACCCTAATCATCATC"}
        self.collection.load(os.path.join('tests','resources','legacy_sequences_1_1.json'))
        self.assertTrue(legacy_sequences == set(self.collection))

    def test_certificate_without_complements(self):
        self.collection.add("ATCG")
        self.collection.add("TTTT")
        certificate = self.collection.make_certificate(FakeOracle(), include_complements = False)
        self.assertTrue(len(certificate.get_singles()) == 2)
        self.assertTrue(len(certificate.get_pairs()) == 4)

    def test_certificate_with_complements(self):
        self.collection.add("ATCG")
        self.collection.add("TTTT")
        certificate = self.collection.make_certificate(FakeOracle(), include_complements = True)
        self.assertTrue(len(certificate.get_singles()) == 4)
        self.assertTrue(len(certificate.get_pairs()) == 16)
