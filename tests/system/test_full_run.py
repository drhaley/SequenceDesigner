import unittest
import importlib

class FullRun(unittest.TestCase):
    TEMPERATURE = 40.0
    DOMAIN_LENGTH = 10

    def setUp(self):
        self.oracle_lib = importlib.import_module(f"oracle.viennaCLI")
        self.generator_lib = importlib.import_module(f"generator.random")
        self.collection_lib = importlib.import_module(f"collection.set")
        self.arbiter_lib = importlib.import_module(f"arbiter.base")
        

        self.oracle = self.oracle_lib.Oracle(self.TEMPERATURE)
        self.generator = self.generator_lib.Generator(self.DOMAIN_LENGTH)
        self.collection = self.collection_lib.Collection()
        self.arbiter = self.arbiter_lib.Arbiter(self.oracle, self.collection)

    def test_run(self):
        NUMBER_OF_ITERATIONS = 5

        for _ in range(NUMBER_OF_ITERATIONS):
            sequence = next(self.generator)
            if self.arbiter.consider(sequence):
                self.collection.add(sequence)
