from util import common
from arbiter.decorators.abstract import AbstractArbiterDecorator, Rejection

class NotStickyReject(Rejection):
    def __str__(self):
        return "not_sticky"

class Decorator(AbstractArbiterDecorator):
    """
    Asserts that the sequence has high affinity to its own complement (a-a*)
    """
    def __init__(self, parent, threshold):
        super().__init__(parent)
        self._threshold = threshold

    def _check_single_condition(self, sequence):
        affinity_to_complement = self._oracle.binding_affinity(sequence, common.wc(sequence))
        sticky_to_complement = affinity_to_complement >= self._threshold
        if sticky_to_complement:
            return True
        else:
            raise NotStickyReject()
