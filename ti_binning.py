#!/usr/bin/env python
"""
    This module parses the TI special bin csv files.
"""

import csv
import re
import argparse
import sys
from common import *
from pprint import pprint
from TestflowParser import Testflow
from testtable_parser import VALID_LIM_HEADERS
import time
_start_time = time.time()

__author__ = 'Roger'
__verbose__ = True

# global constants below here in CAPS

BINNING_CONDITION = 1
"""Index for Condition field in Binning Categories (CSV) file"""

BINNING_FIRST_TESTNAME = 2
"""Starting Index for Testname fields in Binning Categories (CSV) file"""

BINNING_GROUP_TESTNAME = 0
"""Index for Condition field in Binning Groups (CSV) file"""

SPEED_SORT_GROUP_TESTNAME = 4
"""Index for Condition field in Speed Sort Groups (CSV) file"""

SBIN_NUM_COLUMN_NAME = 'SW Bin Number'

CONDITION_COLUMN_NAME = 'Condition'

TESTSUITE_COLUMN_NAME = 'Test name'

CATEGORY_VALID_AND = ['S_ALL','AND']

CATEGORY_VALID_OR = ['S_ANY','OR']

MEMORYREPAIRED = 'MEMORYREPAIRED'
"""Defined like this in case the name of this virtual test ever changes"""

# control variables below here (boolean)

bin_groups_exist = False
bin_groups_done = False
speed_sort_groups_done = False
test_name_type_done = False

# data collection variables below here

bin_groups = {}
"""list of dict() with group names as keys and values are lists of testsuites for that group name"""

speed_sort_groups = []
"""list of virtual test names used for binning categories"""

test_name_type = {}
"""2-D dict() of 'Test name'(primary key), TITESTTYPE(secondary key), and flag(value) 1=expect, 0=don't expect"""

category_defs = []
"""Ordered list of category definitions"""

category_tests = {}

categories_extra_tests = []

testflow_extra_tests = []

testflow = None
"""Parsed Testflow object"""

def get_testflow(pathfn):
    global testflow
    testflow = Testflow(pathfn)
    if __verbose__:
        print sys.modules[testflow.__module__].__doc__

def get_category_testname(test, sbin):
    global category_tests

    if test[0] == '+':
        good = True
    elif test[0] == '-':
        good = False
    else:
        err = '\nERROR!!! Unknown polarity in categories!\n'
        err += 'Test: ' + test + '\n'
        err += 'sbin: ' + sbin + '\n'
        err += 'Exiting ...\n'
        sys.exit(err)

    if '!' in test:
        ignore = True
        test = test[2:]
    else:
        ignore = False
        test = test[1:]

    if test not in category_tests:
        category_tests[test] = {}
    if sbin in category_tests[test]:
        err = '\nERROR!!! Duplicate test/bin combination in Binning Categories!\n'
        err += 'Test: ' + test + '\n'
        err += 'sbin: ' + sbin + '\n'
        err += 'Exiting ...\n'
        sys.exit(err)
    category_tests[test][sbin] = {
        'good' : good,
        'ignore' : ignore
    }
    return test

