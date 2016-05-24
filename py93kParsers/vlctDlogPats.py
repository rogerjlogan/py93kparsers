#!/usr/bin/env python
"""
    Reads a verbose (patterns visible) VLCT datalog to find
    all patterns that are run.
"""
import time
import logging
from common import *
import argparse
import sys
from pprint import pprint
from collections import defaultdict
import glob

_start_time = time.time()
log = None
all_patlist = []

__author__ = 'Roger'

def parse_dlog(dlog_file):
    global all_patlist
    testPat = re.compile(r'^\s*TestName\s*:\s*(?P<test>\S+)')
    hdrPat = re.compile(r'^Pattern\s+P\/F')
    patPat = re.compile(r'^\s*(?P<pattern>[\S+]+)\s+(?P<supply>MODTDL_SLDO_Supplies_(?:Restore|Reset)\(\))?') 
    patlist = defaultdict(list)

    with open(dlog_file) as ifile:
        msg = 'Reading: '+dlog_file+' ...'
        print msg
        log.info(msg)
        in_patlist = False
        header = False
        test = 'INIT TEST STRING'
        pat = 'INIT PAT STRING'
        lineno = 0
        for line in ifile:
            lineno+=1
            testObj = testPat.search(line)
            if testObj:
                test = testObj.group('test')
                if test in patlist:
                    err = 'Duplicate test name in log: '+test
                    log.error(err)
               # patlist[test] = []
                
            if hdrPat.search(line):
                header = True
                in_patlist = True
                continue
            elif header:
                #skip line after header
                header = False
                continue
            if not len(line.replace('-','').strip()):
                in_patlist = False
            elif in_patlist:
                patObj = patPat.search(line)
                if patObj:
                    pat = patObj.group('pattern').strip()
                    if pat == 'Executing':
                        pat += ' '+patObj.group('supply')
                    patlist[test].append(pat)
                    if pat not in all_patlist:
                        all_patlist.append(pat)
    return patlist

def getPmflContent(pmfl_file):
    pmfl_list = []
    with open(pmfl_file) as pmfl:
        for line in pmfl:
            if line.strip().endswith(('.binl','binl.gz')):
                pmfl_list.append(line.strip())
    return pmfl_list

def createCsv(args,patlist,pmfls):

    matches = dict.fromkeys(all_patlist,False)
    for p in all_patlist:
        if p.lower() in [pat.lower()[:len(p)] for pat in pmfls]:
            matches[p] = True
    csv_dir,info_msg,warn_msg = get_valid_dir(name=args.name, outdir=args.output_dir)
    for msg in warn_msg:
        print 'WARNING!!! ',msg
        log.warning(msg)
    for msg in info_msg:
        log.info(msg)

    ofile_pathfn = os.path.join(csv_dir,args.name+'.csv')
    msg  = 'Creating file: '+ofile_pathfn
    print msg
    log.info(msg)

    with open(ofile_pathfn,'w') as ofile:
        ofile.write('TEST,PATTERN,MATCHED?\n')
        for test,value in patlist.iteritems():
            for v in value:
                ofile.write(test+','+v+','+str(matches[v])+'\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description: "+sys.modules[__name__].__doc__)
    parser.add_argument('-name','--name',required=False,default='vlct',help='Optional name used for output files/logs.')
    parser.add_argument('-d','--debug',action='store_true',help='print a lot of debug stuff to dlog')
    parser.add_argument('-out','--output_dir',required=False,default='', help='Directory to place log file(s).')
    parser.add_argument('-max','--maxlogs',type=int,default=1,required=False, help='(0=OFF:log data to stdout). Set to 1 to keep only one log (subsequent runs will overwrite).')
    parser.add_argument('-vlct','--vlct_dlog',required=True,default='', help='Verbose VLCT Datalog input file.')
    parser.add_argument('-pmfl','--pmfl',required=True,default='', help='Pmfl file')
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

#--------------------------------------------------------------------------
# DO NOT CODE ABOVE THIS LINE

    patlist = parse_dlog(args.vlct_dlog)
    pmfls = getPmflContent(args.pmfl)
    createCsv(args,patlist,pmfls)

# DO NOT CODE BELOW THIS LINE
#--------------------------------------------------------------------------

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
