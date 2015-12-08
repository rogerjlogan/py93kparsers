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
"""really stupid that this is called 'Test name' so wanted a global constant to switch later easily"""

CATEGORY_VALID_AND = ['S_ALL','AND']

CATEGORY_VALID_OR = ['S_ANY','OR']

testflow = None
testflow_file = None
testtable = None
categories_file = None
test_name_type_file = None
speed_sort_groups_file = None
binning_csv_file = None

test_type_to_check = ''

# control variables below here (boolean)

ti_binning_done = False
bin_groups_exist = False
bin_groups_done = False
speed_sort_groups_done = False
test_name_type_done = False
bin_groups_file = False
tt2c_valid = False

# data collection variables below here

bin_groups = {}
"""list of dict() with group names as keys and values are lists of testsuites for that group name"""

speed_sort_groups = []
"""list of virtual test names used for ti_binning categories"""

test_name_type = {}
"""2-D dict() of 'Test name'(primary key), TITESTTYPE(secondary key), and flag(value) 1=expect, 0=don't expect"""

category_defs = []
"""Ordered list of category definitions"""

category_tests = {}

categories_extra_tests = []

testflow_extra_tests = []
"""Parsed Testflow object"""

testsuite_all_sbins = {}

ignore_suites = []

ti_binning = {}

testflow_binning = {}

testflow_bin_defs = {}

hard_bins = {}

