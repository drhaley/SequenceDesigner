# SequenceDesigner
A Python tool for generating DNA sequences for lab experiment
via a design pattern using orthogonal domains.

## Requirements
+ A Linux-based OS or Windows Subsystem for Linux
+ [Python 3.6](https://www.python.org/downloads/) (or higher)
+ [ViennaRNA](https://www.tbi.univie.ac.at/RNA/) (must install Core *and* Python 3 bindings)

### Installing requirements

To install Python 3 (if it is not already installed):

    $ sudo apt install python3

To install ViennaRNA, consult their
[download page](https://www.tbi.univie.ac.at/RNA/#download)
and follow the instructions there.  You will need to install both the "Core" and "Python3 bindings".
In some of our tests we used Ubuntu 20.04 under WSL2, and found the following sequence of commands helpful:

    $ sudo dpkg -i viennarna_2.4.18-1_amd64.deb   # does not install dependencies, even with gdebi
    $ sudo apt --fix-broken install               # fixes broken dependencies
    $ sudo dpkg -i python3-rna_2.4.18-1_amd64.deb

# Running the example

    $ python3 example.py

    ...

    ['ACCACCATAC', 'CCTTCCTACT', 'AACCAAACTC', 'ACACACTCTA', 'CCTCATTCTC', 'CTTTCCCATC']

The example creates a set of pairwise-orthogonal 3-letter 10-length sequences.
It caps at 100k attempts (sufficient for an example).  Depending upon the random seed, the example will typically create 5 or 6 sequences.

To qualify, the sequences must (at 40C)
+ have at least 10 kcal/mol affinity to their complement sequence
+ only use A, T, and C (i.e. 3-letter code heuristic for minimal self-structure)
+ have no more than 5 kcal/mol affinity to other sequences, their complements, or pairwise concatenations thereof
    + this must also be true of the complement sequences
+ not contain any subsequences of the following forms:
    + {C,G}^4
    + {A,T}^5
    + AAAA
    + TTTT
+ must not begin or end with a subsequence of form {A,T}^3

The examples are saved by default in `./sequences/example.json`

## Specific experiments

For three specific experiments,
branches of the code were created to allow for specific modifications to the algorithm
as required by each experimental design.
This allowed for continued custom modifications during the design phase as well as preserving
the exact code for experimental reproducibility.
For convenience, these branches are linked below.

+ [Two-domain reporter experiment](https://github.com/drhaley/SequenceDesigner/tree/design_a_b_TBN)
+ [LCM concatemer experiment](https://github.com/drhaley/SequenceDesigner/tree/design_LCM_TBN)
+ [2x2 grid gate experiment](https://github.com/drhaley/SequenceDesigner/tree/grid_gate_2_by_2)
