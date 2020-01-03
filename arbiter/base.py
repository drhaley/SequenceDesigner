#Arbiter is built with the decorator pattern.  Wrap new tests around the base class

class Arbiter():
    def __init__(self, oracle, collection):
        self._oracle = oracle
        self._collection = collection

    def consider(self, sequence):
        return True
