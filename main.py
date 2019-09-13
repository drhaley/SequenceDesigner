import itertools

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

def main():
	#TODO: get command-line arguments, if any

	#TODO: get tuning parameters from file, if any
	TEMPERATURE = 40.0

	oracle = oracle_lib.Oracle(TEMPERATURE)
	sequence_iterator = sequence_iterator_lib.SequenceIterator(domain_length=13)

	#TODO: load "found sequences" from file, if any

	for sequence in sequence_iterator:
		#TODO: do relevant comparisons to existing set

		if(True):	#TODO: kick the new sequence if it has poor energetic interactions
			#TODO: add the new sequence
			#TODO: update "found sequences" in the relevant file
			raise NotImplementedError()

		#TODO: give feedback to the user about the ongoing process
	

if __name__ == "__main__":
	main()
