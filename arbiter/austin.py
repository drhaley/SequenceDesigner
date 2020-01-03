#factory method to produce the arbiter discussed with collaborators in DS group at UT Austin

from arbiter.base import Arbiter as BaseArbiter
from arbiter.decorators import \
    not_sticky_to_others,\
    not_sticky_to_pairs_lite,\
    sticky_to_complement,\
    heuristic_filter

def Arbiter(oracle, collection, stickiness, single_domain_threshold, double_domain_threshold):
    forbidden_substrings = [
			r"[CG]{4}",
			r"[AT]{5}",
			r"^[AT]{3}",
			r"[AT]{3}$",
			r"AAAA",
			r"TTTT",
		]

    #outer decorators should be the fastest checks, so put those last
    arbiter = BaseArbiter(oracle, collection)
    arbiter = not_sticky_to_pairs_lite.Decorator(arbiter, double_domain_threshold)
    arbiter = not_sticky_to_others.Decorator(arbiter, single_domain_threshold)
    arbiter = sticky_to_complement.Decorator(arbiter, stickiness)
    arbiter = heuristic_filter.Decorator(arbiter, forbidden_substrings)

    return arbiter
