import itertools
import argparse
import importlib
import json
from util.constants import *
import util.common as common

#these imports and the sys.path call are to add the current directory to the python path,
# so that the latter exports will work
import sys
import os
sys.path.append(os.getcwd())

#TODO: connect verbosity and max_considered to command-line arguments or to the parameter file
VERBOSE = True
MAX_SEQUENCES_CONSIDERED = 100

#TODO: factor out tuning parameters to a separate file and accept them as arguments in related functions
MIN_AFFINITY_TO_SELF = 12.0  # TODO: tune
MAX_AFFINITY_TO_OTHER_SINGLE = 6.0  # TODO: tune
MAX_AFFINITY_TO_OTHER_PAIR = 6.0  # TODO: tune

def main():
	command_line_parameters = process_command_line_args()
	
	if SETTINGS_FILENAME in command_line_parameters:
		settings_filename = command_line_parameters[SETTINGS_FILENAME]
	else:
		settings_filename = "settings.json"
	
	with open(settings_filename) as infile:
		runtime_parameters = json.load(infile)
	
	#the settings from the file can be overriden by the command line arguments
	runtime_parameters.update(command_line_parameters)

	oracle_name = runtime_parameters[ORACLE]
	oracle_lib = importlib.import_module(f"oracle.{oracle_name}")
	oracle = oracle_lib.Oracle(
		runtime_parameters[TEMPERATURE]
	)

	sequence_iterator_name = runtime_parameters[SEQUENCE_ITERATOR]
	sequence_iterator_lib = importlib.import_module(f"sequence_iterator.{sequence_iterator_name}")
	sequence_iterator = sequence_iterator_lib.SequenceIterator(
		domain_length = 13,
		max_G = 1,
		forbidden_substrings = [
			r"[CG]{4}",
			r"[AT]{5}",
			r"^[AT]{3}",
			r"[AT]{3}$",
			r"AAAA",
			r"TTTT",
		]
	)

	#TODO: load "found sequences" from file, if any
	found_sequences = []
	
	for count, sequence in enumerate(sequence_iterator):
		if VERBOSE: print() #newline
		accept, fitness = consider(sequence, found_sequences, oracle, verbose = VERBOSE)

		if(accept):
			found_sequences.append(sequence)
			print(f"Accepted {sequence}")
			#TODO: update "found sequences" in the relevant file
		else:
			sequence_iterator.feedback(fitness)
			if VERBOSE: print(f"Rejected {sequence}")

		#TODO: give feedback to the user about the ongoing process

		if (count >= MAX_SEQUENCES_CONSIDERED): break   #TODO: don't break


def process_command_line_args():
	parser = argparse.ArgumentParser()

	parser.add_argument(
		'-t',
		dest=TEMPERATURE,
		help="Temperature in Celsius (e.g. 40.0)",
		metavar="<temperature>",
		required=False
	)
	parser.add_argument(
		'-p',
		dest=SETTINGS_FILENAME,
		help="Name of settings JSON file (e.g. 'settings.json')",
		metavar="<settings_filename>",
		required=False
	)
	parser.add_argument(
		'--oracle',
		dest=ORACLE,
		help="Name of Oracle program (e.g. 'vienna')",
		metavar="<oracle_name>",
		required=False
	)
	parser.add_argument(
		'--iterator',
		dest=SEQUENCE_ITERATOR,
		help="Name of sequence iterator to use (e.g. 'random')",
		metavar="<iterator_name>",
		required=False
	)

	# parser.add_argument(
	# 	'--booleanarg',
	# 	dest=KEYNAME,
	# 	action='store_true',
	# 	required=False
	# )

	command_line_parameters = vars(parser.parse_args())

	scrubbed_parameters = {
		key:val
		for key,val in command_line_parameters.items()
		if val is not None
	}
	return scrubbed_parameters


def consider(sequence, found_sequences, oracle, verbose = False):
	affinity_to_self = oracle.binding_affinity(sequence, common.wc(sequence))
	sticky_to_itself = affinity_to_self >= MIN_AFFINITY_TO_SELF
	if verbose: print(f"\tself affinity: {affinity_to_self}");

	affinity_to_other_singles = [
		oracle.binding_affinity(seq1, seq2)
		for found_sequence in found_sequences
		for seq1 in [sequence, common.wc(sequence)]
		for seq2 in [found_sequence, common.wc(found_sequence)]
	]
	not_sticky_to_other_singles = all([
		affinity <= MAX_AFFINITY_TO_OTHER_SINGLE
		for affinity in affinity_to_other_singles
	])
	if verbose and found_sequences: print(f"\tmax affinity to other singles: {max(affinity_to_other_singles)}");

	affinity_to_other_pairs = [
		oracle.binding_affinity(joined_sequence, common.wc(sequence))
		for joined_sequence in [seq1 + seq2 for seq1 in found_sequences for seq2 in found_sequences]
	]
	not_sticky_to_other_pairs = all([
		affinity <= MAX_AFFINITY_TO_OTHER_PAIR
		for affinity in affinity_to_other_pairs
	])
	if verbose and found_sequences:	print(f"\tmax affinity to other pairs: {max(affinity_to_other_pairs)}");

	mid_domain_affinities = [
		oracle.binding_affinity(joined_sequence, common.wc(starred_domain))
		for adjacent_domain in found_sequences + [sequence]
		for starred_domain in found_sequences
		for joined_sequence in [adjacent_domain + sequence, sequence + adjacent_domain]
		if adjacent_domain != starred_domain
	]
	not_sticky_when_with_adjacent_domain = all([
		affinity <= MAX_AFFINITY_TO_OTHER_PAIR
		for affinity in mid_domain_affinities
	])
	if verbose and found_sequences:	print(f"\tmax mid-domain affinity: {max(mid_domain_affinities)}");


	accept = \
		sticky_to_itself and \
		not_sticky_to_other_singles and \
		not_sticky_to_other_pairs and \
		not_sticky_when_with_adjacent_domain

	fitness = 100 #TODO: implement and document fitness value

	return accept, fitness

if __name__ == "__main__":
	main()
