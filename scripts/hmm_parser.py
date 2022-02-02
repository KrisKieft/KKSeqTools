#! /usr/bin/env python3
# Author: Kristopher Kieft
# University of Wisconsin-Madison

import os
import argparse
import pandas as pd


class HMMparse:
    def __init__(self, i, o, m, pfam):
        self.i = i
        self.o = o
        self.m = m

        if self.m == 'score':
            self.asc = False
        elif self.m == 'evalue':
            self.asc = True
    
        if self.o == '':
            self.o = self.i.rsplit('.',1)[0] + f'.parsed-{self.m}.tsv'
            self.full = self.i.rsplit('.',1)[0] + f'.unparsed-full.tsv'
            if os.path.exists(self.o):
                print('Error: output file already exists. Exiting.')
                print(f'{self.o}')
                exit()
        else:
            self.full = self.o.rsplit('.',1)[0] + '.unparsed-full.tsv'
            if os.path.exists(self.full):
                print('Error: output temp file file already exists. Try a different -o. Exiting.')
                print(f'{self.full}')
                exit()
        
        if pfam:
            self.pfam()
        else:
            self.main()


    def main(self):
        with open(self.i) as f, open(self.full, 'w') as out:
            out.write('protein\taccession\tevalue\tscore\n')
            next(f)
            next(f)
            next(f)
            for line in f:
                if line[0] == '#':
                    break
                line = list(filter(None, line.split(' ')))
                prot = line[0]
                acc = line[2]
                evalue = line[4]
                score = line[5]
                out.write(f'{prot}\t{acc}\t{evalue}\t{score}\n')
        
        df = pd.read_table(self.full)
        df.sort_values(by=self.m, ascending=self.asc, inplace=True)
        df.drop_duplicates(subset='protein', keep='first', inplace=True)
        df.to_csv(self.o, index=False, sep='\t')


    def pfam(self):
        with open(self.i) as f, open(self.full, 'w') as out:
            out.write('protein\taccession\tevalue\tscore\n')
            next(f)
            next(f)
            next(f)
            for line in f:
                if line[0] == '#':
                    break
                line = list(filter(None, line.split(' ')))
                prot = line[0]
                acc = line[3]
                evalue = line[4]
                score = line[5]
                out.write(f'{prot}\t{acc}\t{evalue}\t{score}\n')
        
        df = pd.read_table(self.full)
        df.sort_values(by=self.m, ascending=self.asc, inplace=True)
        df.drop_duplicates(subset='protein', keep='first', inplace=True)
        df.to_csv(self.o, index=False, sep='\t')

if __name__ == '__main__':
    descript = """
    Parse a raw output from HMMsearch. Get the best hit per protein. 

    Generates 2 files:
        > full tsv results (unparsed/filtered)
        > output will best hit per protein

    Use --pfam for a pfam search because the columns are different,
    or if the results just look wrong. Maybe this will fix it.
"""

    parser = argparse.ArgumentParser(description=descript, formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
    parser.add_argument('-i', metavar='', type=str, nargs=1, required=True, help="input raw hmm result")
    parser.add_argument('-o', metavar='', type=str, nargs=1, default=[''], help="output parsed hmm result")
    parser.add_argument('-m', metavar='', type=str, nargs=1, default=['score'], choices=['score', 'evalue'], help="sort/select column [score]")
    parser.add_argument('--pfam', action='store_true', help="use this flag if the raw hmm is from Pfam")

    args = parser.parse_args()
    i = args.i[0]
    o = args.o[0]
    m = args.m[0]

    HMMparse(i, o, m, args.pfam)