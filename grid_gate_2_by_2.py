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

forbidden_domain_substrings = [
	r"[CG]{4}",
	r"[AT]{5}",
	r"AAAA",
	r"TTTT",
	r"^[AT]{3}",
	r"[AT]{3}$",
	r"^[CG]{3}",
	r"[CG]{3}$",
]

forbidden_strand_substrings = [
	r"[CG]{4}",
	r"AAAA",
]

# thresholds for the long domains against themselves
hairpin_threshold = 0.05
desired_affinity_min = 12.0
desired_affinity_max = 1.25 * desired_affinity_min
undesirable_affinity_max = 8.0

# threshold for the strands' self structure
strand_hairpin_threshold = 2.0

def main():
	filename_suffix = random.randint(1000, 9999)
	filename = os.path.join("sequences", f"GG_size_2_w_staples_{filename_suffix}.json")

	accept = False
	while(not accept):
		domains = generate_internal_domains()
		strands, aliases, accept = assemble_strands(domains)

	save_to_file(filename, domains, strands, aliases)

def generate_internal_domains():
	MAX_NUMBER_OF_ITERATIONS = 100000

	sizes = {"long1": 10, "long2": 11}
	number_of_each_size = {10: 6, 11: 6}

	oracle = Oracle(temperature = 25.0, partition_function = False)  #this needs to be fast, so just look at mfe
	generators = {
			size: Generator(domain_length = size, alphabet = "ATC")
				for size in sizes.values()
	}
	collection = Collection()

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

		if len(collection) == 1 + sum(number_of_each_size.values()):  # +1 for poly-T
			break   #move to second phase and try to assemble these strands
	else:
		print(rejection_dict)
		raise AssertionError(f"Did not find sequences after {MAX_NUMBER_OF_ITERATIONS} iterations")

	collection.remove(poly_T)

	print(rejection_dict)
	print('\n')

	return collection

def assemble_strands(sequences):
	oracle = Oracle(temperature = 25.0, partition_function = True)  #here we check for secondary structure; need pf

	arbiter = BaseArbiter(oracle, Collection())
	hairpin_arbiter = no_hairpin.Decorator(arbiter, strand_hairpin_threshold)
	heuristic_arbiter = heuristic_filter.Decorator(arbiter, forbidden_strand_substrings)

	namer = NameGenerator()

	aliases = {}
	for sequence in sequences:
		print(f"naming {sequence}")
		name = namer.assign(sequence)
		if name:
			print(f"assign {name} to domain {sequence}")
			aliases[sequence] = name
			aliases[common.wc(sequence)] = f"{aliases[sequence]}*"

	reverse_aliases = {alias: sequence for sequence, alias in aliases.items()}
	design_strands = Collection()

	#concatenate the strands
	S_left = f"{reverse_aliases['b'][5:]}{reverse_aliases['a']}{reverse_aliases['l']}{reverse_aliases['k'][:-5]}"
	V1 = f"{reverse_aliases['c']}{reverse_aliases['j']}"
	V2 = f"{reverse_aliases['i']}{reverse_aliases['d']}"
	S_right = f"{reverse_aliases['h']}{reverse_aliases['g']}{reverse_aliases['f']}{reverse_aliases['e'][:-5]}"
	H1 = f"{reverse_aliases['d']}{reverse_aliases['c']}"
	H2 = f"{reverse_aliases['j']}{reverse_aliases['i']}"
	Scaffold_short = \
			  f"{reverse_aliases['a*']}{reverse_aliases['b*']}{reverse_aliases['c*']}{reverse_aliases['d*']}" \
			+ f"{reverse_aliases['e*'][:5]}TTTTT" \
			+ f"{reverse_aliases['i*']}{reverse_aliases['j*']}{reverse_aliases['k*']}{reverse_aliases['l*']}"
	Scaffold_long = \
			  f"{reverse_aliases['a*']}{reverse_aliases['b*']}{reverse_aliases['c*']}" \
			+ f"{reverse_aliases['d*']}{reverse_aliases['e*']}{reverse_aliases['f*']}" \
			+ ("T"*10) \
			+ f"{reverse_aliases['g*']}{reverse_aliases['h*']}{reverse_aliases['i*']}" \
			+ f"{reverse_aliases['j*']}{reverse_aliases['k*']}{reverse_aliases['l*']}"

	Catalyst = f"{reverse_aliases['d']}{reverse_aliases['c']}{reverse_aliases['j']}"

	H1_th = H1 + reverse_aliases['b'][:5]
	H2_th = reverse_aliases['k'][-5:] + H2
	Catalyst_th = reverse_aliases['e'][-5:] + Catalyst

	for strand in [S_left, V1, V2, S_right, H1, H2, Catalyst, H1_th, H2_th, Catalyst_th]:
		design_strands.add(strand)

	aliases[S_left] = "S_left"
	aliases[V1] = "V1"
	aliases[V2] = "V2"
	aliases[S_right] = "S_right"
	aliases[H1] = "H1"
	aliases[H2] = "H2"
	aliases[Scaffold_long] = "Scaffold_long"
	aliases[Scaffold_short] = "Scaffold_short"
	aliases[Catalyst] = "Catalyst"
	aliases[H1_th] = "H1_th"
	aliases[H2_th] = "H2_th"
	aliases[Catalyst_th] = "Catalyst_th"

	for strand in design_strands:
		try:
			hairpin_arbiter.consider(strand)
		except hairpin_arbiter.Rejection as e:
			handle_rejection(aliases[strand], e, {}, verbose = True)
			accept = False
			break
	else:
		design_strands.add(Scaffold_short)
		design_strands.add(Scaffold_long)
		for strand in design_strands:
			try:
				heuristic_arbiter.consider(strand)
			except heuristic_arbiter.Rejection as e:
				handle_rejection(aliases[strand], e, {}, verbose = True)
				accept = False
				break
		else:
			accept = True

	return design_strands, aliases, accept

def save_to_file(filename, domains, strands, aliases):
	oracle = NupackOracle(temperature = 25.0, partition_function = True)
	domains.save(filename, oracle, strands = strands, aliases = aliases)

def handle_rejection(sequence, exception, rejection_dict, verbose = False):
	reason = str(exception)
	if verbose:
		print(f"Rejected {sequence} for reason {reason}")

	if reason in rejection_dict:
		rejection_dict[reason] += 1
	else:
		rejection_dict[reason] = 1

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
	arbiter = heuristic_filter.Decorator(arbiter, forbidden_domain_substrings)

	return arbiter

class NameGenerator():
	def __init__(self):
		self._even_index = 0
		self._odd_index = 1
		self._names = string.ascii_lowercase

	def assign(self, sequence):
		if len(sequence) == 10:
			name = self._names[self._even_index]
			self._even_index += 2
		elif len(sequence) == 11:
			name = self._names[self._odd_index]
			self._odd_index += 2
		else:
			name = None
		return name

if __name__ == "__main__":
	main()