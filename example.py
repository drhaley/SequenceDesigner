# an example of using the designer to produce quasi-orthogonal sequences

#########################################################
from oracle.vienna import Oracle
from generator.random import Generator
from arbiter.austin import Arbiter
from collection.set import Collection
#########################################################


def main():
	oracle = Oracle(temperature = 40.0)
	generator = Generator(domain_length = 10, alphabet="ATC")
	collection = Collection()

	try:
		collection.load("example.txt")
	except FileNotFoundError:
		pass

	arbiter = Arbiter(oracle, collection,
		desired_affinity = 10.0,
		single_domain_threshold = 5.0,
		double_domain_threshold = 5.0
	)

	NUMBER_OF_ITERATIONS = 100000

	for _ in range(NUMBER_OF_ITERATIONS):
		sequence = next(generator)
		try:
			arbiter.consider(sequence)

			collection.add(sequence)
			print(f"Accepted {sequence}")
		except arbiter.Rejection as e:
			print(f"Rejected {sequence} for reason {e}")

	print(list(collection))
	collection.save("example.txt")

if __name__ == "__main__":
	main()
