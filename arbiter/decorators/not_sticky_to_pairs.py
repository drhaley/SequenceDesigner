from util import common
from arbiter.decorators.abstract import AbstractArbiterDecorator, Rejection

class StickyToPairReject(Rejection):
    def __str__(self):
        return "sticky_pair"

class Decorator(AbstractArbiterDecorator):
    """
    Asserts that the sequence has weak affinity in a 2-1 situation
    (i.e. for new sequence a, the following affinities are weak:
        aa-x, xx-a, xy-a, ax-y, xa-y
    )
    Also checks the same conditions with the complements of these sequences
    """
    def __init__(self, parent, threshold):
        super().__init__(parent)
        self._threshold = threshold

    def _check_single_condition(self, sequence):
        a = sequence
        a_star = common.wc(a)
        for x in self._collection:
            x_star = common.wc(x)

            for seq1, seq2 in [(a,x), (a, x_star), (a_star, x), (a_star, x_star)]:
                if self._affinity_difference(seq1 + seq1, seq2) >= self._threshold: #aa-x
                    raise StickyToPairReject()
                elif self._affinity_difference(seq2 + seq2, seq1) >= self._threshold: #xx-a
                    raise StickyToPairReject()

                for y in self._collection:
                    if x != y:
                        y_star = common.wc(y)
                        for seq3 in [y, y_star]:
                            if self._affinity_difference(seq2 + seq3, seq1) >= self._threshold: #xy-a
                                raise StickyToPairReject()
                            elif self._affinity_difference(seq1 + seq2, seq3) >= self._threshold: #ax-y
                                raise StickyToPairReject()
                            elif self._affinity_difference(seq2 + seq1, seq3) >= self._threshold: #xa-y
                                raise StickyToPairReject()

        else:
            return True

    def _affinity_difference(self, seq1, seq2):
        return \
            self._oracle.binding_affinity(seq1, seq2) \
                - self._oracle.self_affinity(seq1) \
                - self._oracle.self_affinity(seq2)
