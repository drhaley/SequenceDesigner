# produces histogram of domain binding energies subject to certain heuristics

from oracle.vienna import Oracle
from generator.random import Generator
from collection.set import Collection

from arbiter.base import Arbiter as BaseArbiter
from arbiter.decorators import \
    heuristic_filter

import matplotlib.pyplot as plt
import random
from util import common

forbidden_domain_substrings = [
    r"[CG]{4}",
    r"[AT]{5}",
    r"AAAA",
    r"TTTT",
    r"^[AT]{3}",
    r"[AT]{3}$",
    r"^[CG]{3}",
    r"[CG]{3}$",
]

forbidden_strand_substrings = [
    r"[CG]{4}",
    r"AAAA",
]

oracle = Oracle(temperature=25.0, partition_function=False)  # this needs to be fast, so just look at mfe

number_of_domains_per_sample = 2000


def main():
    for sizes in [
            {"long1": 10, "long2": 11},
            {"staple_domain": 16},
            {"half domain": 8},
    ]:
        affinities = run_single_domain_analysis(sizes)
        produce_histogram(affinities, color="blue")

        affinities = run_two_domain_analysis(sizes)
        produce_histogram(affinities, color="red")
        save_plot("", f"binding_{make_str(sizes)}.svg")

    affinities = run_heterogeneous_analysis()
    produce_histogram(affinities)
    save_plot("", "spurious_complement_heterogeneous.svg")

    # stapled experiment
    domain_affinities = run_single_domain_analysis({"long1": 10, "long2": 11})
    produce_histogram(domain_affinities, color="green")
    staple_affinities = run_single_domain_analysis({"staple_domain": 16})
    produce_histogram(staple_affinities, color="black")
    bad_staple_affinities = run_two_domain_analysis({"staple_domain": 16})
    produce_histogram(bad_staple_affinities, color="gray")
    heterogeneous_affinities = run_heterogeneous_analysis()
    produce_histogram(heterogeneous_affinities, color="purple")
    bad_domain_affinities = run_two_domain_analysis({"long1": 10, "long2": 11})
    produce_histogram(bad_domain_affinities, color="red")
    save_plot("", "binding_heterogeneous.svg")


def make_str(sizes):
    return "_".join([str(x) for x in sizes.values()])


def run_single_domain_analysis(sizes):
    domain_collection = get_many_domains(sizes, number_of_domains_per_sample)

    return [oracle.binding_affinity(seq, common.wc(seq)) for seq in domain_collection]


def run_two_domain_analysis(sizes):
    domain_collection_a = iter(get_many_domains(sizes, number_of_domains_per_sample))
    domain_collection_b = iter(get_many_domains(sizes, number_of_domains_per_sample))

    affinities = []
    for seq1 in domain_collection_a:
        seq2 = next(domain_collection_b)
        if seq1 != seq2:
            affinities.append(
                oracle.binding_affinity(seq1, common.wc(seq2))
            )

    return affinities


def run_heterogeneous_analysis():
    internal_domain_collection = iter(get_many_domains({"long1": 10, "long2": 11}, number_of_domains_per_sample))
    staple_domain_collection = iter(get_many_domains({"staple_domain": 16}, number_of_domains_per_sample))

    affinities = []
    for seq1 in internal_domain_collection:
        seq2 = next(staple_domain_collection)
        affinities.append(
            oracle.binding_affinity(common.wc(seq1), seq2)  # staples competing for interior domains
        )

    return affinities


def get_many_domains(sizes, number):
    domain_collection = Collection()
    while True:
        domain_collection.add(generate_domain(sizes))  # can produce duplicates
        if len(domain_collection) >= number:
            break

    return domain_collection


def generate_domain(sizes):
    generators = {
        size: Generator(domain_length=size, alphabet="ATC")
        for size in sizes.values()
    }

    arbiter = BaseArbiter(oracle, Collection())
    arbiter = heuristic_filter.Decorator(arbiter, forbidden_domain_substrings)

    while True:
        size = random.choice(list(sizes.values()))
        sequence = next(generators[size])
        try:
            arbiter.consider(sequence)
            return sequence
        except arbiter.Rejection:
            pass


def produce_histogram(affinities, color="blue"):
    number_of_bins = 20
    _ = plt.hist(affinities, number_of_bins, density=1, facecolor=color)
    plt.xlabel("affinity (kcal/mol)")
    plt.ylabel("density")


def save_plot(title, filename):
    plt.title(title)
    print(f"Saving {filename}")
    plt.savefig(filename)
    plt.clf()


if __name__ == "__main__":
    main()
