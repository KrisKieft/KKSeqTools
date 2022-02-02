#! /usr/bin/env python3
# Author: Kristopher Kieft
# University of Wisconsin-Madison

import sys
from fasta_parse import fasta_parse


class Annotations:
    def __init__(self, base, folder, aux, form):
        self.base = base
        self.folder = folder
        self.aux = aux
        self.form = form

        self.get_lists()
        self.make_accnos()
        self.get_annos()
        self.write_annos()



    def get_lists(self):
        with open(f'{self.aux}VIBRANT_names.tsv') as f:
            items = f.read().replace('\n', '\t').split('\t')
            self.names = {items[i]:items[i+1] for i in range(0,len(items),2)}
            self.names.pop('', None)
        
        with open(f'{self.aux}VIBRANT_AMGs.tsv') as f:
            next(f)
            self.amgs = set(f.read().split('\n'))
            self.amgs.discard('')

        with open(f'{self.aux}VIBRANT_categories.tsv') as f:
            next(f)
            items = f.read().replace('\n', '\t').split('\t')
            self.cats = {items[i]:(float(items[i+1])/100) for i in range(0,len(items),2)}
            self.cats.pop('', None)
    
    def make_accnos(self):
        self.accnos_file = f'{self.folder}split_files/{self.base}.accnos'
        with open(self.accnos_file, 'w') as out:
            if self.form == 'nucl':
                for name,_ in fasta_parse(f'{self.folder}split_files/{self.base}.faa'):
                    name = name.split(' # ',1)[0]
                    out.write(f'{name}\n')
            else:
                for name,_ in fasta_parse(f'{self.folder}split_files/{self.base}.faa'):
                    out.write(f'{name}\n')
    
    
    def get_annos(self):
        self.annotations = {}
        with open(f'{self.folder}parsed_hmm_results/{self.base}.KEGG.tsv') as infile:
            next(infile)
            for line in infile:
                line = line.strip('\n').split('\t')
                data = (line[1], float(line[2]), float(line[3]))
                k = self.annotations.setdefault(line[0], [('', '', ''), ('', '', ''), ('', '', '')])
                k[0] = data
        
        with open(f'{self.folder}parsed_hmm_results/{self.base}.Pfam.tsv') as infile:
            next(infile)
            for line in infile:
                line = line.strip('\n').split('\t')
                data = (line[1], float(line[2]), float(line[3]))
                p = self.annotations.setdefault(line[0], [('', '', ''), ('', '', ''), ('', '', '')])
                p[1] = data
        
        with open(f'{self.folder}parsed_hmm_results/{self.base}.VOG.tsv') as infile:
            next(infile)
            for line in infile:
                line = line.strip('\n').split('\t')
                data = (line[1], float(line[2]), float(line[3]))
                v = self.annotations.setdefault(line[0], [('', '', ''), ('', '', ''), ('', '', '')])
                v[2] = data
    

    def write_annos(self):
        with open(self.accnos_file) as acc, open(f'{self.folder}annotations_temp/{self.base}.full.tsv', 'w') as full, open(f'{self.folder}annotations_temp/{self.base}.best.tsv', 'w') as best, open(f'{self.folder}annotations_temp/{self.base}.amgs.tsv', 'w') as metabolic:
            for prot in acc:
                amg = ''
                prot = prot.strip('\n')
                kegg, pfam, vog = self.annotations.get(prot, [('', '', ''), ('', '', ''), ('', '', '')])
                k0,k1,k2 = kegg
                p0,p1,p2 = pfam
                v0,v1,v2 = vog
                score = ('','','','')
                k_name,k_cat,p_name,p_cat,v_name,v_cat = '','','','','',''
                
                if k0:
                    k_name = self.names.get(k0, 'hypothetical protein')
                    k_cat = self.cats.get(k0, 0)
                    if k0 in self.amgs:
                        amg = 'AMG'
                    score = (k0,k1,k2,k_name)
                if p0:
                    p_name = self.names.get(p0, 'hypothetical protein')
                    p_cat = self.cats.get(p0, 0)
                    try:
                        if p2 >= score[2]:
                            score = (p0,p1,p2,p_name)
                    except TypeError:
                        score = (p0,p1,p2,p_name)
                if v0:
                    v_name = self.names.get(v0, 'hypothetical protein')
                    v_cat = self.cats.get(v0, 0)
                    try:
                        if v2 >= score[2]:
                            score = (v0,v1,v2,v_name)
                    except TypeError:
                        score = (v0,v1,v2,v_name)

                prot = prot.replace('$~&', ' ')
                scaffold = prot.rsplit('_',1)[0]
                full.write(f'{prot}\t{scaffold}\t{k0}\t{amg}\t{k_name}\t{k1}\t{k2}\t{k_cat}\t{p0}\t{p_name}\t{p1}\t{p2}\t{p_cat}\t{v0}\t{v_name}\t{v1}\t{v2}\t{v_cat}\n')

                s0,s1,s2,s_name = score
                best.write(f'{prot}\t{scaffold}\t{s0}\t{s_name}\t{s1}\t{s2}\n')

                if amg:
                    metabolic.write(f'{prot}\t{scaffold}\t{k0}\t{k_name}\t{k1}\t{k2}\n')
    

if __name__ == '__main__':
    Annotations(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])