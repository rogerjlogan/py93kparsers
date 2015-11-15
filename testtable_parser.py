#!/usr/bin/env python
"""
    This module parses the bin csv files.
"""

import re
import csv
import argparse
import logging as log
import sys
from common import *
from pprint import pformat
import time
from common import humanize_time,init_logging

_start_time = time.time()

from pprint import pprint

__author__ = 'Roger'

TESTTABLE_OPTFILE_HEADER = 'hp93000,testtable_master_file,0.1'

# these were taken from TDC Topic: 112490 (SMT 7.3.3)
VALID_LIM_HEADERS = ['Limit key', 'Suite name', 'Test name', 'Pins', 'Test number',
                     'Units', 'Lsl', 'Lsl_typ', 'Usl_typ', 'Usl', 'Offset',
                     'Bin_s_num', 'Bin_s_name', 'Bin_h_num', 'Bin_h_name', 'Bin_type',
                     'Bin_reprobe', 'Bin_overon', 'Test_remarks', 'Exec']

REPEATABLE_LIM_HEADERS = ['Units', 'Lsl', 'Lsl_typ', 'Usl_typ', 'Usl', 'Offset']

# in order of precedence
POSSIBLE_LIM_ROW_KEYS = [('Suite name', 'Test name', 'Pins'),
                         ('Suite name', 'Test name'),
                         ('Limit key', 'Pins'),
                         ('Limit key')]


def get_row_key_names(fieldnames):
    row_key = []
    for key in POSSIBLE_LIM_ROW_KEYS:
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


class TestTable(object):

    testtables = []
    special_testtables = []
    limit_data = {}

    def __init__(self,pathfn):
        self.path, self.fn = os.path.split(pathfn)
        log.info('Parsing testtable master file: '+self.fn+' .....')
        limPat = re.compile(r'^\s*testerfile\s*:(?P<limit_file>.*)')
        hdr_found = False
        for line in open(pathfn).readlines():
            if not hdr_found:
                if -1 != line.find(TESTTABLE_OPTFILE_HEADER):
                    hdr_found = True
            else:
                obj = re.search(limPat,line)
                if obj:
                    fn = os.path.join(self.path,obj.group('limit_file').strip())
                    self.parse_testtable(fn)
        if not hdr_found:
            err = 'ERROR!!! OptFileHeader ('+TESTTABLE_OPTFILE_HEADER+') not found'
            log.critical(err)
            sys.exit(err)

        # log first 5 elements
        # log.debug('Sample of TestTable().limit_data = '+pformat(self.limit_data[:5]))

    def parse_testtable(self,pathfn):

        with open(pathfn) as csvFile:

            stand_lim = True # init control var

            path, fn = os.path.split(pathfn)

            csvDict = csv.DictReader(csvFile)
            headers = csvDict.fieldnames

            unknown_headers = [x for x in headers if x not in VALID_LIM_HEADERS]
            """Collect unknown headers to see if this is a standard testtable or not"""

            if len(unknown_headers):
                stand_lim = False
                self.special_testtables.append(pathfn)

            row_key_names = get_row_key_names(headers)
            if row_key_names is None:
                stand_lim = False
                self.special_testtables.append(pathfn)

            if not stand_lim:
                return
            else:
                log.info('Parsing testtable standard file: '+fn+' .....')
                self.testtables.append(pathfn)

                if fn in self.limit_data:
                    log.fatal('Duplicate testtable found: '+fn)
                else:
                    self.limit_data[fn] = {}

                # using csv.reader() for slice indexing
                row_data = csv.reader(csvFile)

                modes = []

                for row in row_data:
                    if row[0] == 'Test mode':
                        # this row is reserved for mode settings
                        modes = row
                    else:
                        row_key, row_key_indices = get_row_key(row_key_names,row,headers)
                        if row_key not in self.limit_data[fn]:
                            self.limit_data[fn][row_key] = {}
                        # iterate over columns
                        for i,cell in enumerate(row):
                            if headers[i] in REPEATABLE_LIM_HEADERS and len(modes):
                                header = (headers[i], modes[i])
                            else:
                                header = headers[i]
                                self.limit_data[fn][row_key][header] = cell

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description: "+sys.modules[__name__].__doc__)
    parser.add_argument('-tt','--path_to_testtable_file',required=True, help='Path to testtable master file')
    parser.add_argument('-v','--verbose',action='store_true',help='print a lot of stuff')
    parser.add_argument('-out','--output_dir',required=False, help='Directory to place log file(s).')
    parser.add_argument('-max','--maxlogs',type=int,default=1,required=False, help='(0=no log created). Set to 1 to keep only one log (subsequent runs will overwrite).')
    args = parser.parse_args()

    init_logging(scriptname=os.path.split(sys.modules[__name__].__file__)[1],args=args)

    tt = TestTable(args.path_to_testtable_file)

    time = time.time()-_start_time
    msg = 'Script took ' + str(round(time,3)) + ' seconds (' + humanize_time(time) + ')'
    log.info(msg)
    print '\n' + msg
