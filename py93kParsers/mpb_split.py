#!/usr/bin/env python
"""
    This script splits mpb's (must have '_MPB' in file name) into 2 mpb's if a match is found.
    The match is the first label name that has a substring which is passed in.
    For example, if the string to search for (-str <string> option) is found in any of the label names,
    then the split happens on the first label that matches.  It also updates the label counts.
    
    Currently, this script only supports MPB's with the following FW commands and this supported structure:
        DMAS SQPG,SM,<integer>,<string>
        SQLB "<string>",MPBU,<integer>,<integer>,"",<string>
        SQLB "<string>",MPBU,<integer>,<integer>,,<string>
        SQPG <integer>,CALL,,"<string>",,<string>
        SQPG <integer>,BEND,,,,<string>
        NOOP "<string>",,,
    MPB's with unsupported FW commands are skipped and noted in the log file (placed in the output directory)
"""
import glob
import time
import logging
from common import *
import argparse
import csv
import collections

_start_time = time.time()
log = None

__author__ = 'Roger'

VECTOR_OPTFILE_HEADER = 'hp93000,vector,0.1'
PMFL_OPTFILE_HEADER = 'hp93000,pattern_master_file,0.1'
TESTFLOW_OPTFILE_HEADER = 'hp93000,testflow,0.1'
TESTFLOW_MFH_OPTFILE_HEADER = 'hp93000,testflow_master_file,0.1'
TESTFLOW_LANGUAGE_HEADER = 'language_revision = 1;'
DEFAULT_FUNC_TM = 'ti_tml.Digital.Functional'
DEFAULT_CONN_TM = 'VAYU_tml.Misc.DcSigMultPinSetup'
DEFAULT_DISC_TM = 'VAYU_tml.DcSigPinDisconnect'
MFH_FILENAME = 'split.mfh'
DEFAULT_MFH_CONTENT = 'testerfile : Final_flow\n'\
                      'information : common/information.tf\n'\
                      'flags : common/flags.tf\n'\
                      'bins : common/bins.tf\n'\
                      'setup : Final/setup.tf\n'\
                      'var_default : Final/var_default.tf\n'

INIT_LABEL_ID = '_init'
MAIN_LABEL_ID = '_main'
VECTORS_SUBDIR = 'vectors'
TESTFLOW_SUBDIR = 'tf_files'

