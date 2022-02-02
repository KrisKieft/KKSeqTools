#! /usr/bin/env python3
# Author: Kristopher Kieft
# University of Wisconsin-Madison
# 2021


import argparse
import os
import sys
from fasta_parse import fasta_parse


def count_length(fasta, output):
    with open(output, 'w') as outfile:
        outfile.write('sequence\tlength\n')
        for name,seq in fasta_parse(fasta):
            seq = seq.replace('\n','')
            outfile.write(f'{name}\t{len(seq)}\n')


if __name__ == '__main__':

    descript = """
    Counts the length of sequences in a fasta file.
    Works for nucleotides or amino acids.

    """
    parser = argparse.ArgumentParser(description=descript, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-f', metavar='', type=str, nargs=1, required=True, help="input fasta file")
    parser.add_argument('-o', metavar='', type=str, nargs=1, required=True, help='output tsv file')
    #
    args = parser.parse_args()
    fasta = args.f[0]
    output = args.o[0]
    #
    #
    if os.path.exists(output):
        sys.stderr.write("\nError: The output file already exists. Exiting.\n\n")
        exit()

    count_length(fasta, output)

#
#
#
