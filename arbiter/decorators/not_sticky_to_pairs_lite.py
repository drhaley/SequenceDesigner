from util import common
from arbiter.decorators.abstract import AbstractArbiterDecorator, Rejection

class StickyToPairReject(Rejection):
    def __str__(self):
        return "sticky_pair"

class Decorator(AbstractArbiterDecorator):
    """
    Asserts that the sequence has weak affinity in a 2-1 situation
    (i.e. for new sequence a, the following affinities are weak:
        xx-a*, aa-x*, xy-a*, ax-y*, xa-y*
    )
    DOES NOT CHECK ANY OTHER COMPLEMENTS
    Designed for efficiency, so that unnecessary checks are not performed when using three-letter code sequences
    """
    def __init__(self, parent, threshold):
        super().__init__(parent)
        self._threshold = threshold

    def _check_single_condition(self, sequence):
        a = sequence
        a_star = common.wc(a)
        for x in self._collection:
            x_star = common.wc(x)

            if self._affinity_difference(x + x, a_star) >= self._threshold:
                raise StickyToPairReject()
            elif self._affinity_difference(a + a, x_star) >= self._threshold:
                raise StickyToPairReject()

            for y in self._collection:
                if x != y:
                    y_star = common.wc(y)
                    if self._affinity_difference(x + y, a_star) >= self._threshold:
                        raise StickyToPairReject()
                    elif self._affinity_difference(a + x, y_star) >= self._threshold:
                        raise StickyToPairReject()
                    elif self._affinity_difference(x + a, y_star) >= self._threshold:
                        raise StickyToPairReject()

        else:
            return True

    def _affinity_difference(self, seq1, seq2):
        return \
            self._oracle.binding_affinity(seq1, seq2) \
                - self._oracle.self_affinity(seq1) \
                - self._oracle.self_affinity(seq2)