def get_category_testname(test, sbin):
    global category_tests

    if test[0] == '+':
        good = True
    elif test[0] == '-':
        good = False
    else:
        err = 'Unknown polarity in categories!\n'
        err += 'Test: ' + test + '\n'
        err += 'sbin: ' + sbin + '\n'
        err += 'Exiting ...\n'
        print 'ERROR!!!',err;log.error(err)
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
        err = 'POSSIBLE ERRROR !!! Duplicate test/bin combination in Binning Categories!\n'
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
    global ti_binning_done,bin_groups_exist,bin_groups_done,speed_sort_groups_done,test_name_type_done
    global bin_groups,category_defs,categories_extra_tests,testflow_extra_tests,test_name_type,tt2c_valid

    # we gotta make sure we parse speed/bin groups and insertions first before categories
    if csv_type == 'categories':
        if not ti_binning_done or (bin_groups_exist and not bin_groups_done) or not speed_sort_groups_done or not test_name_type_done:
            err = 'ti_binning_done={}, '.format(ti_binning_done)
            err += 'bin_groups_exist={}, bin_groups_done={}\n'.format(bin_groups_exist,bin_groups_done)
            err += 'speed_sort_groups_done={}, test_name_type_done={}\n'.format(speed_sort_groups_done,test_name_type_done)
            print err; log.debug(err)
            err = 'Need to process Binning (binning_csv), Bin Groups(if exists), Speed Sort Groups, and Test Name Types *BEFORE* processing Categories!  Exiting ...'
            print 'ERROR!!!',err; log.critical(err)
            sys.exit(err)

    with open(pathfn) as csvFile:
        tp_path, fn = os.path.split(pathfn)
        msg = 'Parsing TI specific testtable file: '+fn+' .....'
        print msg
        log.info(msg)

        if csv_type == 'ti_binning':
            for row in csv.DictReader(csvFile):
                Bin_s_num = row['Bin_s_num'].strip()
                Bin_s_name = row['Bin_s_name'].strip()
                Bin_h_num  = row['Bin_h_num'].strip()
                Bin_h_name = row['Bin_h_name'].strip()
                try:
                    # if it can't be converted to an int, we don't care about this row
                    int(Bin_s_num)
                except:
                    continue
                if Bin_s_num not in ti_binning:
                    ti_binning[Bin_s_num] = {
                        'Bin_s_name' : Bin_s_name,
                        'Bin_h_num' : Bin_h_num,
                        'Bin_h_name' : Bin_h_name
                    }
                else:
                    prev = ('SBIN='+Bin_s_num,ti_binning[Bin_s_num]['Bin_s_name'],
                            'HBIN='+ti_binning[Bin_s_num]['Bin_h_num'],ti_binning[Bin_s_num]['Bin_h_name'])
                    curr = ('SBIN='+Bin_s_num,Bin_s_name,
                            'HBIN='+Bin_h_num,Bin_h_name)
                    if True or prev != curr:
                        err = 'Duplicate Softbin Number found in: "{}".... \n\t{}\n\t{}'.format(fn,prev,curr)
                        log.error(err)
                        sys.exit(err)
            ti_binning_done = True

        elif csv_type == 'bin_groups':
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
            if len(test_type_to_check):
                valid_testtypes = [x.strip('"') for x in testflow.variables['@TITESTTYPE_valid'].split(',')]
                if test_type_to_check not in valid_testtypes:
                    err = 'TestType To Check you gave (-tt2c) not valid in Testflow: "{}". Skipping check ...\n\t(@TITESTTYPE_valid = "{}").'\
                        .format(test_type_to_check,', '.join(valid_testtypes))
                    print 'ERROR!!! '+err
                    log.error(err)
                else:
                    # setting a flag for later parsing
                    tt2c_valid = True
            test_name_type_done = True

        elif csv_type == 'categories':
            # using csv.DictReader() for key indexing
            for row in csv.DictReader(csvFile):
                sbin = row[SBIN_NUM_COLUMN_NAME]
                not_empty_row = any([True if len(row[x]) and x not in [SBIN_NUM_COLUMN_NAME, CONDITION_COLUMN_NAME] else False for x in row.keys()])
                if sbin not in ti_binning and not_empty_row:
                    err = 'Softbin Number: "{}" found in: "{}" but not in: "{}"'.format(sbin,fn,binning_csv_file)
                    log.error(err)
                    log.debug(row)
                    log.debug(not_empty_row)
                    log.debug(pformat([True if len(row[x]) and x not in [SBIN_NUM_COLUMN_NAME, CONDITION_COLUMN_NAME] else False for x in row.keys()]))
                    sys.exit(SBIN_NUM_COLUMN_NAME+':'+err)
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

            # calculate set differences
            categories_extra_tests = set(category_tests.keys()) - set(testflow.testsuite_data.keys() + bin_groups.keys())
            categories_extra_tests = categories_extra_tests - set(ignore_suites)
            testflow_extra_tests = set(testflow.testsuite_data.keys()) - set(category_tests.keys())
            testflow_extra_tests = testflow_extra_tests - set(ignore_suites)

            if len(categories_extra_tests):
                cat_extra_str = '\n\t'.join(categories_extra_tests)
                warn = 'Extra tests in: "{}" that do not exist in: "{}" OR in "{}"\n\t{}'.format(os.path.basename(categories_file),
                                                                                                 os.path.basename(testflow_file),
                                                                                                 os.path.basename(bin_groups_file),
                                                                                                 cat_extra_str)
                log.warning(warn)
            if len(testflow_extra_tests):
                tf_extra_str = '\n\t'.join(testflow_extra_tests)
                warn = 'Extra tests in: "{}" that do not exist in: "{}"\n\t{}'.format(os.path.basename(testflow_file),
                                                                                      os.path.basename(categories_file),
                                                                                      tf_extra_str)
                log.warning(warn)

        else:
            err = 'Unknown csv_type found!\n'
            err += 'File: '+fn+'\n'
            err += 'csv_type: '+csv_type+'\n'
            err += 'valid csv_types: '+csv_type+'\n'
            err += 'Skipping ...'
            print 'ERROR!!!',err; log.critical(err)
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
            elif 'Test name' in headers and any([True if x in [t.strip('"') for t in testflow.variables['@TITESTTYPE_valid'].split(',')] else False for x in headers]):
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
    global testsuite_all_sbins,hard_bins
    for node_id in testflow.nodeData:
        if 'testsuite' in testflow.nodeData[node_id]:
            testtable_binnable = False # init
            tf_testsuite = testflow.nodeData[node_id]['testsuite']
            descendants = testflow.nodeData[node_id]['descendants']
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
                    Bin_s_num = testflow.nodeData[desc_id]['swBin'].replace('"','')
                    if Bin_s_num not in hard_bins:
                        hard_bins[Bin_s_num] = []
                    Bin_s_name = testflow.nodeData[desc_id]['swBinDescription'].replace('"','')
                    Bin_h_num = testflow.nodeData[desc_id]['binNumber'].replace('"','')
                    try:
                        Bin_h_name = testflow.hbin_descriptions[Bin_h_num].replace('"','')
                    except:
                        Bin_h_name = ''
                    if Bin_s_num not in ti_binning:
                        hard_bins[Bin_s_num] = {
                            'Bin_s_name' : Bin_s_name,
                            'Bin_h_num' : Bin_h_num,
                            'Bin_h_name' : Bin_h_name
                        }
                    else:
                        prev = ('SBIN='+Bin_s_num,hard_bins[Bin_s_num]['Bin_s_name'],
                                'HBIN='+ti_binning[Bin_s_num]['Bin_h_num'],hard_bins[Bin_s_num]['Bin_h_name'])
                        curr = ('SBIN='+Bin_s_num,Bin_s_name,
                                'HBIN='+Bin_h_num,Bin_h_name)
                        if prev != curr:
                            err = 'Duplicate HW bin info found .... \n\t{}\n\t{}'.format(prev,curr)
                            log.error(err)
                    if Bin_s_num not in testsuite_all_sbins[tf_testsuite]['stop_sbins']:
                        testsuite_all_sbins[tf_testsuite]['stop_sbins'].append(Bin_s_num)
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
                    log.warning(warn)
                for group in groups:
                    if group in category_tests:
                        sbins = category_tests[group].keys()
                        unique_sbins = list(set(testsuite_all_sbins[tf_testsuite]['cat_sbins'] + sbins))
                        testsuite_all_sbins[tf_testsuite]['cat_sbins'] = unique_sbins

