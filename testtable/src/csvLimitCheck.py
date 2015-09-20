#!/usr/local/bin/python2.6-2.6.4
import time
import csv
from string import *
import argparse
from common import *

_description_ = "Analyzes csv limit files and looks for potential problems."

__RD_ERROR__ = "Make sure you have permissions to READ files in this directory."
__WR_ERROR__ = "Make sure you have permissions to WRITE files in this directory."

start_time = time.time()
localtime = time.asctime(time.localtime(start_time))
_logfile_ = "csvLimitCheck.log"
_duptestname_err_ = []
_testnamelen_err_ = ''

_sbin_name_err_ = {}
_sbin_num_to_testname_ = {}

_hbin_name_err_ = {}
_hbin_num_to_testname_ = {}

_sbin_num_err_ = {}
_sbin_name_to_testname_ = {}

_hbin_num_err_ = {}
_hbin_name_to_testname_ = {}

_binmap_err_ = {}
_binmap_err_tests_ = {}

_files_analyzed_ = []
_files_skipped_ = []

_testnums_ = []
_sbin_names_ = {}
_hbin_names_ = {}
_sbin_nums_ = {}
_hbin_nums_ = {}
_binmaps_ = {}
_MAXLENGTH_TESTNAME_ = 30
_MAXFILENAMELENGTH_ = 30
_MAXBINNUMLENGTH_ = 10
_MAXBINNAMELENGTH_ = 30

_file_header_ = \
"""
\t# Script File Name: csvLimitCheck.py
\t# Author: Roger Logan
\t# Version: 1.0
\t# Property of Anora, LLC
\t# Script Run Date:"""+localtime+"""
\t# Description: """+_description_+"""\n\n
"""

