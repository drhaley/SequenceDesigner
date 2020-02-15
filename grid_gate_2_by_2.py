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
	r"^[CG]", #end in A or T
	r"[CG]$", #end in A or T
]

forbidden_strand_substrings = [
	r"[CG]{4}",
	r"AAAA",
]

# thresholds for the long domains against themselves
hairpin_threshold = 0.05
desired_affinity_min = 13.0
desired_affinity_max = 1.1 * desired_affinity_min
undesirable_affinity_max = 5.5

# thresholds for the staple domains against themselves
staple_hairpin_threshold = 0.05
staple_affinity_min = 20.0
staple_affinity_max = 1.25 * staple_affinity_min
staple_to_all_affinity_max = 10.0

# staples should not be sticky to the internal domains
staple_to_internal_affinity_max = 7.5

# threshold for the strands' self structure
strand_hairpin_threshold = 1.0
scaffold_hairpin_threshold = 3.0

def main():
	filename_suffix = random.randint(1000, 9999)
	filename = os.path.join("sequences", f"GG_stapled_{filename_suffix}.json")

	accept = False
	while(not accept):
		print("Generating internal domains")
		domains = generate_internal_domains()
		print("Generating staple domains")
		domains = additionally_generate_staple_domains(domains)
		print("Assembling strands")
		strands, aliases, accept = assemble_strands(domains)

	print(f"Saving design as {filename}")
	save_to_file(filename, domains, strands, aliases)

def generate_internal_domains():
	MAX_NUMBER_OF_ITERATIONS = 100000

	sizes = {"long1": 10, "long2": 11}
	number_of_each_size = {10: 2, 11: 2}

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
			break   #move to next phase
	else:
		print(rejection_dict)
		raise AssertionError(f"Did not find sequences after {MAX_NUMBER_OF_ITERATIONS} iterations")

	collection.remove(poly_T)

	print(rejection_dict)
	print('\n')

	return collection

def additionally_generate_staple_domains(internal_domains):
	MAX_NUMBER_OF_ITERATIONS = 100000

	sizes = {"half staple": 16}
	number_of_each_size = {16: 4}

	oracle = Oracle(temperature = 25.0, partition_function = False)  #this needs to be fast, so just look at mfe
	generators = {
			size: Generator(domain_length = size, alphabet = "ATC")
				for size in sizes.values()
	}
	all_domains = Collection()
	for seq in internal_domains:
		all_domains.add(seq)

	staple_to_internal_arbiter = Arbiter(oracle, internal_domains,
			desired_affinity_min = staple_affinity_min,
			desired_affinity_max = staple_affinity_max,
			hairpin_threshold = staple_hairpin_threshold,
			undesirable_single_domain_affinity = staple_to_internal_affinity_max,
			undesirable_middle_domain_affinity = staple_to_internal_affinity_max,
	)
	staple_to_all_arbiter = Arbiter(oracle, all_domains,
			desired_affinity_min = staple_affinity_min,
			desired_affinity_max = staple_affinity_max,
			hairpin_threshold = staple_hairpin_threshold,
			undesirable_single_domain_affinity = staple_to_all_affinity_max,
			undesirable_middle_domain_affinity = staple_to_all_affinity_max,
	)

	short_poly_T = "T"*11
	internal_domains.add(short_poly_T)       #we want domains to be orthogonal to poly-T segments
	long_poly_T = "T"*max(sizes.values())
	all_domains.add(long_poly_T)  # we want domains to be orthogonal to poly-T segments

	rejection_dict = {}

	for _ in range(MAX_NUMBER_OF_ITERATIONS):
		size = random.choice(list(sizes.values()))
		sequence = next(generators[size])
		try:
			staple_to_internal_arbiter.consider(sequence)
			staple_to_all_arbiter.consider(sequence)
			all_domains.add(sequence)
		except (staple_to_internal_arbiter.Rejection, staple_to_all_arbiter.Rejection) as e:
			handle_rejection(sequence, e, rejection_dict)

		if len(all_domains) == len(internal_domains) + sum(number_of_each_size.values()):
			break   #move to next phase
	else:
		print(rejection_dict)
		raise AssertionError(f"Did not find sequences after {MAX_NUMBER_OF_ITERATIONS} iterations")

	internal_domains.remove(short_poly_T)
	all_domains.remove(long_poly_T)

	print(rejection_dict)
	print('\n')

	return all_domains