def create_ti_binning_csv(scriptname=os.path.basename(sys.modules[__name__].__file__), outdir='', fn='', maxlogs=1):

    csv_file,outdir,info_msg,warn_msg = get_valid_file(scriptname=scriptname, name=fn, outdir=outdir, maxlogs=maxlogs, ext='.csv')
    for msg in warn_msg:
        print 'WARNING!!! ',msg
        log.warning(msg)
    for msg in info_msg:
        log.info(msg)

    msg = '\tNOTE: For "multi_sbins" column in "{}"...\n'.format(os.path.basename(csv_file))
    msg += '\t"X_" indicates that the bin is not reachable in the testflow "downstream".\n'
    msg += '\tIn other words, there is no multibin TO THE RIGHT of the Testsuite (fail branches, etc) in the testflow.\n'
    msg += '\tThe "multi_sbins" column only applies to standard testtables (limit files) which can bin only with a multibin in the testflow.'
    print msg
    log.info(msg)
    headers = ['node_id','SuiteName','bypassed','stop_sbins','category_sbins','multi_sbins']
    with open(csv_file,'wb') as csvFile:
        writer = csv.DictWriter(csvFile,fieldnames=headers)
        writer.writeheader()
        for testsuite in testsuite_all_sbins:
            if testsuite not in ignore_suites:
                writer.writerow({'node_id' : testflow.testsuite_nodeids[testsuite],
                                 'SuiteName' : testsuite,
                                 'bypassed' : 'Y' if testsuite in testflow.bypassed_testsuites else '',
                                 'stop_sbins': '|'.join(testsuite_all_sbins[testsuite]['stop_sbins']),
                                 'category_sbins': '|'.join(testsuite_all_sbins[testsuite]['cat_sbins']),
                                 'multi_sbins': '|'.join(testsuite_all_sbins[testsuite]['multi_sbins'])})

