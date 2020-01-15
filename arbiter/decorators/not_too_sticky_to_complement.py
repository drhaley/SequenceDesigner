from util import common
from arbiter.decorators.abstract import AbstractArbiterDecorator, Rejection

class TooStickyReject(Rejection):
    def __str__(self):
        return "too_sticky"

class Decorator(AbstractArbiterDecorator):
    """
    Asserts that the sequence does not have too high of affinity to its own complement (a-a*)
    """
    def __init__(self, parent, threshold):
        super().__init__(parent)
        self._threshold = threshold

    def _check_single_condition(self, sequence):
        affinity_to_complement = self._oracle.binding_affinity(sequence, common.wc(sequence))
        too_sticky_to_complement = affinity_to_complement >= self._threshold
        if too_sticky_to_complement:
            raise TooStickyReject()
        else:
            return True

    def _affinity_difference(self, seq1, seq2):
        return \
            self._oracle.binding_affinity(seq1, seq2) \
                - self._oracle.self_affinity(seq1) \
                - self._oracle.self_affinity(seq2)
