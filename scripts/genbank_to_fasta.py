#! /usr/bin/env python3
# Author: Kristopher Kieft
# University of Wisconsin-Madison
# 2022

import os
import argparse

class Convert:
    def __init__(self, args):
        self.get_args(args)
        self.parse_genbank()
        self.logit()
    
    def logit(self):
        log = \
"""fasta:  genomes
faa:    proteins (header | product)
ffn:    genes (header | product)
gff:    GFF v3 (seqname source feature start end score strand frame attribute)
trna:   tRNA sequences (DNA)
rrna:   rRNAs sequences (DNA)
len:    length of genomes (bp)
"""
        with open(f'{self.folder}info.log', 'w') as f:
            f.write(log)

    def get_args(self, args):
        self.genbank = args.genbank[0]
        try:
            temp = self.genbank.rsplit('/',1)[1]
            self.base = temp.rsplit('.',1)[0]
        except IndexError:
            self.base = self.genbank.rsplit('.',1)[0]
        self.folder = args.folder[0]
        if not self.folder:
            self.folder = f'{self.base}_GenBank_parse/'
        if self.folder[-1] != '/':
            self.folder += '/'
        err = False
        if not os.path.exists(self.genbank):
            print(f'\nError: genbank file "{self.genbank}" does not exist. Exiting\n')
            err = True
        if os.path.exists(self.folder):
            print(f'\nError: output folder "{self.folder}" exists. Exiting\n')
            err = True
        if err:
            exit()
        os.mkdir(self.folder)
    
    def exit_parse(self, err):
        print('\nError: could not parse misformatted GenBank file. Exiting.')
        print(f'Exit message: {err}\n')
        os.system(f'rm -R {self.folder}')
        exit()
    
    def parse_genbank(self):
        with open(self.genbank) as self.f, \
            open(f'{self.folder}{self.base}.faa', 'w') as self.faa_handle, \
            open(f'{self.folder}{self.base}.fasta', 'w') as self.fasta_handle, \
            open(f'{self.folder}{self.base}.ffn', 'w') as self.ffn_handle, \
            open(f'{self.folder}{self.base}.gff', 'w') as self.gff_handle, \
            open(f'{self.folder}{self.base}.rrna', 'w') as self.rrna_handle, \
            open(f'{self.folder}{self.base}.trna', 'w') as self.trna_handle, \
            open(f'{self.folder}{self.base}.len', 'w') as self.len_handle:

            self.gff_handle.write('##gff-version 3\n')

            buffer_whole = 0
            while True: # until return
                self.proteins = []
                self.trna = []
                self.rrna = []
                buffer_whole += 1
                d = False # found def line
                buffer_header = 0 # break endless loop
                while True:
                    buffer_header += 1
                    line = self.f.readline()
                    if line[:5] == 'LOCUS':
                        self.locus_line(line)
                        d = True
                    elif line[:8] == 'FEATURES':
                        if not d:
                            self.exit_parse('no genome name found')
                        else:
                            buffer_header = 0
                            break
                    elif line == '':
                        return 
                    if buffer_header > 1000:
                        self.exit_parse('failed to parse LOCUS information')
                
                self.loc = (0,0,0)
                self.total = 0 # total CDS
                self.total_r = 0 # total rRNA
                self.total_t = 0 # total tRNA
                while True:
                    line = self.f.readline().strip()
                    if line[:3] == 'CDS':
                        self.total += 1
                        self.feature_line(line)
                        self.aminos_line()
                    elif line[:4] == 'tRNA':
                        self.feature_line(line)
                        self.tRNA_line()
                    elif line[:4] == 'rRNA':
                        self.feature_line(line)
                        self.rRNA_line()

                    elif line[:6] == 'ORIGIN':
                        self.loc = (0,0,0)
                        break

                self.origin_line()

                if buffer_whole > 1000:
                    self.exit_parse('failed to parse GenBank entries')
    
    def locus_line(self, line):
        line = list(filter(None, line.split('  ')))
        self.genome = line[1].strip(' ')
        for l in line:
            if 'bp' in l:
                length = l.strip().split(' bp')[0]
                self.len_handle.write(f'{self.genome}\t{length}\n')
    
    def feature_line(self, line):
        try:
            self.loc = line.split(' ')[-1]
            if self.loc[:10] == 'complement':
                self.loc = [int(i) for i in self.loc.replace('complement(','').replace(')','').split('..')]
                self.loc.append('-')
                self.loc = tuple(self.loc)
            else:
                self.loc = [int(i) for i in self.loc.split('..')]
                self.loc.append('+')
                self.loc = tuple(self.loc)
        except ValueError:
            try:
                self.loc = line.split(' ')[-1]
                if self.loc[:10] == 'complement':
                    self.loc = [int(i) for i in self.loc.replace('complement(','').replace(')','').replace('>','').replace('<','').split('..')]
                    self.loc.append('-')
                    self.loc = tuple(self.loc)
                else:
                    self.loc = [int(i) for i in self.loc.replace('>','').replace('<','').split('..')]
                    self.loc.append('+')
                    self.loc = tuple(self.loc)
            except ValueError:
                self.exit_parse(f'failed to parse entry coordinates "{self.loc}"')
    
    def tRNA_line(self):
        buffer_product = 0
        buffer_trna = 0
        product = ''
        found_name = False
        self.total_t += 1
        while True:
            buffer_trna += 1
            line = self.f.readline().strip()
            if line[:10] == '/locus_tag':
                name = line[12:-1]
                found_name = True
            elif line[:8] == '/product':
                temp = line[10:]
                if temp[-1] == '"':
                    product += line[10:-1]
                else:
                    product += line[10:]
                    while True:
                        buffer_product += 1
                        line = self.f.readline().strip()
                        if line[-1] == '"':
                            product += line[:-1]
                            break
                        else:
                            product += line
                        if buffer_product > 1000:
                            self.exit_parse('failed to parse tRNA product name')
                product = product.replace('\n','')
                if not found_name:
                    name = f'{self.genome}_tRNA_{self.total_t}'
                self.trna.append((name, product, self.loc))
                break
            if buffer_trna > 1000:
                self.exit_parse('failed to parse tRNA entry')


    def rRNA_line(self):
        buffer_product = 0
        buffer_rrna = 0
        product = ''
        found_name = False
        self.total_r += 1
        while True:
            buffer_rrna += 1
            line = self.f.readline().strip()
            if line[:10] == '/locus_tag':
                name = line[12:-1]
                found_name = True
            elif line[:8] == '/product':
                temp = line[10:]
                if temp[-1] == '"':
                    product += line[10:-1]
                else:
                    product += line[10:]
                    while True:
                        buffer_product += 1
                        line = self.f.readline().strip()
                        if line[-1] == '"':
                            product += line[:-1]
                            break
                        else:
                            product += line
                        if buffer_product > 1000:
                            self.exit_parse('failed to parse rRNA product name')
                product = product.replace('\n','')
                if not found_name:
                    name = f'{self.genome}_rRNA_{self.total_r}'
                self.rrna.append((name, product, self.loc))
                break
            if buffer_rrna > 1000:
                self.exit_parse('failed to parse rRNA entry')

    def aminos_line(self):
        found_name = False
        line = self.f.readline().strip()
        buffer_lines = 0
        buffer_aminos = 0
        buffer_product = 0
        aminos = ''
        product = ''
        while True:
            buffer_lines += 1
            line = self.f.readline().strip()
            if line[:10] == '/locus_tag':
                name = line[12:-1]
                found_name = True
            elif line[:8] == '/product':
                temp = line[10:]
                if temp[-1] == '"':
                    product += line[10:-1]
                else:
                    product += line[10:]
                    while True:
                        buffer_product += 1
                        line = self.f.readline().strip()
                        if line[-1] == '"':
                            product += line[:-1]
                            break
                        else:
                            product += line
                        if buffer_product > 1000:
                            self.exit_parse('failed to parse CDS product name')
                    product = product.replace('\n','')
            elif line[:12] == '/translation':
                temp = line[14:]
                if temp[-1] == '"':
                    aminos += line[14:-1]
                else:
                    aminos += line[14:]
                    while True:
                        buffer_aminos += 1
                        line = self.f.readline().strip()
                        if line[-1] == '"':
                            aminos += line[:-1]
                            break
                        else:
                            aminos += line
                        if buffer_aminos > 1000:
                            self.exit_parse('failed to parse CDS amino acids')
                aminos = '\n'.join([aminos[i:i+60] for i in range(0,len(aminos),60)])
                if not found_name:
                    name = f'{self.genome}_{self.total}'
                self.faa_handle.write(f'>{name} | {product}\n{aminos}\n')
                self.proteins.append((name, product, self.loc))
                break

            if buffer_lines > 1000:
                self.exit_parse('failed to parse CDS information')
    
    def origin_line(self):
        buffer_origin = 0
        seq = ''
        while True:
            buffer_origin += 1
            line = self.f.readline().strip()
            if line == '//':
                seq = seq.upper()
                self.fasta_handle.write(f'>{self.genome}\n{seq}')
                seq = seq.replace('\n','')
                self.genes(seq)
                self.tRNAs(seq)
                self.rRNAs(seq)
                break
            seq += ''.join(line.split(' ')[1:])
            seq += '\n'

            if buffer_origin > 2000000:
                self.exit_parse('failed to parse ORIGIN information')


    def genes(self, seq):
        complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
        if self.proteins[0][0] == '':
            self.proteins = self.proteins[1:]

        for entry in self.proteins:
            prot,product,locs = entry
            start,stop,orient = locs

            gene = seq[start-1:stop]
            
            if orient == '-':
                gene = ''.join([complement.get(base, 'X') for base in gene[::-1]])
            
            gene = '\n'.join([gene[i:i+60] for i in range(0,len(gene),60)])
            self.ffn_handle.write(f'>{prot} | {product}\n{gene}\n')
            self.gff_handle.write(f'{self.genome}\t.\tCDS\t{start}\t{stop}\t.\t.\t{orient}\t{prot}; {product}\n')
    
    def tRNAs(self, seq):
        complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
        try:
            if self.trna[0][0] == '':
                self.trna = self.trna[1:]
        except IndexError:
            pass

        if self.trna:
            for entry in self.trna:
                t,product,locs = entry
                start,stop,orient = locs

                rna = seq[start-1:stop]
                
                if orient == '-':
                    rna = ''.join([complement.get(base, 'X') for base in rna[::-1]])
                
                rna = '\n'.join([rna[i:i+60] for i in range(0,len(rna),60)])
                self.trna_handle.write(f'>{t} | {product}\n{rna}\n')
                self.gff_handle.write(f'{self.genome}\t.\ttRNA\t{start}\t{stop}\t.\t.\t{orient}\t{t}; {product}\n')
 
    def rRNAs(self, seq):
        complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
        try:
            if self.rrna[0][0] == '':
                self.rrna = self.rrna[1:]
        except IndexError:
            pass

        if self.rrna:
            for entry in self.rrna:
                r,product,locs = entry
                start,stop,orient = locs

                rna = seq[start-1:stop]
                
                if orient == '-':
                    rna = ''.join([complement.get(base, 'X') for base in rna[::-1]])
                
                rna = '\n'.join([rna[i:i+60] for i in range(0,len(rna),60)])
                self.rrna_handle.write(f'>{r} | {product}\n{rna}\n')
                self.gff_handle.write(f'{self.genome}\t.\trRNA\t{start}\t{stop}\t.\t.\t{orient}\t{r}; {product}\n')


if __name__ == '__main__':

    descript = """
    Convert file formats: GenBank -> Fasta

    Usage:
    genbank_to_fasta.py genbank.gb [output_folder]
"""
    parser = argparse.ArgumentParser(description=descript, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('genbank', type=str, nargs=1, help='genbank file')
    parser.add_argument('folder', type=str, nargs='*', default=[''], help='output folder (optional)')
    #
    #
    Convert(parser.parse_args())

#
#
#