def create_flowaudit_csv(scriptname=os.path.basename(sys.modules[__name__].__file__), outdir='', fn='', maxlogs=1):

    csv_file,outdir,info_msg,warn_msg = get_valid_file(scriptname=scriptname, name=fn, outdir=outdir, maxlogs=maxlogs, ext='.csv')
    for msg in warn_msg:
        print 'WARNING!!! ',msg
        log.warning(msg)
    for msg in info_msg:
        log.info(msg)

    # need this section to create a list of tuples that can be sorted later (next section of code)
    unsorted_rows = []
    for ts,values in testflow_binning.iteritems():
        if ts not in ignore_suites:
            nid = testflow.testsuite_nodeids[ts]
            nid = re.sub('\d+', lambda x:x.group().zfill(20), str(nid))
            if len(values):
                for v in values:
                    hbin = re.sub('\d+', lambda x:x.group().zfill(20), v['Bin_h_num'])
                    unsorted_rows.append((nid,ts,v['Bin_s_num'],v['Bin_s_name'],hbin,v['Bin_h_name'],v['bintype']))
            else:
                unsorted_rows.append((nid,ts,'MISSING BIN','---','---','---','---'))

    if tt2c_valid:
        headers = ['node_id','SuiteName','SoftBinNum','SoftBinName','HardBinName','BinNumber','BinSource','TestTypeCheckValue']
    else:
        headers = ['node_id','SuiteName','SoftBinNum','SoftBinName','HardBinName','BinNumber','BinSource']
    all_suites = []
    with open(csv_file,'wb') as csvFile:
        writer = csv.DictWriter(csvFile,fieldnames=headers)
        writer.writeheader()
        for nid,suite,sbin,sname,hbin,hname,bintype in sorted(unsorted_rows, key=lambda x: (x[0],x[4],x[2])):
            if suite not in all_suites:
                all_suites.append(suite)
                suite2show = suite
            else:
                suite2show = suite+'-DUPLICATE'
            if tt2c_valid:
                if suite in test_name_type:
                    tt2c = test_name_type[suite][test_type_to_check]
                else:
                    tt2c = 'SUITE: "{}" NOT IN "{}"'.format(suite,os.path.basename(test_name_type_file))
                    log.warning(tt2c+'\tNOTE: this WARNING is also in "%s"',os.path.basename(csv_file))
                writer.writerow({'node_id' : nid.lstrip('0'),
                                 'SuiteName' : suite2show,
                                 'SoftBinNum' : sbin.lstrip('0'),
                                 'SoftBinName': sname,
                                 'HardBinName': hname,
                                 'BinNumber': hbin.lstrip('0'),
                                 'BinSource': bintype,
                                 'TestTypeCheckValue': tt2c})
            else:
                writer.writerow({'node_id' : nid.lstrip('0'),
                                 'SuiteName' : suite2show,
                                 'SoftBinNum' : sbin.lstrip('0'),
                                 'SoftBinName': sname,
                                 'HardBinName': hname,
                                 'BinNumber': hbin.lstrip('0'),
                                 'BinSource': bintype})


