import unittest

from arbiter.base import Arbiter
from arbiter.decorators.abstract import AbstractArbiterDecorator

class TrueDecorator(AbstractArbiterDecorator):
    def _check_single_condition(self, sequence):
        return True

class FalseDecorator(AbstractArbiterDecorator):
    def _check_single_condition(self, sequence):
        return False


class TestAbstractDecorator(unittest.TestCase):
    def setUp(self):
        self.oracle = None
        self.collection = set()
        self.base_arbiter = Arbiter(self.oracle, self.collection)
        self.true_arbiter = TrueDecorator(self.base_arbiter)
        self.false_arbiter = FalseDecorator(self.base_arbiter)

    def test_consider_passthrough(self):
        SEQUENCE = "CCC"
        accept = self.true_arbiter.consider(SEQUENCE)
        self.assertEqual(accept, True)
        accept = self.false_arbiter.consider(SEQUENCE)
        self.assertEqual(accept, False)

    def test_oracle_passthrough(self):
        self.assertTrue(self.oracle is self.true_arbiter._oracle)

    def test_collection_passthrough(self):
        self.assertTrue(self.collection is self.true_arbiter._collection)
