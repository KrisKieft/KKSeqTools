#! /usr/bin/env python3
# Author: Kristopher Kieft
# University of Wisconsin-Madison
# 2022

import os
import argparse


class Methods:
    def __init__(self,l,f,o):
        self.l = l
        self.f = f
        self.o = o

        self.get_coords()
        self.main()
        

    def get_coords(self):
        self.coords = {}
        with open(self.l, 'r') as f:
            next(f)
            for line in f:
                line = line.strip('\n').split('\t')
                if not line: continue
                name = line[0]
                frag = line[1]

                start = int(line[5])
                stop = int(line[6])

                self.coords.setdefault(name, []).append((frag, start, stop))

    def fasta_parse(self):
        with open(self.f, 'r') as fasta:
            for line in fasta:
                if line[0] == '>':
                    try:
                        yield header, seq
                    except NameError:
                        pass
                    seq = ''
                    header = line[1:].strip("\n")
                else:
                    seq += line.strip("\n")

            yield header, seq
    
    def main(self):
        with open(self.o, 'w') as out:
            for name,seq in self.fasta_parse():
                phages = self.coords.get(name, False)
                if phages:
                    for entry in phages:
                        frag,start,stop = entry
                        excise = seq[start-1:stop]
                        out.write(f'>{frag}\n{excise}\n')
    

if __name__ == '__main__':
 
    descript = """
    Extract VIBRANT-predicted prophage ('fragment') sequences from whole scaffolds
    using an input prophage coordiantes file.
    VIBRANT: https://doi.org/10.1186/s40168-020-00867-0
"""
    parser = argparse.ArgumentParser(description=descript, formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
    parser.add_argument('-l', metavar='', type=str, nargs=1, required=True, help="input VIBRANT coordinates file")
    parser.add_argument('-f', metavar='', type=str, nargs=1, required=True, help="input fasta file")
    parser.add_argument('-o', metavar='', type=str, nargs=1, required=True, help="output prophage fasta file")
    #
    args = parser.parse_args()
    l = args.l[0]
    f = args.f[0]
    o = args.o[0]
    
    if os.path.exits(o):
        print(f'Error. Output file already exists:  "{o}". Exiting.')
        exit()
    
    Methods(l, f, o)