import itertools
import random    #TODO: is this needed in main?

#these imports and the sys.path call are to add the current directory to the python path, so that the latter exports will work
import sys
import os
sys.path.append(os.getcwd())


###############################################
#choose which oracle to use here.  TODO: tie this option to the command-line
#import oracle.nupack as oracle_lib
import oracle.vienna as oracle_lib
###############################################
#choose which sequence iterator to use here.  TODO: tie this option to the command-line
#import sequence_iterator.exhaustive as sequence_iterator_lib
import sequence_iterator.random as sequence_iterator_lib
###############################################


def random_sequence(length, bases=['A','T','C']):
	return ''.join([
		random.choice(['A','T','C'])
		for _ in range(length)
	])

def main():
	TEMPERATURE = 40.0

	oracle = oracle_lib.Oracle(TEMPERATURE)
	sequence_iterator = sequence_iterator_lib.SequenceIterator(domain_length=13)

	sequences = [
		next(sequence_iterator)
		for _ in range(2)
	]
	
	print(sequences)
	print(f"self_affinity of first: {oracle.self_affinity(sequences[0])}")
	print(f"self_affinity of second: {oracle.self_affinity(sequences[1])}")
	print(f"binding affinity: {oracle.binding_affinity(*sequences)}")

if __name__ == "__main__":
	main()