def create_softbinaudit_csv(scriptname=os.path.basename(sys.modules[__name__].__file__), outdir='', fn='', maxlogs=1):
    csv_file,outdir,info_msg,warn_msg = get_valid_file(scriptname=scriptname, name=fn, outdir=outdir, maxlogs=maxlogs, ext='.csv')
    for msg in warn_msg:
        print 'WARNING!!! ',msg
        log.warning(msg)
    for msg in info_msg:
        log.info(msg)

    unsorted_sbin_rows = []
    for sbin,values in testflow_bin_defs['sbins'].iteritems():
        sbin = re.sub('\d+', lambda x:x.group().zfill(20), sbin)
        if len(values):
            for v in values:
                unsorted_sbin_rows.append((sbin,v['Bin_s_name'],v['Bin_h_num'],v['Bin_h_name']))
        else:
            unsorted_sbin_rows.append((sbin,'MISSING BIN','---','---'))

    headers = ['SoftBinNumber','SoftBinName','HardBinName','HardBinNumber']
    with open(csv_file,'wb') as csvFile:
        writer = csv.DictWriter(csvFile,fieldnames=headers)
        writer.writeheader()
        for sbin,sname,hbin,hname in sorted(unsorted_sbin_rows, key=lambda x: (x[0],x[3])):
            writer.writerow({'SoftBinNumber' : sbin.lstrip('0'),
                             'SoftBinName': sname,
                             'HardBinName': hname,
                             'HardBinNumber': hbin.lstrip('0')})

def create_hardbinaudit_csv(scriptname=os.path.basename(sys.modules[__name__].__file__), outdir='', fn='', maxlogs=1):
    csv_file,outdir,info_msg,warn_msg = get_valid_file(scriptname=scriptname, name=fn, outdir=outdir, maxlogs=maxlogs, ext='.csv')
    for msg in warn_msg:
        print 'WARNING!!! ',msg
        log.warning(msg)
    for msg in info_msg:
        log.info(msg)

    unsorted_hbin_rows = []
    for hbin,values in testflow_bin_defs['hbins'].iteritems():
        hbin = re.sub('\d+', lambda x:x.group().zfill(20), str(hbin))
        if len(values):
            for hname in values:
                unsorted_hbin_rows.append((hname,hbin))
        else:
            unsorted_hbin_rows.append(('',hbin))

    headers = ['HardBinName','HardBinNumber']
    with open(csv_file,'wb') as csvFile:
        writer = csv.DictWriter(csvFile,fieldnames=headers)
        writer.writeheader()
        for hname,hbin in sorted(unsorted_hbin_rows, key=lambda x: (x[1],x[0])):
            writer.writerow({'HardBinName': hname,
                             'HardBinNumber': hbin.lstrip('0')})

def create_tt_missing_suites_csv(scriptname=os.path.basename(sys.modules[__name__].__file__), outdir='', fn='', maxlogs=1):
    csv_file,outdir,info_msg,warn_msg = get_valid_file(scriptname=scriptname, name=fn, outdir=outdir, maxlogs=maxlogs, ext='.csv')
    for msg in warn_msg:
        print 'WARNING!!! ',msg
        log.warning(msg)
    for msg in info_msg:
        log.info(msg)

    found = False
    headers = ['Missing Suites in Testflow',test_type_to_check]
    with open(csv_file,'wb') as csvFile:
        writer = csv.DictWriter(csvFile,fieldnames=headers)
        writer.writeheader()
        for ts in test_name_type:
            if ts not in testflow.testsuite_nodeids and '1' == test_name_type[ts][test_type_to_check]:
                found = True
                writer.writerow({'Missing Suites in Testflow': ts,
                                 test_type_to_check: test_name_type[ts][test_type_to_check]})
    if not found:
        os.remove(csv_file)

