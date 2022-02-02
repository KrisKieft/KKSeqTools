#! /usr/bin/env python3
# Author: Kristopher Kieft
# University of Wisconsin-Madison

import sys
import pandas as pd


class HMMparse:
    def __init__(self, base, folder):
        self.base = base
        self.parsed = f'{folder}parsed_hmm_results/'
        self.raw = f'{folder}raw_hmm_results/'

        self.kegg()
        self.pfam()
        self.vog()

    def kegg(self):
        with open(f'{self.raw}{self.base}.KEGG.temp') as f, open(f'{self.raw}{self.base}.KEGG.hmmtbl', 'w') as out:
            #out.write('protein\taccession\tevalue\tscore\n')
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
        
        df = pd.read_table(f'{self.raw}{self.base}.KEGG.hmmtbl', names=['protein', 'accession', 'evalue', 'score'])
        df.sort_values(by='evalue', ascending=True, inplace=True)
        df.drop_duplicates(subset='protein', keep='first', inplace=True)
        df.to_csv(f'{self.parsed}{self.base}.KEGG.tsv', index=False, sep='\t')


    def pfam(self):
        with open(f'{self.raw}{self.base}.Pfam.temp') as f, open(f'{self.raw}{self.base}.Pfam.hmmtbl', 'w') as out:
            #out.write('protein\taccession\tevalue\tscore\n')
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
        
        df = pd.read_table(f'{self.raw}{self.base}.Pfam.hmmtbl', names=['protein', 'accession', 'evalue', 'score'])
        df.sort_values(by='evalue', ascending=True, inplace=True)
        df.drop_duplicates(subset='protein', keep='first', inplace=True)
        df.to_csv(f'{self.parsed}{self.base}.Pfam.tsv', index=False, sep='\t')

    def vog(self):
        with open(f'{self.raw}{self.base}.VOG.temp') as f, open(f'{self.raw}{self.base}.VOG.hmmtbl', 'w') as out:
            #out.write('protein\taccession\tevalue\tscore\n')
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
        
        df = pd.read_table(f'{self.raw}{self.base}.VOG.hmmtbl', names=['protein', 'accession', 'evalue', 'score'])
        df.sort_values(by='evalue', ascending=True, inplace=True)
        df.drop_duplicates(subset='protein', keep='first', inplace=True)
        df.to_csv(f'{self.parsed}{self.base}.VOG.tsv', index=False, sep='\t')

if __name__ == '__main__':
    HMMparse(sys.argv[1], sys.argv[2])