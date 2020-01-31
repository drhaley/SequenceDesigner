#experimental design for grid gate 2x2 experiment

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
import string
from util import common

forbidden_internal_substrings = [
	r"[CG]{4}",
	r"[AT]{5}",
	r"AAAA",
	r"TTTT",
]

forbidden_substrings = forbidden_internal_substrings + [
	r"^[AT]{3}",
	r"[AT]{3}$"
]

def main():
	filename_suffix = random.randint(1000, 9999)
	filename = os.path.join("sequences", f"GG_size_two_{filename_suffix}.json")

	try:
		domains = Collection()
		domains.load(filename)
	except FileNotFoundError:
		domains = generate_internal_domains()

	summarize_and_save(domains, filename)

def generate_internal_domains():
	MAX_NUMBER_OF_ITERATIONS = 1000

	sizes = {"long1": 10, "long2": 11}
	number_of_each_size = {10: 4, 11: 4}

	oracle = Oracle(temperature = 25.0, partition_function = True)
	generators = {
			size: Generator(domain_length = size, alphabet = "ATC")
				for size in sizes.values()
	}
	collection = Collection()

	#thresholds for the long domains against themselves
	hairpin_threshold = 0.1
	desired_affinity_min = 12.0
	desired_affinity_max = 1.25 * desired_affinity_min
	undesirable_affinity_max = 8.0

	arbiter = Arbiter(oracle, collection,
		desired_affinity_min = desired_affinity_min,
		desired_affinity_max = desired_affinity_max,
		hairpin_threshold = hairpin_threshold,
		undesirable_single_domain_affinity = undesirable_affinity_max,
		undesirable_middle_domain_affinity = undesirable_affinity_max,
	)

	poly_T = "T"*(1+max(sizes.values()))
	collection.add(poly_T)       #we want domains to be orthogonal to poly-T segments

	rejection_dict = {}

	for _ in range(MAX_NUMBER_OF_ITERATIONS):
		size = random.choice(list(sizes.values()))
		sequence = next(generators[size])
		try:
			arbiter.consider(sequence)
			collection.add(sequence)
		except arbiter.Rejection as e:
			handle_rejection(sequence, e, rejection_dict)

		for size in sizes.values():
			sequences_of_certain_size = [seq for seq in collection if len(seq) == size]
			if len(sequences_of_certain_size) > number_of_each_size[size]:
				collection.remove(random.choice(sequences_of_certain_size))

		if len(collection) == 1 + sum(number_of_each_size.values()):  #+1 for poly-T
			#TODO: try to assemble some strands
			if(True):  #combined strands are good
				break

	collection.remove(poly_T)

	print(rejection_dict)
	print('\n')

	return collection

def summarize_and_save(collection, filename):
	nupack_oracle = NupackOracle(temperature = 25.0, partition_function = True)

	namer = NameGenerator()

	aliases = {}
	for sequence in collection:
		aliases[sequence] = namer.assign(sequence)
		aliases[common.wc(sequence)] = f"{aliases[sequence]}*"

	design_strands = Collection()
	#TODO: concatenate the strands

	print(f"Found sequence:")
	print(list(collection))
	print("Complement:")
	print([common.wc(seq) for seq in collection])

	print("\nComputing analysis and saving sequence...")
	collection.save(filename, oracle = nupack_oracle, strands = design_strands, aliases = aliases)


def handle_rejection(sequence, exception, rejection_dict):
	reason = str(exception)
	print(f"Rejected {sequence} for reason {reason}")
	if reason in rejection_dict:
		rejection_dict[reason] += 1
	else:
		rejection_dict[reason] = 1

# def good_structure_in_combined_strands(oracle, collection, hairpin_threshold):
# 	arbiter = BaseArbiter(oracle, Collection())
# 	arbiter = no_hairpin.Decorator(arbiter, hairpin_threshold)
# 	arbiter = heuristic_filter.Decorator(arbiter, forbidden_substrings)
#
# 	sequences = [seq for seq in collection if seq != 'T' * len(seq)] #not poly-T
# 	concatenated_sequence = concatenate(*sequences)
# 	try:
# 		arbiter.consider(concatenated_sequence)
# 		arbiter.consider(5*concatenated_sequence)
# 		return True
# 	except arbiter.Rejection as e:
# 		print(f"Secondary rejection of {concatenated_sequence} for reason {e}")
# 		return False
#
# def concatenate(seq1, seq2):
# 	return ''.join(['C',seq1,seq2,'C'])  #heuristic: sequences must start and end in C
#
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
	arbiter = heuristic_filter.Decorator(arbiter, forbidden_internal_substrings)

	return arbiter

class NameGenerator():
	def __init__(self):
		self._even_index = 0
		self._odd_index = 1
		self._names = string.ascii_lowercase

	def assign(self, sequence):
		if len(sequence) % 2 == 0:
			name = self._names[self._even_index]
			self._even_index += 2
		else:
			name = self._names[self._odd_index]
			self._odd_index += 2
		return name

if __name__ == "__main__":
	main()
