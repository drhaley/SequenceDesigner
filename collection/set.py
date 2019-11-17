from collection.abstract import AbstractCollection

class Collection(AbstractCollection):
    def __init__(self):
        self.sequences = set()

    def add(self, sequence):
        self.sequences.add(sequence)

    def discard(self, sequence):
        self.sequences.discard(sequence)

    def __contains__(self, sequence):
        return sequence in self.sequences
    
    def __len__(self):
        return len(self.sequences)

    def __iter__(self):
        return iter(self.sequences)
