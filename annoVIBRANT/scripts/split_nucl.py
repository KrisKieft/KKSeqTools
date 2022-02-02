#! /usr/bin/env python3
# Author: Kristopher Kieft
# University of Wisconsin-Madison

from fasta_parse import fasta_parse
import os
import math


class SplitNucl:

    def __init__(self, infile, folder, threads):
        self.infile = infile
        self.folder = folder + 'split_files/'
        self.threads = threads
        self.ext = self.infile.rsplit('.',1)[1]
        self.check = True

        self.check_format()
        if not self.check:
            return

        os.mkdir(self.folder)
        self.splitter()

    def check_format(self):
        letters = ['A', 'T', 'C', 'G', 'N']
        with open(self.infile) as f:
            next(f)
            seq = f.readline().strip('\n')
        c = 0
        for l in letters:
            c += seq.count(l)
        if c != len(seq): # not nucl ATCGN format
            self.check = False

    def bytes_per_file(self):
        self.main = os.path.getsize(self.infile)
        self.size = math.ceil(self.main/self.threads)

    def splitter(self):
        self.bytes_per_file()
        file = 1
        for name,seq in fasta_parse(self.infile):
            name = name.replace(" ", "$~&")

            try:
                byte = os.path.getsize(f'{self.folder}{file}.{self.ext}')
                if byte >= self.size and file < self.threads:
                    file += 1
            except FileNotFoundError:
                pass

            with open(f'{self.folder}{file}.{self.ext}', 'a') as out:
                out.write(f'>{name}\n{seq}\n')
    
        self.check = True