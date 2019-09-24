from arbiter.abstract import AbstractArbiter

class Arbiter(AbstractArbiter):
###################################################
    def _conditions_to_check(self):
        return [
            self._sticky_to_complement,           #a-a* strong
            self._not_sticky_to_others,       #a-b* weak
            self._not_sticky_to_pairs,        #xy-a* weak, and xx-a* weak
            self._not_sticky_with_adjacent,   #ay-x* weak, and aa-x* weak
        ]
###################################################
