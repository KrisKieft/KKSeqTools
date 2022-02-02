#! /usr/bin/env python3
# Author: Kristopher Kieft
# University of Wisconsin-Madison

import argparse
import os


def split_hmms(infile, folder, prefix):
    buffer = []
    with open(infile) as f:
        name = 'FAILED'
        for line in f:
            if line[:3] == prefix or line[:4] == prefix:
                name = line.strip('\n').split(' ')[-1]
            elif line[:2] == '//':
                with open(f'{folder}{name}.hmm', 'w') as out:
                    for b in buffer:
                        out.write(b)
                    out.write('//')
                buffer = []
            else:
                buffer.append(line)



if __name__ == '__main__':

    descript = """
    Take in a large HMM file and split into individual files, 1 HMM per file. 
"""
    parser = argparse.ArgumentParser(description=descript, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', metavar='', type=str, nargs=1, required=True, help="input HMM file")
    parser.add_argument('-o', metavar='', type=str, nargs=1, required=True, help='output folder')
    parser.add_argument('-n', choices=['NAME', 'ACC'], default=['ACC'], help='prefix of output files [choices: NAME or ACC, default: ACC]')
    #
    args = parser.parse_args()
    infile = args.i[0]
    folder = args.o[0]
    if folder[-1] != '/':
        folder += '/'
    prefix = args.n[0].upper()
    #
    #
    if os.path.exists(folder):
        print("\nError: The output folder already exists. Exiting.\n\n")
        exit()
    os.mkdir(folder)

    split_hmms(infile, folder, prefix)