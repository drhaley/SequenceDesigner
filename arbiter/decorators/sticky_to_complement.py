from util import common
from arbiter.decorators.abstract import AbstractArbiterDecorator

class StickyToComplementDecorator(AbstractArbiterDecorator):
    """
    Asserts that the sequence has high affinity to its own complement (a-a*)
    """
    def _check_single_condition(self, sequence):
        affinity_to_self = self._oracle.binding_affinity(sequence, common.wc(sequence))
        sticky_to_complement = affinity_to_self >= self._threshold

        return sticky_to_complement
