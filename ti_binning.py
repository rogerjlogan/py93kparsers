#!/usr/bin/env python
"""
    This module parses the TI special bin csv files.
"""

import csv
import argparse
from common import *
from TestflowParser import Testflow
from testtable_parser import TestTable
from testtable_parser import VALID_LIM_HEADERS
import time
_start_time = time.time()

__author__ = 'Roger'

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

testflow = None
testtable = None
categories_file = None
test_name_type_file = None
speed_sort_groups_file = None

# control variables below here (boolean)

bin_groups_exist = False
bin_groups_done = False
speed_sort_groups_done = False
test_name_type_done = False
bin_groups_file = False

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
"""Parsed Testflow object"""

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
                if 0 == i or '#' == row[0][0]:
                    # skip header row or if row starts with '#'
                    continue
                bin_groups[row[BINNING_GROUP_TESTNAME]] = [x for x in row[BINNING_GROUP_TESTNAME+1:] if len(x.strip())]
            bin_groups_done = True

        elif csv_type == 'speed_sort_groups':
            # using csv.reader() for slice indexing
            for i,row in enumerate(csv.reader(csvFile)):
                if 0 == i or '#' == row[i][0]:
                    # skip header row or if row starts with '#'
                    continue
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
            categories_extra_tests = set(category_tests.keys() + [MEMORYREPAIRED]) - set(testflow.testsuite_data.keys() + bin_groups.keys())
            testflow_extra_tests = set(testflow.testsuite_data.keys()) - set(category_tests.keys())

            if len(categories_extra_tests):
                log.warning('Extra tests in '+os.path.basename(categories_file)+' that do not exist in Testflow or Binning Groups!')
                log.debug(pformat(categories_extra_tests))
            if len(testflow_extra_tests):
                log.warning('Extra tests in Testflow that do not exist in '+os.path.basename(categories_file))
                log.debug(pformat(testflow_extra_tests))

            # TODO: Get bins from testflow, testtable and categories and build bins.csv

        else:
            err += 'Unknown csv_type found!\n'
            err += 'File: '+fn+'\n'
            err += 'csv_type: '+csv_type+'\n'
            err += 'valid csv_types: '+csv_type+'\n'
            err += 'Exiting ...'
            sys.exit(err)

def identify_ti_csv_files(special_testtables):
    global categories_file,speed_sort_suites_file,speed_sort_groups_file,test_name_type_file,bin_groups_file
    for pathfn in special_testtables:
        fn = os.path.split(pathfn)[1]
        with open(pathfn) as csvFile:
            headers = csv.DictReader(csvFile).fieldnames
            if 'SW Bin Number' in headers:
                categories_file = pathfn
                log.info('Found categories_file: %s',fn)
            elif 'SpeedSortSuites' in headers:
                speed_sort_suites_file = pathfn
                log.info('Found speed_sort_suites_file: %s',fn)
            elif 'SpeedSortGroups' in headers:
                speed_sort_groups_file = pathfn
                log.info('Found speed_sort_groups_file: %s',fn)
            elif 'Test name' in headers and any([True if x in testflow.variables['@TITESTTYPE_valid'] else False for x in headers]):
                test_name_type_file = pathfn
                log.info('Found test_name_type_file: %s',fn)
            elif 'Group' in headers and 'testname0' in headers:
                bin_groups_file = pathfn
                log.info('Found bin_groups_file: %s',fn)
    if categories_file is None:
        log.error('Unable to find categories_file')
    if speed_sort_suites_file is None:
        log.error('Unable to find speed_sort_suites_file')
    if speed_sort_groups_file is None:
        log.error('Unable to find speed_sort_groups_file')
    if test_name_type_file is None:
        log.error('Unable to find test_name_type_file')
    if bin_groups_file is None:
        log.warning('Unable to find bin_groups_file - This may not be a problem if you don\'t care about insertion specific enable/disable checks')

def main():
    global testflow,testtable,bin_groups_exist
    parser = argparse.ArgumentParser(description="Description: "+sys.modules[__name__].__doc__)
    parser.add_argument('-tf','--testflow_file',required=False, help='name of testflow file (Example: Final_RPC_flow (not .mfh which is not supported yet anyway)')
    parser.add_argument('-tt','--testtable_file',required=True, help='name of testtable file type csv file (Example: Kepler_TestNameTypeList.csv)')
    parser.add_argument('-out','--output_dir',required=False,default='', help='Directory to place log file(s).')
    parser.add_argument('-n','--name',required=False,default='',help='Optional name used for output files/logs.')
    parser.add_argument('-max','--maxlogs',type=int,default=10,required=False, help='(0=OFF:log data to stdout). Set to 1 to keep only one log (subsequent runs will overwrite).')
    parser.add_argument('-r','--renumber',action='store_true',help='Re-number "Test number" column across all STANDARD csv testtables')
    parser.add_argument('-d','--debug',action='store_true',help='print a lot of debug stuff to dlog')
    args = parser.parse_args()

    init_logging(scriptname=os.path.basename(sys.modules[__name__].__file__),args=args)

    testflow = Testflow(args.testflow_file,args.debug)
    testtable = TestTable(args.testtable_file,args.renumber)

    identify_ti_csv_files(testtable.special_testtables)

    if bin_groups_file is not None:
        parse_special_csv(bin_groups_file,'bin_groups')
        bin_groups_exist = True
    parse_special_csv(speed_sort_groups_file,'speed_sort_groups')
    parse_special_csv(test_name_type_file,'test_name_type')
    parse_special_csv(categories_file,'categories')

    # list all data containers and their contents
    log.debug('bin_groups: ' + pformat(bin_groups))
    log.debug('speed_sort_groups: ' + pformat(speed_sort_groups))
    log.debug('test_name_type: ' + pformat(test_name_type))
    log.debug('category_defs: ' + pformat(category_defs))
    log.debug('category_tests: ' + pformat(category_tests))
    log.debug('categories_extra_tests: ' + pformat(categories_extra_tests))
    log.debug('testflow_extra_tests: ' + pformat(testflow_extra_tests))

if __name__ == "__main__":
    main()
    time = time.time()-_start_time
    msg = 'Script took ' + str(round(time,3)) + ' seconds (' + humanize_time(time) + ')'
    log.info(msg)
    print '\n' + msg
