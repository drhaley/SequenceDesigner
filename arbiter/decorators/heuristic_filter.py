from util import common
from arbiter.decorators.abstract import AbstractArbiterDecorator, Rejection

class HeuristicReject(Rejection):
    def __str__(self):
        return "heuristic"

class Decorator(AbstractArbiterDecorator):
    """
    Filters out user-provided regular expressions
    to create:
        arbiter = Decorator(arbiter, [regex1, regex2, ...])
    """
    def __init__(self, parent, filter_list):
        super().__init__(parent)
        self._filter_list = filter_list

    def _check_single_condition(self, sequence):
        if common.regex_search(sequence, self._filter_list):
            raise HeuristicReject()
        else:
            return True
