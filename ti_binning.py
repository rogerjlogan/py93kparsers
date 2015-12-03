#!/usr/bin/env python
"""
    This module parses the TI special bin csv files.
"""

import csv
import argparse
from common import *
from testprog_parser import ProgFile
from TestflowParser import Testflow
from testtable_parser import TestTable
from testtable_parser import VALID_LIM_HEADERS
import time
_start_time = time.time()
log = None

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
testflow_file = None
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

testsuite_all_sbins = {}

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
        # err = '\nCRITICAL ERROR!!! Duplicate test/bin combination in Binning Categories!\n'
        err = '\nPOSSIBLE ERRROR !!! Duplicate test/bin combination in Binning Categories!\n'
        err += 'Test: ' + test + '\n'
        err += 'sbin: ' + sbin + '\n'
        # err += 'Exiting ...\n'
        # sys.exit(err)
        # print err
        log.warning(err)
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
        msg = 'Parsing TI specific testtable file: '+fn+' .....'
        print msg
        log.info(msg)

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
                log.warning('Extra tests in '+os.path.basename(categories_file)+' that do not exist in '+os.path.basename(testflow_file) + ' or '+os.path.basename(bin_groups_file))
                log.debug(pformat(categories_extra_tests,indent=4))
            if len(testflow_extra_tests):
                log.warning('Extra tests in '+os.path.basename(testflow_file) + ' that do not exist in '+os.path.basename(categories_file))
                log.debug(pformat(testflow_extra_tests,indent=4))

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

def gather_all_testsuites_bins():
    global testsuite_all_sbins
    for node_id in testflow.nodeData:
        if 'testsuite' in testflow.nodeData[node_id]:
            testtable_binnable = False # init
            tf_testsuite = testflow.nodeData[node_id]['testsuite']
            descendants = testflow.nodeData[node_id]['descendants']
            # stop_sbin = testflow.nodeData[node_id][]
            if tf_testsuite not in testsuite_all_sbins:
                testsuite_all_sbins[tf_testsuite] = {
                    'stop_sbins' : [],
                    'multi_sbins' : [],
                    'cat_sbins' : []
                }
            for desc in descendants:
                try:
                    desc_id = int(desc.split('-')[-1])
                except:
                    # can't make int out of id, which means it can't be a bin anyways... skip
                    continue
                if testflow.nodeData[desc_id]['type'] == 'StopBinStatement':
                    sbin = testflow.nodeData[desc_id]['swBin'].replace('"','')
                    if sbin not in testsuite_all_sbins[tf_testsuite]['stop_sbins']:
                        testsuite_all_sbins[tf_testsuite]['stop_sbins'].append(sbin)
                if testflow.nodeData[desc_id]['type'] == 'MultiBinStatement':
                    testtable_binnable = True

            if tf_testsuite in testtable.testsuite_sbins:
                if not testtable_binnable:
                    sbins = ['X_'+x for x in testtable.testsuite_sbins[tf_testsuite]]
                else:
                    sbins = testtable.testsuite_sbins[tf_testsuite]
                unique_sbins = list(set(testsuite_all_sbins[tf_testsuite]['multi_sbins'] + sbins))
                testsuite_all_sbins[tf_testsuite]['multi_sbins'] = unique_sbins

            if tf_testsuite in category_tests:
                sbins = category_tests[tf_testsuite].keys()
                unique_sbins = list(set(testsuite_all_sbins[tf_testsuite]['cat_sbins'] + sbins))
                testsuite_all_sbins[tf_testsuite]['cat_sbins'] = unique_sbins
            else:
                # testsuite not in categories, so let's check groups
                groups = [x for x in bin_groups if tf_testsuite in bin_groups[x]]
                if len(groups) > 1:
                    warn = 'POSSIBLE ERROR!!! Testflow Testsuite: "{}" in more than one Category Group: "{}"'.format(tf_testsuite,','.join(groups))
                    print warn
                    log.warning(warn)
                for group in groups:
                    if group in category_tests:
                        sbins = category_tests[group].keys()
                        unique_sbins = list(set(testsuite_all_sbins[tf_testsuite]['cat_sbins'] + sbins))
                        testsuite_all_sbins[tf_testsuite]['cat_sbins'] = unique_sbins

def create_binning_csv(outdir,fn):
    if not len(outdir):
        outdir = os.path.dirname(os.path.realpath(__file__))
    if len(fn):
        progname = fn+'_'
    else:
        progname = ''
    basename = progname + os.path.basename(sys.modules[__name__].__file__).split('.')[0]
    csvname = basename + '.csv'
    csv_file = os.path.join(outdir, csvname)

    # csv_file = os.path.join(outdir,fn+'_binning.csv')
    # pprint(testsuite_all_sbins)
    msg = 'Creating {}...\n\tNOTE: For "multi_sbins" column, "X_" indicates that the '.format(csv_file)
    msg += 'bin is not reachable in the testflow "downstream".\n'
    msg += '\tIn other words, there is no multibin TO THE RIGHT of the Testsuite (fail branches, etc) in the testflow.\n'
    msg += '\tThe "multi_sbins" column only applies to standard testtables (limit files) which bin only with multibins in the testflow'
    print msg
    log.info(msg)
    headers = ['node_id','Testsuite','bypassed','stop_sbins','category_sbins','multi_sbins']
    with open(csv_file,'wb') as csvFile:
        writer = csv.DictWriter(csvFile,fieldnames=headers)
        writer.writeheader()
        for testsuite in testsuite_all_sbins:
            writer.writerow({'node_id' : testflow.testsuite_nodeids[testsuite],
                             'Testsuite' : testsuite,
                             'bypassed' : 'Y' if testsuite in testflow.bypassed_testsuites else '',
                             'stop_sbins': '|'.join(testsuite_all_sbins[testsuite]['stop_sbins']),
                             'category_sbins': '|'.join(testsuite_all_sbins[testsuite]['cat_sbins']),
                             'multi_sbins': '|'.join(testsuite_all_sbins[testsuite]['multi_sbins'])})

