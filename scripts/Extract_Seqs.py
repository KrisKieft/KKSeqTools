#! /usr/bin/env python3
# Author: Kristopher Kieft
# University of Wisconsin-Madison
# 2021

import sys
import argparse
import os
import gzip
import time

class Methods:
    def __init__(self,l,f,o,m,s,r,v,gzip,start):
        self.l = l
        self.f = f
        self.o = o
        self.m = m
        self.gzip = gzip
        self.s = s
        self.r = r
        self.v = v
        self.start = start

        self.get_names()
        if self.m == '1':
            self.method_1()
        elif self.m == '2':
            self.method_2()
        elif self.m == '3':
            self.method_3()
        elif self.m == '4':
            self.method_4()
        
        if self.v:
            sys.stdout.write(f"\n{self.len_names} input names found\n")
            if self.m != '2':
                self.len_names = len(self.names)
                sys.stdout.write(f"{self.total - self.len_names} seqs written ({self.o})\n")
                sys.stdout.write(f"{self.len_names} names were unused\n")
            else:
                sys.stdout.write(f"{self.total} seqs written ({self.o})\n")
            sys.stdout.write(f"elapsed: {round(time.time()-self.start,2)}s\n\n")

    def get_names(self):
        with open(l, 'r') as infile:
            self.names = set(infile.read().split('\n'))
            self.names.discard('')
        self.total = len(self.names)
        self.len_names = self.total

    def method_1(self):
        with open(self.o, 'w') as outfile:
            for name,seq in self.fasta_parse():
                if name in self.names:
                    seq = ''.join(seq)
                    outfile.write(f'>{name}\n{seq}')
                    self.names.remove(name)
                    if not self.names:
                        break

    def method_2(self):
        self.total = 0
        with open(self.o, 'w') as outfile:
            for name,seq in self.fasta_parse():
                new = name.rsplit('_',1)[0]
                if new in self.names:
                    seq = ''.join(seq)
                    outfile.write(f'>{name}\n{seq}')
                    self.total += 1


    def method_3(self):
        new = set([n.rsplit('_',1)[0] for n in list(self.names)])
        with open(self.o, 'w') as outfile:
            for name,seq in self.fasta_parse():
                if name in new:
                    seq = ''.join(seq)
                    outfile.write(f'>{name}\n{seq}')
                    self.names.remove(name)
                    if not self.names:
                        break

    def method_4(self):
        with open(self.o, 'w') as outfile:
            for name,seq in self.fasta_parse():
                if name not in self.names:
                    seq = ''.join(seq)
                    outfile.write(f'>{name}\n{seq}')
                else:
                    self.names.remove(name)

    def fasta_parse(self):
        if self.gzip:
            with gzip.open(self.f, 'r') as fasta:
                if not self.s:
                    for line in fasta:
                        line = line.decode("utf-8")
                        if line[0] == '>':
                            try:
                                yield header, seq
                            except NameError:
                                pass
                            seq = []
                            header = line[1:].strip("\n")
                        else:
                            seq.append(line)

                    yield header, seq
                else:
                    for line in fasta:
                        line = line.decode("utf-8")
                        if line[0] == '>':
                            try:
                                yield header, seq
                            except NameError:
                                pass
                            seq = []
                            header = line[1:].strip("\n")
                            if not self.r:
                                header = header.split(self.s,1)[0]
                            else:
                                header = header.rsplit(self.s,1)[0]
                        else:
                            seq.append(line)

                    yield header, seq
                    
        else:
            with open(self.f, 'r') as fasta:
                if not self.s:
                    for line in fasta:
                        if line[0] == '>':
                            try:
                                yield header, seq
                            except NameError:
                                pass
                            seq = []
                            header = line[1:].strip("\n")
                        else:
                            seq.append(line)

                    yield header, seq
                else:
                    for line in fasta:
                        if line[0] == '>':
                            try:
                                yield header, seq
                            except NameError:
                                pass
                            seq = []
                            header = line[1:].strip("\n")
                            if not self.r:
                                header = header.split(self.s,1)[0]
                            else:
                                header = header.rsplit(self.s,1)[0]
                        else:
                            seq.append(line)

                    yield header, seq

if __name__ == '__main__':
 
    descript = """
    Extract sequences from a fasta file using an input list of names. 
    The list of names should be new line separated.

    Methods (-m):
    1: match list exactly to definition lines (e.g., -l genomes -f genomes, -l proteins -f proteins)
    2: extract fasta proteins (Prodigal format) using list of genomes (e.g., -l genomes -f proteins)
    3: extract fasta genomes using list of proteins (Prodigal format) (e.g., -l proteins -f genomes)
    4: EXCLUDE match list exactly to definition lines and exclude any hits
    5: any suggestions?

    Split (--split):
    Skip this flag to not split database names
    By default it will split by first instance from the start of the header
    Use --reverse to split by first instance from the end of the header
    * space: split by space
    * comma: split by comma
    * tab: split by tab
    * prodigal: split by " # " (space pound space)
    * underscore: split by _ (underscore)
    * dunder: split by __ (double underscore)
    * tilde: split by ~ (tilde)

"""
    parser = argparse.ArgumentParser(description=descript, formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
    parser.add_argument('-l', metavar='', type=str, nargs=1, required=True, help="input list of names")
    parser.add_argument('-f', metavar='', type=str, nargs=1, required=True, help="input fasta file")
    parser.add_argument('--gzip', action='store_true', help="input fasta file in gzip format")
    parser.add_argument('-o', metavar='', type=str, nargs=1, required=True, help="output fasta file")
    parser.add_argument('-m', metavar='', type=str, nargs=1, default=['1'], choices=['1', '2', '3', '4'], help="method [default: 1]")
    parser.add_argument('--split', metavar='', type=str, nargs=1, default=[False], choices=[False, 'space', 'comma', 'tab', 'prodigal', 'underscore', 'dunder', 'tilde'], help="split database headers by delimiter (first instance from start)")
    parser.add_argument('--reverse', action='store_true', help="first instance from end (use with --split)")
    parser.add_argument('-v', metavar='', type=str, nargs=1, default=['1'], choices=['0', '1'], help="verbose [default: 1]")
    #parser.add_argument('--whole', action='store_true', help="keep the whole database name in the ouput when splitting (by default keeps the split name)")
    #
    start = time.time()
    args = parser.parse_args()
    l = args.l[0]
    f = args.f[0]
    o = args.o[0]
    m = args.m[0]
    v = args.v[0]
    options = {'space':' ', 'comma':',', 'tab':'\t', 'prodigal':' # ', 'underscore':'_', 'dunder':'__', 'tilde':'~'}
    s = options.get(args.split[0], False)
    if os.path.exists(o):
        sys.stderr.write("\nError: output file (-o) already exists. Exiting.\n\n")
        exit()
    if f.endswith('.gz') and not args.gzip:
        sys.stderr.write("\n\n!!!!!\nCAUTION: the input file looks to be gzip format.\nIf you get an error use --gzip.\n!!!!!\n\n")

    Methods(l,f,o,m,s,args.reverse,v,args.gzip,start)
    