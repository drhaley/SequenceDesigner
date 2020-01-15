import abc
import re
import json
import datetime
from util import common

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
        data_dict = {
            "comment": "Written by SequenceDesigner",
            "version": "1.0.2",
            "timestamp": str(datetime.datetime.now()),
            "sequences": [seq for seq in self],
            "complements": [common.wc(seq) for seq in self],
        }
        with open(filename, 'w') as f:
            json.dump(data_dict, f, indent=4)

    def load(self, filename, append=False):
        with open(filename, 'r') as f:
            data_dict = json.load(f)
            major_minor_version = re.match(r"([0-9]+.[0-9]+).[0-9]+", data_dict["version"]).group(1)

        if major_minor_version == "1.0":
            pass #At this time, only v1.0 is implemented, so backwards compatibility not needed
        else:
            raise AssertionError(f"unrecognized version error: save file version {data_dict['version']}")

        if not append:
            self._wipe()

        for sequence in data_dict["sequences"]:
            self.add(sequence)

    def _wipe(self):
        sequences = list(self)
        for sequence in sequences:
            self.discard(sequence)
