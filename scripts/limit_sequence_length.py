#! /usr/bin/env python3
# Author: Kristopher Kieft
# University of Wisconsin-Madison
# 2021


import argparse
import os
import sys
from fasta_parse import fasta_parse

class Limit:
    def __init__(self,fasta, output, length, method):
        self.fasta = fasta
        self.output = output
        self.length = [int(i) for i in length]
        self.method = method

        if self.method == 'above':
            self.method_above()
        elif self.method == 'below':
            self.method_below()
        elif self.method == 'between':
            self.method_between()

    def method_above(self):
        l = self.length[0]
        with open(self.output, 'w') as outfile:
            for name,seq in fasta_parse(self.fasta):
                seq = seq.replace('\n','')
                if len(seq) >= l:
                    outfile.write(f'>{name}\n{seq}\n')
    
    def method_below(self):
        l = self.length[0]
        with open(self.output, 'w') as outfile:
            for name,seq in fasta_parse(self.fasta):
                seq = seq.replace('\n','')
                if len(seq) <= l:
                    outfile.write(f'>{name}\n{seq}\n')
    
    def method_between(self):
        try:
            low = self.length[0]
            high = self.length[1]
        except IndexError:
            sys.stderr.write("\nError: Two values must be entered for '-l' with '-m between' (e.g., -l 2000 10000). Exiting.\n\n")
            exit()
        with open(self.output, 'w') as outfile:
            for name,seq in fasta_parse(self.fasta):
                seq = seq.replace('\n','')
                l_seq = len(seq)
                if l_seq >= low and l_seq <= high:
                    outfile.write(f'>{name}\n{seq}\n')



if __name__ == '__main__':

    descript = """
    Limit the sequences in a file to a given length (inclusive).
    Works for nucleotides or amino acids.

    Methods (-m):
    * above: retain sequences >= length (e.g., -m above -l 2000)
    * below: retain sequences <= length (e.g., -m below -l 100000)
    * between: retain sequences >= length 1 and <= length 2 (e.g., -m between -l 2000 100000)
    For 'between', enter 2 lengths separated by a space (above below)

    """
    parser = argparse.ArgumentParser(description=descript, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-f', metavar='', type=str, nargs=1, required=True, help="input fasta file")
    parser.add_argument('-o', metavar='', type=str, nargs=1, required=True, help='output fasta file')
    parser.add_argument('-l', metavar='', type=str, nargs='*', required=True, help='length to limit sequences')
    parser.add_argument('-m', metavar='', type=str, nargs=1, choices=['above', 'below', 'between'], default=['above'], help='method of limiting length [default=above]')
    #
    args = parser.parse_args()
    fasta = args.f[0]
    output = args.o[0]
    length = args.l
    method = args.m[0]
    #
    #
    if os.path.exists(output):
        sys.stderr.write("\nError: The output file already exists. Exiting.\n\n")
        exit()

    Limit(fasta, output, length, method)

#
#
#
