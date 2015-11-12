#!/usr/bin/env python
"""
    This module parses the bin csv files.
"""

import time
_start_time = time.time()
import csv
import argparse
import sys
from common import *
from pprint import pprint

__author__ = 'Roger'

# these were taken from TDC Topic: 112490 (SMT 7.3.3)
VALID_BIN_HEADERS = ['Limit key', 'Suite name', 'Test name', 'Pins', 'Test number',
                     'Units', 'Lsl', 'Lsl_typ', 'Usl_typ', 'Usl', 'Offset',
                     'Bin_s_num', 'Bin_s_name', 'Bin_h_num', 'Bin_h_name', 'Bin_type',
                     'Bin_reprobe', 'Bin_overon', 'Test_remarks', 'Exec']

REPEATABLE_HEADERS = ['Units', 'Lsl', 'Lsl_typ', 'Usl_typ', 'Usl', 'Offset']

# in order of precedence
POSSIBLE_ROW_KEYS = [('Suite name', 'Test name', 'Pins'),
                     ('Suite name', 'Test name'),
                     ('Limit key', 'Pins'),
                     ('Limit key')]


def get_row_key_names(fieldnames):
    row_key = []
    for key in POSSIBLE_ROW_KEYS:
        row_key = tuple([x for x in key if x in fieldnames])
        if len(row_key):
            return row_key
    return None

def get_row_key(row_key_names,row,headers):
    row_key_list = []
    row_key_indices = []
    for i,h in enumerate(headers):
        if h in row_key_names:
            row_key_list.append(row[i])
            row_key_indices.append(i)
    return tuple(row_key_list),tuple(row_key_indices)


def read_tm_limits(pathfn):

    with open(pathfn) as csvFile:

        path, fn = os.path.split(pathfn)

        csvDict = csv.DictReader(csvFile)
        headers = csvDict.fieldnames
        unknown_headers = [x for x in headers if x not in VALID_BIN_HEADERS]
        if len(unknown_headers):
            print fn, color.BOLD+color.RED+" is not a bin file! Skipping due to UNKNOWN headers: "+color.END,
            print ",".join(unknown_headers)
            return

        row_key_names = get_row_key_names(headers)
        if row_key_names is None:
            print fn, color.BOLD+color.RED+" is not a bin file! Skipping due to MISSING KEY(s) headers (must have one of these combinations): "+color.END,
            print POSSIBLE_ROW_KEYS
            return

        # using csv.reader() for slice indexing
        row_data = csv.reader(csvFile)

        limit_data = {}
        modes = []

        for row in row_data:
            if row[0] == 'Test mode':
                # this row is reserved for mode settings
                modes = row
            else:
                row_key, row_key_indices = get_row_key(row_key_names,row,headers)
                if row_key not in limit_data:
                    limit_data[row_key] = {}
                # iterate over columns
                for i,cell in enumerate(row):
                    if headers[i] in REPEATABLE_HEADERS and len(modes):
                        header = (headers[i], modes[i])
                    else:
                        header = headers[i]
                    if header not in limit_data[row_key]:
                        limit_data[row_key][header] = []
                    limit_data[row_key][header].append(cell)
    return limit_data


def main():
    parser = argparse.ArgumentParser(description="Description: "+sys.modules[__name__].__doc__)
    parser.add_argument("files", nargs='*', help="Limit files to be analyzed (*.csv)")
    args = parser.parse_args()

    if not len(args.files):
        sys.exit("ERROR !!! No limit files given! Aborting ...")

    args.files,numfiles = get_files(args.files)

    for pathfn in args.files:
        dump = read_tm_limits(pathfn)
        pprint(dump)
        sys.exit()

if __name__ == "__main__":
    main()
    time = time.time()-_start_time
    print '\nScript took',round(time,3),'seconds','('+humanize_time(time)+')'