def main():
    global log,testflow,testflow_file,testtable,bin_groups_exist
    parser = argparse.ArgumentParser(description="Description: "+sys.modules[__name__].__doc__)
    parser.add_argument('-tf','--testflow_file',required=False,default='', help='name of testflow file (Example: Final_RPC_flow(.tf or .mfh)\
                        WARNING: THIS GOES WITH -tt (--testtable_file), BUT NOT WITH -tp (--testprog_file)')
    parser.add_argument('-tt','--testtable_file',required=False,default='', help='name of testtable file type csv file (Example: Kepler_TestNameTypeList.csv)\
                        WARNING: THIS GOES WITH -tt (--testflow_file), BUT NOT WITH -tp (--testprog_file)')
    parser.add_argument('-tp','--testprog_file',required=False,default='', help='name of testprog file (Example: F791857_Final_RPC.tpg)\
                        WARNING: THIS DOES NOT GO WITH -tt (--testflow_file) OR WITH -tp (--testprog_file)')
    parser.add_argument('-out','--output_dir',required=False,default='', help='Directory to place log file(s).')
    parser.add_argument('-name','--name',required=False,default='',help='Optional name used for output files/logs.')
    parser.add_argument('-max','--maxlogs',type=int,default=10,required=False, help='(0=OFF:log data to stdout). Set to 1 to keep only one log (subsequent runs will overwrite).')
    parser.add_argument('-r','--renumber',action='store_true',help='Re-number "Test number" column across all STANDARD csv testtables')
    parser.add_argument('-s','--split',action='store_true',help='split image files into top level groups (USE THIS OPTION FOR REALLY LARGE TESTFLOW FILES!')
    parser.add_argument('-d','--debug',action='store_true',help='print a lot of debug stuff to dlog')
    args = parser.parse_args()

    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logger_name,outdir = init_logging(scriptname=os.path.basename(sys.modules[__name__].__file__),
                                      outdir=args.output_dir, name=args.name, maxlogs=args.maxlogs ,level=log_level)

    log = logging.getLogger(logger_name)

    if len(args.testprog_file):
        if len(args.testflow_file) or len(args.testtable_file):
            err = 'INPUT ERROR!!! testprog_file (-tp) already provided.  Cannot provide testflow_file (-tf) and/or testtable_file (-tt) also! Exiting ...'
            log.error(err)
            sys.exit(err)
        tp = ProgFile(pathfn=args.progfile,debug=args.debug,progname=args.name,maxlogs=args.maxlogs,outdir=args.output_dir)
        testflow_file = os.path.join(tp.progdir,'testflow',tp.contents['Testflow'])
        testtable_file = os.path.join(tp.progdir,'testtable',tp.contents['Testtable'])
    elif len(args.testflow_file) and len(args.testtable_file):
        testflow_file = args.testflow_file
        testtable_file = args.testtable_file
    else:
        err = 'UNSTABLE INPUT: Must provide either testprog_file (-tp) OR both testflow_file (-tf) AND testtable_file (-tt) BUT not all 3! Exiting ...'
        log.error(err)
        sys.exit(err)

    testflow = Testflow(tf_file=testflow_file,debug=args.debug,split=args.split,progname=args.name,maxlogs=args.maxlogs,outdir=args.output_dir)
    testtable = TestTable(testtable_file,args.renumber)

    identify_ti_csv_files(testtable.special_testtables)

    if bin_groups_file is not None:
        parse_special_csv(bin_groups_file,'bin_groups')
        bin_groups_exist = True
    parse_special_csv(speed_sort_groups_file,'speed_sort_groups')
    parse_special_csv(test_name_type_file,'test_name_type')
    parse_special_csv(categories_file,'categories')

    gather_all_testsuites_bins()
    create_binning_csv(args.output_dir,args.name)

    # For debug and future development, list this module's data containers and their contents
    log.debug('bin_groups:\n' + pformat(bin_groups,indent=4))
    log.debug('speed_sort_groups:\n' + pformat(speed_sort_groups,indent=4))
    log.debug('test_name_type:\n' + pformat(test_name_type,indent=4))
    log.debug('category_defs:\n' + pformat(category_defs,indent=4))
    log.debug('category_tests:\n' + pformat(category_tests,indent=4))
    log.debug('categories_extra_tests:\n' + pformat(categories_extra_tests,indent=4))
    log.debug('testflow_extra_tests:\n' + pformat(testflow_extra_tests,indent=4))

if __name__ == "__main__":
    main()
    time = time.time()-_start_time
    msg = 'Script took ' + str(round(time,3)) + ' seconds (' + humanize_time(time) + ')'
    log.info(msg)
    print '\n' + msg
