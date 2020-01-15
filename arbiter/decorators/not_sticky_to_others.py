from util import common
from arbiter.decorators.abstract import AbstractArbiterDecorator, Rejection

class StickyToOtherReject(Rejection):
    def __str__(self):
        return "sticky_other"

class Decorator(AbstractArbiterDecorator):
    """
    Asserts that the sequence has weak affinity to other sequences in the collection
    (i.e. for new sequence a, the affinities of a-b, a-b*, a*-b, and a*-b* are all weak)
    """
    def __init__(self, parent, threshold):
        super().__init__(parent)
        self._threshold = threshold

    def _check_single_condition(self, sequence):
        a = sequence
        a_star = common.wc(a)
        for b in self._collection:
            b_star = common.wc(b)
            for seq1, seq2 in [(a,b), (a, b_star), (a_star, b), (a_star, b_star)]:
                if self._affinity_difference(seq1, seq2) >= self._threshold:
                    raise StickyToOtherReject()
        else:
            return True

    def _affinity_difference(self, seq1, seq2):
        return \
            self._oracle.binding_affinity(seq1, seq2) \
                - self._oracle.self_affinity(seq1) \
                - self._oracle.self_affinity(seq2)