def assemble_strands(sequences):
	oracle = Oracle(temperature = 25.0, partition_function = True)  #here we check for secondary structure; need pf

	arbiter = BaseArbiter(oracle, Collection())
	heuristic_arbiter = heuristic_filter.Decorator(arbiter, forbidden_strand_substrings)

	strand_arbiter = no_hairpin.Decorator(heuristic_arbiter, strand_hairpin_threshold)

	scaffold_arbiter = no_hairpin.Decorator(heuristic_arbiter, scaffold_hairpin_threshold)

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

	# simplified design schematic:
	# abcd
	# efgh

	S_left = f"{reverse_aliases['e']}{reverse_aliases['a']}"
	V1 = f"{reverse_aliases['b']}{reverse_aliases['f']}"
	V2 = f"{reverse_aliases['g']}{reverse_aliases['c']}"
	S_right = f"{reverse_aliases['d']}{reverse_aliases['h']}"
	H1 = f"{reverse_aliases['c']}{reverse_aliases['b']}"
	H2 = f"{reverse_aliases['f']}{reverse_aliases['g']}"
	Scaffold_short = \
			  f"{reverse_aliases['a*']}{reverse_aliases['b*']}{reverse_aliases['c*']}" \
			+ f"{'T'*8}" \
			+ f"{reverse_aliases['g*']}{reverse_aliases['f*']}{reverse_aliases['e*']}"
	Scaffold_long = \
			  f"{reverse_aliases['a*']}{reverse_aliases['b*']}{reverse_aliases['c*']}{reverse_aliases['d*']}" \
			+ f"{reverse_aliases['h*']}{reverse_aliases['g*']}{reverse_aliases['f*']}{reverse_aliases['e*']}"

	Catalyst = f"{reverse_aliases['c']}{reverse_aliases['b']}{reverse_aliases['f']}"

	aliases[S_left] = "S_left"
	aliases[V1] = "V_left"
	aliases[V2] = "V_right"
	aliases[S_right] = "S_right"
	aliases[H1] = "H_top"
	aliases[H2] = "H_bottom"
	aliases[Scaffold_long] = "Scaffold_long"
	aliases[Scaffold_short] = "Scaffold_short"
	aliases[Catalyst] = "Catalyst"

	for strand in [S_left, V1, V2, S_right, H1, H2, Catalyst]:
		try:
			strand_arbiter.consider(strand)
			design_strands.add(strand)
		except strand_arbiter.Rejection as e:
			handle_rejection(aliases[strand], e, {}, verbose = True)
			accept = False
			break
	else:
		for strand in [Scaffold_long, Scaffold_short]:
			try:
				scaffold_arbiter.consider(strand)
				design_strands.add(strand)
			except scaffold_arbiter.Rejection as e:
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
		self._short_index = 0
		self._long_index = 0
		self._staple_index = 0
		self._short_names = "cf"
		self._long_names = "bg"
		self._staple_names = "adeh"

	def assign(self, sequence):
		if len(sequence) == 10:
			name = self._short_names[self._short_index]
			self._short_index += 1
		elif len(sequence) == 11:
			name = self._long_names[self._long_index]
			self._long_index += 1
		elif len(sequence) == 16:
			name = self._staple_names[self._staple_index]
			self._staple_index += 1
		else:
			name = None
		return name

if __name__ == "__main__":
	main()
