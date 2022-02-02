#! /usr/bin/env python3
# Author: Kristopher Kieft
# University of Wisconsin-Madison

# annoVIBRANT v1.0.0
# Auxiliary function for VIBRANT
# Virus Identification By iteRative ANnoTation

# import warnings
# warnings.filterwarnings("ignore")
import os
import sys
import time
import argparse
import subprocess
from datetime import datetime,date
from scripts import hmm_run
from scripts import split_prot
from scripts import split_nucl
from scripts import run_prodigal
from scripts import combine_clean

def check_folder(folder):
    if os.path.exists(folder):
        print(f'\nOutput folder {folder} exists! Exiting.\n')
        exit()

def check_format(check, form):
    if not check:
        print(f'Input fasta does not appear to be in the correct "{form}" format! Exiting.')
        exit()

def check_dependents(db, aux, form):
    failed = False
    if not db:
        try:
            db = os.environ['VIBRANTDB']
        except KeyError:
            print(f'\nSpecify HMM database folder with -d or set the VIBRANTDB env. Exiting.')
            print(f"Example: export VIBRANTDB='enter_path_here/VIBRANT_v1.2.1/databases/'\n")
            exit()
    if db[-1] != '/':
        db += '/'
    if not os.path.exists(db + 'KEGG_profiles_prokaryotes.HMM.h3f'):
        print("Error: could not identify KEGG HMM files in database directory. Please set up HMMs.")
        failed = True
    if not os.path.exists(db + 'Pfam-A_v32.HMM.h3f'):
        print("Error: could not identify Pfam HMM files in database directory. Please set up HMMs.")
        failed = True
    if not os.path.exists(db + 'VOGDB94_phage.HMM.h3f'):
        print("Error: could not identify VOG HMM files in database directory. Please set up HMMs.")
        failed = True
    #
    if not aux:
        try:
            aux = os.environ['VIBRANTAUX']
        except KeyError:
            print(f'\nSpecify auxiliary files folder with -m or set the VIBRANTAUX env. Exiting.')
            print(f"Example: export VIBRANTAUX='enter_path_here/VIBRANT_v1.2.1/files/'\n")
            exit()
    if aux[-1] != '/':
        aux += '/'
    if not os.path.exists(aux + 'VIBRANT_categories.tsv'):
        print("Error: could not identify VIBRANT_categories.tsv in files directory.")
        failed = True
    if not os.path.exists(aux + 'VIBRANT_AMGs.tsv'):
        print("Error: could not identify VIBRANT_AMGs.tsv in files directory.")
        failed = True
    if not os.path.exists(aux + 'VIBRANT_names.tsv'):
        print("Error: could not identify VIBRANT_names.tsv in files directory.")
        failed = True
    #
    try:
        subprocess.check_output("which hmmsearch", shell=True)
    except Exception:
        print("\nError: hmmsearch cannot be found. Please install HMMER.")
        failed = True
    if form == 'nucl':
        try:
            subprocess.check_output("which prodigal", shell=True)
        except Exception:
            print("\nError: prodigal cannot be found. Please install prodigal. Exiting.\n")
            failed = True
    #
    if failed:
        print("Exiting.\n")
        exit()
    return db, aux

def hmm_parse_threader(folder):
    os.mkdir(f'{folder}parsed_hmm_results/')
    files = os.listdir(f'{folder}split_files/')
    files = [f[0] for f in files if f[-4:] == '.faa']

    holder = []
    for f in files:
        s = subprocess.Popen(f'./scripts/hmm_parse.py {f} {folder}', shell=True)
        holder.append(s)
    for h in holder:
        h.wait()

def annotations_threader(folder, aux, form):
    os.mkdir(f'{folder}annotations_temp/')
    files = os.listdir(f'{folder}split_files/')
    files = [f[0] for f in files if f[-4:] == '.faa']

    holder = []
    for f in files:
        s = subprocess.Popen(f'./scripts/annotations.py {f} {folder} {aux} {form}', shell=True)
        holder.append(s)
    for h in holder:
        h.wait()