def create_logfile():#[ expression for item in list if conditional ]
    global _testnamelen_err_
    errors = False
    try:
        print "\n\nCreating",_logfile_
        logFile=open(_logfile_,'w')
        logFile.write(_file_header_)
        if len(_files_skipped_):
            header='\n***********************************************\n'\
                      +'FILES SKIPPED DUE TO ERRORS:\n'\
                      +'***********************************************\n\t'
            logFile.write(header+'\n\t'.join(_files_skipped_)+'\n')
        if len(_files_analyzed_):
            header='\n***********************************************\n'\
                      +'FILES ANALYZED:\n'\
                      +'***********************************************\n\t'
            logFile.write(header+'\n\t'.join(_files_analyzed_)+'\n')
        else:
            err_msg = "\n\nERROR !!! No Files Were Analyzed ! Exiting ...\n"
            logFile.write(err_msg)
            logFile.close()
            sys.exit(err_msg)
        if len(_duptestname_err_):
            errors = True
            header='\n***********************************************\n'\
                  +'DUPLICATE TEST NUMBERS FOUND !!!!\n'\
                  +'***********************************************\n'
            logFile.write(header+','.join(_duptestname_err_)+'\n')
        if len(_testnamelen_err_):
            errors = True
            header='\n***********************************************\n'\
                  +'TEST NAME LENGTH ERRORS LISTED BELOW !!!!\n'\
                  +'MAX ALLOWED LENGTH = '+str(_MAXLENGTH_TESTNAME_)+' (INCLUDING \'@pin\',IF \'Pins\' COLUMN FOUND)\n'\
                  +'***********************************************\n'
            logFile.write(header+_testnamelen_err_)
        if len(_sbin_name_err_):
            errors = True
            header='\n***********************************************\n'\
                  +'SBIN NAME TO NUMS ERRORS LISTED BELOW !!!!\n'\
                  +'CANNOT USE MORE THAN ONE !!!!\n'\
                  +'***********************************************\n'
            err_str = ''
            for thisname in _sbin_name_err_:
                err_str +='\tSBIN NAME: '+ljust(thisname,_MAXBINNAMELENGTH_,'.')+'.USES SBIN NUMS(testname(s)):\n\t\t\t\t\t\t\t\t'
                for thisnum in _sbin_name_err_[thisname]:
                    num_testnames = len(_sbin_num_to_testname_[thisnum])
                    if num_testnames > 10:
                        testnames = ','.join(_sbin_num_to_testname_[thisnum][:10])+' ... and '+str(num_testnames-10)+' more'
                    else:
                        testnames = ','.join(_sbin_num_to_testname_[thisnum])
                    err_str += thisnum + '('+testnames+')\n\t\t\t\t\t\t\t\t'
                err_str += '\n'
            logFile.write(header+err_str)
        if len(_hbin_name_err_):
            errors = True
            header='\n***********************************************\n'\
                  +'HBIN NAME TO NUMS ERRORS LISTED BELOW !!!!\n'\
                  +'CANNOT USE MORE THAN ONE !!!!\n'\
                  +'***********************************************\n'
            err_str = ''
            for thisname in _hbin_name_err_:
                err_str +='\tHBIN NAME: '+ljust(thisname,_MAXBINNAMELENGTH_,'.')+'.USES HBIN NUMS(testname(s)):\n\t\t\t\t\t\t\t\t'
                for thisnum in _hbin_name_err_[thisname]:
                    num_testnames = len(_hbin_num_to_testname_[thisnum])
                    if num_testnames > 10:
                        testnames = ','.join(_hbin_num_to_testname_[thisnum][:10])+' ... and '+str(num_testnames-10)+' more'
                    else:
                        testnames = ','.join(_hbin_num_to_testname_[thisnum])
                    err_str += thisnum +'('+testnames+')\n\t\t\t\t\t\t\t\t'
                err_str += '\n'
            logFile.write(header+err_str)
        if len(_sbin_num_err_):
            errors = True
            header='\n***********************************************\n'\
                  +'SBIN NUMS TO NAMES ERRORS LISTED BELOW !!!!\n'\
                  +'CANNOT USE MORE THAN ONE !!!!\n'\
                  +'***********************************************\n'
            err_str = ''
            for thisnum in _sbin_num_err_:
                err_str +='\tSBIN NUM: '+ljust(thisnum,_MAXBINNUMLENGTH_,'.')+'.USES SBIN NAMES(testname(s)):\n\t\t\t\t\t\t\t\t'
                for thisname in _sbin_num_err_[thisnum]:
                    num_testnames = len(_sbin_name_to_testname_[thisname])
                    if num_testnames > 10:
                        testnames = ','.join(_sbin_name_to_testname_[thisname][:10])+' ... and '+str(num_testnames-10)+' more'
                    else:
                        testnames = ','.join(_sbin_name_to_testname_[thisname])
                    err_str += thisname + '('+testnames+')\n\t\t\t\t\t\t\t\t'
                err_str += '\n'
            logFile.write(header+err_str)
        if len(_hbin_num_err_):
            errors = True
            header='\n***********************************************\n'\
                  +'HBIN NUMS TO NAMES ERRORS LISTED BELOW !!!!\n'\
                  +'CANNOT USE MORE THAN ONE !!!!\n'\
                  +'***********************************************\n'
            err_str = ''
            for thisnum in _hbin_num_err_:
                err_str +='\tHBIN NUM: '+ljust(thisnum,_MAXBINNUMLENGTH_,'.')+'.USES HBIN NAMES(testname(s)):\n\t\t\t\t\t\t\t\t'
                for thisname in _hbin_num_err_[thisnum]:
                    num_testnames = len(_hbin_name_to_testname_[thisname])
                    if num_testnames > 10:
                        testnames = ','.join(_hbin_name_to_testname_[thisname][:10])+' ... and '+str(num_testnames-10)+' more'
                    else:
                        testnames = ','.join(_hbin_name_to_testname_[thisname])
                    err_str += thisname + '('+testnames+')\n\t\t\t\t\t\t\t\t'
                err_str += '\n'
            logFile.write(header+err_str)
        if len(_binmap_err_):
            errors = True
            header='\n***********************************************\n'\
                  +'INCONSISTENT SBIN NAME/HBIN NAME MAPPING ERRORS LISTED BELOW !!!!\n'\
                  +'CANNOT MAP TO MORE THAN ONE !!!!\n'\
                  +'***********************************************\n'
            err_str = ''
            for sbin in _binmap_err_:
                err_str +='\tSBIN NAME: '+ljust(sbin,_MAXBINNAMELENGTH_,'.')+'.USES HBIN NAMES(testname(s)):\n\t\t\t\t\t\t\t\t'
                for hbin in _binmap_err_[sbin]:
                    thisname = sbin+hbin
                    num_testnames = len(_binmap_err_tests_[thisname])
                    if num_testnames > 10:
                        testnames = ','.join(_binmap_err_tests_[thisname][:10])+' ... and '+str(num_testnames-10)+' more'
                    else:
                        testnames = ','.join(_binmap_err_tests_[thisname])
                    err_str += hbin + '('+testnames+')\n\t\t\t\t\t\t\t\t'
            logFile.write(header+err_str)
        if not errors:
            header='\n***********************************************\n'\
                  +'YAY !!! NO ERRRORS FOUND !\n'\
                  +'SEE BIN REPORT BELOW\n'\
                  +'***********************************************\n'
            ostr='|'+'-'*_MAXBINNUMLENGTH_+'|-'+'-'*_MAXBINNAMELENGTH_+'|-'+'-'*_MAXBINNAMELENGTH_+'|-'+'-'*_MAXBINNUMLENGTH_+'|\n'
            ostr+='|'+ljust('SBIN #',_MAXBINNUMLENGTH_)+'| '
            ostr+=ljust('SBIN NAME',_MAXBINNAMELENGTH_)+'| '
            ostr+=ljust('HBIN NAME',_MAXBINNAMELENGTH_)+'| '
            ostr+=ljust('HBIN #',_MAXBINNUMLENGTH_)+'|\n'
            ostr+='|'+'-'*_MAXBINNUMLENGTH_+'|-'+'-'*_MAXBINNAMELENGTH_+'|-'+'-'*_MAXBINNAMELENGTH_+'|-'+'-'*_MAXBINNUMLENGTH_+'|\n'
            for sbin_name, hbin_name in _binmaps_.items():
                ostr+='|'+ljust(_sbin_names_[sbin_name],_MAXBINNUMLENGTH_)+'| '
                ostr+=ljust(sbin_name,_MAXBINNAMELENGTH_)+'| '
                ostr+=ljust(hbin_name,_MAXBINNAMELENGTH_)+'| '
                ostr+=ljust(_hbin_names_[hbin_name],_MAXBINNUMLENGTH_)+'|\n'
            logFile.write(header+ostr)
    except IOError:
        print "\nFile WRITE Error !!!: "+_logfile_+"\n"+__WR_ERROR__+"\n"
    finally:
        logFile.close()


