#! /usr/bin/env python3
# Author: Kristopher Kieft
# University of Wisconsin-Madison
# 2021


import argparse
import os
import sys
import subprocess
import math
from fasta_parse import fasta_parse

class Splitter:
    def __init__(self,fasta, output, s, n, p, v, b):
        self.fasta = fasta
        self.output = output
        self.s = s
        self.n = n
        self.p = p
        self.b = b
        self.v = v
        if self.v:
            sys.stdout.write(f'\n')
        self.ext = self.fasta.rsplit('.',1)[1]
        self.counter = 0
        self.holder = 0
        self.avg = 0
        self.file = 1

        self.check_p()
        if self.s:
            self.s = self.s[0]
            self.method_s()
        elif self.n:
            self.n = self.n[0]
            self.method_n()
        elif self.b:
            self.b = self.b[0]
            self.method_b()
        if self.v:
            sys.stdout.write(f'Sequences written:  {self.holder}\n')
            sys.stdout.write(f'New files created:  {self.file}\n')
            if self.s:
                sys.stdout.write(f'Sequences in last file ({self.file}):  {self.counter} (of {self.s})\n')
            elif self.n:
                sys.stdout.write(f'Sequences in last file ({self.file}):  {self.counter} (of {self.per})\n')
            elif self.b:
                sys.stdout.write(f'Average file size (Mb):  {round(self.avg/1e6,1)}\n')
            sys.stdout.write('\n')

    def check_p(self):
        if not self.p:
            try:
                temp = self.fasta.rsplit('/')[0]
                self.p = temp.rsplit('.',1)[0]
            except IndexError:
                self.p = self.fasta.rsplit('.',1)[0]

    def count_seqs(self):
        self.c = subprocess.check_output(f"grep -c '>' {self.fasta}", shell=True)
        self.c = int(self.c.decode("utf-8"))
        if self.v:
            sys.stdout.write(f'Sequences identified:  {self.c}\n')
    
    def seqs_per_file(self):
        self.per = math.ceil(self.c/self.n)
        if self.v:
            sys.stdout.write(f'Sequences per file:  {self.per}\n')
    
    def bytes_per_file(self):
        self.main = os.path.getsize(self.fasta)
        self.size = math.ceil(self.main/self.b)
        if self.v:
            sys.stdout.write(f'Size of input file (Mb):  {round(self.main/1e6,1)}\n')
            sys.stdout.write(f'Size goal per file (Mb):  {round(self.size/1e6,1)}\n')

    def method_s(self):
        for name,seq in fasta_parse(self.fasta):
            self.counter += 1
            with open(f'{self.output}{self.p}.{self.file}.{self.ext}', 'a') as out:
                out.write(f'>{name}\n{seq}\n')
            if self.counter >= self.s:
                self.file += 1
                self.holder += self.counter
                self.counter = 0
        self.holder += self.counter

    def method_n(self):
        self.count_seqs()
        self.seqs_per_file()
        for name,seq in fasta_parse(self.fasta):
            self.counter += 1
            with open(f'{self.output}{self.p}.{self.file}.{self.ext}', 'a') as out:
                out.write(f'>{name}\n{seq}\n')
            if self.counter >= self.per:
                self.file += 1
                self.holder += self.counter
                self.counter = 0
        self.holder += self.counter
    
    def method_b(self):
        self.bytes_per_file()
        for name,seq in fasta_parse(self.fasta):
            self.holder += 1
            with open(f'{self.output}{self.p}.{self.file}.{self.ext}', 'a') as out:
                out.write(f'>{name}\n{seq}\n')
            byte = os.path.getsize(f'{self.output}{self.p}.{self.file}.{self.ext}')
            if byte >= self.size:
                self.file += 1
                self.avg += byte
        self.avg += byte
        self.avg /= self.file
    

if __name__ == '__main__':

    descript = """
    Take an input fasta file with many sequences and 
    split into multiple, separate files.
    Does its best to split evenly (rounds up).

    For both -n and -s, the last file will contain any remainder.
    For -b, size in Mb calculated by Python may differ from terminal interface.
    """
    parser = argparse.ArgumentParser(description=descript, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-f', metavar='', type=str, nargs=1, required=True, help="input fasta file")
    parser.add_argument('-o', metavar='', type=str, nargs=1, default=['split_fasta_files/'], help='output folder to deposit files [default = split_fasta_files/]')
    parser.add_argument('-s', metavar='', type=int, nargs=1, default=[], help='number of sequences to deposit per file')
    parser.add_argument('-n', metavar='', type=int, nargs=1, default=[], help='number of files to create; distribute sequences evenly')
    parser.add_argument('-b', metavar='', type=int, nargs=1, default=[], help='number of files to create; distribute bytes evenly (roughly)')
    parser.add_argument('-p', metavar='', type=str, nargs=1, default=[''], help='prefix to name output files (default is prefix of -f)')
    parser.add_argument('-v', metavar='', type=int, nargs=1, choices=[1,0], default=[1], help='verbose [default=1]')
    #
    args = parser.parse_args()
    fasta = args.f[0]
    output = args.o[0]
    if output[-1] != '/':
        output += '/'
    s = args.s
    n = args.n
    b = args.b
    p = args.p[0]
    v = args.v[0]
    #
    #
    check = sum([bool(s), bool(n), bool(b)])
    if check > 1:
        sys.stderr.write("\nError: Please choose one option -s/-n/-b. Exiting.\n\n")
        exit()
    elif check == 0:
        sys.stderr.write("\nError: Please provide one option -s/-n/-b. Exiting.\n\n")
        exit()
    if not os.path.exists(fasta):
        sys.stderr.write("\nError: The fasta file does not exist. Exiting.\n\n")
        exit()
    if os.path.exists(output):
        sys.stderr.write("\nError: The output folder already exists. Exiting.\n\n")
        exit()
    else:
        subprocess.run(f'mkdir {output}', shell=True)

    Splitter(fasta, output, s, n, p, v, b)

#
#
#
