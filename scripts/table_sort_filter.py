#! /usr/bin/env python3
# Author: Kristopher Kieft
# University of Wisconsin-Madison
# 2022

import os
import argparse
import pandas as pd

class TableSortFilter:
    def __init__(self, args):
        self.i = args.i[0]
        self.o = args.o[0]
        self.d = args.d[0]
        self.filt = args.filt[0]
        self.maxx = args.max[0]
        self.minn = args.min[0]
        self.drop = args.drop[0]
        self.srt = args.sort[0]
        self.order = args.ord[0]

        self.setup()
        self.main()
    
    def setup(self):
        e = False
        if self.minn and self.maxx and self.minn >= self.maxx:
            print('Error: --min cannot be >= --max!\n')
            e = True
        if not self.o:
            self.o = f'{self.i.rsplit(".",1)[0]}.filtered.{self.d}'
        if os.path.exists(self.o):
            print('Error: output table (-o) already exists!')
            print(f'{self.o}\n')
            e = True
        if not os.path.exists(self.i):
            print('Error: input table (-i) does not exist!')
            e = True
        if not self.srt:
            self.srt = self.filt
        if not self.srt and not self.filt:
            print('Error: provide --sort and/or --filt!')
            e = True
        if e:
            exit()
        
    
    def main(self):
        df = pd.read_table(self.i)
        
        try:
            if self.order == 'des':
                df.sort_values(by=self.srt, ascending=False, inplace=True)
            elif self.order == 'asc':
                df.sort_values(by=self.srt, ascending=True, inplace=True)
            
            if self.filt:
                if isinstance(self.minn, float) and isinstance(self.maxx, float):
                    df = df[(df[self.filt] >= self.minn) & (df[self.filt] <= self.maxx)]
                elif isinstance(self.minn, float):
                    df = df[(df[self.filt] >= self.minn)]
                elif isinstance(self.maxx, float):
                    df = df[(df[self.filt] <= self.maxx)]

            if self.drop:
                df.drop_duplicates(subset=self.drop, keep='first', inplace=True)

            sep = {'csv': ',', 'tsv': '\t', 'ssv': ' '}
            df.to_csv(self.o, index=False, sep=sep[self.d])
        except KeyError as e:
            print('Error: column does not appear to be in the table!')
            print(f'KeyError: {e}')


def getArgs():
    descript = """

    Sort and/or filter a table by given column(s).
    read -> sort -> filter -> drop duplicates

    For columns with spaces, enter the name in quotes.
    Ord key: asc (ascending), des (descending), none (no sort)

    Example (sort and filter by score 50, keep first protein hit)
    -i table.tsv -o new.tsv --filt "KEGG score" --min 50 --drop protein

    Example (sort by evalue in ascending order, do not filter or drop duplicates)
    -i table.tsv --sort "evalue" --asc
"""

    parser = argparse.ArgumentParser(description=descript, formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
    parser.add_argument('-i', metavar='', type=str, nargs=1, required=True, help="input table")
    parser.add_argument('-o', metavar='', type=str, nargs=1, default=[''], help="output table")
    parser.add_argument('-d', type=str, nargs=1, choices=['tsv', 'csv', 'ssv'], default=['tsv'], help="table delimiter [tsv]")
    #
    parser.add_argument('--filt', metavar='', type=str, nargs=1, default=[''], help="column name to filter by [none]")
    parser.add_argument('--max', metavar='', type=float, nargs=1, default=[''], help="maximum value for filter [none]")
    parser.add_argument('--min', metavar='', type=float, nargs=1, default=[''], help="minimum value for filter [none]")
    #
    parser.add_argument('--drop', metavar='', type=str, nargs=1, default=[''], help="column name to drop duplicates by, keep first instance [none]")
    parser.add_argument('--sort', metavar='', type=str, nargs=1, default=[''], help="column name to sort by if different than filter")
    parser.add_argument('--ord', choices=['asc', 'des', 'none'], nargs=1, default=['des'], help="sort order [des]")
    #
    return parser.parse_args()


if __name__ == '__main__':
    TableSortFilter(getArgs())