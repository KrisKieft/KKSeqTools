#! /usr/bin/env python3
# Author: Kristopher Kieft
# University of Wisconsin-Madison

import os
import subprocess


def prodigal(folder):
    files = os.listdir(f'{folder}split_files')
    files = [f'{folder}split_files/{f}' for f in files]
   
    holder = []
    for f in files:
        base = f.rsplit('.',1)[0]
        faa = base + '.faa'
        ffn = base + '.ffn'
        gff = base + '.gff'
        s = subprocess.Popen(f'prodigal -m -p meta -f gff -q -i {f} -a {faa} -d {ffn} -o {gff}', shell=True)
        holder.append(s)
    for h in holder:
        h.wait()
