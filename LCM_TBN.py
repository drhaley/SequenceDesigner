#experimental design for LCM single domain TBN experiment
#approach: find two orthogonal domains and concatenate

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

forbidden_substrings = [
	r"[CG]{4}",
	r"[AT]{5}",
	r"^[AT]{3}",
	r"[AT]{3}$",
	r"AAAA",
	r"TTTT",
]

def main():
	domain_length = 7   #7*2 + 2 Cs on the end = 16
	hairpin_threshold = 0.0001
	desired_affinity_min = 6.0
	desired_affinity_max = 1.5 * desired_affinity_min
	undesirable_affinity_max = 1.5

	MAX_NUMBER_OF_ITERATIONS = 500000
	INVERSE_CHANCE_TO_RESTART = 500

	oracle = Oracle(temperature = 25.0)
	generator = Generator(domain_length = domain_length, alphabet="ATC")
	collection = Collection()

	filename_suffix = random.randint(1000, 9999)

	filename = os.path.join("sequences", f"LCM_TBN_{filename_suffix}.json")

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

	poly_T = "T"*domain_length
	collection.add(poly_T)       #we want domains to be orthogonal to poly-T segments

	rejection_dict = {}

	for _ in range(MAX_NUMBER_OF_ITERATIONS):
		sequence = next(generator)
		try:
			arbiter.consider(sequence)

			collection.add(sequence)
			print(f"Accepted {sequence}")
		except arbiter.Rejection as e:
			handle_rejection(sequence, e, rejection_dict)
			if len(collection) >= 2 and random.randint(0, INVERSE_CHANCE_TO_RESTART) == 0:
				delete_random_sequence(collection) #restart

		if len(collection) >= 3:  #3 = 2 good domains + 1 poly-T "domain"
			if (good_structure_in_combined_strands(oracle, collection, hairpin_threshold)):
				break
			else:
				delete_random_sequence(collection)

	collection.remove(poly_T)

	print(rejection_dict)
	print('\n')
	if len(collection) == 2:
		concatenated_collection = Collection()
		concatenated_collection.add(concatenate(*list(collection)))
		concatenated_collection.save(filename)
		print(f"Found sequence:")
		print(list(concatenated_collection))
		print("Complement:")
		print([common.wc(seq) for seq in concatenated_collection])

	else:
		print("terminated without finding a sequence")

def delete_random_sequence(collection):
	sequence_to_delete = random.choice(list(collection))
	while sequence_to_delete == 'T' * len(sequence_to_delete): #poly-T
		sequence_to_delete = random.choice(list(collection))
	print(f"Removing {sequence_to_delete}")
	collection.remove(sequence_to_delete)

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