class MpbSplit(object):

    # define regex for searches
    dmasPat = re.compile(r'DMAS SQPG,SM,(?P<port_count>[0-9]+),\((?P<port>\S+)\)')
    sqlbPat = re.compile(r'SQLB "(?P<mpb_name>[^"]+)",MPBU,(?P<start>\S+),(?P<stop>[0-9]+),("")?,\((?P<port>[^\)]+)\)')
    sqpgPat = re.compile(r'SQPG (?P<number>[0-9]+),(?P<command>CALL|BEND)?,,(?:"(?P<label>[^"]+)")?,,\((?P<port>\S+)\)')
    noopPat = re.compile(r'NOOP ("[^\"]*")?,,,')

    # all mpbs that were read in and their data for each port
    mpbs = collections.OrderedDict()

    # list of mpbs that are to be split and label number of first label to begin the 2nd mpb
    mpbs2split = collections.OrderedDict()

    # list of mpbs that were skipped due to unsupported FW commands
    skiplist = []

    # mpb label names that were created
    mpb_label_names_created = collections.OrderedDict()

    def __init__(self,args,out_dir,brstObj):
        outdir,info_msg,warn_msg = get_valid_dir(name=args.name,outdir=out_dir)
        for msg in warn_msg:
            print 'WARNING!!! ',msg
            log.warning(msg)
        for msg in info_msg:
            log.info(msg)

        for pathfn in glob.glob(args.mpb_dir+"/*_MPB*"):
            fn = os.path.basename(pathfn)
            labelFromFileName = fn.split('.')[0]
            if labelFromFileName not in brstObj.burst_corners:
                continue

            msg = 'Analyzing: '+fn+' ...'
            print msg
            log.info(msg)

            # init values for mpb
            hdr_found = False
            port = None
            total = 0

            for line in myOpen(pathfn):
                unknown_line_error = 'Unknown line found in MPB: '+fn+'\n\t   offending line: '+line + '\t(Use -h option to see what FW commands are supported)'
                if not hdr_found:
                    if -1 != line.find(VECTOR_OPTFILE_HEADER):
                        hdr_found = True
                else:

                    dmasObj = re.search(self.dmasPat,line)
                    sqlbObj = re.search(self.sqlbPat,line)
                    sqpgObj = re.search(self.sqpgPat,line)
                    noopObj = re.search(self.noopPat,line)

                    if dmasObj:

                        total = int(dmasObj.group('port_count'))
                        port = dmasObj.group('port')

                    elif sqlbObj:

                        mpb_name = sqlbObj.group('mpb_name')
                        if mpb_name not in brstObj.burst_corners:
                            break
                        start = int(sqlbObj.group('start'))
                        stop = int(sqlbObj.group('stop'))
                        if (stop-start)+1 != total:
                            sys.exit('Invalid DMAS count vs SQLB count in: '+fn+'\n\tDMAS total          : '+str(total)+'\n\tSQLB (stop-start)+1 : '+str(stop+1))
                        elif sqlbObj.group('port') != port:
                            sys.exit('Multiple ports found in MPB: '+sqlbObj.group('port')+' and '+port)
                        elif mpb_name not in self.mpbs:
                            self.mpbs[mpb_name] = collections.OrderedDict()
                        if port not in self.mpbs[mpb_name]:
                            self.mpbs[mpb_name][port] = []

                    elif sqpgObj:

                        label = sqpgObj.group('label')
                        command = sqpgObj.group('command')
                        number = int(sqpgObj.group('number'))

                        if command == 'CALL':
                            if label is None:
                                sys.exit(unknown_line_error)
                            elif -1 != label.find(args.string2match):
                                if number == 0:
                                    #this binl does not need to be split (match starts on first label)
                                    break
                                if mpb_name not in self.mpbs2split:
                                    log.info('\t\t\t'+fn+' Criteria matched.  Will attempt to split (unless skipped due to unsupported FW commands) ....')
                                    self.mpbs2split[mpb_name] = number
                            self.mpbs[mpb_name][port].append(label)
                        elif command == 'BEND':
                            if label is not None:
                                self.mpbs2split.pop(mpb_name,None)
                                if fn not in self.skiplist:
                                    self.skiplist.append(fn)
                                    warn = unknown_line_error+'\tSkipping ...'
                                    log.warning(warn)
                                    print warn
                                continue
                        else:
                            self.mpbs2split.pop(mpb_name,None)
                            if fn not in self.skiplist:
                                self.skiplist.append(fn)
                                warn = unknown_line_error+'\tSkipping ...'
                                log.warning(warn)
                                print warn
                            continue
                    elif noopObj:
                        pass
                    else:
                        self.mpbs2split.pop(mpb_name,None)
                        if fn not in self.skiplist:
                            self.skiplist.append(fn)
                            warn = unknown_line_error+'\tSkipping ...'
                            log.warning(warn)
                            print warn
                        continue
            if fn in self.skiplist:
                break

        msg1 = 'NUMBER OF MPB\'s THAT WE ARE SPLITTING: '+str(len(self.mpbs2split))
        msg2 = 'NUMBER OF MPB\'s THAT MATCHED BUT WERE SKIPPED (DUE TO UNSUPPORTED USE OF FW COMMANDS): '+str(len(self.skiplist))
        print msg1
        print msg2
        log.info(msg1)
        log.info(msg2)

        pmfl_pathfn = os.path.join(outdir,'mpb_split.pmfl')
        msg = 'Creating: '+pmfl_pathfn+' ...'
        print msg
        log.info(msg)
        pmfl = myOpen(pmfl_pathfn,'w')
        pmfl.write(PMFL_OPTFILE_HEADER+'\n\n')
        pmfl.write('path:\n')
        pmfl.write('../'+VECTORS_SUBDIR+'\n\n')
        pmfl.write('files:\n\n')

        vectors_dir,info_msg,warn_msg = get_valid_dir(name=args.name, outdir=os.path.join(outdir, VECTORS_SUBDIR))
        for msg in warn_msg:
            print 'WARNING!!! ',msg
            log.warning(msg)
        for msg in info_msg:
            log.info(msg)

        for mpb_name in self.mpbs2split:
            mpb1_name = mpb_name+INIT_LABEL_ID
            mpb2_name = mpb_name+MAIN_LABEL_ID
            if mpb1_name in self.mpb_label_names_created:
                sys.exit("Duplicate label found: "+mpb1_name)
            if mpb2_name in self.mpb_label_names_created:
                sys.exit("Duplicate label found: "+mpb2_name)
            self.mpb_label_names_created[mpb1_name] = mpb_name
            self.mpb_label_names_created[mpb2_name] = mpb_name
            mpb1_pathfn = os.path.join(vectors_dir,mpb1_name+args.extension)
            mpb2_pathfn = os.path.join(vectors_dir,mpb2_name+args.extension)
            pmfl.write('  '+mpb1_name+args.extension+'\n')
            pmfl.write('  '+mpb2_name+args.extension+'\n')
            msg = 'Creating: '+mpb1_pathfn+' ...'
            print msg
            log.info(msg)
            msg = 'Creating: '+mpb2_pathfn+' ...'
            print msg
            log.info(msg)
            mpb1 = myOpen(mpb1_pathfn,'w')
            mpb2 = myOpen(mpb2_pathfn,'w')
            mpb1.write(VECTOR_OPTFILE_HEADER+'\n')
            mpb2.write(VECTOR_OPTFILE_HEADER+'\n')
            num = int(self.mpbs2split[mpb_name])

            for port in self.mpbs[mpb_name]:
                orig_total = len(self.mpbs[mpb_name][port])

                for n,label in enumerate(self.mpbs[mpb_name][port]):

                    if n < num:
                        loc = n
                        mpb1_total = num + 1
                        if loc == 0:
                            mpb1.write('DMAS SQPG,SM,'+str(mpb1_total)+',('+port+')\n')
                            mpb1.write('SQLB "'+mpb1_name+'",MPBU,0,'+str(mpb1_total-1)+',"",('+port+')\n')
                        mpb1.write('SQPG '+str(loc)+',CALL,,"'+label+'",,('+port+')\n')
                        if loc == mpb1_total - 2:
                            mpb1.write('SQPG '+str(loc+1)+',BEND,,,,('+port+')\n')
                    else:
                        loc = n - num
                        mpb2_total = (orig_total - num) + 1
                        if loc == 0:
                            mpb2.write('DMAS SQPG,SM,'+str(mpb2_total)+',('+port+')\n')
                            mpb2.write('SQLB "'+mpb2_name+'",MPBU,0,'+str(mpb2_total-1)+',"",('+port+')\n')
                        mpb2.write('SQPG '+str(loc)+',CALL,,"'+label+'",,('+port+')\n')
                        if loc == mpb2_total - 2:
                            mpb2.write('SQPG '+str(loc+1)+',BEND,,,,('+port+')\n')

            mpb1.close()
            mpb2.close()
        pmfl.close()
        return


