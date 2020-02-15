#a quick script to summarize the JSON results output for the grid gate designs
# more thought will be required to adapt this code for general use

import os
import json

def main():
    for filename in find_files():
        print(f"\n\nLOADING {filename}\n")
        design = load(filename)
        summarize_to_file(design)

def find_files():
    design_filenames = []
    for full_filename in os.scandir("sequences"):
        filename = full_filename.name
        if filename.startswith("GG_stapled") and filename.endswith(".json"):
            design_filenames.append(os.path.join("sequences", filename))

    return design_filenames

def load(filename):
    with open(filename, 'r') as f:
        design = json.load(f)

    return design

def summarize_to_file(design):
    strands = {
        "Catalyst": "Catalyst",
        "H1": "H_top",
        "H2": "H_bottom",
        "S_left": "S_left",
        "S_right": "S_right",
        "Scaffold_long": "Scaffold_long",
        "Scaffold_short": "Scaffold_short",
        "V1": "V_left",
        "V2": "V_right",
    }
    strands_no_scaffolds = {key:val for key,val in strands.items() if not key.startswith("Scaffold")}
    for old_name, new_name in strands.items():
        print(f"{new_name}: {design['aliases'][old_name]}")

    domains = {
        "a": "StapLT",
        "b": "LT",
        "c": "RT",
        "d": "StapRT",
        "e": "StapLB",
        "f": "LB",
        "g": "RB",
        "h": "StapRB",
    }
    all_domains = list(domains.keys()) + [f"{x}*" for x in domains.keys()]
    for old_name, new_name in domains.items():
        print(f"{new_name}: {design['aliases'][old_name]}")

    def domain_analysis(domain1, domain2):
        key = f"({domain1}, {domain2})"
        return design['domain_level_analysis']['pairwise_affinities'][key]

    def strand_self_structure(strand):
        return design['strand_level_analysis']['Self_affinities'][strand]

    def strand_analysis(strand1, strand2):
        key = f"({strand1}, {strand2})"
        return design['strand_level_analysis']['pairwise_affinities'][key]

    print("\nIntended domain binding:")
    for old_name, new_name in domains.items():
        printw(f"{new_name}-{new_name}*", domain_analysis(old_name, f'{old_name}*'))

    print("\nSpurious domain binding maxima:")
    for old_name, new_name in domains.items():
        unstarred_max_spurious = max([
            domain_analysis(old_name, other)
                for other in all_domains if other != f"{old_name}*"
        ])
        starred_max_spurious = max([
            domain_analysis(f"{old_name}*", other)
                for other in all_domains if other != old_name
        ])
        printw(f"{new_name}-other", unstarred_max_spurious)
        printw(f"{new_name}*-other", starred_max_spurious)

    print("\nSecondary Structure:")
    for old_name, new_name in strands.items():
        printw(new_name, strand_self_structure(old_name))

    print("\nIntended Strand Binding:")
    for old_name, new_name in strands_no_scaffolds.items():
        printw(f"{new_name}-{strands['Scaffold_long']}", strand_analysis(old_name, 'Scaffold_long'))
        if old_name != "S_right":
            printw(f"{new_name}-{strands['Scaffold_short']}", strand_analysis(old_name, 'Scaffold_short'))

    print("\nSpurious Strand Binding:")
    for old_name, new_name in strands_no_scaffolds.items():
        max_spurious = max([
            strand_analysis(f"{old_name}", other)
                for other in strands_no_scaffolds
        ])
        printw(f"{new_name}-other", max_spurious)

    print("\nFalse Positive Strand Binding")
    printw(f"{strands['V1']}-{strands['V2']}", strand_analysis('V1', 'V2'))
    printw(f"{strands['H1']}-{strands['H2']}", strand_analysis('H1', 'H2'))

    print()

def printw(header, value):
    PRINT_WIDTH = 25
    print(header.ljust(PRINT_WIDTH,'.'), value)



if __name__ == "__main__":
    main()
