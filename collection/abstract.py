import abc
import re

class AbstractCollection(abc.ABC):
    """
    The Collection is responsible for maintaining a record of the
    'accepted' sequences, and must handle file I/O related to that data
    """
###################################################
    @abc.abstractmethod
    def add(self, sequence):
        pass

    @abc.abstractmethod
    def discard(self, sequence):
        pass

    @abc.abstractmethod
    def __contains__(self, sequence):
        pass

    @abc.abstractmethod
    def __len__(self):
        pass

    @abc.abstractmethod
    def __iter__(self):
        pass
###################################################

    def remove(self, sequence):
        if sequence in self:
            self.discard(sequence)
        else:
            raise KeyError(f"'{sequence}' is not in collection {self}")

    def save(self, filename):
        with open(filename, 'w') as f:
            f.write("Written by SequenceDesigner\n")
            f.write("v1.0\n\n")
            for sequence in self:
                f.write(f"{sequence}\n")

    def load(self, filename, append=False):
        with open(filename, 'r') as f:
            f.readline() #skip first line
            version = re.match(r"v([0-9]+.[0-9]+)", f.readline()).group(1)

        new_sequences = self._read_from_file_by_version(filename, version)

        if not append:
            self._wipe()

        for sequence in new_sequences:
            self.add(sequence)

    def _wipe(self):
        sequences = list(self)
        for sequence in sequences:
            self.discard(sequence)

    def _read_from_file_by_version(self, filename, version):
        new_sequences = []
        with open(filename, 'r') as f:
            if version == "1.0":
                for _ in range(3):
                    f.readline()

                sequence = f.readline().split('\n')[0]
                while sequence:
                    new_sequences.append(sequence)
                    sequence = f.readline().split('\n')[0]
            else:
                raise AssertionError(f"Did not recognize file structure in {filename}")
        return new_sequences