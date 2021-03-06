import itertools
import re

def product_strings(length,alphabet):
    return [''.join(character_list) for character_list in itertools.product(alphabet,repeat=length)]

def powerset(iterable):
    #https://docs.python.org/3/library/itertools.html#itertools-recipes
    s = list(iterable)
    return itertools.chain.from_iterable(
        itertools.combinations(s, r) for r in range(len(s)+1)
    )

def wc(sequence):
    #Watson-Crick complement
    wc_map = {
        "A": "T",
        "T": "A",
        "C": "G",
        "G": "C",
    }
    lowercase_map = {
        key.lower():value.lower()
        for key, value in wc_map.items()
    }
    wc_map.update(lowercase_map)

    mapped_char_list = [
        wc_map[base_pair] for base_pair in sequence[::-1]
    ]

    return ''.join(mapped_char_list)

def regex_search(full_string, search_list):
    for regex in search_list:
        if re.search(regex, full_string) is not None:
            return True
    else:
        return False