def check_csv(pathfn):
    global _duptestname_err_,_testnamelen_err_,_sbin_name_err_,_hbin_name_err_,_sbin_num_err_,_hbin_num_err_,_binmap_err_
    global _testnums_,_sbin_names_,_hbin_names_,_sbin_nums_,_hbin_nums_,_binmaps_
    tp_path, fn = os.path.split(pathfn)
    with open(pathfn) as csvFile:
        print "\nAnalyzing "+pathfn
        # print "\tLine count = "+get_linecount(pathfn)
        pinwarning = False
        lineno = 0
        for line in csv.DictReader(csvFile):
            lineno+=1
            progress_tracker(lineno)
            try:
                try:
                    testname = line['Test name'].strip()
                except:
                    print "\tERROR !!! \'Test name\' not found !"
                    raise Exception
                try:
                    testnum = line['Test number'].strip()
                except:
                    print "\tERROR !!! \'Test number\' not found !"
                    raise Exception
                if not pinwarning:
                    try:
                        pin = line['Pins'].strip()
                    except:
                        pinwarning = True
                        print "\tWARNING ! \'Pins\' column not found in "+pathfn
                        print "\tSetting pin = \'\'"
                        pin = ''
                else:
                    pin = ''
                try:
                    Bin_s_num  = line['Bin_s_num'].strip()
                except:
                    print "\tERROR !!! \'Bin_s_num\' not found !"
                    raise Exception
                try:
                    Bin_s_name = line['Bin_s_name'].strip()
                except:
                    print "\tERROR !!! \'Bin_s_name\' not found !"
                    raise Exception
                try:
                    Bin_h_num  = line['Bin_h_num'].strip()
                except:
                    print "\tERROR !!! \'Bin_h_num\' not found !"
                    raise Exception
                try:
                    Bin_h_name = line['Bin_h_name'].strip()
                except:
                    print "\tERROR !!! \'Bin_h_name\' not found !"
                    raise Exception
            except:
                print "\tIncompatible Format. Skipping "+pathfn+"\n"
                if pathfn not in _files_skipped_:
                    _files_skipped_.append(pathfn)
                break
            if pathfn not in _files_analyzed_:
                _files_analyzed_.append(pathfn)
            
            # check for duplicate test numbers
            if len(testnum):
                if testnum not in _testnums_:
                    _testnums_.append(testnum)
                else:
                    _duptestname_err_.append(testnum)

            # check for pinlength too long
            if len(pin):
                fulltestname = testname+'@'+pin
            else:
                fulltestname = testname
            if len(fulltestname) > _MAXLENGTH_TESTNAME_:
                _testnamelen_err_ += '\tFILE = '+ljust(pathfn,_MAXFILENAMELENGTH_,'.')+'LENGTH = '+str(len(fulltestname))+'...TESTNAME = '+fulltestname+'\n'

            # check for sbin name to too many nums
            if len(Bin_s_name):
                if Bin_s_name not in _sbin_names_:
                    _sbin_names_[Bin_s_name] = Bin_s_num
                else:
                    if _sbin_names_[Bin_s_name] != Bin_s_num:
                        if Bin_s_name not in _sbin_name_err_:
                            _sbin_name_err_[Bin_s_name] = []
                        if Bin_s_num not in _sbin_name_err_[Bin_s_name]:
                            _sbin_name_err_[Bin_s_name].append(Bin_s_num)
                        if _sbin_names_[Bin_s_name] not in _sbin_name_err_[Bin_s_name]:
                            _sbin_name_err_[Bin_s_name].append(_sbin_names_[Bin_s_name])
                # adding testname info
                if Bin_s_num not in _sbin_num_to_testname_:
                    _sbin_num_to_testname_[Bin_s_num] = []
                if testname not in _sbin_num_to_testname_[Bin_s_num]:
                    _sbin_num_to_testname_[Bin_s_num].append(testname)

            # check for hbin name to too many nums
            if len(Bin_h_name):
                if Bin_h_name not in _hbin_names_:
                    _hbin_names_[Bin_h_name] = Bin_h_num
                else:
                    if _hbin_names_[Bin_h_name] != Bin_h_num:
                        if Bin_h_name not in _hbin_name_err_:
                            _hbin_name_err_[Bin_h_name] = []
                        if Bin_h_num not in _hbin_name_err_[Bin_h_name]:
                            _hbin_name_err_[Bin_h_name].append(Bin_h_num)
                        if _hbin_names_[Bin_h_name] not in _hbin_name_err_[Bin_h_name]:
                            _hbin_name_err_[Bin_h_name].append(_hbin_names_[Bin_h_name])
                # adding testname info
                if Bin_h_num not in _hbin_num_to_testname_:
                    _hbin_num_to_testname_[Bin_h_num] = []
                if testname not in _hbin_num_to_testname_[Bin_h_num]:
                    _hbin_num_to_testname_[Bin_h_num].append(testname)

            # check for sbin num to too many names
            if len(Bin_s_num):
                if Bin_s_num not in _sbin_nums_:
                    _sbin_nums_[Bin_s_num] = Bin_s_name
                else:
                    if _sbin_nums_[Bin_s_num] != Bin_s_name:
                        if Bin_s_num not in _sbin_num_err_:
                            _sbin_num_err_[Bin_s_num] = []
                        if Bin_s_name not in _sbin_num_err_[Bin_s_num]:
                            _sbin_num_err_[Bin_s_num].append(Bin_s_name)
                        if _sbin_nums_[Bin_s_num] not in _sbin_num_err_[Bin_s_num]:
                            _sbin_num_err_[Bin_s_num].append(_sbin_nums_[Bin_s_num])
                # adding testname info
                if Bin_s_name not in _sbin_name_to_testname_:
                    _sbin_name_to_testname_[Bin_s_name] = []
                if testname not in _sbin_name_to_testname_[Bin_s_name]:
                    _sbin_name_to_testname_[Bin_s_name].append(testname)

            # check for hbin num to too many names
            if len(Bin_h_num):
                if Bin_h_num not in _hbin_nums_:
                    _hbin_nums_[Bin_h_num] = Bin_h_name
                else:
                    if _hbin_nums_[Bin_h_num] != Bin_h_name:
                        if Bin_h_num not in _hbin_num_err_:
                            _hbin_num_err_[Bin_h_num] = []
                        if Bin_h_name not in _hbin_num_err_[Bin_h_num]:
                            _hbin_num_err_[Bin_h_num].append(Bin_h_name)
                        if _hbin_nums_[Bin_h_num] not in _hbin_num_err_[Bin_h_num]:
                            _hbin_num_err_[Bin_h_num].append(_hbin_nums_[Bin_h_num])
                # adding testname info
                if Bin_h_name not in _hbin_name_to_testname_:
                    _hbin_name_to_testname_[Bin_h_name] = []
                if testname not in _hbin_name_to_testname_[Bin_h_name]:
                    _hbin_name_to_testname_[Bin_h_name].append(testname)

            # check for sbin name/hbin name mapping inconsistencies
            if len(Bin_s_name) and len(Bin_h_name):
                if Bin_s_name not in _binmaps_:
                    _binmaps_[Bin_s_name] = Bin_h_name
                else:
                    if _binmaps_[Bin_s_name] != Bin_h_name:
                        if Bin_s_name not in _binmap_err_:
                            _binmap_err_[Bin_s_name] = []
                        if Bin_h_name not in _binmap_err_[Bin_s_name]:
                            _binmap_err_[Bin_s_name].append(Bin_h_name)
                        if _binmaps_[Bin_s_name] not in _binmap_err_[Bin_s_name]:
                            _binmap_err_[Bin_s_name].append(_binmaps_[Bin_s_name])
                # adding testname info
                namekey = Bin_s_name+Bin_h_name
                if namekey not in _binmap_err_tests_:
                    _binmap_err_tests_[namekey] = []
                if testname not in _binmap_err_tests_[namekey]:
                    _binmap_err_tests_[namekey].append(testname)
            elif len(Bin_s_name):
                if Bin_s_name not in _binmap_err_:
                    _binmap_err_[Bin_s_name] = []
                if "MISSING_HBIN_NAME" not in _binmap_err_[Bin_s_name]:
                    _binmap_err_[Bin_s_name].append("MISSING_HBIN_NAME")
    return


def main():
    print _file_header_

    parser = argparse.ArgumentParser(description="Description: "+_description_)
    parser.add_argument("files", nargs='*', help="Limit files to be analyzed (*.csv)")
    args = parser.parse_args()

    if not len(args.files):
        sys.exit("ERROR !!! No limit files given! Aborting ...")

    args.files,numfiles = get_files(args.files)

    for csv in args.files:
        check_csv(csv)
    create_logfile()

if __name__ == "__main__":
    main()
    time = time.time()-start_time
    print '\nScript took',round(time,3),'seconds','('+humanize_time(time)+')'