def parse_special_csv(pathfn, csv_type=None):
    global bin_groups_done,speed_sort_groups_done,test_name_type_done
    global bin_groups,category_defs,categories_extra_tests,testflow_extra_tests

    # we gotta make sure we parse speed/bin groups and insertions first before categories
    if csv_type == 'categories':
        if (bin_groups_exist and not bin_groups_done) or not speed_sort_groups_done or not test_name_type_done:
            print 'bin_groups_exist:',bin_groups_exist,'bin_groups_done:',bin_groups_done
            print 'speed_sort_groups_done:',speed_sort_groups_done,'test_name_type_done:',test_name_type_done
            sys.exit('ERROR! Need to process Binning Groups(if exists), Speed Sort Groups, and Test Name Types *BEFORE* processing Categories!  Exiting ...')

    with open(pathfn) as csvFile:
        tp_path, fn = os.path.split(pathfn)
        print 'Parsing '+fn+' .....'

        # no error yet, just preparing for the worst (is that a glass half empty thing?)
        err = '\nERROR!!! Houston, we have a problem!\n'

        if csv_type == 'bin_groups':
            # using csv.reader() for slice indexing
            for i,row in enumerate(csv.reader(csvFile)):
                if 0 == i or '#' == row[0][0] : continue # skip header row or if row starts with '#'
                bin_groups[row[BINNING_GROUP_TESTNAME]] = [x for x in row[BINNING_GROUP_TESTNAME+1:] if len(x.strip())]
            bin_groups_done = True

        elif csv_type == 'speed_sort_groups':
            # using csv.reader() for slice indexing
            for i,row in enumerate(csv.reader(csvFile)):
                if 0 == i or '#' == row[i][0] : continue # skip header row or if row starts with '#'
                speed_sort_groups.append(row[SPEED_SORT_GROUP_TESTNAME])
            speed_sort_groups_done = True

        elif csv_type == 'test_name_type':
            # using csv.DictReader() for key indexing
            for row in csv.DictReader(csvFile):
                test_name_type[row[TESTSUITE_COLUMN_NAME]] = {x:row[x] for x in row.keys() if x not in VALID_LIM_HEADERS}
            test_name_type_done = True

        elif csv_type == 'categories':
            # using csv.DictReader() for key indexing
            for row in csv.DictReader(csvFile):
                sbin = row[SBIN_NUM_COLUMN_NAME]
                if row[CONDITION_COLUMN_NAME] in CATEGORY_VALID_AND:
                    condition = 'and'
                else: # row[CONDITION_COLUMN_NAME] in CATEGORY_VALID_OR:
                    condition = 'or'
                category_defs.append(
                    {
                        'sbin' : sbin,
                        'condition' : condition,
                        'tests' : [get_category_testname(row[x], sbin) for x in row.keys()
                                   if len(row[x]) and x not in [SBIN_NUM_COLUMN_NAME, CONDITION_COLUMN_NAME]]
                    }
                )
            # calculate set differences (exclude MEMORYREPAIRED which is a virtual test
            categories_extra_tests = set(category_tests.keys() + [MEMORYREPAIRED]) -\
                                     set(testflow.testsuite_data.keys() + bin_groups.keys())
            testflow_extra_tests = set(testflow.testsuite_data.keys()) - set(category_tests.keys())

            if len(categories_extra_tests):
                print '\n'+'='*80+'\nWARNING!!! Extra tests in Binning Categories that do not exist in Testflow or Binning Groups!'
                if __verbose__:
                    pprint(categories_extra_tests)
            if len(testflow_extra_tests):
                print '\n'+'='*80+'\nWARNING!!! Extra tests in Testflow that do not exist in Binning Categories!'
                if __verbose__:
                    pprint(testflow_extra_tests)

            sys.exit()

        else:
            err += 'Unknown csv_type found!\n'
            err += 'File: '+fn+'\n'
            err += 'csv_type: '+csv_type+'\n'
            err += 'valid csv_types: '+csv_type+'\n'
            err += 'Exiting ...'
            sys.exit(err)

def main():
    global __verbose__,bin_groups_exist
    parser = argparse.ArgumentParser(description="Description: "+sys.modules[__name__].__doc__)
    parser.add_argument('-f','--testflow_file',required=False, help='name of testflow file (Example: Final_RPC_flow (not .mfh which is not supported yet anyway)')
    parser.add_argument('-t','--testtable_file',required=True, help='name of testtable file type csv file (Example: Kepler_TestNameTypeList.csv)')
    parser.add_argument('-out','--output_dir',required=False,default='', help='Directory to place log file(s).')
    parser.add_argument('-n','--name',required=False,default='',help='Optional name used for output files/logs.')
    parser.add_argument('-max','--maxlogs',type=int,default=10,required=False, help='(0=OFF:log data to stdout). Set to 1 to keep only one log (subsequent runs will overwrite).')
    parser.add_argument('-d','--debug',action='store_true',help='print a lot of debug stuff to dlog')
    args = parser.parse_args()

    init_logging(args.verbose, scriptname=os.path.split(sys.modules[__name__].__file__)[1], logDir=args.output_dir, args=args)

    get_testflow(args.testFlowFile)
    if 'binBinGrpsFile' in args:
        parse_special_csv(args.binBinGrpsFile,'bin_groups')
        bin_groups_exist = True
    parse_special_csv(args.binSpdSrtGrpsFile,'speed_sort_groups')
    parse_special_csv(args.binTNTFile,'test_name_type')
    parse_special_csv(args.binCatsFile,'categories')

if __name__ == "__main__":
    main()
    time = time.time()-_start_time
    print '\nScript took',round(time,3),'seconds','('+humanize_time(time)+')'
