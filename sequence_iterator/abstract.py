import abc   #abstract classes
import itertools
import re
import random

DEFAULT_DOMAIN_LENGTH = 10

class AbstractSequenceIterator(abc.ABC):
###################################################
    @abc.abstractmethod
    def get(self):
        """Retrieves the next sequence, called by __next__()"""
        pass
    
    @abc.abstractmethod
    def feedback(self, fitness):
        """Method by which to give a measure of fitness of the previous sequence
        which can then be used by the class to learn"""
        pass
###################################################
    
    _MAX_ATTEMPTS_BEFORE_WARNING = 1000

    def __init__(self,
            domain_length = DEFAULT_DOMAIN_LENGTH,
            alphabet = "ATCG",
            forbidden_substrings = [],    #accepts regular expressions, e.g. (r"^AA", r"[AT]{5}")
            max_G = float("inf"),         #maximum number of Gs in the unstarred strands
        ):
        self._alphabet = alphabet
        self._domain_length = domain_length
        self._forbidden_substrings = forbidden_substrings
        self._max_G = max_G

    def __iter__(self):
        return self

    def __next__(self):
        while(True):
            for _ in range(self._MAX_ATTEMPTS_BEFORE_WARNING):
                potential_sequence = self.get()

                #There are two obvious ways to implement max_G:
                # generate strings and replace "excess" G's (not uniform!)
                # reject strings with too many G's (but this could be most of them!)
                #To fine tune this, I recommend to handle this in the child class
                while potential_sequence.count("G") > self._max_G:
                    #replace a random G
                    G_locations = [x.start() for x in re.finditer('G', potential_sequence)]
                    replace_location = random.choice(G_locations)
                    new_letter = random.choice(self._alphabet)
                    potential_sequence = new_letter.join([
                        potential_sequence[:replace_location],
                        potential_sequence[replace_location+1:]
                    ])

                if all(
                    re.search(forbidden_substring, potential_sequence) is None  #not found
                    for forbidden_substring in self._forbidden_substrings
                ):
                    return potential_sequence
            else:
                print(f"WARNING: Did not yet find a random sequence in {self._MAX_ATTEMPTS_BEFORE_WARNING} attempts")
    