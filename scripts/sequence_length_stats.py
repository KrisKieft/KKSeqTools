#! /usr/bin/env python3
# Author: Kristopher Kieft
# University of Wisconsin-Madison
# 2021

# Purpose
# Quick check of sequence length stats of a fasta file

# Usage
# input a fasta file

import argparse
import sys
from Bio.SeqIO.FastaIO import SimpleFastaParser

vRhyme = argparse.ArgumentParser(description='Calculate sequence stats for a fasta file')
vRhyme.add_argument('-i', metavar='', type=str, nargs=1, required=True, help="input fasta file")
vRhyme.add_argument('-o', metavar='', type=str, nargs=1, required=True, help='output tsv results file')
vRhyme.add_argument('-l', metavar='', type=str, nargs=1, default=['1 5 10 15 20 50 100'], help='length cutoffs in kb separated by spaces within quotes, input "none" (no quotes) for all lengths listed [default: "1 5 10 15 20 50 100"]')
#
args = vRhyme.parse_args()

check = args.l[0].lower()

if check != 'none':
    raw = args.l[0].split(" ")
    header = 'kb\t'.join(raw)
    zero = [0.0]
    lengths = zero + [float(i)*1000 for i in raw]


try:
    base = args.i[0].rsplit("/",1)[0]
except Exception:
    base = args.i[0]

# if len(lengths) < 3:
#     print("\nError: please provide at least 2 lengths\n")
#     exit()

holder = []
value = {}
with open(args.i[0], 'r') as fasta:
    if check == 'none':
        with open(args.o[0], 'w') as outfile:
            outfile.write(f'sequence\tlength\n')
            for name, seq in SimpleFastaParser(fasta):
                seq = seq.replace('\n','')
                outfile.write(f'{name}\t{len(seq)}\n')
    else:
        for name, seq in SimpleFastaParser(fasta):
            seq = seq.replace('\n','')
            holder.append(len(seq))

if check != 'none':
    for idx,l in enumerate(lengths):
        if l != 0.0:
            result = [val for val in holder if val < l if val >= lengths[idx-1]]
            value.update({l:len(result)})
    result = [val for val in holder if val >= lengths[-1]]
    value.update({l+1:len(result)})

    with open(args.o[0], 'w') as outfile:
        outfile.write(f'file\t{header}kb\t>{int(lengths[-1]/1000)}kb')
        outfile.write(f'\n{base}')
        for key,val in value.items():
            outfile.write(f'\t{val}')
        outfile.write('\n')