class CreateTestFlow(object):

    # unique testmethod id for each testsuite
    __tm = 0

    # container for all testsuites that we need to create and their relevant data
    testsuites = collections.OrderedDict()
    ts_orig_labels = {}

    #empty sections
    sect_top = '-'*65 + '\n'
    sect_bot = '\n' + 'end' + '\n' + '-'*65
    testmethodlimits = sect_top + 'testmethodlimits' + sect_bot
    binning = sect_top + 'binning' + sect_bot
    oocrule = sect_top + 'oocrule' + sect_bot
    context = sect_top + 'context' + sect_bot
    hardware_bin_descriptions = sect_top + 'hardware_bin_descriptions' + sect_bot

    @staticmethod
    def getTMId():
        """Get unique testmethod id"""
        CreateTestFlow.__tm += 1
        return 'tm_'+str(CreateTestFlow.__tm)

    def assignTMIds(self,brstObj,mpbObj):
        for mpb_label,orig_label in mpbObj.mpb_label_names_created.iteritems():

            if orig_label not in brstObj.burst_corners:
                continue

            # init and main testsuites
            suite = mpb_label+'_st'
            self.testsuites[suite] = self.getTMId()
            self.ts_orig_labels[suite] = orig_label

            # create connect and disconnect testsuites
            if mpb_label[-len(INIT_LABEL_ID):] == INIT_LABEL_ID:
                suite = mpb_label[:-5]+'_conn_st'
                self.testsuites[suite] = self.getTMId()
                self.ts_orig_labels[suite] = orig_label
            if mpb_label[-len(MAIN_LABEL_ID):] == MAIN_LABEL_ID:
                suite = mpb_label[:-5]+'_disc_st'
                self.testsuites[suite] = self.getTMId()
                self.ts_orig_labels[suite] = orig_label

    def __init__(self,args,out_dir,brstObj,mpbObj):
        self.assignTMIds(brstObj,mpbObj)

        mfh_pathfn = os.path.join(outdir,MFH_FILENAME)
        with open(mfh_pathfn,'w') as splitfn:
            msg = 'Creating: '+mfh_pathfn+' ...'
            print msg
            log.info(msg)
            splitfn.write(TESTFLOW_MFH_OPTFILE_HEADER+'\n')
            splitfn.write(DEFAULT_MFH_CONTENT)

            with open(args.tc_file) as tc_file:
                msg = 'Reading: '+args.tc_file+' ...'
                print msg
                log.info(msg)
                for row in csv.DictReader(tc_file):
                    condition = row['TestCondition'].strip()

                    # check for any labels that have this condition
                    matched_labels = [label for label,cond in brstObj.burst_corners.iteritems() if cond == condition]
                    if not len(matched_labels):
                        continue
                    else:
                        msg = "\tMATCHED Condition : Label(s) => {} : {}".format(condition,','.join(matched_labels))
                        print msg
                        log.info(msg)

                    supplies = ','.join([s.strip() for s in row if s.strip() not in ['TestCondition','ShortName']])
                    voltages = ','.join([row[s].strip() for s in row if s.strip() not in ['TestCondition','ShortName']])

                    flows_dir,info_msg,warn_msg = get_valid_dir(name=args.name, outdir=os.path.join(outdir, TESTFLOW_SUBDIR))
                    for msg in warn_msg:
                        print 'WARNING!!! ',msg
                        log.warning(msg)
                    for msg in info_msg:
                        log.info(msg)

                    ofile_pathfn = os.path.join(flows_dir,condition+'.tf')
                    with open(ofile_pathfn,'w') as ofile:
                        msg = 'Creating: '+ofile_pathfn+' ...'
                        print msg
                        log.info(msg)
                        ofile.write(TESTFLOW_OPTFILE_HEADER+'\n')
                        ofile.write(TESTFLOW_LANGUAGE_HEADER+'\n\n')

                        ofile.write('testmethodparameters\n\n')
                        for ts,tm in self.testsuites.iteritems():
                            if ts not in self.ts_orig_labels:
                                sys.exit("Unknown testsuite: "+ts)
                            elif self.ts_orig_labels[ts] not in matched_labels:
                                continue
                            ofile.write(tm+':\n')
                            if ts[-8:] == '_conn_st':
                                # Parameters for DCSig Connect Testsuite
                                ofile.write('  "DcSig Pins" = "'+supplies+'";\n')
                                ofile.write('  "DcSig Volts" = "'+voltages+'";\n')
                                ofile.write('  "Settle Time" = "0";\n')
                            elif ts[-8:] == '_disc_st':
                                # Parameter for DCSig Disconnect Testsuite
                                ofile.write('  "SIG Pins" = "'+supplies+'";\n')
                            else:
                                # Parameters for Functional Testsuite
                                ofile.write('  "ComplementBurst" = "No";\n')
                                ofile.write('  "ComplementBurstName" = "";\n')
                                ofile.write('  "Corner" = "'+condition+'";\n')
                                ofile.write('  "Func_limit_name" = "'+ts[:-3]+'";\n')
                                ofile.write('  "Init_limit_name" = "";\n')
                                ofile.write('  "Init_pattern" = "";\n')
                                ofile.write('  "Interleave_init_pattern" = "No";\n')
                                ofile.write('  "Mask_pins" = "";\n')
                                ofile.write('  "Masked_pins" = "";\n')
                                ofile.write('  "Results_per_label" = "Yes";\n')
                                ofile.write('  "Retest" = "No";\n')
                                ofile.write('  "Site_match_mode" = "No";\n')
                                ofile.write('  "SpeedSort" = "No";\n')
                                ofile.write('  "SpeedSortAdaptiveSpec" = "";\n')
                                ofile.write('  "Stop_on_fail" = "No";\n')
                                ofile.write('  "Util_purpose_off" = "";\n')
                                ofile.write('  "Util_purpose_on" = "SuppliesOn";\n')
                        ofile.write('\nend\n')

                        ofile.write(self.testmethodlimits+'\n')

                        ofile.write('testmethods\n\n')
                        for ts,tm in self.testsuites.iteritems():
                            if ts not in self.ts_orig_labels:
                                sys.exit("Unknown testsuite: "+ts)
                            elif self.ts_orig_labels[ts] not in matched_labels:
                                continue
                            ofile.write(tm+':\n')
                            if ts[-8:] == '_conn_st':
                                ofile.write('  testmethod_class = "'+args.conn_tm+'";\n')
                            elif ts[-8:] == '_disc_st':
                                ofile.write('  testmethod_class = "'+args.disc_tm+'";\n')
                            else:
                                ofile.write('  testmethod_class = "'+args.func_tm+'";\n')
                        ofile.write('\nend\n')

                        ofile.write('-'*65+'\n')
                        ofile.write('test_suites\n\n')
                        for ts,tm in self.testsuites.iteritems():
                            if ts not in self.ts_orig_labels:
                                sys.exit("Unknown testsuite: "+ts)
                            elif self.ts_orig_labels[ts] not in matched_labels:
                                continue
                            ofile.write(ts+'__'+condition+':\n')
                            ofile.write('local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;\n')
                            ofile.write('  override = 1;\n')
                            if ts[-(len(INIT_LABEL_ID)+3):] == INIT_LABEL_ID+'_st':
                                ofile.write('  override_seqlbl = "'+ts.split(INIT_LABEL_ID)[0]+INIT_LABEL_ID+'";\n')
                            elif ts[-(len(MAIN_LABEL_ID)+3):] == MAIN_LABEL_ID+'_st':
                                ofile.write('  override_seqlbl = "'+ts.split(MAIN_LABEL_ID)[0]+MAIN_LABEL_ID+'";\n')
                            ofile.write('  override_testf = '+tm+';\n')
                        ofile.write('\nend\n')

                        ofile.write('-'*65+'\n')
                        ofile.write('test_flow\n\n')
                        ofile.write('{\n')
                        for ts in self.testsuites:
                            if ts not in self.ts_orig_labels:
                                sys.exit("Unknown testsuite: "+ts)
                            elif self.ts_orig_labels[ts] not in matched_labels:
                                continue
                            in_init = ts[-(len(INIT_LABEL_ID)+3):] == INIT_LABEL_ID+'_st'
                            in_conn = ts[-8:] == '_conn_st'
                            in_disc = ts[-8:] == '_disc_st'
                            if in_init:
                                ofile.write('  {\n')
                            if in_conn or in_disc:
                                ofile.write('    run('+ts+'__'+condition+');\n')
                            else:
                                ofile.write('    run_and_branch('+ts+'__'+condition+')\n    then\n    {\n    }\n    else\n    {\n      multi_bin;\n    }\n')
                            if in_disc:
                                ofile.write('  },open,"'+ts[:-(len('_disc_st')+4)]+'_S",""\n')
                        ofile.write('},open,"'+condition+'_S",""\n')
                        ofile.write('\nend\n')

                        ofile.write(self.binning)
                        ofile.write(self.oocrule)
                        ofile.write(self.context)
                        ofile.write(self.hardware_bin_descriptions)

                        ofile.close()

                        splitfn.write('GROUP '+condition+'_S [open] : '+os.path.basename(os.path.normpath(out_dir))+'/'+condition+'.tf\n')

