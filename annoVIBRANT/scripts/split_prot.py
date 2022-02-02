#! /usr/bin/env python3
# Author: Kristopher Kieft
# University of Wisconsin-Madison

from fasta_parse import fasta_parse
import os
import math


class SplitProt:

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
            name = f.readline().strip('\n')
            name = name.split(' # ',1)[0]
            base = name.rsplit('_',1)
            if len(base) == 1:
                self.check = False
            seq = f.readline().strip('\n')
        c = 0
        for l in letters:
            c += seq.count(l)
        if c == len(seq): # is nucl ATCGN format
            self.check = False
    
    def remake_file(self):
        '''
        Editing definition lines of proteins causes byte size to be off.
        To fix, re-make the protein file before splitting.
        '''
        self.remake = f'{self.folder}temp.protfile.faa'
        with open(self.remake, 'w') as out:
            for name,seq in fasta_parse(self.infile):
                name = name.split(' # ',1)[0].replace(" ", "$~&")
                out.write(f'>{name}\n{seq}\n')

    def bytes_per_file(self):
        self.main = os.path.getsize(self.remake)
        self.size = math.ceil(self.main/self.threads)

    def splitter(self):
        self.remake_file()
        self.bytes_per_file()
        file = 1
        prev = ''
        for name,seq in fasta_parse(self.remake):
            base = name.rsplit('_',1)[0]
            
            try:
                byte = os.path.getsize(f'{self.folder}{file}.{self.ext}')
                if byte >= self.size and prev != base and file < self.threads:
                    file += 1
            except FileNotFoundError:
                pass

            with open(f'{self.folder}{file}.{self.ext}', 'a') as out:
                out.write(f'>{name}\n{seq}\n')
            
            prev = base
    
        self.check = True
        os.system(f'rm {self.remake}')