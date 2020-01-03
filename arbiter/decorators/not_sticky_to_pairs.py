from util import common
from arbiter.decorators.abstract import AbstractArbiterDecorator

class NotStickyToPairsDecorator(AbstractArbiterDecorator):
    """
    Asserts that the sequence has weak affinity in a 2-1 situation
    (i.e. for new sequence a, the following affinities are weak:
        aa-x, xx-a, xy-a, ax-y, xa-y
    )
    Also checks the same conditions with the complements of these sequences
    """
    def _check_single_condition(self, sequence):
        a = sequence
        a_star = common.wc(a)
        for x in self._collection:
            x_star = common.wc(x)

            for seq1, seq2 in [(a,x), (a, x_star), (a_star, x), (a_star, x_star)]:
                if self._oracle.binding_affinity(seq1 + seq1, seq2) >= self._threshold: #aa-x
                    return False
                elif self._oracle.binding_affinity(seq2 + seq2, seq1) >= self._threshold: #xx-a
                    return False

                for y in self._collection:
                    if x != y:
                        y_star = common.wc(y)
                        for seq3 in [y, y_star]:
                            if self._oracle.binding_affinity(seq2 + seq3, seq1) >= self._threshold: #xy-a
                                return False
                            elif self._oracle.binding_affinity(seq1 + seq2, seq3) >= self._threshold: #ax-y
                                return False
                            elif self._oracle.binding_affinity(seq2 + seq1, seq3) >= self._threshold: #xa-y
                                return False

        else:
            return True
