#! /usr/bin/env python3
# Author: Kristopher Kieft
# University of Wisconsin-Madison
# 2021

import argparse
import sys
import os
from fasta_parse import fasta_parse
 
class Edit:
    def __init__(self,f,o,m,a,s,k):
        self.f = f
        self.o = o
        self.m = m
        self.a = a
        self.k = k
        self.s = s
        if 'tab' in self.s:
            self.s = self.s.replace('tab','\t')

        if not self.o:
            fsplit = self.f.rsplit('.',1)
            self.o = f'{fsplit[0]}.edited.{fsplit[1]}'
        if os.path.exists(self.o):
            sys.stderr.write(f'\nError: The output file already exists. Exiting.\n')
            exit()

        if self.m == 1:
            self.method_1()
        elif self.m == 2:
            self.method_2()
        else:
            if not self.a:
                sys.stderr.write(f'\nError: -a is required with -m (except -m 1/2). Exiting.\n')
                exit()
            if self.m == 3:
                self.method_3()
            if self.m == 4:
                self.method_4()
            if self.m == 5:
                self.method_5()
            if self.m == 6:
                self.method_6()
            if self.m == 7:
                self.method_7()
            if self.m == 8:
                self.method_8()
            if self.m == 9:
                self.method_9()

    def get_base(self):
        try:
            temp = self.f.rsplit('/',1)[0]
            self.base = temp.rsplit('.',1)[0]
        except IndexError:
            self.base = self.f.rsplit('.',1)[0]

    def method_1(self):
        self.get_base()
        with open(self.o, 'w') as out:
            for name,seq in fasta_parse(self.f):
                out.write(f'>{self.base}{self.s}{name}\n{seq}\n')
    
    def method_2(self):
        self.get_base()
        with open(self.o, 'w') as out:
            for name,seq in fasta_parse(self.f):
                out.write(f'>{name}{self.s}{self.base}\n{seq}\n')
    
    def method_3(self):
        with open(self.o, 'w') as out:
            for name,seq in fasta_parse(self.f):
                out.write(f'>{self.a}{self.s}{name}\n{seq}\n')
    
    def method_4(self):
        with open(self.o, 'w') as out:
            for name,seq in fasta_parse(self.f):
                out.write(f'>{name}{self.s}{self.a}\n{seq}\n')
    
    def method_5(self):
        if not self.k:
            sys.stderr.write(f'\nError: -k keyword is required with -m {self.m}. Exiting.\n')
            exit()
        with open(self.o, 'w') as out:
            for name,seq in fasta_parse(self.f):
                name = name.replace(self.k, f'{self.s}{self.a}{self.s}{self.k}')
                out.write(f'>{name}\n{seq}\n')
    
    def method_6(self):
        if not self.k:
            sys.stderr.write(f'\nError: -k keyword is required with -m {self.m}. Exiting.\n')
            exit()
        with open(self.o, 'w') as out:
            for name,seq in fasta_parse(self.f):
                name = name.replace(self.k, f'{self.k}{self.s}{self.a}{self.s}')
                out.write(f'>{name}\n{seq}\n')
    
    def method_7(self):
        if not self.s:
            self.s = 0
        if self.s != 0 or self.s != 1:
            sys.stderr.write(f'\nError: -s must be 0 or 1 with -m {self.m}. Exiting.\n')
            exit()
        with open(self.o, 'w') as out:
            for name,seq in fasta_parse(self.f):
                name = name.split(self.a,1)[self.s]
                out.write(f'>{name}\n{seq}\n')
    
    def method_8(self):
        if not self.s:
            self.s = 0
        if self.s != 0 or self.s != 1:
            sys.stderr.write(f'\nError: -s must be 0 or 1 with -m {self.m}. Exiting.\n')
            exit()
        with open(self.o, 'w') as out:
            for name,seq in fasta_parse(self.f):
                name = name.rsplit(self.a,1)[self.s]
                out.write(f'>{name}\n{seq}\n')
    
    def method_9(self):
        with open(self.o, 'w') as out:
            for name,seq in fasta_parse(self.f):
                name = name.replace(self.s, self.a)
                out.write(f'>{name}\n{seq}\n')


if __name__ == '__main__':

    descript = """
    
    Edit fasta file headers (definition lines) according to the given method (-m)

    Methods (-m): 

        Special characters key:
        * Put special characters in quotes
        * 'tab' is the only one that should be spelled out
           ' ': space
           '.': period
           'tab': tab
           "'": single apostrophe
           '"': double apostrophe
           '~': tilde
           ' # ': e.g. splitting prodigal headers
           ',': comma
           ' , tab !': space comma tab space exclamation


        * input a single value (-m int), some may require -a -s -k
        * 'separator': optional, will default to no separator (i.e., just go with -a)
        * 'part': optional, keep first part [-s 0] or second part [-s 1] after split (default: 0)
        * 'keyword': required, specify keyword
        * 'insert': required, specify what to insert/append
        * 'split': required, what to split header by
        * 'replace': required, what to replace in header

        1: append filename to beginning of header (-s separator)
        2: append filename to end of header (-s separator)
        3: append to beginning of header (-a insert -s separator)
        4: append to end of header (-a insert -s separator)
        5: append within header before keyword (-a insert -s separator -k keyword) (result: header -s -a -s -k header)
        6: append within header after keyword (-a insert -s separator -k keyword) (result: header -k -s -a -s header)
        7: split header by first instance from start, keep -s part (-a split -s part), defaults to first part (0)
        8: split header by first instance from end, keep -s part (-a split -s part), defaults to first part (0)
        9: replace in header (-a insert -s replace)
        10: any suggestions?

        Examples:
        -f fasta -o out -m 1 -s '__'
        -f fasta -o out -m 3 -a sample1 -s '__'
        -f fasta -o out -m 7 -a ' '
    """

    parser = argparse.ArgumentParser(description=descript, formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
    parser.add_argument('-f', metavar='', type=str, nargs=1, required=True, help='input fasta file')
    parser.add_argument('-o', metavar='', type=str, default=[''], nargs=1, help='output fasta file (default = -f.edited)')
    parser.add_argument('-m', type=int, nargs=1, choices=[1,2,3,4,5,6,7,8,9], required=True, help='method')
    parser.add_argument('-a', metavar='', type=str, nargs=1, default=[''], help='insert/split')
    parser.add_argument('-s', metavar='', type=str, nargs=1, default=[''], help='separator/replace/part')
    parser.add_argument('-k', metavar='', type=str, nargs=1, default=[''], help='keyword')
    args = parser.parse_args()
    #
    f = args.f[0]
    o = args.o[0]
    m = args.m[0]
    a = args.a[0]
    s = args.s[0]
    k = args.k[0]

    if not os.path.exists(f):
        sys.stderr.write(f'\nError: The fasta file does not exist. Exiting.\n')
        exit()

    Edit(f,o,m,a,s,k)