import unittest

from arbiter.base import Arbiter
from arbiter.decorators.abstract import AbstractArbiterDecorator

class TrueDecorator(AbstractArbiterDecorator):
    class ArbiterReject(Exception):
        def __str__(self):
            return "fake"

    def _check_single_condition(self, sequence):
        return True

class FalseDecorator(AbstractArbiterDecorator):
    class ArbiterReject(Exception):
        def __str__(self):
            return "fake"

    def _check_single_condition(self, sequence):
        raise self.ArbiterReject()

class TestAbstractDecorator(unittest.TestCase):
    def setUp(self):
        self.oracle = None
        self.collection = set()
        self.base_arbiter = Arbiter(self.oracle, self.collection)
        self.true_arbiter = TrueDecorator(self.base_arbiter)

    def test_consider_passthrough(self):
        SEQUENCE = "CCC"
        accept = self.true_arbiter.consider(SEQUENCE)
        self.assertEqual(accept, True)

    def test_oracle_passthrough(self):
        self.assertTrue(self.oracle is self.true_arbiter._oracle)

    def test_collection_passthrough(self):
        self.assertTrue(self.collection is self.true_arbiter._collection)

    def test_exception_throwing(self):
        arbiter = FalseDecorator(self.base_arbiter)
        with self.assertRaises(arbiter.ArbiterReject):
            arbiter.consider("AAA")
