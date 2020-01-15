#experimental design for two domain ("a b") TBN experiment

from oracle.vienna import Oracle
from generator.random import Generator
from collection.set import Collection

from arbiter.base import Arbiter as BaseArbiter
from arbiter.decorators import \
	not_sticky_to_others, \
	not_sticky_to_pairs_lite, \
	sticky_to_complement, \
	not_too_sticky_to_complement, \
	heuristic_filter, \
	no_hairpin

import os
import random
from util import common

def main():
	domain_lengths = [20, 25]
	hairpin_threshold = 0.0001
	desired_affinity_min = 30.0
	desired_affinity_max = 1.3 * desired_affinity_min
	undesirable_affinity_max = 4.5

	oracle = Oracle(temperature = 25.0)
	generators = [
		Generator(domain_length = domain_length, alphabet="ATC")
			for domain_length in domain_lengths
	]
	collection = Collection()

	filename_suffix = random.randint(1000, 9999)

	filename = os.path.join("sequences", f"a_b_TBN_{filename_suffix}.json")

	try:
		collection.load(filename)
	except FileNotFoundError:
		pass

	arbiter = Arbiter(oracle, collection,
		desired_affinity_min = desired_affinity_min,
		desired_affinity_max = desired_affinity_max,
		hairpin_threshold = hairpin_threshold,
		undesirable_single_domain_affinity = undesirable_affinity_max,
		undesirable_middle_domain_affinity = undesirable_affinity_max,
	)

	poly_T = "T"*max(domain_lengths)
	collection.add(poly_T)       #we want domains to be orthogonal to poly-T segments

	MAX_NUMBER_OF_ITERATIONS = 100000

	rejection_dict = {}

	generator_index = 0

	for _ in range(MAX_NUMBER_OF_ITERATIONS):
		sequence = next(generators[generator_index])
		try:
			arbiter.consider(sequence)

			collection.add(sequence)
			print(f"Accepted {sequence}")
			generator_index = min(generator_index + 1, len(generators) - 1)
		except arbiter.Rejection as e:
			handle_rejection(sequence, e, rejection_dict)

		if len(collection) >= 3:  #3 = 2 good domains + 1 poly-T "domain"
			if (good_structure_in_combined_strands(oracle, collection, hairpin_threshold)):
				break
			else:
				collection.remove(sequence)

	collection.remove(poly_T)

	print(rejection_dict)
	print('\n')
	print(f"Found {len(collection)} sequences:")
	print(list(collection))
	print("Complements:")
	print([common.wc(seq) for seq in collection])
	if len(collection) >= 2:
		collection.save(filename)

def handle_rejection(sequence, exception, rejection_dict):
	reason = str(exception)
	print(f"Rejected {sequence} for reason {reason}")
	if reason in rejection_dict:
		rejection_dict[reason] += 1
	else:
		rejection_dict[reason] = 1

def good_structure_in_combined_strands(oracle, collection, hairpin_threshold):
	arbiter = BaseArbiter(oracle, Collection())
	arbiter = no_hairpin.Decorator(arbiter, hairpin_threshold)

	for seq1 in collection:
		for seq2 in collection:
			try:
				arbiter.consider(seq1 + seq2)
				arbiter.consider(seq2 + seq1)
			except arbiter.Rejection as e:
				return False
	else:
		return True

def Arbiter(
			oracle,
			collection,
			desired_affinity_min,
			desired_affinity_max,
			hairpin_threshold,
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
	arbiter = not_too_sticky_to_complement.Decorator(arbiter, desired_affinity_max)
	arbiter = sticky_to_complement.Decorator(arbiter, desired_affinity_min)
	arbiter = no_hairpin.Decorator(arbiter, hairpin_threshold)
	arbiter = heuristic_filter.Decorator(arbiter, forbidden_substrings)

	return arbiter

if __name__ == "__main__":
	main()
