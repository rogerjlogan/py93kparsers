#!/usr/bin/env python
"""
    This module parses the bin csv files.
"""

import re
import csv
import argparse
import logging
import sys
from pprint import *
import time
from common import *
from string import *
_start_time = time.time()
log = None

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

MAXLENGTH_TESTNAME = 30
MAXLENGTH_FILENAME = 30
MAXLENGTH_BINNUM = 10
MAXLENGTH_BINNAME = 30


class TestTable(object):

    __testnum = 0
    testtables = []
    special_testtables = []
    unordered_limit_data = {}
    all_row_keys = []
    testnums = []
    sbin_names = {}
    hbin_names = {}
    sbin_nums = {}
    hbin_nums = {}
    binmaps = {}

    sbin_name_err = {}
    sbin_num_to_testname = {}
    
    hbin_name_err = {}
    hbin_num_to_testname = {}
    
    sbin_num_err = {}
    sbin_name_to_testname = {}
    
    hbin_num_err = {}
    hbin_name_to_testname = {}

    binmap_err = {}
    binmap_err_tests = {}

    testsuite_sbins = {}

    binning = {}

    binning2testname = {}

    @staticmethod
    def getNewTestNumber():
        """Get unique 'Test number'"""
        TestTable.__testnum += 1
        return str(TestTable.__testnum)

    def __init__(self, pathfn, renum=False, debug=False, progname='', maxlogs=1,
                 outdir=os.path.dirname(os.path.realpath(__file__)), ignore_csv_files=[]):
        global log
        if debug:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
        logger_name,outdir = init_logging(scriptname=os.path.basename(sys.modules[__name__].__file__),
                                          outdir=outdir, name=progname, maxlogs=maxlogs ,level=log_level)
        log = logging.getLogger(logger_name)
        log.warning=callcounted(log.warning)
        log.error=callcounted(log.error)
        msg = 'Running ' + os.path.basename(sys.modules[__name__].__file__) + '...'
        # print msg
        log.info(msg)

        if renum:
            renum_msg = 'WARNING: You\'ve chosen to renumber ALL STANDARD testtables (limit files)?\n\t'
            renum_msg += 'DO YOU REALLY WANT TO RENUMBER "Test number" column IN PLACE WITH NO BACKUP\n\t'
            renum_msg += 'Press \'y\' or \'n\' (or \'q\' to quit) and then press <enter>\n'
            renum_err = "\nERROR!!! You Must Choose 'y' or 'n' (or 'q' to quit) and then press <enter>\n"
            renum_choices = ('y', 'n')
            ans = prompt_user(renum_msg, renum_err, renum_choices)
            if ans == 'n':
                msg = 'MODIFYING Renumber choice to \'NO\'. Will NOT be modifying limit files.'
                print msg
                log.info(msg)
                renum = False

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
                    if os.path.basename(fn) not in ignore_csv_files:
                        self.parse_testtable(fn,renum)
                    else:
                        msg = 'Skipping file: '+fn
                        log.info(msg)
        if not hdr_found:
            err = 'ERROR!!! OptFileHeader ('+TESTTABLE_OPTFILE_HEADER+') not found'
            log.critical(err)
            sys.exit(err)

        self.log_errors()

        msg = 'Number of WARNINGS for "{}": {}'.format(os.path.basename(sys.modules[__name__].__file__),log.warning.counter)
        print msg
        log.info(msg)
        msg = 'Number of ERRORS for "{}": {}'.format(os.path.basename(sys.modules[__name__].__file__),log.error.counter)
        print msg
        log.info(msg)

    def renum_test_numbers(self,pathfn):
        fn = os.path.split(pathfn)[1]
        if os.path.exists(pathfn+'.bak'):
            os.remove(pathfn+'.bak')
        os.rename(pathfn, pathfn+'.bak')
        csv_in = open(pathfn+'.bak', 'rb')
        csv_out = open(pathfn, 'wb')
        reader = csv.reader(csv_in)

        # get headers since we are not using DictReader, then reset the file pointer
        headers = reader.next()[:]
        tnum_idx = headers.index('Test number')
        csv_in.seek(0)

        log.info('Re-numbering "Test number" column for %s',fn)
        log.debug(headers)

        writer = csv.writer(csv_out)

        for r,row in enumerate(reader):
            if 0 == r or row[0].strip() == 'Test mode':
                writer.writerow(row)
            else:
                new_row = row[:tnum_idx]+[self.getNewTestNumber()]+row[tnum_idx+1:]
                writer.writerow(new_row)

    def get_row_key_names(self,fieldnames):
        for key in POSSIBLE_LIM_ROW_KEYS:
            row_key = tuple([x for x in key if x in fieldnames])
            if len(row_key):
                return row_key
        return None

    def get_row_key(self,row_key_names,row,headers,fn):
        row_key_list = []
        row_key_indices = []
        for i,h in enumerate(headers):
            if h in row_key_names:
                row_key_list.append(row[i])
                row_key_indices.append(i)
        row_key_list = tuple(row_key_list)
        rkl_str = str(row_key_list)
        row_key_indices = tuple(row_key_indices)
        if rkl_str in self.all_row_keys:
            log.error('Duplicate occurrence of Row Key combination found in File: %s; Row Key combination: %s',fn,row_key_list)
        else:
            self.all_row_keys.append(rkl_str)
        return row_key_list,row_key_indices

    def parse_testtable(self,pathfn,runum=False):

        with open(pathfn) as csvFile:

            special_testtable = False
            """control variable to determine if this is a standard testtable or a special one"""

            path, fn = os.path.split(pathfn)

            csvDict = csv.DictReader(csvFile)
            """dict() of all data in this csv"""

            headers = csvDict.fieldnames
            """list of all headers in this csv file"""

            unknown_headers = [x for x in headers if x not in VALID_LIM_HEADERS]
            """Collect unknown headers to see if this is a standard testtable or not"""

            if len(unknown_headers):
                # Found some unknown headers.  This must be a special testtable.
                special_testtable = True
                if pathfn not in self.special_testtables:
                    self.special_testtables.append(pathfn)
                log.debug('Non-Standard Testtable: %s',pathfn)

            row_key_names = self.get_row_key_names(headers)

            if row_key_names is None and not special_testtable:
                # None of the required row key combinations were found.  This must be a special testtable.
                special_testtable = True
                if pathfn not in self.special_testtables:
                    self.special_testtables.append(pathfn)

            if special_testtable:
                # not able to parse non standard testtables
                return
            else:
                # this is a standard testtable, so let's continue with the parsing
                msg = 'Parsing standard testtable file: '+fn+' .....'
                print msg
                log.info(msg)
                self.testtables.append(pathfn)

                if fn in self.unordered_limit_data:
                    log.fatal('Duplicate testtable found: '+fn)
                else:
                    self.unordered_limit_data[fn] = {}

                modes = []

                # using csv.reader() for slice indexing
                for row in csv.reader(csvFile):
                    if row[0] == 'Test mode':
                        # this row is reserved for mode settings
                        modes = row
                    else:
                        row_key, row_key_indices = self.get_row_key(row_key_names,row,headers,fn)
                        if row_key not in self.unordered_limit_data[fn]:
                            self.unordered_limit_data[fn][row_key] = {}
                        # iterate over columns
                        for i,cell in enumerate(row):
                            if headers[i] in REPEATABLE_LIM_HEADERS and len(modes):
                                header = (headers[i], modes[i])
                            else:
                                header = headers[i]
                            self.unordered_limit_data[fn][row_key][header] = cell

                # reset the file pointer for dict reader
                csvFile.seek(0)
                lineno = 0
                # using csv.DictReader() for key indexing
                for row in csv.DictReader(csvFile):
                    lineno += 1

                    testsuite = row['Suite name'].strip()
                    if testsuite not in self.testsuite_sbins:
                        self.testsuite_sbins[testsuite] = []

                    testname = row['Test name'].strip()
                    testnum = row['Test number'].strip()
                    if 'Pins' in row:
                        pin = row['Pins'].strip()
                    else:
                        pin = ''
                    Bin_s_num  = row['Bin_s_num'].strip()
                    Bin_s_name = row['Bin_s_name'].strip()
                    Bin_h_num  = row['Bin_h_num'].strip()
                    Bin_h_name = row['Bin_h_name'].strip()

                    try:
                        # if it can't be converted to an int, we don't care about this row
                        int(Bin_s_num)
                    except:
                        continue
                    if Bin_s_num not in self.binning:
                        self.binning[Bin_s_num] = {
                            'Bin_s_name' : Bin_s_name,
                            'Bin_h_num' : Bin_h_num,
                            'Bin_h_name' : Bin_h_name
                        }
                    else:
                        prev = ('SBIN='+Bin_s_num,self.binning[Bin_s_num]['Bin_s_name'],
                                'HBIN='+self.binning[Bin_s_num]['Bin_h_num'],self.binning[Bin_s_num]['Bin_h_name'])
                        curr = ('SBIN='+Bin_s_num,Bin_s_name,
                                'HBIN='+Bin_h_num,Bin_h_name)
                        if prev != curr:
                            err = 'Duplicate Softbin Number found in: "{}".... \n\t{}\n\t{}'.format(fn,prev,curr)
                            log.error(err)

                    binkey = (Bin_s_num,Bin_s_name,Bin_h_num,Bin_h_name)
                    # if Bin_s_num == '995':
                    #     print 'binkey:',binkey
                    if binkey not in self.binning2testname:
                        self.binning2testname[binkey] = []
                    self.binning2testname[binkey].append(testname)

                    if Bin_s_num not in self.testsuite_sbins[testsuite]:
                        self.testsuite_sbins[testsuite].append(Bin_s_num)

                    # check for duplicate test numbers
                    if len(testnum):
                        if testnum not in self.testnums:
                            self.testnums.append(testnum)
                        else:
                            log.error('Duplicate "Test number" : %s found in file: %s',testnum,fn)

                    # check for max testname length
                    if len(pin):
                        fulltestname = testname+'@'+pin
                    else:
                        fulltestname = testname
                    if len(fulltestname) > MAXLENGTH_TESTNAME:
                        log.warning('Max length of testname(max=%d: %s reached in file: %s.  Possible truncation in STDF',MAXLENGTH_TESTNAME,fulltestname,fn)

                    # check for sbin name to too many nums
                    if len(Bin_s_name):
                        if Bin_s_name not in self.sbin_names:
                            self.sbin_names[Bin_s_name] = Bin_s_num
                        else:
                            if self.sbin_names[Bin_s_name] != Bin_s_num:
                                if Bin_s_name not in self.sbin_name_err:
                                    self.sbin_name_err[Bin_s_name] = []
                                if Bin_s_num not in self.sbin_name_err[Bin_s_name]:
                                    self.sbin_name_err[Bin_s_name].append(Bin_s_num)
                                if self.sbin_names[Bin_s_name] not in self.sbin_name_err[Bin_s_name]:
                                    self.sbin_name_err[Bin_s_name].append(self.sbin_names[Bin_s_name])
                        # adding testname info
                        if Bin_s_num not in self.sbin_num_to_testname:
                            self.sbin_num_to_testname[Bin_s_num] = []
                        if testname not in self.sbin_num_to_testname[Bin_s_num]:
                            self.sbin_num_to_testname[Bin_s_num].append(testname)
        
                    # check for hbin name to too many nums
                    if len(Bin_h_name):
                        if Bin_h_name not in self.hbin_names:
                            self.hbin_names[Bin_h_name] = Bin_h_num
                        else:
                            if self.hbin_names[Bin_h_name] != Bin_h_num:
                                if Bin_h_name not in self.hbin_name_err:
                                    self.hbin_name_err[Bin_h_name] = []
                                if Bin_h_num not in self.hbin_name_err[Bin_h_name]:
                                    self.hbin_name_err[Bin_h_name].append(Bin_h_num)
                                if self.hbin_names[Bin_h_name] not in self.hbin_name_err[Bin_h_name]:
                                    self.hbin_name_err[Bin_h_name].append(self.hbin_names[Bin_h_name])
                        # adding testname info
                        if Bin_h_num not in self.hbin_num_to_testname:
                            self.hbin_num_to_testname[Bin_h_num] = []
                        if testname not in self.hbin_num_to_testname[Bin_h_num]:
                            self.hbin_num_to_testname[Bin_h_num].append(testname)
        
                    # check for sbin num to too many names
                    if len(Bin_s_num):
                        if Bin_s_num not in self.sbin_nums:
                            self.sbin_nums[Bin_s_num] = Bin_s_name
                        else:
                            if self.sbin_nums[Bin_s_num] != Bin_s_name:
                                if Bin_s_num not in self.sbin_num_err:
                                    self.sbin_num_err[Bin_s_num] = []
                                if Bin_s_name not in self.sbin_num_err[Bin_s_num]:
                                    self.sbin_num_err[Bin_s_num].append(Bin_s_name)
                                if self.sbin_nums[Bin_s_num] not in self.sbin_num_err[Bin_s_num]:
                                    self.sbin_num_err[Bin_s_num].append(self.sbin_nums[Bin_s_num])
                        # adding testname info
                        if Bin_s_name not in self.sbin_name_to_testname:
                            self.sbin_name_to_testname[Bin_s_name] = []
                        if testname not in self.sbin_name_to_testname[Bin_s_name]:
                            self.sbin_name_to_testname[Bin_s_name].append(testname)
        
                    # check for hbin num to too many names
                    if len(Bin_h_num):
                        if Bin_h_num not in self.hbin_nums:
                            self.hbin_nums[Bin_h_num] = Bin_h_name
                        else:
                            if self.hbin_nums[Bin_h_num] != Bin_h_name:
                                if Bin_h_num not in self.hbin_num_err:
                                    self.hbin_num_err[Bin_h_num] = []
                                if Bin_h_name not in self.hbin_num_err[Bin_h_num]:
                                    self.hbin_num_err[Bin_h_num].append(Bin_h_name)
                                if self.hbin_nums[Bin_h_num] not in self.hbin_num_err[Bin_h_num]:
                                    self.hbin_num_err[Bin_h_num].append(self.hbin_nums[Bin_h_num])
                        # adding testname info
                        if Bin_h_name not in self.hbin_name_to_testname:
                            self.hbin_name_to_testname[Bin_h_name] = []
                        if testname not in self.hbin_name_to_testname[Bin_h_name]:
                            self.hbin_name_to_testname[Bin_h_name].append(testname)
        
                    # check for sbin name/hbin name mapping inconsistencies
                    if len(Bin_s_name) and len(Bin_h_name):
                        if Bin_s_name not in self.binmaps:
                            self.binmaps[Bin_s_name] = Bin_h_name
                        else:
                            if self.binmaps[Bin_s_name] != Bin_h_name:
                                if Bin_s_name not in self.binmap_err:
                                    self.binmap_err[Bin_s_name] = []
                                if Bin_h_name not in self.binmap_err[Bin_s_name]:
                                    self.binmap_err[Bin_s_name].append(Bin_h_name)
                                if self.binmaps[Bin_s_name] not in self.binmap_err[Bin_s_name]:
                                    self.binmap_err[Bin_s_name].append(self.binmaps[Bin_s_name])
                        # adding testname info
                        namekey = Bin_s_name+Bin_h_name
                        if namekey not in self.binmap_err_tests:
                            self.binmap_err_tests[namekey] = []
                        if testname not in self.binmap_err_tests[namekey]:
                            self.binmap_err_tests[namekey].append(testname)
                    elif len(Bin_s_name):
                        if Bin_s_name not in self.binmap_err:
                            self.binmap_err[Bin_s_name] = []
                        if "MISSING_HBIN_NAME" not in self.binmap_err[Bin_s_name]:
                            self.binmap_err[Bin_s_name].append("MISSING_HBIN_NAME")
        if runum and not special_testtable:
            self.renum_test_numbers(pathfn)

    def log_errors(self):
        errors = False
        if len(self.sbin_name_err):
            errors = True
            header='\n***********************************************\n'\
                  +'SBIN NAME TO NUMS ERRORS LISTED BELOW !!!!\n'\
                  +'CANNOT USE MORE THAN ONE !!!!\n'\
                  +'***********************************************\n'
            err_str = ''
            for thisname in self.sbin_name_err:
                err_str +='\tSBIN NAME: '+ljust(thisname,MAXLENGTH_BINNAME,'.')+'.USES SBIN NUMS(testname(s)):\n\t\t\t\t\t\t\t\t'
                for thisnum in self.sbin_name_err[thisname]:
                    num_testnames = len(self.sbin_num_to_testname[thisnum])
                    if num_testnames > 10:
                        testnames = ','.join(self.sbin_num_to_testname[thisnum][:10])+' ... and '+str(num_testnames-10)+' more'
                    else:
                        testnames = ','.join(self.sbin_num_to_testname[thisnum])
                    err_str += thisnum + '('+testnames+')\n\t\t\t\t\t\t\t\t'
                err_str += '\n'
        else:
            header='\n***********************************************\n'\
                  +'PASSED: SBIN NAME TO NUMS CHECK !!!!\n'\
                  +'***********************************************\n'
        log.error(header+err_str)
        if len(self.hbin_name_err):
            errors = True
            header='\n***********************************************\n'\
                  +'HBIN NAME TO NUMS ERRORS LISTED BELOW !!!!\n'\
                  +'CANNOT USE MORE THAN ONE !!!!\n'\
                  +'***********************************************\n'
            err_str = ''
            for thisname in self.hbin_name_err:
                err_str +='\tHBIN NAME: '+ljust(thisname,MAXLENGTH_BINNAME,'.')+'.USES HBIN NUMS(testname(s)):\n\t\t\t\t\t\t\t\t'
                for thisnum in self.hbin_name_err[thisname]:
                    num_testnames = len(self.hbin_num_to_testname[thisnum])
                    if num_testnames > 10:
                        testnames = ','.join(self.hbin_num_to_testname[thisnum][:10])+' ... and '+str(num_testnames-10)+' more'
                    else:
                        testnames = ','.join(self.hbin_num_to_testname[thisnum])
                    err_str += thisnum +'('+testnames+')\n\t\t\t\t\t\t\t\t'
                err_str += '\n'
        else:
            header='\n***********************************************\n'\
                  +'PASSED: HBIN NAME TO NUMS CHECK !!!!\n'\
                  +'***********************************************\n'
        log.error(header+err_str)
        if len(self.sbin_num_err):
            errors = True
            header='\n***********************************************\n'\
                  +'SBIN NUMS TO NAMES ERRORS LISTED BELOW !!!!\n'\
                  +'CANNOT USE MORE THAN ONE !!!!\n'\
                  +'***********************************************\n'
            err_str = ''
            for thisnum in self.sbin_num_err:
                err_str +='\tSBIN NUM: '+ljust(thisnum,MAXLENGTH_BINNUM,'.')+'.USES SBIN NAMES(testname(s)):\n\t\t\t\t\t\t\t\t'
                for thisname in self.sbin_num_err[thisnum]:
                    num_testnames = len(self.sbin_name_to_testname[thisname])
                    if num_testnames > 10:
                        testnames = ','.join([x for x in self.sbin_name_to_testname[thisname][:10] if len(x)])+' ... and '+str(num_testnames-10)+' more'
                    else:
                        testnames = ','.join([x for x in self.sbin_name_to_testname[thisname] if len(x)])
                    err_str += thisname + '('+testnames+')\n\t\t\t\t\t\t\t\t'
                err_str += '\n'
        else:
            header='\n***********************************************\n'\
                  +'PASSED: SBIN NUMS TO NAMES CHECK !!!!\n'\
                  +'***********************************************\n'
        log.error(header+err_str)
        if len(self.hbin_num_err):
            errors = True
            header='\n***********************************************\n'\
                  +'HBIN NUMS TO NAMES ERRORS LISTED BELOW !!!!\n'\
                  +'CANNOT USE MORE THAN ONE !!!!\n'\
                  +'***********************************************\n'
            err_str = ''
            for thisnum in self.hbin_num_err:
                err_str +='\tHBIN NUM: '+ljust(thisnum,MAXLENGTH_BINNUM,'.')+'.USES HBIN NAMES(testname(s)):\n\t\t\t\t\t\t\t\t'
                for thisname in self.hbin_num_err[thisnum]:
                    num_testnames = len(self.hbin_name_to_testname[thisname])
                    if num_testnames > 10:
                        testnames = ','.join([x for x in self.hbin_name_to_testname[thisname][:10] if len(x)])+' ... and '+str(num_testnames-10)+' more'
                    else:
                        testnames = ','.join([x for x in self.hbin_name_to_testname[thisname] if len(x)])
                    err_str += thisname + '('+testnames+')\n\t\t\t\t\t\t\t\t'
                err_str += '\n'
        else:
            header='\n***********************************************\n'\
                  +'PASSED: HBIN NUMS TO NAMES CHECK !!!!\n'\
                  +'***********************************************\n'
        log.error(header+err_str)
        if len(self.binmap_err):
            errors = True
            header='\n***********************************************\n'\
                  +'INCONSISTENT SBIN NAME/HBIN NAME MAPPING ERRORS LISTED BELOW !!!!\n'\
                  +'CANNOT MAP TO MORE THAN ONE !!!!\n'\
                  +'***********************************************\n'
            err_str = ''
            for sbin in self.binmap_err:
                err_str +='\tSBIN NAME: '+ljust(sbin,MAXLENGTH_BINNAME,'.')+'.USES HBIN NAMES(testname(s)):\n\t\t\t\t\t\t\t\t'
                for hbin in self.binmap_err[sbin]:
                    thisname = sbin+hbin
                    num_testnames = len(self.binmap_err_tests[thisname])
                    if num_testnames > 10:
                        testnames = ','.join([x for x in self.binmap_err_tests[thisname][:10] if len(x)])+' ... and '+str(num_testnames-10)+' more'
                    else:
                        testnames = ','.join([x for x in self.binmap_err_tests[thisname] if len(x)])
                    err_str += hbin + '('+testnames+')\n\t\t\t\t\t\t\t\t'
        else:
            header='\n***********************************************\n'\
                  +'INCONSISTENT SBIN NAME/HBIN NAME MAPPING ERRORS LISTED BELOW !!!!\n'\
                  +'CANNOT MAP TO MORE THAN ONE !!!!\n'\
                  +'***********************************************\n'
        log.error(header+err_str)
        if not errors:
            header='\n***********************************************\n'\
                  +'YAY !!! NO ERRRORS FOUND !\n'\
                  +'SEE BIN REPORT BELOW\n'\
                  +'***********************************************\n'
            ostr='|'+'-'*MAXLENGTH_BINNUM+'|-'+'-'*MAXLENGTH_BINNAME+'|-'+'-'*MAXLENGTH_BINNAME+'|-'+'-'*MAXLENGTH_BINNUM+'|\n'
            ostr+='|'+ljust('SBIN #',MAXLENGTH_BINNUM)+'| '
            ostr+=ljust('SBIN NAME',MAXLENGTH_BINNAME)+'| '
            ostr+=ljust('HBIN NAME',MAXLENGTH_BINNAME)+'| '
            ostr+=ljust('HBIN #',MAXLENGTH_BINNUM)+'|\n'
            ostr+='|'+'-'*MAXLENGTH_BINNUM+'|-'+'-'*MAXLENGTH_BINNAME+'|-'+'-'*MAXLENGTH_BINNAME+'|-'+'-'*MAXLENGTH_BINNUM+'|\n'
            for sbin_name, hbin_name in self.binmaps.items():
                ostr+='|'+ljust(self.sbin_names[sbin_name],MAXLENGTH_BINNUM)+'| '
                ostr+=ljust(sbin_name,MAXLENGTH_BINNAME)+'| '
                ostr+=ljust(hbin_name,MAXLENGTH_BINNAME)+'| '
                ostr+=ljust(self.hbin_names[hbin_name],MAXLENGTH_BINNUM)+'|\n'
            log.error(header+ostr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description: "+sys.modules[__name__].__doc__)
    parser.add_argument('-name','--name',required=False,default='',help='Optional name used for output files/logs.')
    parser.add_argument('-d','--debug',action='store_true',help='print a lot of debug stuff to dlog')
    parser.add_argument('-out','--output_dir',required=False,default='', help='Directory to place log file(s).')
    parser.add_argument('-max','--maxlogs',type=int,default=1,required=False, help='(0=OFF:log data to stdout). Set to 1 to keep only one log (subsequent runs will overwrite).')
    parser.add_argument('-r','--renumber',action='store_true',help='Re-number "Test number" column across all STANDARD csv testtables')
    parser.add_argument('-tt','--testtable_file',required=True, help='Path to testtable master file')
    parser.add_argument('-ignore','--ignore_tables',required=False, help='Ignore tables (csv files). Place testtables (\'\\n\' separated) in this text file to suppress parsing')
    args = parser.parse_args()

    ignore_tables = []
    if args.ignore_tables is not None:
        try:
            with open(args.ignore_tables, 'r') as f:
                ignore_tables = [x.strip() for x in f.readlines()]
        except:
            err = '%s is NOT a valid ignore file. Skipping your ignore file.'.format(args.ignore_tables)
            print err
            log.error(err)
        msg = 'IGNORING THE FOLLOWING TESTTABLES:\n'+pformat(ignore_tables, indent=4)
        # print msg
        log.info(msg)

    tt = TestTable(pathfn=args.testtable_file, renum=args.renumber, debug=args.debug, progname=args.name,
                   maxlogs=args.maxlogs, outdir=args.output_dir, ignore_csv_files=ignore_tables)

    # For debug and future development, list this module's data containers and their contents
    log.debug('testtables:\n' + pformat(tt.testtables,indent=4))
    log.debug('unordered_limit_data: (data set too large .. displaying only a sample 2 rows from 3 tables) ... ')
    for table in take(3,tt.unordered_limit_data.iteritems()):
        log.debug(table[:2])
    log.debug('special_testtables:\n' + pformat(tt.special_testtables,indent=4))
    log.debug('sbin_names:\n' + pformat(tt.sbin_names,indent=4))
    log.debug('hbin_names:\n' + pformat(tt.hbin_names,indent=4))
    log.debug('sbin_nums:\n' + pformat(tt.sbin_nums,indent=4))
    log.debug('hbin_nums:\n' + pformat(tt.hbin_nums,indent=4))
    log.debug('binmaps:\n' + pformat(tt.binmaps,indent=4))

    log.info('ARGUMENTS:\n\t'+'\n\t'.join(['--'+k+'='+str(v) for k,v in args.__dict__.iteritems()]))

    time = time.time()-_start_time
    msg = 'Script took ' + str(round(time,3)) + ' seconds (' + humanize_time(time) + ')'
    log.info(msg)
    print '\n' + msg