def find_actual_bindefs():
    global testflow_bin_defs
    sbin_defs,hbin_defs = {},{}
    for ts,bins in testflow_binning.iteritems():
        if len(bins):
            for b in bins:
                Bin_s_num = b['Bin_s_num']
                Bin_s_name = b['Bin_s_name']
                Bin_h_num = b['Bin_h_num']
                Bin_h_name = b['Bin_h_name']
                bin_info = {
                    'Bin_s_name' :  Bin_s_name,
                    'Bin_h_num' : Bin_h_num,
                    'Bin_h_name' : Bin_h_name
                }
                if Bin_s_num not in sbin_defs:
                    sbin_defs[Bin_s_num] = [bin_info]
                else:
                    for sbin_defined in sbin_defs[Bin_s_num]:
                        # checking if another definition of sbin # has the same other 3 definitions (sbin name, hbin #/name)
                        prev = ('SBIN='+Bin_s_num,sbin_defined['Bin_s_name'],
                                'HBIN='+sbin_defined['Bin_h_num'],sbin_defined['Bin_h_name'])
                        curr = ('SBIN='+Bin_s_num,Bin_s_name,
                                'HBIN='+Bin_h_num,Bin_h_name)
                        if prev != curr:
                            sbin_defs[Bin_s_num].append(bin_info)
                # get hbin info
                if Bin_h_num not in hbin_defs:
                    hbin_defs[Bin_h_num] = [Bin_h_name]
                elif Bin_h_name not in hbin_defs[Bin_h_num]:
                    hbin_defs[Bin_h_num].append(Bin_h_name)

    testflow_bin_defs['sbins'] = sbin_defs
    testflow_bin_defs['hbins'] = hbin_defs

def find_actual_binning():
    global testflow_binning
    bin_info = {}
    for ts,v in testsuite_all_sbins.iteritems():
        testflow_binning[ts] = []
        bin_info[ts] = []
        bintype = ''
        if len(v['stop_sbins']):
            bintype = 'stop'
            for sbin in v['stop_sbins']:
                if sbin not in hard_bins:
                    err = 'Found stop_sbin: {} in "testsuite_all_sbins" dict(), but now not found in "hard_bins" dict()...\n\t{}'\
                        .format(sbin,'\n\thard_bins:\n\t'+'\n\t'.join(hard_bins))
                    log.critical(err)
                    sys.exit(err)
                bin_info[ts].append({
                    'Bin_s_num' : sbin,
                    'Bin_s_name' : hard_bins[sbin]['Bin_s_name'],
                    'Bin_h_num' : hard_bins[sbin]['Bin_h_num'],
                    'Bin_h_name' : hard_bins[sbin]['Bin_h_name'],
                    'bintype' : bintype
                })

        elif len(v['multi_sbins']):
            bintype = 'multi'
            try:
                # we don't want unreachable multibins (unreachables start with 'X_' which can't be made into an int)
                int(v['multi_sbins'][0])
                sbins = v['multi_sbins']
            except:
                bintype = ''
            if len(bintype):
                for sbin in v['multi_sbins']:
                    bin_info[ts].append({
                        'Bin_s_num' : sbin,
                        'Bin_s_name' : testtable.binning[sbin]['Bin_s_name'],
                        'Bin_h_num' : testtable.binning[sbin]['Bin_h_num'],
                        'Bin_h_name' : testtable.binning[sbin]['Bin_h_name'],
                        'bintype' : bintype
                    })

        if not len(bintype) and len(v['cat_sbins']):
            bintype = 'cat'
            for sbin in v['cat_sbins']:
                bin_info[ts].append({
                    'Bin_s_num' : sbin,
                    'Bin_s_name' : ti_binning[sbin]['Bin_s_name'],
                    'Bin_h_num' : ti_binning[sbin]['Bin_h_num'],
                    'Bin_h_name' : ti_binning[sbin]['Bin_h_name'],
                    'bintype' : bintype
                })

        if len(bintype) and len(bin_info[ts]):
            testflow_binning[ts] = bin_info[ts]
    find_actual_bindefs()

