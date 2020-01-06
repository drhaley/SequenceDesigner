import unittest
import tempfile

from collection.abstract import AbstractCollection

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
