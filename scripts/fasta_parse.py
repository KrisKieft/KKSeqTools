#! /usr/bin/env python3
# Author: Kristopher Kieft
# University of Wisconsin-Madison
# 2021

# Faster Parser - Generator
# from fasta_parse import fasta_parse


def fasta_parse(infile):
    with open(infile, 'r') as fasta:
        for line in fasta:
            if line[0] == '>':
                try:
                    yield header, ''.join(seq)
                except NameError:
                    pass # first line
                seq = []
                header = line[1:].strip("\n")
            else:
                seq.append(line)

        # last one
        yield header, ''.join(seq)
            