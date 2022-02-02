#! /usr/bin/env python3
# Author: Kristopher Kieft
# University of Wisconsin-Madison


import os
import subprocess


class HMMsearch:

    def __init__(self, folder, db, score):
        self.folder = folder
        self.results = f'{self.folder}raw_hmm_results/'
        os.mkdir(self.results)
        self.db = db
        self.score = score
        self.files = os.listdir(f'{self.folder}split_files/')
        self.files = [f'{self.folder}split_files/{f}' for f in self.files if f[-4:] == '.faa']
        
        self.kegg()
        self.pfam()
        self.vog()
    
    def kegg(self):
        holder = []
        for f in self.files:
            base = f.rsplit('.',1)[0].rsplit('/',1)[1]
            out = f'{self.results}{base}.KEGG.temp'
            hmm = f'{self.db}KEGG_profiles_prokaryotes.HMM'
            s = subprocess.Popen(f'hmmsearch --tblout {out} -T {self.score} --cpu 1 --noali {hmm} {f} > /dev/null', shell=True)
            holder.append(s)
        for h in holder:
            h.wait()
    
    def pfam(self):
        holder = []
        for f in self.files:
            base = f.rsplit('.',1)[0].rsplit('/',1)[1]
            out = f'{self.results}{base}.Pfam.temp'
            hmm = f'{self.db}Pfam-A_v32.HMM'
            s = subprocess.Popen(f'hmmsearch --tblout {out} -T {self.score} --cpu 1 --noali {hmm} {f} > /dev/null', shell=True)
            holder.append(s)
        for h in holder:
            h.wait()
    
    def vog(self):
        holder = []
        for f in self.files:
            base = f.rsplit('.',1)[0].rsplit('/',1)[1]
            out = f'{self.results}{base}.VOG.temp'
            hmm = f'{self.db}VOGDB94_phage.HMM'
            s = subprocess.Popen(f'hmmsearch --tblout {out} -T {self.score} --cpu 1 --noali {hmm} {f} > /dev/null', shell=True)
            holder.append(s)
        for h in holder:
            h.wait()