from util import common
from arbiter.decorators.abstract import AbstractArbiterDecorator, Rejection

class HairpinReject(Rejection):
    def __str__(self):
        return "hairpin"

class Decorator(AbstractArbiterDecorator):
    """
    Asserts that the sequence is not likely to form a hairpin (and same for its complement)
    """
    def __init__(self, parent, threshold):
        super().__init__(parent)
        self._threshold = threshold

    def _check_single_condition(self, specified_sequence):
        for sequence in [specified_sequence, common.wc(specified_sequence)]:
            affinity_to_self = self._oracle.self_affinity(sequence)
            sticky_to_self = affinity_to_self >= self._threshold
            if sticky_to_self:
                raise HairpinReject()
        else:
            return True

