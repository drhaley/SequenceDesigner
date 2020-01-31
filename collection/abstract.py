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

    def save(self, filename, oracle = None, strands = None):
        '''
        :param filename: filename to save as
        :param oracle: if not None, uses this Oracle to produce a domain-level analysis
        :param strands: if not None, uses this Collection (and the Oracle) to produce a strand-level analysis
        '''
        data_dict = {
            "comment": "Written by SequenceDesigner",
            "version": "1.1.0",
            "timestamp": str(datetime.datetime.now()),
            "Sequences": [seq for seq in self],
            "Sequences_complement": [common.wc(seq) for seq in self],
        }
        if oracle is not None:
            data_dict["domain_level_analysis"] = self.make_certificate(oracle)
            if strands is not None:
                data_dict["strand_level_analysis"] = strands.make_certificate(oracle, include_complements = False)
        with open(filename, 'w') as f:
            json.dump(data_dict, f, indent = 4, sort_keys = True)

    def load(self, filename, append=False):
        with open(filename, 'r') as f:
            data_dict = json.load(f)
            major_minor_version = re.match(r"([0-9]+.[0-9]+).[0-9]+", data_dict["version"]).group(1)

        if major_minor_version == "1.1":
            sequences = data_dict["Sequences"]
        elif major_minor_version == "1.0":
            sequences = data_dict["sequences"]
        else:
            raise AssertionError(f"unrecognized version error: save file version {data_dict['version']}")

        if not append:
            self._wipe()

        for sequence in sequences:
            self.add(sequence)

    def _wipe(self):
        sequences = list(self)
        for sequence in sequences:
            self.discard(sequence)

    def make_certificate(self, oracle, include_complements = True):
        if include_complements:
            all_sequences = list(self) + [common.wc(seq) for seq in self]
        else:
            all_sequences = list(self)
        self_affinities = {}
        binding_affinities = {}
        for sequence1 in all_sequences:
            self_affinities[sequence1] = oracle.self_affinity(sequence1)
            for sequence2 in all_sequences:
                binding_affinities[', '.join([sequence1, sequence2])] = oracle.binding_affinity(sequence1, sequence2)
        certificate = {
            'Self_affinities': self_affinities,
            'pairwise_affinities': binding_affinities,
        }
        return certificate
