from util import common
from arbiter.decorators.abstract import AbstractArbiterDecorator

class Decorator(AbstractArbiterDecorator):
    """
    Asserts that the sequence is not likely to form a hairpin
    """
    def _check_single_condition(self, sequence):
        affinity_to_self = self._oracle.self_affinity(sequence, common.wc(sequence))
        sticky_to_self = affinity_to_self >= self._threshold

        return sticky_to_self
