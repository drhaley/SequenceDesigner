from sequence_iterator.abstract import AbstractSequenceIterator

import random

class SequenceIterator(AbstractSequenceIterator):
    def __init__(self,
            *args,
            generator = None,  #provide your generator as an argument
            **kargs
        ):
        super().__init__(*args, **kargs)
        if generator:
            self._generator = generator
        else:
            print("WARNING: Using custom iterator with the default generator")
            self._generator = self._default_get
        
    def get(self):
        return self._generator()
    
    def _default_get(self):
        return ''.join([
            random.choice(self._alphabet)
            for _ in range(self._domain_length)
        ])

    def feedback(self, fitness):
        pass #this iterator does not learn from feedback