class GetBursts(object):
    def __init__(self,brst_file):
        with open(brst_file) as file:
            msg = 'Reading: '+brst_file+' ...'
            print msg
            log.info(msg)
            # skip the first row which has headers and create dictionary with {key : value} from {1st column : 2nd column}
            self.burst_corners = dict([x for i,x in enumerate(csv.reader(file)) if i != 0])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description: "+sys.modules[__name__].__doc__)
    parser.add_argument('-name','--name',required=False,default='',help='Optional name used for output files/logs.')
    parser.add_argument('-d','--debug',action='store_true',help='print a lot of debug stuff to dlog')
    parser.add_argument('-out','--output_dir',required=False,default='', help='Directory to place log file(s).')
    parser.add_argument('-max','--maxlogs',type=int,default=1,required=False, help='(0=OFF:log data to stdout). Set to 1 to keep only one log (subsequent runs will overwrite).')
    parser.add_argument('-mpb','--mpb_dir',required=True, help='Path to MPB files that you want to split')
    parser.add_argument('-str','--string2match',required=True,default='', help='Substring to search for in label names where MPB is to be split.')
    parser.add_argument('-ext','--extension',required=False,default='.mpb', help='Extension to give MPB output files.')
    parser.add_argument('-tc','--tc_file',required=True,default='', help='Test conditions file.')
    parser.add_argument('-brst','--burst_file',required=True,default='', help='Burst needed to split file.')
    parser.add_argument('-func_tm','--func_tm',required=False,default=DEFAULT_FUNC_TM, help='Test method for functional tests.')
    parser.add_argument('-conn_tm','--conn_tm',required=False,default=DEFAULT_CONN_TM, help='Test method for DCSig connect.')
    parser.add_argument('-disc_tm','--disc_tm',required=False,default=DEFAULT_DISC_TM, help='Test method for DCSig disconnect.')
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

    b = GetBursts(args.burst_file)
    m = MpbSplit(args, outdir,b)
    tc = CreateTestFlow(args, outdir,b,m)

    log.info('ARGUMENTS:\n\t'+'\n\t'.join(['--'+k+'='+str(v) for k,v in args.__dict__.iteritems()]))
    msg = 'Number of WARNINGS for "{}": {}'.format(os.path.basename(sys.modules[__name__].__file__),log.warning.counter)
    print msg
    log.info(msg)
    msg = 'Number of ERRORS for "{}": {}'.format(os.path.basename(sys.modules[__name__].__file__),log.error.counter)
    print msg
    log.info(msg)

    time = time.time()-_start_time
    msg = 'Script took ' + str(round(time,3)) + ' seconds (' + humanize_time(time) + ')'
    log.info(msg)
    print '\n' + msg