def main():
    global log,ignore_suites,testflow,testflow_file,testtable,bin_groups_exist,binning_csv_file,test_type_to_check
    parser = argparse.ArgumentParser(description="Description: "+sys.modules[__name__].__doc__)
    parser.add_argument('-name','--name',required=False,default='',help='Optional name used for output files/logs.')
    parser.add_argument('-d','--debug',action='store_true',help='print a lot of debug stuff to dlog')
    parser.add_argument('-out','--output_dir',required=True,default='', help='Directory to place output files/logs.')
    parser.add_argument('-max','--maxlogs',type=int,default=1,required=False, help='(0=OFF:log data to stdout). Set to 1 to keep only one log (subsequent runs will overwrite).')
    parser.add_argument('-r','--renumber',action='store_true',help='Re-number "Test number" column across all STANDARD csv testtables')
    parser.add_argument('-s','--split',action='store_true',help='split image files into top level groups (USE THIS OPTION FOR REALLY LARGE TESTFLOW FILES!')
    parser.add_argument('-tf','--testflow_file',required=False,default='', help='name of testflow file (Example: Final_RPC_flow(.tf or .mfh)\
                        WARNING: THIS GOES WITH -tt (--testtable_file), BUT NOT WITH -tp (--testprog_file)')
    parser.add_argument('-tt','--testtable_file',required=False,default='', help='name of testtable file type csv file (Example: Kepler_TestNameTypeList.csv)\
                        WARNING: THIS GOES WITH -tf (--testflow_file), BUT NOT WITH -tp (--testprog_file)')
    parser.add_argument('-tp','--testprog_file',required=False,default='', help='name of testprog file (Example: F791857_Final_RPC.tpg)\
                        WARNING: THIS DOES NOT GO WITH -tt (--testtable_file) OR WITH -tf (--testflow_file)')
    parser.add_argument('-ignore','--ignore_suites',required=False, help='Ignore testsuites file. Place testsuites (\'\\n\' separated) in this text file to suppress in csv output')
    parser.add_argument('-bin','--binning_csv',required=True, help='Path to bining csv file (Example: BinningKepler.csv')
    parser.add_argument('-tt2c','--test_type_to_check',required=False,default='', help='check this test type against binning groups')

    args = parser.parse_args()

    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logger_name,outdir = init_logging(scriptname=os.path.basename(sys.modules[__name__].__file__),
                                      outdir=args.output_dir, name=args.name, maxlogs=args.maxlogs ,level=log_level)

    log = logging.getLogger(logger_name)
    log.warning=callcounted(log.warning)
    log.error=callcounted(log.error)

    msg = 'Running ' + os.path.basename(sys.modules[__name__].__file__) + '...'
    print msg
    log.info(msg)

    if args.ignore_suites is not None:
        try:
            with open(args.ignore_suites, 'r') as f:
                ignore_suites = [x.strip() for x in f.readlines()]
        except:
            err = '%s is NOT a valid ignore file. Skipping your ignore file.'.format(args.ignore_suites)
            print err
            log.error(err)
        ignore_str = '\n\t'.join(ignore_suites)
        msg = 'IGNORING THE FOLLOWING TESTSUITES:\n\t'+ignore_str
        # print msg
        log.info(msg)

    if len(args.testprog_file):
        if len(args.testflow_file) or len(args.testtable_file):
            err = 'INPUT ERROR!!! testprog_file (-tp) already provided.  Cannot provide testflow_file (-tf) and/or testtable_file (-tt) also! Exiting ...'
            log.error(err)
            sys.exit(err)
        tp = ProgFile(pathfn=args.testprog_file,debug=args.debug,progname=args.name,maxlogs=args.maxlogs,outdir=args.output_dir)
        testflow_file = os.path.join(tp.progdir,'testflow',tp.contents['Testflow'])
        testtable_file = os.path.join(tp.progdir,'testtable',tp.contents['Testtable'])
    elif len(args.testflow_file) and len(args.testtable_file):
        testflow_file = args.testflow_file
        testtable_file = args.testtable_file
    else:
        err = 'UNSTABLE INPUT: Must provide either testprog_file (-tp) OR both testflow_file (-tf) AND testtable_file (-tt) BUT not all 3! Exiting ...'
        log.error(err)
        sys.exit(err)

    # need this global for easy access
    test_type_to_check = args.test_type_to_check

    # silently ignoring path (in case the user was being silly).  We already have the path
    binning_csv_file = os.path.basename(args.binning_csv)

    testflow = Testflow(tf_file=testflow_file,split=args.split,debug=args.debug,progname=args.name,
                        maxlogs=args.maxlogs,outdir=args.output_dir)
    testtable = TestTable(testtable_file, args.renumber, debug=args.debug, progname=args.name, maxlogs=args.maxlogs,
                          outdir=args.output_dir, ignore_csv_files=[args.binning_csv])

    identify_ti_csv_files(testtable.special_testtables)
    ti_binning_file = os.path.join(os.path.dirname(categories_file),binning_csv_file)

    parse_special_csv(ti_binning_file,csv_type='ti_binning')
    if bin_groups_file is not None:
        parse_special_csv(bin_groups_file,csv_type='bin_groups')
        bin_groups_exist = True
    parse_special_csv(speed_sort_groups_file,csv_type='speed_sort_groups')
    parse_special_csv(test_name_type_file,csv_type='test_name_type')
    parse_special_csv(categories_file,csv_type='categories')

    gather_all_testsuites_bins()
    find_actual_binning()

    create_ti_binning_csv(scriptname=os.path.basename(sys.modules[__name__].__file__), outdir=args.output_dir,
                          fn=args.name, maxlogs=max(1, args.maxlogs))
    create_flowaudit_csv(scriptname=os.path.basename(sys.modules[__name__].__file__), outdir=args.output_dir,
                         fn=args.name+'_ActualFlowBins', maxlogs=max(1, args.maxlogs))
    create_softbinaudit_csv(scriptname=os.path.basename(sys.modules[__name__].__file__), outdir=args.output_dir,
                            fn=args.name+'_ActualSoftBinDefs', maxlogs=max(1, args.maxlogs))
    create_hardbinaudit_csv(scriptname=os.path.basename(sys.modules[__name__].__file__), outdir=args.output_dir,
                            fn=args.name+'_ActualHarBinDefs', maxlogs=max(1, args.maxlogs))

    if tt2c_valid:
        create_tt_missing_suites_csv(scriptname=os.path.basename(sys.modules[__name__].__file__), outdir=args.output_dir,
                                     fn=args.name+'_TestTypeMissingSuites_'+test_type_to_check+'_', maxlogs=max(1, args.maxlogs))

    # For debug and future development, list this module's data containers and their contents
    log.debug('ti_binning:\n' + pformat(ti_binning,indent=4))
    log.debug('bin_groups:\n' + pformat(bin_groups,indent=4))
    log.debug('speed_sort_groups:\n' + pformat(speed_sort_groups,indent=4))
    log.debug('test_name_type:\n' + pformat(test_name_type,indent=4))
    log.debug('category_defs:\n' + pformat(category_defs,indent=4))
    log.debug('category_tests:\n' + pformat(category_tests,indent=4))
    log.debug('categories_extra_tests:\n' + pformat(categories_extra_tests,indent=4))
    log.debug('testflow_extra_tests:\n' + pformat(testflow_extra_tests,indent=4))
    log.debug('testflow_binning:\n' + pformat(testflow_binning, indent=4))
    log.debug('testflow_bin_defs:\n' + pformat(testflow_bin_defs, indent=4))

    log.info('ARGUMENTS:\n\t'+'\n\t'.join(['--'+k+'='+str(v) for k,v in args.__dict__.iteritems()]))
    msg = 'Number of WARNINGS for "{}": {}'.format(os.path.basename(sys.modules[__name__].__file__),log.warning.counter)
    print msg
    log.info(msg)
    msg = 'Number of ERRORS for "{}": {}'.format(os.path.basename(sys.modules[__name__].__file__),log.error.counter)
    print msg
    log.info(msg)


if __name__ == "__main__":
    main()

    time = time.time()-_start_time
    msg = 'Script took ' + str(round(time,3)) + ' seconds (' + humanize_time(time) + ')'
    log.info(msg)
    print '\n' + msg
