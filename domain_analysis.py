#produces histogram of domain binding energies subject to certain heuristics

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
	r"^[CG]",
	r"[CG]$",
]

forbidden_strand_substrings = [
	r"[CG]{4}",
	r"AAAA",
]

oracle = Oracle(temperature=25.0, partition_function=False)  # this needs to be fast, so just look at mfe

NUMBER_OF_DOMAINS_PER_SAMPLE = 10000
NUMBER_OF_DOMAINS_PER_DUAL_SAMPLE = 100

def main():
    run_single_domain_analysis()
    run_two_domain_analysis()
    run_heterogeneous_analysis()

def run_single_domain_analysis():
    for sizes in [
            {"long1": 10, "long2": 11},
            {"staple_domain": 16},
            {"half domain": 8},
    ]:
        domain_collection = get_many_domains(sizes, NUMBER_OF_DOMAINS_PER_SAMPLE)

        affinities = []
        for seq in domain_collection:
            affinities.append(
                oracle.binding_affinity(seq, common.wc(seq))
            )

        if len(sizes) == 1:
            title = f"Sample of {NUMBER_OF_DOMAINS_PER_SAMPLE} domains of length {list(sizes.values())[0]}"
        else:
            lengths_with_commas = ', '.join([str(val) for val in list(sizes.values())])
            title = f"Sample of {NUMBER_OF_DOMAINS_PER_SAMPLE} domains of lengths {lengths_with_commas}"
        filename = f"affinity_to_complement_{'_'.join([str(val) for val in list(sizes.values())])}.svg"

        xlabel = "affinity to complement"

        produce_histogram(affinities, title, xlabel, filename)

def run_two_domain_analysis():
    for sizes in [
            {"long1": 10, "long2": 11},
            {"staple_domain": 16},
            {"half domain": 8},
    ]:
        domain_collection = get_many_domains(sizes, NUMBER_OF_DOMAINS_PER_DUAL_SAMPLE)

        complementary_affinities = []
        ATC_affinities = []
        ATG_affinities = []
        for seq1 in domain_collection:
            for seq2 in domain_collection:
                if seq1 != seq2:
                    complementary_affinities.append(
                        oracle.binding_affinity(seq1, common.wc(seq2))
                    )
                    ATC_affinities.append(
                        oracle.binding_affinity(seq1, seq2)
                    )
                    ATG_affinities.append(
                        oracle.binding_affinity(common.wc(seq1), common.wc(seq2))
                    )

        if len(sizes) == 1:
            title = f"Sample of {NUMBER_OF_DOMAINS_PER_DUAL_SAMPLE} domains of length {list(sizes.values())[0]}"
        else:
            lengths_with_commas = ', '.join([str(val) for val in list(sizes.values())])
            title = f"Sample of {NUMBER_OF_DOMAINS_PER_SAMPLE} domains of lengths {lengths_with_commas}"

        filename = f"spurious_complement_{'_'.join([str(val) for val in list(sizes.values())])}.svg"
        xlabel = "spurious complementary binding affinity"
        produce_histogram(complementary_affinities, title, xlabel, filename)

        filename = f"spurious_ATC_{'_'.join([str(val) for val in list(sizes.values())])}.svg"
        xlabel = "spurious ATC binding affinity"
        produce_histogram(ATC_affinities, title, xlabel, filename)

        filename = f"spurious_ATG_{'_'.join([str(val) for val in list(sizes.values())])}.svg"
        xlabel = "spurious ATG binding affinity"
        produce_histogram(ATG_affinities, title, xlabel, filename)

def run_heterogeneous_analysis():
    internal_domain_collection = get_many_domains({"long1": 10, "long2": 11}, NUMBER_OF_DOMAINS_PER_DUAL_SAMPLE)
    staple_domain_collection = get_many_domains({"staple_domain": 16}, NUMBER_OF_DOMAINS_PER_DUAL_SAMPLE)

    complementary_affinities = []
    ATC_affinities = []
    ATG_affinities = []
    for seq1 in internal_domain_collection:
        for seq2 in staple_domain_collection:
            complementary_affinities.append(
                oracle.binding_affinity(seq1, common.wc(seq2))
            )
            complementary_affinities.append(
                oracle.binding_affinity(common.wc(seq1), seq2)
            )
            ATC_affinities.append(
                oracle.binding_affinity(seq1, seq2)
            )
            ATG_affinities.append(
                oracle.binding_affinity(common.wc(seq1), common.wc(seq2))
            )

    title = f"{NUMBER_OF_DOMAINS_PER_DUAL_SAMPLE**2} pairwise samples of length 10,11 domains with length 16 domains"

    filename = f"spurious_complement_heterogeneous.svg"
    xlabel = "spurious complementary binding affinity"
    produce_histogram(complementary_affinities, title, xlabel, filename)

    filename = f"spurious_ATC_heterogeneous.svg"
    xlabel = "spurious ATC binding affinity"
    produce_histogram(ATC_affinities, title, xlabel, filename)

    filename = f"spurious_ATG_heterogeneous.svg"
    xlabel = "spurious ATG binding affinity"
    produce_histogram(ATG_affinities, title, xlabel, filename)

def get_many_domains(sizes, number):
    domain_collection = Collection()
    for _ in range(number):
        domain_collection.add(generate_domain(sizes))

    return domain_collection

def generate_domain(sizes):
    generators = {
        size: Generator(domain_length=size, alphabet="ATC")
        for size in sizes.values()
    }

    arbiter = BaseArbiter(oracle, Collection())
    arbiter = heuristic_filter.Decorator(arbiter, forbidden_domain_substrings)

    while(True):
        size = random.choice(list(sizes.values()))
        sequence = next(generators[size])
        try:
            arbiter.consider(sequence)
            return sequence
        except arbiter.Rejection as e:
            pass

    raise AssertionError("exited generate_domain() without a domain")

def produce_histogram(affinities, title, xlabel, filename):
    number_of_bins = 20
    _ = plt.hist(affinities, number_of_bins, density = 1, facecolor = 'blue')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("density")
    print(f"Saving {filename}")
    plt.savefig(filename)
    plt.clf()

if __name__ == "__main__":
	main()
