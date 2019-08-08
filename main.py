import itertools

#these imports and the sys.path call are to add the current directory to the python path, so that the latter exports will work
import sys
import os
sys.path.append(os.getcwd())

#these imports are the external files pulled from the repo
import dsd
import sst_dsd

def product_strings(length,alphabet):
	return [''.join(character_list) for character_list in itertools.product(alphabet,repeat=length)]

def main():
	DOMAIN_LENGTH = 12
	ALPHABET = 'ATC'
	# FORBIDDEN_SUBSTRINGS_LENGTH_4 = \
	# 						itertools.chain	(
	# 											product_strings(4,'CG'),
	# 											product_strings(4,'A'),
	# 											product_strings(4,'T'),
	# 										)
	FORBIDDEN_SUBSTRINGS_LENGTH_4 = ['CCCC','AAAA','TTTT']
	FORBIDDEN_SUBSTRINGS_LENGTH_5 = product_strings(5,'AT')

	sequence_list = dsd.DNASeqList(DOMAIN_LENGTH,alphabet=tuple(char for char in ALPHABET))
	#sequence_list = sequence_list.filter_base_nowhere('G')    #remove all G's
	#k=1;sequence_list = sequence_list.filter_base_count('G', 0, k) #no more than k G's
	sequence_list = sequence_list.filter_substring(list(FORBIDDEN_SUBSTRINGS_LENGTH_4))
	sequence_list = sequence_list.filter_substring(list(FORBIDDEN_SUBSTRINGS_LENGTH_5))
	print(sequence_list)

if __name__ == "__main__":
	main()
