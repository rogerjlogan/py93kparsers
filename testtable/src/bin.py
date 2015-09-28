__author__ = 'Roger'
__description__ = """
    This module parses the bin csv files.
    """

import time
_start_time = time.time()
import csv
import argparse
import sys
from common import *
from pprint import pprint


# these were taken from TDC Topic: 112490 (SMT 7.3.3)
BIN_HEADERS =  ['Limit key'         ,\
                'Suite name'        ,\
                'Test name'         ,\
                'Pins'              ,\
                'Test number'       ,\
                'Units'             ,\
                'Lsl'               ,\
                'Lsl_typ'           ,\
                'Usl_typ'           ,\
                'Usl'               ,\
                'Offset'            ,\
                'Bin_s_num'         ,\
                'Bin_s_name'        ,\
                'Bin_h_num'         ,\
                'Bin_h_name'        ,\
                'Bin_type'          ,\
                'Bin_reprobe'       ,\
                'Bin_overon'        ,\
                'Test_remarks'      ,\
                'Exec'              ]

def check_csv(pathfn):
    with open(pathfn) as csvFile:
        # pprint(csv.DictReader(csvFile,fieldnames=names))
        # sys.exit()
        this_csv = csv.DictReader(csvFile)
        headers = this_csv.fieldnames
        problems = len([x for x in headers if x not in BIN_HEADERS])
        if problems:
            print color.BOLD+color.RED+"Unknown headers in "+color.END, pathfn, color.BOLD+color.RED+" ... skipping ...."+color.END


        # for field in this_csv.fieldnames:
        #     if field not in BIN_HEADERS:
        #         print field
        # sys.exit()
        # for line in this_csv:
        #     print line
def main():
    parser = argparse.ArgumentParser(description="Description: "+__description__)
    parser.add_argument("files", nargs='*', help="Limit files to be analyzed (*.csv)")
    args = parser.parse_args()

    if not len(args.files):
        sys.exit("ERROR !!! No limit files given! Aborting ...")

    args.files,numfiles = get_files(args.files)

    for pathfn in args.files:
        check_csv(pathfn)

if __name__ == "__main__":
    main()
    time = time.time()-_start_time
    print '\nScript took',round(time,3),'seconds','('+humanize_time(time)+')'
