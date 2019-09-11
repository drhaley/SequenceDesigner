import itertools

def product_strings(length,alphabet):
    return [''.join(character_list) for character_list in itertools.product(alphabet,repeat=length)]
