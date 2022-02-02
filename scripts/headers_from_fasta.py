#! /usr/bin/env python3
# Author: Kristopher Kieft
# University of Wisconsin-Madison
# 2021

import os
import sys
import argparse

def extract(fasta,outfile):
    with open(fasta, 'r') as infile, open(outfile, 'w') as out:
        for line in infile:
            if line[0] == '>':
                out.write(line[1:])

if __name__ == '__main__':

    descript = '''
    Simply grab all the definition lines (headers) from a fasta file.
    -f: required
    -o: optional. Will create a new file ending in accnos for accession numbers
    '''

    parser = argparse.ArgumentParser(description=descript, formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
    parser.add_argument('-f', metavar='', type=str, nargs=1, required=True, help='input fasta file')
    parser.add_argument('-o', metavar='', type=str, default=[''], nargs=1, help='output file with headers')
    args = parser.parse_args()
    #
    fasta = args.f[0]
    outfile = args.o[0]
    if not outfile:
        outfile = fasta.rsplit('.',1)[0] + '.accnos'
    if os.path.exists(outfile):
        sys.stderr.write(f'\nError: the output file ({outfile}) already exists. Exiting.\n\n')
        exit()
    
    extract(fasta, outfile)