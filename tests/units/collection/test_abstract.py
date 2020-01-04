import unittest

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
        self.collection.discard(test_sequence)
        self.assertFalse(test_sequence in self.collection)

    def test_remove_when_absent(self):
        with self.assertRaises(KeyError):
            self.collection.remove("CCCC")

    def test_save(self):
        self.assertTrue(False)

    def test_append(self):
        self.assertTrue(False)

    def test_load_v1_0(self):
        self.assertTrue(False)
