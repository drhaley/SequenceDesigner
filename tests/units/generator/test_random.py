import unittest
import importlib

class TestRandomGenerator(unittest.TestCase):
    DOMAIN_LENGTH = 10
    ALTERNATE_DOMAIN_LENGTH = 11
    NUMBER_OF_TRIALS_PER_TEST = 10

    def setUp(self):
        self.generator_lib = importlib.import_module(f"generator.random")
        self.generator = self.generator_lib.Generator(self.DOMAIN_LENGTH)

    def test_iter(self):
        iterator = iter(self.generator)
        for _ in range(self.NUMBER_OF_TRIALS_PER_TEST):
            next(iterator)

    def test_default_alphabet(self):
        for _ in range(self.NUMBER_OF_TRIALS_PER_TEST):
            sequence = next(self.generator)
            self.assertTrue(all(char in "ATCG" for char in sequence))

    def test_three_letter_code(self):
        THREE_LETTER_CODE = "ATC"
        three_letter_generator = self.generator_lib.Generator(
            self.DOMAIN_LENGTH,
            alphabet = THREE_LETTER_CODE
        )
        for _ in range(self.NUMBER_OF_TRIALS_PER_TEST):
            sequence = next(three_letter_generator)
            self.assertTrue(all(char in THREE_LETTER_CODE for char in sequence))

    def test_domain_length(self):
        for _ in range(self.NUMBER_OF_TRIALS_PER_TEST):
            sequence = next(self.generator)
            self.assertTrue(len(sequence) == self.DOMAIN_LENGTH)

    def test_alternate_domain_length(self):
        alternate_generator = self.generator_lib.Generator(self.ALTERNATE_DOMAIN_LENGTH)
        for _ in range(self.NUMBER_OF_TRIALS_PER_TEST):
            sequence = next(alternate_generator)
            self.assertTrue(len(sequence) == self.ALTERNATE_DOMAIN_LENGTH)
