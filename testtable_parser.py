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
from pprint import *
import time
from common import humanize_time,init_logging
from string import *
_start_time = time.time()

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

        self.log_errors()

    def get_row_key_names(self,fieldnames):
        row_key = []
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

    def parse_testtable(self,pathfn):

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
                self.special_testtables.append(pathfn)

            row_key_names = self.get_row_key_names(headers)
            if row_key_names is None:
                # None of the required row key combinations were found.  This must be a special testtable.
                special_testtable = True
                self.special_testtables.append(pathfn)

            if special_testtable:
                # not able to parse non standard testtables
                return
            else:
                # this is a standard testtable, so let's continue with the parsing
                log.info('Parsing testtable standard file: '+fn+' .....')
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
                        log.warning('Max length of testname: %s reached in file: %s.  Possible truncation in STDF',fulltestname,fn)

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
    parser.add_argument('-tt','--path_to_testtable_file',required=True, help='Path to testtable master file')
    parser.add_argument('-v','--verbose',action='store_true',help='print a lot of stuff')
    parser.add_argument('-out','--output_dir',required=False,default='',help='Directory to place log file(s).')
    parser.add_argument('-max','--maxlogs',type=int,default=10,required=False, help='(0=OFF:log data to stdout). Set to 1 to keep only one log (subsequent runs will overwrite).')
    args = parser.parse_args()

    init_logging(scriptname=os.path.split(sys.modules[__name__].__file__)[1],args=args)

    tt = TestTable(args.path_to_testtable_file)

    time = time.time()-_start_time
    msg = 'Script took ' + str(round(time,3)) + ' seconds (' + humanize_time(time) + ')'
    log.info(msg)
    print '\n' + msg
