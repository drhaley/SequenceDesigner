from util import common
from arbiter.decorators.abstract import AbstractArbiterDecorator

class NotStickyToPairsLiteDecorator(AbstractArbiterDecorator):
    """
    Asserts that the sequence has weak affinity in a 2-1 situation
    (i.e. for new sequence a, the following affinities are weak:
        xx-a*, aa-x*, xy-a*, ax-y*, xa-y*
    )
    DOES NOT CHECK ANY OTHER COMPLEMENTS
    Designed for efficiency, so that unnecessary checks are not performed when using three-letter code sequences
    """
    def _check_single_condition(self, sequence):
        a = sequence
        a_star = common.wc(a)
        for x in self._collection:
            x_star = common.wc(x)

            if self._oracle.binding_affinity(x + x, a_star) >= self._threshold:
                return False
            elif self._oracle.binding_affinity(a + a, x_star) >= self._threshold:
                return False

            for y in self._collection:
                if x != y:
                    y_star = common.wc(y)
                    if self._oracle.binding_affinity(x + y, a_star) >= self._threshold:
                        return False
                    elif self._oracle.binding_affinity(a + x, y_star) >= self._threshold:
                        return False
                    elif self._oracle.binding_affinity(x + a, y_star) >= self._threshold:
                        return False

        else:
            return True