def logit(folder, hold_time, start_time, date_today, program):
    runtime = round((time.time()-hold_time)/60,2)
    end_time = datetime.now().strftime("%H:%M")
    with open(f'{folder}info.log', 'w') as f:
        cmd = ' '.join(sys.argv)
        f.write(f'Command:   {cmd}\n')
        f.write(f'Date:      {date_today} (M/D/Y)\n')
        f.write(f'Start:     {start_time}\n')
        f.write(f'End:       {end_time}\n')
        f.write(f'Runtime:   {runtime} minutes\n')
        f.write(f'Program:   {program}\n')

if __name__ == '__main__':
    program = 'annoVIBRANT v1.0.0'
    hold_time = time.time()
    start_time = datetime.now().strftime("%H:%M")
    date_today = date.today().strftime("%m/%d/%y")

    descript = f"""
    {program}

    Run the annotation pipeline of VIBRANT: KEGG, Pfam, VOG
    Does not:
        filter by sequence length or number of proteins
        predict viruses
        excise proviruses
        identify circular sequences
        estimate virus genome quality

    Setup:
    1) Ensure VIBRANT databases are setup
        VIBRANT_setup.py in the main VIBRANT package
        source: https://github.com/AnantharamanLab/VIBRANT
    2) set VIBRANTDB environment or use -d
        example: export VIBRANTDB='enter_path_here/VIBRANT_v1.2.1/databases/'
    3) set VIBRANTAUX environment or use -m
        example: export VIBRANTAUX='enter_path_here/VIBRANT_v1.2.1/files/'

    Usage Example:
    annoVIBRANT.py -i fasta -o folder -t threads

"""
    vibrant = argparse.ArgumentParser(description=descript, formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
    vibrant.add_argument('--version', action='version', version=f'{program}')
    vibrant.add_argument('-i', type=str, nargs=1, required=True, help='input virus scaffolds/genomes or virus proteins')
    vibrant.add_argument('-f', type=str, nargs=1, default=['nucl'], choices=["nucl", "prot"], help='format of input [nucl]')
    vibrant.add_argument('-o', type=str, nargs=1, default=[''], help="output folder")
    vibrant.add_argument('-t', type=str, nargs=1, default=['1'], help='threads [1]')
    vibrant.add_argument('-s', type=str, nargs=1, default=['40'], help='score threshold for hmmsearch [40]')
    vibrant.add_argument('-d', type=str, nargs=1, default=[''], help='specify HMM database folder or set VIBRANTDB env')
    vibrant.add_argument('-m', type=str, nargs=1, default=[''], help='specify auxiliary files folder or set VIBRANTAUX env')
    #
    args = vibrant.parse_args()
    infile = args.i[0]
    try:
        temp = infile.rsplit('/',1)[1]
        base = temp.rsplit('.',1)[0]
    except IndexError:
        base = infile.rsplit('.',1)[0]
    form = args.f[0]
    score = args.s[0]
    folder = args.o[0]
    if not folder:
        folder = f'annoVIBRANT_results_{base}/'
    if folder[-1] != '/':
        folder += '/'
    threads = int(args.t[0])
    if threads < 1:
        print(f'\nThreads must be at least 1. Exiting.\n')
        exit()
    db = args.d[0]
    aux = args.m[0]
    #
    db, aux = check_dependents(db, aux, form)
    check_folder(folder)
    os.mkdir(folder)
    #
    if form == 'nucl':
        check = split_nucl.SplitNucl(infile, folder, threads)
        check_format(check.check, form)
        run_prodigal.prodigal(folder)
    elif form == 'prot':
        check = split_prot.SplitProt(infile, folder, threads)
        check_format(check.check, form)
    
    #
    hmm_run.HMMsearch(folder, db, score)
    hmm_parse_threader(folder)
    annotations_threader(folder, aux, form)
    #
    combine_clean.CombineClean(folder, base, aux, form)
    #
    logit(folder, hold_time, start_time, date_today, program)

