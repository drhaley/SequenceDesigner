# an example of using the designer to produce quasi-orthogonal sequences

#########################################################
from oracle.viennaCLI import Oracle
from generator.random import Generator
from arbiter.austin import Arbiter
from collection.set import Collection
#########################################################


def main():
	oracle = Oracle(temperature = 40.0)
	generator = Generator(domain_length = 10)
	collection = Collection()

	arbiter = Arbiter(oracle, collection,
		desired_affinity = 12.0,
		single_domain_threshold = 5.0,
		double_domain_threshold = 5.0
	)

	NUMBER_OF_ITERATIONS = 1000

	for _ in range(NUMBER_OF_ITERATIONS):
		sequence = next(generator)
		if arbiter.consider(sequence):
			collection.add(sequence)

	print(list(iter(collection)))

if __name__ == "__main__":
	main()
