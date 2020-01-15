#experimental design for two domain ("a b") TBN experiment

from oracle.vienna import Oracle
from generator.random import Generator
from collection.set import Collection

from arbiter.base import Arbiter as BaseArbiter
from arbiter.decorators import \
	not_sticky_to_others, \
	not_sticky_to_pairs_lite, \
	sticky_to_complement, \
	heuristic_filter

import os
import random

def main():
	domain_length = 20
	oracle = Oracle(temperature = 40.0)
	generator = Generator(
		domain_length = domain_length,
		alphabet="ATC",	 #NOTE: no hairpin check because of three letter code
	)
	collection = Collection()

	filename_suffix = random.randint(1000, 9999)

	filename = os.path.join("sequences", f"a_b_TBN_{filename_suffix}.json")

	try:
		collection.load(filename)
	except FileNotFoundError:
		pass

	arbiter = Arbiter(oracle, collection,
		desired_affinity = 21.0,
		undesirable_single_domain_affinity = 4.0,
		undesirable_middle_domain_affinity = 4.0,
	)

	poly_T = "T"*domain_length
	collection.add(poly_T)       #we want domains to be orthogonal to poly-T segments

	NUMBER_OF_ITERATIONS = 500000

	rejection_dict = {}

	for _ in range(NUMBER_OF_ITERATIONS):
		sequence = next(generator)
		try:
			arbiter.consider(sequence)

			collection.add(sequence)
			print(f"Accepted {sequence}")
		except arbiter.Rejection as e:
			handle_rejection(sequence, e, rejection_dict)

	collection.remove(poly_T)

	print(rejection_dict)
	print('\n')
	print(f"Found {len(collection)} sequences:")
	print(list(collection))
	collection.save(filename)

def handle_rejection(sequence, exception, rejection_dict):
	reason = str(exception)
	print(f"Rejected {sequence} for reason {reason}")
	if reason in rejection_dict:
		rejection_dict[reason] += 1
	else:
		rejection_dict[reason] = 1

def Arbiter(
			oracle,
			collection,
			desired_affinity,
			undesirable_single_domain_affinity,
			undesirable_middle_domain_affinity
	):
	forbidden_substrings = [
		r"[CG]{4}",
		r"[AT]{5}",
		r"^[AT]{3}",
		r"[AT]{3}$",
		r"AAAA",
		r"TTTT",
	]

	# outer decorators should be the fastest checks, so put those last
	arbiter = BaseArbiter(oracle, collection)
	arbiter = not_sticky_to_pairs_lite.Decorator(arbiter, undesirable_middle_domain_affinity)
	arbiter = not_sticky_to_others.Decorator(arbiter, undesirable_single_domain_affinity)
	arbiter = sticky_to_complement.Decorator(arbiter, desired_affinity)
	arbiter = heuristic_filter.Decorator(arbiter, forbidden_substrings)

	return arbiter

if __name__ == "__main__":
	main()
