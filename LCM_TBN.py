#experimental design for LCM single domain TBN experiment
#approach: find two orthogonal domains and concatenate

from oracle.vienna import Oracle
from oracle.nupack import Oracle as NupackOracle
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

forbidden_substrings = [
	r"[CG]{4}",
	r"[AT]{5}",
	r"^[AT]{3}",
	r"[AT]{3}$",
	r"AAAA",
	r"TTTT",
]

def main():
	filename_suffix = random.randint(1000, 9999)
	filename = os.path.join("sequences", f"LCM_TBN_{filename_suffix}.json")

	try:
		domains = Collection()
		domains.load(filename)
	except FileNotFoundError:
		domains = generate_domains()

	summarize_and_save(domains, filename)

def generate_domains():
	domain_length = 7   #7*2 + 2 Cs on the end = 16
	hairpin_threshold = 0.0001
	desired_affinity_min = 6.0
	desired_affinity_max = 1.5 * desired_affinity_min
	undesirable_affinity_max = 1.5

	MAX_NUMBER_OF_ITERATIONS = 500000

	oracle = Oracle(temperature = 25.0)
	generator = Generator(domain_length = domain_length, alphabet="ATC")
	collection = Collection()

	arbiter = Arbiter(oracle, collection,
		desired_affinity_min = desired_affinity_min,
		desired_affinity_max = desired_affinity_max,
		hairpin_threshold = hairpin_threshold,
		undesirable_single_domain_affinity = undesirable_affinity_max,
		undesirable_middle_domain_affinity = undesirable_affinity_max,
	)

	poly_T = "T"*domain_length
	collection.add(poly_T)       #we want domains to be orthogonal to poly-T segments

	rejection_dict = {}

	for _ in range(MAX_NUMBER_OF_ITERATIONS):
		sequence1 = next(generator)
		sequence2 = next(generator)
		try:
			arbiter.consider(sequence1)
			collection.add(sequence1)
			try:
				arbiter.consider(sequence2)
				collection.add(sequence2)
			except arbiter.Rejection as e:
				collection.remove(sequence1)
				handle_rejection(sequence2, e, rejection_dict)
		except arbiter.Rejection as e:
			handle_rejection(sequence1, e, rejection_dict)

		if len(collection) >= 3:  #3 = 2 good domains + 1 poly-T "domain"
			if (good_structure_in_combined_strands(oracle, collection, hairpin_threshold)):
				break
			else:
				collection.remove(sequence1)
				collection.remove(sequence2)

	collection.remove(poly_T)

	print(rejection_dict)
	print('\n')

	if len(collection) == 2:
		concatenated_collection = Collection()
		concatenated_strand = concatenate(*list(collection))
		concatenated_collection.add(concatenated_strand)
	else:
		raise AssertionError("terminated without finding a sequence")

	return concatenated_collection

def summarize_and_save(collection, filename):
		nupack_oracle = NupackOracle(temperature = 25.0, partition_function = True)

		concatenated_strand = next(iter(collection))

		design_strands = Collection()
		for i in range(2,6):
			design_strands.add(i * concatenated_strand)
			design_strands.add(i * common.wc(concatenated_strand))

		print(f"Found sequence:")
		print(list(collection))
		print("Complement:")
		print([common.wc(seq) for seq in collection])

		print("\nComputing analysis and saving sequence...")
		collection.save(filename, oracle=nupack_oracle, strands=design_strands)

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
	arbiter = heuristic_filter.Decorator(arbiter, forbidden_substrings)

	sequences = [seq for seq in collection if seq != 'T' * len(seq)] #not poly-T
	concatenated_sequence = concatenate(*sequences)
	try:
		arbiter.consider(concatenated_sequence)
		arbiter.consider(5*concatenated_sequence)
		return True
	except arbiter.Rejection as e:
		print(f"Secondary rejection of {concatenated_sequence} for reason {e}")
		return False

def concatenate(seq1, seq2):
	return ''.join(['C',seq1,seq2,'C'])  #heuristic: sequences must start and end in C

def Arbiter(
			oracle,
			collection,
			desired_affinity_min,
			desired_affinity_max,
			hairpin_threshold,
			undesirable_single_domain_affinity,
			undesirable_middle_domain_affinity
	):

	# outer decorators should be the fastest checks, so put those last
	arbiter = BaseArbiter(oracle, collection)
	arbiter = not_sticky_to_pairs_lite.Decorator(arbiter, undesirable_middle_domain_affinity)
	arbiter = not_sticky_to_others.Decorator(arbiter, undesirable_single_domain_affinity)
	arbiter = not_too_sticky_to_complement.Decorator(arbiter, desired_affinity_max)
	arbiter = sticky_to_complement.Decorator(arbiter, desired_affinity_min)
	arbiter = no_hairpin.Decorator(arbiter, hairpin_threshold)
	#no heuristic filter -- applied after concatentation

	return arbiter

if __name__ == "__main__":
	main()
