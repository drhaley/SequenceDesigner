import unittest

from collection.set import Collection

class TestSetCollection(unittest.TestCase):
    def setUp(self):
        self.collection = Collection()

    def test_add(self):
        test_sequence = "AAA"
        self.collection.add(test_sequence)
        self.assertTrue(test_sequence in self.collection)
        
    def test_add_duplicates(self):
        for _ in range(2):
            self.collection.add("AATTC")
        self.assertTrue(len(self.collection) == 1)

    def test_discard(self):
        test_sequence = "ATCG"
        self.collection.add(test_sequence)
        self.collection.discard(test_sequence)
        self.assertFalse(test_sequence in self.collection)

    def test_discard_when_absent(self):
        test_sequence = "AAAAATCG"
        self.collection.discard(test_sequence)
        self.assertFalse(test_sequence in self.collection)

    def test_contains_none(self):
        self.assertFalse("GGGG" in self.collection)
    
    def test_len_zero(self):
        self.assertTrue(len(self.collection) == 0)

    def test_iter(self):
        test_sequence = "TTCA"
        self.collection.add(test_sequence)
        recent_sequence = None
        for sequence in iter(self.collection):
            recent_sequence = sequence
        self.assertTrue(recent_sequence == test_sequence)
