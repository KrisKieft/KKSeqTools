#! /usr/bin/env python3
# Author: Kristopher Kieft
# University of Wisconsin-Madison

import subprocess
import os
import pandas as pd
from collections import Counter

class CombineClean:
    def __init__(self, folder, base, aux, form):
        self.folder = folder
        self.base = base
        self.aux = aux

        self.combine_annotations()
        self.summarize_AMGs()
        if form == 'nucl':
            self.combine_prodigal()
        self.combine_hmms()
        self.cleanup()


    def summarize_AMGs(self):
        with open(f'{self.aux}VIBRANT_names.tsv') as f:
            items = f.read().replace('\n', '\t').split('\t')
            names = {items[i]:items[i+1] for i in range(0,len(items),2) if items[i][0] == 'K'}
        

        pathways = {}
        with open(f'{self.aux}VIBRANT_KEGG_pathways_summary.tsv') as f:
            items = f.read().split('\n')
            for item in items:
                entry,meta,path,kos = item.split('\t')
                kos = kos.split('~')
                for k in kos:
                    pathways.setdefault(k, []).append((entry,meta,path))
            pathways.pop('', None)

        df = pd.read_table(f'{self.folder}annotations/VIBRANT_AMG_individuals_{self.base}.tsv')
        ko = df['KO'].tolist()
        counts = list(Counter(ko).items())
        counts.sort(key=lambda x: x[1], reverse=True)

        with open(f'{self.folder}annotations/VIBRANT_AMG_counts_{self.base}.tsv', 'w') as amgcounts, open(f'{self.folder}annotations/VIBRANT_AMG_pathways_{self.base}.tsv', 'w') as amgpaths:
            amgcounts.write('AMG count\tAMG KO\tAMG KO name\n')
            amgpaths.write('KEGG Entry\tMetabolism\tPathway\tTotal AMGs\tAMG KO\n')
            for item in counts:
                val,count = item
                name = names.get(val, 'hypothetical protein')
                paths = pathways.get(val, [(None,None,None)])
                amgcounts.write(f'{count}\t{val}\t{name}\n')
                for p in paths:
                    amgpaths.write(f'{p[0]}\t{p[1]}\t{p[2]}\t{count}\t{val}\n')

    def combine_annotations(self):
        os.mkdir(f'{self.folder}annotations/')
        files = os.listdir(f'{self.folder}annotations_temp/')
        amgs = ' '.join([f'{self.folder}annotations_temp/{f}' for f in files if f[1:] == '.amgs.tsv'])
        best = ' '.join([f'{self.folder}annotations_temp/{f}' for f in files if f[1:] == '.best.tsv'])
        full = ' '.join([f'{self.folder}annotations_temp/{f}' for f in files if f[1:] == '.full.tsv'])

        with open(f'{self.folder}annotations/VIBRANT_full_annotations_{self.base}.tsv', 'w') as f:
            f.write('protein\tscaffold\tKO\tAMG\tKO name\tKO evalue\tKO score\tKO v-score\tPfam\tPfam name\tPfam evalue\tPfam score\tPfam v-score\tVOG\tVOG name\tVOG evalue\tVOG score\tVOG v-score\n')
        with open(f'{self.folder}annotations/VIBRANT_best_annotations_{self.base}.tsv', 'w') as f:
            f.write('protein\tscaffold\taccession\tname\tevalue\tscore\n')
        with open(f'{self.folder}annotations/VIBRANT_AMG_individuals_{self.base}.tsv', 'w') as f:
            f.write('protein\tscaffold\tKO\tKO name\tevalue\tscore\n')
        
        s1 = subprocess.Popen(f'cat {full} >> {self.folder}annotations/VIBRANT_full_annotations_{self.base}.tsv 2> /dev/null', shell=True)
        s2 = subprocess.Popen(f'cat {best} >> {self.folder}annotations/VIBRANT_best_annotations_{self.base}.tsv 2> /dev/null', shell=True)
        s3 = subprocess.Popen(f'cat {amgs} >> {self.folder}annotations/VIBRANT_AMG_individuals_{self.base}.tsv 2> /dev/null', shell=True)
        s1.wait()
        s2.wait()
        s3.wait()

    def combine_prodigal(self):
        os.mkdir(f'{self.folder}prodigal_results/')
        files = os.listdir(f'{self.folder}split_files/')
        faa = ' '.join([f'{self.folder}split_files/{f}' for f in files if f[-4:] == '.faa'])
        ffn = ' '.join([f'{self.folder}split_files/{f}' for f in files if f[-4:] == '.ffn'])
        gff = ' '.join([f'{self.folder}split_files/{f}' for f in files if f[-4:] == '.gff'])
        

        s1 = subprocess.Popen(f'cat {faa} | sed "s/\$\~\&/ /g" > {self.folder}prodigal_results/{self.base}.prodigal.faa 2> /dev/null', shell=True)
        s2 = subprocess.Popen(f'cat {ffn} | sed "s/\$\~\&/ /g" > {self.folder}prodigal_results/{self.base}.prodigal.ffn 2> /dev/null', shell=True)
        s3 = subprocess.Popen(f'cat {gff} | sed "s/\$\~\&/ /g" > {self.folder}prodigal_results/{self.base}.prodigal.gff 2> /dev/null', shell=True)
        s1.wait()
        s2.wait()
        s3.wait()

    def combine_hmms(self):
        os.mkdir(f'{self.folder}full_hmmsearch_results/')
        files = os.listdir(f'{self.folder}raw_hmm_results/')
        kegg = ' '.join([f'{self.folder}raw_hmm_results/{f}' for f in files if f[1:] == '.KEGG.hmmtbl'])
        pfam = ' '.join([f'{self.folder}raw_hmm_results/{f}' for f in files if f[1:] == '.Pfam.hmmtbl'])
        vog = ' '.join([f'{self.folder}raw_hmm_results/{f}' for f in files if f[1:] == '.VOG.hmmtbl'])

        with open(f'{self.folder}full_hmmsearch_results/{self.base}.KEGG.hmmtbl', 'w') as f:
            f.write('protein\taccession\tevalue\tscore\n')
        with open(f'{self.folder}full_hmmsearch_results/{self.base}.Pfam.hmmtbl', 'w') as f:
            f.write('protein\taccession\tevalue\tscore\n')
        with open(f'{self.folder}full_hmmsearch_results/{self.base}.VOG.hmmtbl', 'w') as f:
            f.write('protein\taccession\tevalue\tscore\n')

        s1 = subprocess.Popen(f'cat {kegg} | sed "s/\$\~\&/ /g" >> {self.folder}full_hmmsearch_results/{self.base}.KEGG.hmmtbl 2> /dev/null', shell=True)
        s2 = subprocess.Popen(f'cat {pfam} | sed "s/\$\~\&/ /g" >> {self.folder}full_hmmsearch_results/{self.base}.Pfam.hmmtbl 2> /dev/null', shell=True)
        s3 = subprocess.Popen(f'cat {vog} | sed "s/\$\~\&/ /g" >> {self.folder}full_hmmsearch_results/{self.base}.VOG.hmmtbl 2> /dev/null', shell=True)
        s1.wait()
        s2.wait()
        s3.wait()

    def cleanup(self):
        s1 = subprocess.Popen(f'rm -R {self.folder}split_files/ 2> /dev/null', shell=True)
        s2 = subprocess.Popen(f'rm -R {self.folder}annotations_temp/ 2> /dev/null', shell=True)
        s3 = subprocess.Popen(f'rm -R {self.folder}parsed_hmm_results/ 2> /dev/null', shell=True)
        s4 = subprocess.Popen(f'rm -R {self.folder}raw_hmm_results/ 2> /dev/null', shell=True)
        s1.wait()
        s2.wait()
        s3.wait()
        s4.wait()