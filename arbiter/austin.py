#factory method to produce the arbiter discussed with collaborators in DS group at UT Austin

from arbiter.base import Arbiter as BaseArbiter
from arbiter.decorators import not_sticky_to_others, not_sticky_to_pairs_lite, sticky_to_complement

def Arbiter(oracle, collection, stickiness, single_domain_threshold, double_domain_threshold):
    #outer decorators should be the fastest checks, so put those last

    arbiter = BaseArbiter(oracle, collection)
    arbiter = not_sticky_to_pairs_lite.Decorator(arbiter, double_domain_threshold)
    arbiter = not_sticky_to_others.Decorator(arbiter, single_domain_threshold)
    arbiter = sticky_to_complement.Decorator(arbiter, stickiness)

    return arbiter
