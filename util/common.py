import itertools

def product_strings(length,alphabet):
    return [''.join(character_list) for character_list in itertools.product(alphabet,repeat=length)]

def powerset(iterable):
    #https://docs.python.org/3/library/itertools.html#itertools-recipes
    s = list(iterable)
    return itertools.chain.from_iterable(
        itertools.combinations(s, r) for r in range(len(s)+1)
    )
