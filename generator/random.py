from generator.abstract import AbstractGenerator

import random

class Generator(AbstractGenerator):
    def __init__(self, domain_length, alphabet="ATCG"):
        self._domain_length = domain_length
        self._alphabet = alphabet
        
    def __next__(self):
        return ''.join([
            random.choice(self._alphabet)
            for _ in range(self._domain_length)
        ])
