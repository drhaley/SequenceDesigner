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
		accept, fitness = consider(sequence, found_sequences, oracle)
		
		if(accept):
			found_sequences.append(sequence)
			#TODO: update "found sequences" in the relevant file
		else:
			sequence_iterator.feedback(fitness)
		
		#give feedback to the user about the ongoing process
		print(sequence)
		print(f"{oracle_name}: {oracle.self_affinity(sequence)}")

		if (count > 10): break   #TODO: don't break

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


def consider(sequence, found_sequences, oracle):
	#TODO: factor out to a separate file and accept the tuning parameters as arguments
	MIN_AFFINITY_TO_SELF = 6.0   #TODO: tune
	MAX_AFFINITY_TO_OTHER_SINGLE = 4.0   #TODO: tune
	MAX_AFFINITY_TO_OTHER_PAIR = 4.0   #TODO: tune

	sticky_to_itself = oracle.binding_affinity(sequence, common.wc(sequence)) >= MIN_AFFINITY_TO_SELF
	#not sticky to other things()
	#starred version not sticky when next to another unstarred()
	#unstarred version not sticky to another pair of unstarred()
	
	accept = sticky_to_itself #TODO
	fitness = 100 #TODO

	return accept, fitness

if __name__ == "__main__":
	main()
