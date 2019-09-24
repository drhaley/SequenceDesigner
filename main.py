import itertools
import argparse
import importlib
import json
from util import common
from util.constants import \
    SETTINGS_FILENAME, \
    ORACLE, \
    TEMPERATURE, \
    SEQUENCE_ITERATOR, \
	ARBITER, \
	VERBOSE, \
	MAX_SEQUENCES_CONSIDERED

#these imports and the sys.path call are to add the current directory to the python path,
# so that the latter exports will work
import sys
import os
sys.path.append(os.getcwd())

###################################################
def main():
	command_line_parameters = process_command_line_args()
	runtime_parameters = get_runtime_parameters(command_line_parameters)

	oracle = get_oracle(
		runtime_parameters[ORACLE],
		runtime_parameters[TEMPERATURE]
	)

	sequence_iterator = get_sequence_iterator(
		runtime_parameters[SEQUENCE_ITERATOR],
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

	arbiter = get_arbiter(
		runtime_parameters[ARBITER],
		oracle = oracle,
		verbose = VERBOSE
	)

	loop_through_sequences(sequence_iterator, arbiter)
	
	print(arbiter.get_sequences())

###################################################

def loop_through_sequences(sequence_iterator, arbiter):
	for count, sequence in enumerate(sequence_iterator):
		if VERBOSE: print() #newline
		arbiter.consider(sequence)

		#TODO: give more feedback to the user about the ongoing process

		if (count >= MAX_SEQUENCES_CONSIDERED): break   #TODO: don't break

###################################################

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

def get_runtime_parameters(command_line_parameters):
	if SETTINGS_FILENAME in command_line_parameters:
		settings_filename = command_line_parameters[SETTINGS_FILENAME]
	else:
		settings_filename = "settings.json"
	
	with open(settings_filename) as infile:
		runtime_parameters = json.load(infile)
	
	#the settings from the file can be overriden by the command line arguments
	runtime_parameters.update(command_line_parameters)

	return runtime_parameters

def get_oracle(oracle_name, *args, **kargs):
	oracle_lib = importlib.import_module(f"oracle.{oracle_name}")
	return oracle_lib.Oracle(*args, **kargs)

def get_sequence_iterator(sequence_iterator_name, *args, **kargs):
	sequence_iterator_lib = importlib.import_module(f"sequence_iterator.{sequence_iterator_name}")
	return sequence_iterator_lib.SequenceIterator(*args, **kargs)

def get_arbiter(arbiter_name, *args, **kargs):
	arbiter_lib = importlib.import_module(f"arbiter.{arbiter_name}")
	return arbiter_lib.Arbiter(*args, **kargs)


if __name__ == "__main__":
	main()
