#!/usr/bin/env python
"""
The script splits a log file into several log files for each unit based on die id

"""

import argparse
from common import *
import time
_start_time = time.time()
log = None

__author__ = 'Roger'

startPat = re.compile("^\s*\*\s*(?P<vector>.*?)\s*\*\s*(?P<sh_wft>.*?)\s*;")

def parse_logfile(pathfn):
    path, fn = os.path.split(pathfn)
    msg = 'Parsing log file: {} .....'.format(fn)
    print msg
    log.info(msg)
    limPat = re.compile(r'^\s*testerfile\s*:(?P<limit_file>.*)')
    hdr_found = False
    lineno = 0
    start = False
    with open(pathfn) as logfile:
        for line in logfile:
            lineno+=1
            if not start and -1 != line.find('Init_framework'):
                start = True
            if start:
                print line
            # if lineno>20:
            #     sys.exit()

def main():
    global log
    parser = argparse.ArgumentParser(description="Description: "+sys.modules[__name__].__doc__)
    parser.add_argument('-name','--name',required=True,default='',help='Optional name used for output files/logs.')
    parser.add_argument('-d','--debug',action='store_true',help='Print a lot of debug stuff to dlog')
    parser.add_argument('-out','--output_dir',required=True,default='', help='Directory to place output files/logs.')
    parser.add_argument('-log','--log_file',required=True,default='', help='Path to log file ')
    parser.add_argument('-max','--maxlogs',type=int,default=1,required=False, help='(0=OFF:log data to stdout). Set to 1 to keep only one log (subsequent runs will overwrite).')

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

    log.info('ARGUMENTS:\n\t'+'\n\t'.join(['--'+k+'='+str(v) for k,v in args.__dict__.iteritems()]))
    msg = 'Number of WARNINGS for "{}": {}'.format(os.path.basename(sys.modules[__name__].__file__),log.warning.counter)
    print msg
    log.info(msg)
    msg = 'Number of ERRORS for "{}": {}'.format(os.path.basename(sys.modules[__name__].__file__),log.error.counter)
    print msg
    log.info(msg)

    parse_logfile(args.log_file)


if __name__ == "__main__":
    main()

    time = time.time()-_start_time
    msg = 'Script took ' + str(round(time,3)) + ' seconds (' + humanize_time(time) + ')'
    log.info(msg)
    print '\n' + msg
