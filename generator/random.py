from generator.abstract import AbstractGenerator
from util import common

import random

class Generator(AbstractGenerator):
    MAX_ATTEMPTS = 100

    def __init__(self, domain_length, alphabet="ATCG"):
        self._domain_length = domain_length
        self._alphabet = alphabet
        self._forbidden = []
        
    def __next__(self):
        for _ in range(self.MAX_ATTEMPTS):
            candidate = ''.join([
                random.choice(self._alphabet)
                for _ in range(self._domain_length)
            ])
            if not common.regex_search(candidate, self._forbidden):
                return candidate
        else:
            raise AssertionError(f"Could not generate a sequence after {MAX_ATTEMPTS} tries")

    def forbid_substring(self, forbidden_regex):
        self._forbidden.append(forbidden_regex)

