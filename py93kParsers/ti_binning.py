#!/usr/bin/env python
"""
The script needs to know:
Where your Testflow file (may or may not be mfh) is located.
Where your Testtables file (MUST be mfh) is located.

So, you can provide:
A. Path to Testflow file AND Testtable (limit mfh) file

	OR ...

B. Path to your Testprog file which indicates your Testflow file and Testtable (limit mfh) file.

Do not try to provide a mixture of both A and B

It is also recommended that you provide a name, especially if you want to track revisions of your program (i.e. kepler_pg2)

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

PARTIAL_BINNING_METHOD = 'ti_tml.Misc.Binning'

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

OTHER_BIN = '13'

UTM_HARDCODED_TESTNAMES = [
    'ArrIddQStorageProg_st',
    'DeltaTemp',
    'ElevatedCTProg_st',
    'FTMemRepEFProg_st',
    'IDDQ_VDDARR_Vnom_Hardline_st',
    'IDDQ_VDD_Vmin_Hardline_st',
    'IDDQ_VDD_Vnom_Hardline_st',
    'IddqVnom_burnin_bin1',
    'IddqVnom_burnin_bin2',
    'IddqVnom_burnin_bin3',
    'IddqVnom_burnin_bin4',
    'IddqVnom_burnin_bin5',
    'MEMORYREPAIRED',
    'MemBistInit_st',
    'PostAdaptiveRepair_st',
    'SRc0BuildStr_st',
    'SRc0Power_st',
    'SampleDieProg_st',
    'SmartReflexRead_st',
    'TDiodeRead_st',
    'TFTFmaxProg_st',
    'TFTOutlier_st',
    'T_CRITICAL_TEMPERATURE',
    'T_CTCS_MAX_READ',
    'T_CTCS_MIN_READ',
    'T_TD_MAX_READ',
    'T_TD_MIN_READ',
    'TempStorageProg_st',
    'VIDSpeedOutOfSpace_st',
    'VIDSpeedProg_st',
    'VerifyProgramVIDSpeeds_st',
    'adaptiveRepairPatterns_st',
    'adaptiveRepair_st',
    'alreadyRepair_st',
    'leak_iddq_fail',
]

testflow = None
testflow_file = None
testtable = None
categories_file = None
test_name_type_file = None
speed_sort_groups_file = None
speed_sort_suites_file = None
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

ignore_suites_file = []

ti_binning = {}

testflow_binning = {}

testflow_bin_defs = {}

hard_bins = {}

suites_w_exclamation = []

def get_category_testname(test, sbin):
    global category_tests,suites_w_exclamation

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
        suites_w_exclamation.append(test)
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
            categories_extra_tests = categories_extra_tests - set(ignore_suites_file)
            testflow_extra_tests = set(testflow.testsuite_data.keys()) - set(category_tests.keys())
            testflow_extra_tests = testflow_extra_tests - set(ignore_suites_file)

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

            # let's first determine if any descendents are partial binning test method suites
            has_partial_bin_suite_below = False
            for desc in descendants:
                try:
                    desc_id = int(desc.split('-')[-1])
                except:
                    # can't make int out of id, which means it can't be a bin anyways... skip
                    continue
                if testflow.nodeData[desc_id]['type'] in ['RunStatement','RunAndBranchStatement'] and testflow.is_partial_suite[desc_id]:
                    # okay, let's set the log,flag and jump out of loop
                    log.info('Suite: "%s" has a downstream Partial Binning Testmethod Testsuite.\n\tDownstream Suite: %s\n\tTestmethod: %s',
                             tf_testsuite,testflow.nodeData[desc_id]['testsuite'],PARTIAL_BINNING_METHOD)
                    has_partial_bin_suite_below = True
                    break

            # let's loop again, this time looking for stop or multi bins
            for desc in descendants:
                try:
                    desc_id = int(desc.split('-')[-1])
                except:
                    # can't make int out of id, which means it can't be a bin anyways... skip
                    continue

                if testflow.nodeData[desc_id]['type'] == 'StopBinStatement':
                    if 'over_on' == testflow.nodeData[desc_id]['overon']:
                        Bin_overon = True
                    elif 'not_over_on' == testflow.nodeData[desc_id]['overon']:
                        Bin_overon = False
                    else:
                        err = 'Unknown overon setting for node_id: {}'.format(desc_id)
                        log.error(err)
                        sys.exit(err)
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
                            'Bin_h_name' : Bin_h_name,
                            'Bin_overon' : Bin_overon
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

            if tf_testsuite in testtable.testsuite_sbins and not has_partial_bin_suite_below:
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
            if testsuite not in ignore_suites_file:
                writer.writerow({'node_id' : testflow.testsuite_nodeids[testsuite],
                                 'SuiteName' : testsuite,
                                 'bypassed' : 'Y' if testsuite in testflow.bypassed_testsuites else '',
                                 'stop_sbins': '|'.join(testsuite_all_sbins[testsuite]['stop_sbins']),
                                 'category_sbins': '|'.join(testsuite_all_sbins[testsuite]['cat_sbins']),
                                 'multi_sbins': '|'.join(testsuite_all_sbins[testsuite]['multi_sbins'])})

def addTiBinningSheet(wkBook):
    assert isinstance(wkBook, xlwt.Workbook)
    headers = ['SuiteName','bypassed','stop_sbins','category_sbins','multi_sbins']
    sheet = wkBook.add_sheet("TI_Binning")

    _addTitle(sheet, headers)
    currRow = 1
    for testsuite in testsuite_all_sbins:
        if testsuite not in ignore_suites_file:
            sheet.row(currRow).write(0, testsuite, style = bodyLeft)
            sheet.row(currRow).write(1, 'Y' if testsuite in testflow.bypassed_testsuites else '', style=bodyLeft)
            sheet.row(currRow).write(2, '|'.join(testsuite_all_sbins[testsuite]['stop_sbins']), style=bodyLeft)
            sheet.row(currRow).write(3, '|'.join(testsuite_all_sbins[testsuite]['cat_sbins']), style=bodyLeft)
            sheet.row(currRow).write(4, '|'.join(testsuite_all_sbins[testsuite]['multi_sbins']), style=bodyLeft)
            currRow += 1

def addFlowAuditSheet(wkBook):
    assert isinstance(wkBook, xlwt.Workbook)
    # need this section to create a list of tuples that can be sorted later (next section of code)
    unsorted_rows = []
    all_suites = []
    duplicate_suites = []
    for ts,values in testflow_binning.iteritems():
        nid = testflow.testsuite_nodeids[ts]
        nid = re.sub('\d+', lambda x:x.group().zfill(20), str(nid))
        if len(values):
            for v in values:
                hbin = re.sub('\d+', lambda x:x.group().zfill(20), v['Bin_h_num'])
                unsorted_rows.append((nid,ts,v['Bin_s_num'],v['Bin_s_name'],hbin,v['Bin_h_name'],v['bintype'],v['Bin_overon']))
                if ts not in all_suites:
                    all_suites.append(ts)
                else:
                    duplicate_suites.append(ts)
        else:
            unsorted_rows.append((nid,ts,'MISSING BIN INFO','---','---','---','---',False))

    if tt2c_valid:
        headers = ['Bypassed','SuiteName','SoftBinNum','SoftBinName','HardBinName','BinNumber','BinSource','BinOveron(local)','Testmethod',os.path.basename(test_name_type_file)+' : '+test_type_to_check]
    else:
        headers = ['Bypassed','SuiteName','SoftBinNum','SoftBinName','HardBinName','BinNumber','BinSource','BinOveron(local)','Testmethod',]
    sheet = wkBook.add_sheet("FlOW_BINNING")
    _addTitle(sheet, headers)
    currRow = 1
    for nid,suite,sbin,sname,hbin,hname,bintype,overon in sorted(unsorted_rows, key=lambda x: (x[0],x[4],x[2])):
        if suite in ignore_suites_file:
            continue
        end = ''
        if 'Testmethods' in testflow.testsuite_data[suite] and 'Class' in testflow.testsuite_data[suite]['Testmethods']:
            testmethod = testflow.testsuite_data[suite]['Testmethods']['Class'].strip('"')
        else:
            testmethod = ''
        if suite in duplicate_suites:
            if bintype == 'multi':
                binkey = (str(int(sbin)),sname,str(int(hbin)),hname)
                if binkey in testtable.binning2testname:
                    testlist = []
                    for test in testtable.binning2testname[binkey]:
                        if test not in testlist:
                            testlist.append(test)
                            end += ' : '+test
                    end = end.lstrip(' : ')
            else:
                end = 'DUPLICATE'
        if len(end):
            suite2show = suite + ' -- ' + end
        else:
            suite2show = suite
        if tt2c_valid:
            if suite in test_name_type:
                if bintype == 'cat' and category_tests[suite][sbin]['ignore']:
                    exclam = '!'
                else:
                    exclam = ''
                tt2c = exclam+test_name_type[suite][test_type_to_check]
            else:
                tt2c = 'MISSING TestNameType ENTRY'
                tt2c_log = 'SUITE: "{}" NOT IN "{}"'.format(suite,os.path.basename(test_name_type_file))
                log.warning(tt2c_log+'\tNOTE: this WARNING is also in binning sheet')


        sheet.row(currRow).write(0, 'Y' if suite in testflow.bypassed_testsuites else '', style = bodyLeft)
        sheet.row(currRow).write(1, suite2show, style = bodyLeft)
        sheet.row(currRow).write(2, sbin.lstrip('0'), style = bodyLeft)
        sheet.row(currRow).write(3, sname , style = bodyLeft)
        sheet.row(currRow).write(4, hname, style = bodyLeft)
        sheet.row(currRow).write(5, hbin.lstrip('0'), style = bodyLeft)
        sheet.row(currRow).write(6, bintype, style = bodyLeft)
        sheet.row(currRow).write(7, 'Y' if overon else '', style = bodyLeft)
        sheet.row(currRow).write(8, testmethod, style = bodyLeft)
        if tt2c_valid:
            sheet.row(currRow).write(9, tt2c, style = bodyLeft)
        currRow +=1

def create_flowaudit_csv(scriptname=os.path.basename(sys.modules[__name__].__file__), outdir='', fn='', maxlogs=1):
    csv_file,outdir,info_msg,warn_msg = get_valid_file(scriptname=scriptname, name=fn, outdir=outdir, maxlogs=maxlogs, ext='.csv')
    for msg in warn_msg:
        print 'WARNING!!! ',msg
        log.warning(msg)
    for msg in info_msg:
        log.info(msg)

    # need this section to create a list of tuples that can be sorted later (next section of code)
    unsorted_rows = []
    all_suites = []
    duplicate_suites = []
    for ts,values in testflow_binning.iteritems():
        nid = testflow.testsuite_nodeids[ts]
        nid = re.sub('\d+', lambda x:x.group().zfill(20), str(nid))
        if len(values):
            for v in values:
                hbin = re.sub('\d+', lambda x:x.group().zfill(20), v['Bin_h_num'])
                unsorted_rows.append((nid,ts,v['Bin_s_num'],v['Bin_s_name'],hbin,v['Bin_h_name'],v['bintype'],v['Bin_overon']))
                if ts not in all_suites:
                    all_suites.append(ts)
                else:
                    duplicate_suites.append(ts)
        else:
            unsorted_rows.append((nid,ts,'MISSING BIN INFO','---','---','---','---',False))

    if tt2c_valid:
        headers = ['node_id','Bypassed','SuiteName','SoftBinNum','SoftBinName','HardBinName','BinNumber','BinSource','BinOveron(local)','Testmethod',os.path.basename(test_name_type_file)+' : '+test_type_to_check]
    else:
        headers = ['node_id','Bypassed','SuiteName','SoftBinNum','SoftBinName','HardBinName','BinNumber','BinSource','BinOveron(local)','Testmethod',]
    with open(csv_file,'wb') as csvFile:
        writer = csv.DictWriter(csvFile,fieldnames=headers)
        writer.writeheader()
        for nid,suite,sbin,sname,hbin,hname,bintype,overon in sorted(unsorted_rows, key=lambda x: (x[0],x[4],x[2])):
            if suite in ignore_suites_file:
                continue
            end = ''
            if 'Testmethods' in testflow.testsuite_data[suite] and 'Class' in testflow.testsuite_data[suite]['Testmethods']:
                testmethod = testflow.testsuite_data[suite]['Testmethods']['Class'].strip('"')
            else:
                testmethod = ''
            if suite in duplicate_suites:
                if bintype == 'multi':
                    binkey = (str(int(sbin)),sname,str(int(hbin)),hname)
                    if binkey in testtable.binning2testname:
                        testlist = []
                        for test in testtable.binning2testname[binkey]:
                            if test not in testlist:
                                testlist.append(test)
                                end += ' : '+test
                        end = end.lstrip(' : ')
                else:
                    end = 'DUPLICATE'
            if len(end):
                suite2show = suite + ' -- ' + end
            else:
                suite2show = suite
            if tt2c_valid:
                if suite in test_name_type:
                    if bintype == 'cat' and category_tests[suite][sbin]['ignore']:
                        exclam = '!'
                    else:
                        exclam = ''
                    tt2c = exclam+test_name_type[suite][test_type_to_check]
                else:
                    tt2c = 'MISSING TestNameType ENTRY'
                    tt2c_log = 'SUITE: "{}" NOT IN "{}"'.format(suite,os.path.basename(test_name_type_file))
                    log.warning(tt2c_log+'\tNOTE: this WARNING is also in "%s"',os.path.basename(csv_file))
                writer.writerow({'node_id' : int(nid),
                                 'Bypassed' : 'Y' if suite in testflow.bypassed_testsuites else '',
                                 'SuiteName' : suite2show,
                                 'SoftBinNum' : sbin.lstrip('0'),
                                 'SoftBinName' : sname,
                                 'HardBinName' : hname,
                                 'BinNumber' : hbin.lstrip('0'),
                                 'BinSource' : bintype,
                                 'BinOveron(local)' : 'Y' if overon else '',
                                 'Testmethod' : testmethod,
                                 os.path.basename(test_name_type_file)+' : '+test_type_to_check : tt2c})
            else:
                writer.writerow({'node_id' : int(nid),
                                 'Bypassed' : 'Y' if suite in testflow.bypassed_testsuites else '',
                                 'SuiteName' : suite2show,
                                 'SoftBinNum' : sbin.lstrip('0'),
                                 'SoftBinName' : sname,
                                 'HardBinName' : hname,
                                 'BinNumber' : hbin.lstrip('0'),
                                 'BinSource' : bintype,
                                 'BinOveron(local)' : 'Y' if overon else '',
                                 'Testmethod' : testmethod})

import xlwt
from genOut import titleStyle, bodyStyle, titleLeft, bodyLeft, _addTitle
def addSoftBinSheet(wkBook):
    unsorted_sbin_rows = []
    for sbin,values in testflow_bin_defs['sbins'].iteritems():
        sbin = re.sub('\d+', lambda x:x.group().zfill(20), sbin)
        if len(values):
            for v in values:
                unsorted_sbin_rows.append((sbin,v['Bin_s_name'],v['Bin_h_num'],v['Bin_h_name']))
        else:
            unsorted_sbin_rows.append((sbin,'MISSING BIN INFO','---','---'))

    headers = ['SoftBinNumber','SoftBinName','HardBinName','HardBinNumber']
    assert isinstance(wkBook, xlwt.Workbook)
    sheet = wkBook.add_sheet("SOFT_BINS")
    _addTitle(sheet, headers)
    currRow = 1
    for sbin,sname,hbin,hname in sorted(unsorted_sbin_rows, key=lambda x: (x[0],x[3])):
        sheet.row(currRow).write(0, sbin.lstrip('0'), style = bodyLeft)
        sheet.row(currRow).write(1, sname, style = bodyLeft)
        sheet.row(currRow).write(2, hname, style = bodyLeft)
        sheet.row(currRow).write(3, hbin.lstrip('0'), style = bodyLeft)
        currRow +=1
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
            unsorted_sbin_rows.append((sbin,'MISSING BIN INFO','---','---'))

    headers = ['SoftBinNumber','SoftBinName','HardBinName','HardBinNumber']
    with open(csv_file,'wb') as csvFile:
        writer = csv.DictWriter(csvFile,fieldnames=headers)
        writer.writeheader()
        for sbin,sname,hbin,hname in sorted(unsorted_sbin_rows, key=lambda x: (x[0],x[3])):
            writer.writerow({'SoftBinNumber' : sbin.lstrip('0'),
                             'SoftBinName': sname,
                             'HardBinName': hname,
                             'HardBinNumber': hbin.lstrip('0')})

def addHBins(wkBook):
    unsorted_hbin_rows = []
    for hbin,values in testflow_bin_defs['hbins'].iteritems():
        hbin = re.sub('\d+', lambda x:x.group().zfill(20), str(hbin))
        if len(values):
            for hname in values:
                unsorted_hbin_rows.append((hname,hbin))
        else:
            unsorted_hbin_rows.append(('',hbin))

    headers = ['HardBinName','HardBinNumber']
    sheet = wkBook.add_sheet("HARD_BINS")
    _addTitle(sheet, headers)
    currRow=1
    for hname,hbin in sorted(unsorted_hbin_rows, key=lambda x: (x[1],x[0])):
        sheet.row(currRow).write(0, hname, style = bodyLeft)
        sheet.row(currRow).write(1, hbin.lstrip('0'))
        currRow += 1

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
def addCatIssues(wkBook):
    assert isinstance(wkBook,xlwt.Workbook)
    sheet = wkBook.add_sheet("CATEGORY_ISSUES")
    testsuite_superset = list(set(testflow_binning.keys()) | categories_extra_tests | set(UTM_HARDCODED_TESTNAMES))

    failchecks = {}
    failcheck_desc = [

        # TODO: change these to tuples to have their fail index with them, since they are no longer serial (we have to change in 4 or 5 places every time this gets updated)

        # ERRORS (<10)
        ('set_pass OR set_fail','ERROR: These testsuite flags CAN break Category binning.'), # 0
        ('InTestflow AND Bypassed AND NOT Bang ("!") AND TT=1','ERROR: Major problem here.  Causes Bin 13.'), # 1
        ('InTestflow AND NOT InCategories','ERROR: All Testsuites in this file use Category binning. (no stop bin or multi bin "downstream").'), # 2
        ('HARDCODED Testname NOT InCategories','ERROR: This Testname must be in BinningCategories.csv because it is hardcoded in the UTM.'), # 3

        # WARNINGS (>=10)
        ('NOT InTestflow AND TT=1','WARNING: This testsuite MUST be in your flow (TT=1) even if bypassed, but it\'s not. Why?'), # 10
        ('InTestflow AND TT=0','WARNING: Potential test escape.  If this testsuite fails, you will not know.'), # 11
        ('InTestflow AND NOT InTestTypes','WARNING: Defaults to "1" but you should probably add it to TestTypes to be explicit.') # 12
    ]

    hdr_null = ['--------------------------------------']
    hdr1 = ['CheckIndex','CheckType','CheckDescription']
    hdr2 = ['Suite','FailedChecks','BinSource','Bypassed?','TestTypeValue : '+test_type_to_check,'Bang? ("!")','set_pass?','set_fail?','InTestflow?','InCategories?','InTestTypes?']
    _addTitle(sheet, hdr1)
    idMap = {4:'10', 5:'11',6:'12'}
    for i,check in enumerate(failcheck_desc):
        try:
            idx = idMap[i]
        except KeyError:
            idx  = str(i)
        sheet.row(i+1).write(0, idx, style = bodyLeft)
        sheet.row(i+1).write(1, check[0], style = bodyLeft)
        sheet.row(i+1).write(2, check[1], style = bodyLeft)

    currRow = i+2
    _addTitle(sheet, hdr2, startRow=currRow)
    currRow +=1
    for ts in testsuite_superset:
        if ts in testflow.partial_suites or ts in ignore_suites_file:
             continue
        # initialize all checks to False(Pass)
        failchecks[ts] = [False]*100
        # set flags and values
        InTestflow = False # init value
        nid = '' # init value
        if ts in testflow_binning:
            InTestflow = True
            double_loop_flag = False
            for i,elem in enumerate(testflow_binning[ts]):
                if elem['bintype'] != 'cat':
                    double_loop_flag = True
                    break
                elif i > 1:
                    err = 'Testsuite: "{}" is using category binning and has more than 1 definition'.format(ts)
                    print err
                    log.error(err)
            if double_loop_flag:
                continue

            bypass = ts in testflow.bypassed_testsuites
            set_fail = 'set_fail' in testflow.testsuite_data[ts]['TestsuiteFlags']
            set_pass = 'set_pass' in testflow.testsuite_data[ts]['TestsuiteFlags']
            bang = ts in suites_w_exclamation
        # else:
        #     continue
        InCategories = ts in category_tests
        InTestTypes = ts in test_name_type
        if InTestTypes:
            testtype_value = test_name_type[ts][test_type_to_check]
        else:
            testtype_value = None

        # Ok, let's start checking for problems

        # ERRORS
        # ho hum, more tediousness... gotta make these indices dynamic instead of hardcoding them... later
        if set_pass or set_fail:
            failchecks[ts][0] = True
        if InTestflow and bypass and not bang and '1' == testtype_value:
            failchecks[ts][1] = True
        if InTestflow and not InCategories:
            failchecks[ts][2] = True
        if ts in UTM_HARDCODED_TESTNAMES and not InCategories:
            failchecks[ts][3] = True

        # WARNINGS
        if not InTestflow and '1' == testtype_value:
            failchecks[ts][10] = True
        if InTestflow and '0' == testtype_value:
            failchecks[ts][11] = True
        if InTestflow and not InTestTypes:
            failchecks[ts][12] = True

        if any(failchecks[ts]):
            sheet.row(currRow).write(0, ts, style = bodyLeft)
            sheet.row(currRow).write(1,','.join([str(i) for i,x in enumerate(failchecks[ts]) if x]), style = bodyLeft)
            sheet.row(currRow).write(2, 'cat', style = bodyLeft)
            sheet.row(currRow).write(3,  'Y' if bypass else '', style = bodyLeft)
            sheet.row(currRow).write(4, testtype_value, style = bodyLeft)
            sheet.row(currRow).write(5, 'Y' if bang else '', style = bodyLeft)
            sheet.row(currRow).write(6, 'Y' if set_pass else '', style = bodyLeft)
            sheet.row(currRow).write(7, 'Y' if set_fail else '', style = bodyLeft)
            sheet.row(currRow).write(8, 'Y' if InTestflow else '', style = bodyLeft)
            sheet.row(currRow).write(9, 'Y' if InCategories else '', style = bodyLeft)
            sheet.row(currRow).write(10, 'Y' if InTestTypes else '', style = bodyLeft)
            currRow +=1



def create_cat_issues_csv(scriptname=os.path.basename(sys.modules[__name__].__file__), outdir='', fn='', maxlogs=1):
    csv_file,outdir,info_msg,warn_msg = get_valid_file(scriptname=scriptname, name=fn, outdir=outdir, maxlogs=maxlogs, ext='.csv')
    for msg in warn_msg:
        print 'WARNING!!! ',msg
        log.warning(msg)
    for msg in info_msg:
        log.info(msg)

    # get union (unique set) of suites in flow and not in flow and create a list of them
    testsuite_superset = list(set(testflow_binning.keys()) | categories_extra_tests | set(UTM_HARDCODED_TESTNAMES))

    failchecks = {}
    failcheck_desc = [

        # TODO: change these to tuples to have their fail index with them, since they are no longer serial (we have to change in 4 or 5 places every time this gets updated)

        # ERRORS (<10)
        ('set_pass OR set_fail','ERROR: These testsuite flags CAN break Category binning.'), # 0
        ('InTestflow AND Bypassed AND NOT Bang ("!") AND TT=1','ERROR: Major problem here.  Causes Bin 13.'), # 1
        ('InTestflow AND NOT InCategories','ERROR: All Testsuites in this file use Category binning. (no stop bin or multi bin "downstream").'), # 2
        ('HARDCODED Testname NOT InCategories','ERROR: This Testname must be in BinningCategories.csv because it is hardcoded in the UTM.'), # 3

        # WARNINGS (>=10)
        ('NOT InTestflow AND TT=1','WARNING: This testsuite MUST be in your flow (TT=1) even if bypassed, but it\'s not. Why?'), # 10
        ('InTestflow AND TT=0','WARNING: Potential test escape.  If this testsuite fails, you will not know.'), # 11
        ('InTestflow AND NOT InTestTypes','WARNING: Defaults to "1" but you should probably add it to TestTypes to be explicit.') # 12
    ]

    hdr_null = ['--------------------------------------']
    hdr1 = ['CheckIndex','CheckType','CheckDescription']
    hdr2 = ['node_id','Suite','FailedChecks','BinSource','Bypassed?','TestTypeValue : '+test_type_to_check,'Bang? ("!")','set_pass?','set_fail?','InTestflow?','InCategories?','InTestTypes?']

    with open(csv_file,'wb') as csvFile:
        writer = csv.DictWriter(csvFile,fieldnames=hdr1)
        writer.writeheader()
        for i,check in enumerate(failcheck_desc):

            # tedious, i know, but i'm pressed for time
            if i == 4:
                idx = 10
            elif i == 5:
                idx = 11
            elif i == 6:
                idx = 12
            else:
                idx = i

            writer.writerow({'CheckIndex': idx,
                             'CheckType': check[0],
                             'CheckDescription': check[1]})
        writer = csv.DictWriter(csvFile,fieldnames=hdr_null)
        writer.writeheader()
        writer = csv.DictWriter(csvFile,fieldnames=hdr2)
        writer.writeheader()

        for ts in testsuite_superset:
            if ts in testflow.partial_suites or ts in ignore_suites_file:
                 continue
            # initialize all checks to False(Pass)
            failchecks[ts] = [False]*100
            # set flags and values
            InTestflow = False # init value
            nid = '' # init value
            if ts in testflow_binning:
                InTestflow = True
                double_loop_flag = False
                for i,elem in enumerate(testflow_binning[ts]):
                    if elem['bintype'] != 'cat':
                        double_loop_flag = True
                        break
                    elif i > 1:
                        err = 'Testsuite: "{}" is using category binning and has more than 1 definition'.format(ts)
                        print err
                        log.error(err)
                if double_loop_flag:
                    continue
                nid = int(testflow.testsuite_nodeids[ts])
                bypass = ts in testflow.bypassed_testsuites
                set_fail = 'set_fail' in testflow.testsuite_data[ts]['TestsuiteFlags']
                set_pass = 'set_pass' in testflow.testsuite_data[ts]['TestsuiteFlags']
                bang = ts in suites_w_exclamation
            # else:
            #     continue
            InCategories = ts in category_tests
            InTestTypes = ts in test_name_type
            if InTestTypes:
                testtype_value = test_name_type[ts][test_type_to_check]
            else:
                testtype_value = None

            # Ok, let's start checking for problems

            # ERRORS
            # ho hum, more tediousness... gotta make these indices dynamic instead of hardcoding them... later
            if set_pass or set_fail:
                failchecks[ts][0] = True
            if InTestflow and bypass and not bang and '1' == testtype_value:
                failchecks[ts][1] = True
            if InTestflow and not InCategories:
                failchecks[ts][2] = True
            if ts in UTM_HARDCODED_TESTNAMES and not InCategories:
                failchecks[ts][3] = True

            # WARNINGS
            if not InTestflow and '1' == testtype_value and ts not in UTM_HARDCODED_TESTNAMES:
                failchecks[ts][10] = True
            if InTestflow and '0' == testtype_value:
                failchecks[ts][11] = True
            if InTestflow and not InTestTypes:
                failchecks[ts][12] = True

            if any(failchecks[ts]):
                writer.writerow({'node_id' : nid,
                                 'Suite': ts,
                                 'FailedChecks': ','.join([str(i) for i,x in enumerate(failchecks[ts]) if x]),
                                 'BinSource': 'cat',
                                 'Bypassed?': 'Y' if bypass else '',
                                 'TestTypeValue : '+test_type_to_check : testtype_value,
                                 'Bang? ("!")':  'Y' if bang else '',
                                 'set_pass?':  'Y' if set_pass else '',
                                 'set_fail?':  'Y' if set_fail else '',
                                 'InTestflow?': 'Y' if InTestflow else '',
                                 'InCategories?': 'Y' if InCategories else '',
                                 'InTestTypes?': 'Y' if InTestTypes else ''
                                 })

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
                    'Bin_overon' : hard_bins[sbin]['Bin_overon'],
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
                        'Bin_overon' : testtable.binning[sbin]['Bin_overon'],
                        'bintype' : bintype
                    })

        if not len(bintype) and len(v['cat_sbins']):
            bintype = 'cat'
            for sbin in v['cat_sbins']:
                if sbin in ti_binning:
                    bin_info[ts].append({
                        'Bin_s_num' : sbin,
                        'Bin_s_name' : ti_binning[sbin]['Bin_s_name'],
                        'Bin_h_num' : ti_binning[sbin]['Bin_h_num'],
                        'Bin_h_name' : ti_binning[sbin]['Bin_h_name'],
                        'Bin_overon' : False,
                        'bintype' : bintype
                    })
                else:
                    bin_info[ts].append({
                        'Bin_s_num' : sbin,
                        'Bin_s_name' : 'MISSING BIN INFO',
                        'Bin_h_num' : '---',
                        'Bin_h_name' : '---',
                        'Bin_overon' : False,
                        'bintype' : bintype
                    })

        if len(bintype) and len(bin_info[ts]):
            testflow_binning[ts] = bin_info[ts]
    find_actual_bindefs()

def main():
    global log,ignore_suites_file,testflow,testflow_file,testtable,bin_groups_exist,binning_csv_file,test_type_to_check,use_cats
    parser = argparse.ArgumentParser(description="Description: "+sys.modules[__name__].__doc__)
    parser.add_argument('-name','--name',required=False,default='',help='Optional name used for output files/logs.')
    parser.add_argument('-d','--debug',action='store_true',help='Print a lot of debug stuff to dlog')
    parser.add_argument('-out','--output_dir',required=True,default='', help='Directory to place output files/logs.')
    parser.add_argument('-max','--maxlogs',type=int,default=1,required=False, help='(0=OFF:log data to stdout). Set to 1 to keep only one log (subsequent runs will overwrite).')
    parser.add_argument('-r','--renumber',action='store_true',help='Re-number "Test number" column across all STANDARD csv testtables')
    parser.add_argument('-s','--split',action='store_true',help='Split image files into top level groups (USE THIS OPTION FOR REALLY LARGE TESTFLOW FILES!')
    parser.add_argument('-tf','--testflow_file',required=False,default='', help='Name of testflow file (Example: Final_RPC_flow(.tf or .mfh)\
                        WARNING: THIS GOES WITH -tt (--testtable_file), BUT NOT WITH -tp (--testprog_file)')
    parser.add_argument('-tt','--testtable_file',required=False,default='', help='Name of testtable file type csv file (Example: Kepler_TestNameTypeList.csv)\
                        WARNING: THIS GOES WITH -tf (--testflow_file), BUT NOT WITH -tp (--testprog_file)')
    parser.add_argument('-tp','--testprog_file',required=False,default='', help='Name of testprog file (Example: F791857_Final_RPC.tpg)\
                        WARNING: THIS DOES NOT GO WITH -tt (--testtable_file) OR WITH -tf (--testflow_file)')
    parser.add_argument('-ignore','--ignore_suites_file',required=False, help='Ignore testsuites file. Place testsuites (\'\\n\' separated) in this text file to suppress in csv output')
    parser.add_argument('-bin','--binning_csv',required=False,default='', help='Path to binning csv file (Example: BinningKepler.csv (use only with -c option to use categories)')
    parser.add_argument('-tt2c','--test_type_to_check',required=False,default='', help='Check this test type against binning groups (use only with -c option to use categories)')
    parser.add_argument('-pic','--pic_type',required=False,default='png',help='Type of pic desired for output (valid options: png[default], none)')
    parser.add_argument('-c','--categories',action='store_true',help='Add this option to use binning categories')

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

    if args.ignore_suites_file is not None:
        if os.path.isfile(args.ignore_suites_file):
            ignore_file = args.ignore_suites_file
        else:
            ignore_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),args.ignore_suites_file)
        try:
            with open(ignore_file, 'r') as f:
                ignore_suites_file = [x.strip() for x in f.readlines()]
        except:
            err = '{} is NOT a valid ignore file. Skipping your ignore file. (check permissions of file also)'.format(args.ignore_suites_file)
            print 'ERROR!!! '+err
            log.error(err)
            raise IOError
        ignore_str = '\n\t'.join(ignore_suites_file)
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

    use_cats = args.categories
    if use_cats:
        if not len(args.test_type_to_check):
            err = 'ILLEGAL ARGUMENT COMBINATION: You\'ve chosen TO USE category binning (-c option passed) but HAVE NOT SUPPLIED the test type to check (-tt2c).'
            log.error(err)
            sys.exit(err)
        else:
            test_type_to_check = args.test_type_to_check
        if not len(args.binning_csv):
            err = 'ILLEGAL ARGUMENT COMBINATION: You\'ve chosen TO USE category binning (-c option passed) but HAVE NOT SUPPLIED the binning csv file (-bin).'
            log.error(err)
            sys.exit(err)
        else:
            # silently ignoring path (in case the user was being silly).  We already have the path
            binning_csv_file = os.path.basename(args.binning_csv)
    elif len(args.test_type_to_check):
        err = 'ILLEGAL ARGUMENT COMBINATION: You\'ve chosen NOT TO USE category binning (-c option NOT passed) but HAVE SUPPLIED the test type to check (-tt2c).'
        log.error(err)
        sys.exit(err)
    elif len(args.binning_csv):
        err = 'ILLEGAL ARGUMENT COMBINATION: You\'ve chosen NOT TO USE category binning (-c option NOT passed) but HAVE NOT SUPPLIED the binning csv file (-bin).'
        log.error(err)
        sys.exit(err)
    else:
        test_type_to_check = None
        binning_csv_file = None

    testflow = Testflow(tf_file=testflow_file,split=args.split,debug=args.debug,progname=args.name,
                        maxlogs=args.maxlogs,outdir=args.output_dir,partial_bin_method=PARTIAL_BINNING_METHOD,pic_type=args.pic_type)
    testtable = TestTable(testtable_file, args.renumber, debug=args.debug, progname=args.name, maxlogs=args.maxlogs,
                          outdir=args.output_dir, ignore_csv_files=[args.binning_csv])

    if use_cats:
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

    if use_cats:
        create_cat_issues_csv(scriptname=os.path.basename(sys.modules[__name__].__file__), outdir=args.output_dir,
                              fn=args.name+'_CategoryBinningIssues_'+test_type_to_check+'_', maxlogs=max(1, args.maxlogs))

    if use_cats and OTHER_BIN in testtable.sbin_nums:
        err = '"#define sOtherBin \'13\'" defined in Binning_helper.cpp conflicts with standard testtable(s): "{}"'\
            .format(','.join(testtable.sbin_files[OTHER_BIN]))
        print 'ERROR!!! '+err
        log.error(err)
    if use_cats and OTHER_BIN not in ti_binning:
        err = 'No softbin 13 defined in: "{}"'.format(binning_csv_file)
        print 'ERROR!!! '+err
        log.error(err)

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
