__author__ = 'Roger'
__description__ = """
    This module parses the TI special bin csv files.
    """

import time
_start_time = time.time()
import csv
import argparse
import sys
from common import *
from pprint import pprint

def parse_special_csv(pathfn,type=None):

    with open(pathfn) as csvFile:

        path, fn = os.path.split(pathfn)

        for line in csv.DictReader(csvFile):
            print line['SW Bin Number']

        sys.exit()

        limit_data = {}
        modes = []

        # for row in row_data:
        #     if row[0] == 'Test mode':
        #         # this row is reserved for mode settings
        #         modes = row
        #     else:
        #         row_key, row_key_indices = get_row_key(row_key_names,row,headers)
        #         if row_key not in limit_data:
        #             limit_data[row_key] = {}
        #         # iterate over columns
        #         for i,cell in enumerate(row):
        #             if headers[i] in REPEATABLE_HEADERS and len(modes):
        #                 header = (headers[i], modes[i])
        #             else:
        #                 header = headers[i]
        #             if header not in limit_data[row_key]:
        #                 limit_data[row_key][header] = []
        #             limit_data[row_key][header].append(cell)
    return limit_data

def main():
    parser = argparse.ArgumentParser(description="Description: "+__description__)
    parser.add_argument('-c','--binCatsFile',required=True, help='name of binning categories csv file')
    parser.add_argument('-g','--binGrpsFile',required=True, help='name of binning groups csv file')
    parser.add_argument('-i','--binInsFile',required=True, help='name of binning insertions csv file')
    args = parser.parse_args()

    parse_special_csv(args.binCatsFile,'categories')
    parse_special_csv(args.binGrpsFile,'groups')
    parse_special_csv(args.binInsFile,'insertions')

if __name__ == "__main__":
    main()
    time = time.time()-_start_time
    print '\nScript took',round(time,3),'seconds','('+humanize_time(time)+')'
