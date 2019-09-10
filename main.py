import itertools
import random    #TODO: is this needed in main?

#these imports and the sys.path call are to add the current directory to the python path, so that the latter exports will work
import sys
import os
sys.path.append(os.getcwd())



###############################################
#choose which oracle to use here.  TODO: tie this option to the command-line
#import oracle.debug as oracle_lib
import oracle.nupack as oracle_lib
###############################################
#choose which sequence iterator to use here.  TODO: tie this option to the command-line
import sequence_iterator.exhaustive as sequence_iterator_lib
###############################################


def random_sequence(length, bases=['A','T','C']):
	return ''.join([
		random.choice(['A','T','C'])
		for _ in range(length)
	])

def main():
	# oracle = oracle_lib.Oracle()
	# sequence_iterator = sequence_iterator_lib.SequenceIterator()

	# TEMPERATURE = 40.0

	# sequences = [
	# 	sequence_iterator.next()
	# 	for _ in range(2)
	# ]
	
	# print(sequences)
	# print(f"self_affinity of first: {oracle.self_affinity(sequences[0], TEMPERATURE)}")
	# print(f"self_affinity of second: {oracle.self_affinity(sequences[1], TEMPERATURE)}")
	# print(f"binding affinity: {oracle.binding_affinity(*sequences, TEMPERATURE)}")

	TEST_CASE = ("AAAATTTTTCCCCCGGGGGGG", "CCCCCCGGGGGGAAAATTT")
	vienna_API = vienna_lib.Oracle(temperature=TEMPERATURE)
	vienna_CLI = vienna_lib.Oracle(temperature=TEMPERATURE,use_subprocess=True)
	nupack = nupack_lib.Oracle(temperature=TEMPERATURE)

	print(vienna_API.binding_affinity(*TEST_CASE))
	print(vienna_CLI.binding_affinity(*TEST_CASE))
	print(nupack.binding_affinity(*TEST_CASE))


if __name__ == "__main__":
	main()
