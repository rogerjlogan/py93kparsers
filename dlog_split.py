#!/usr/bin/env python
"""
The script splits a log file into several log files..

    algorithm:
        1) beginning delim: either beginning of log file (for first split) or first appearance of "] Init_framework ("
        2) end delim: last line before "] Init_framework (" but AFTER "] bin_disconnect (" has been seen
        3) log files are named with their beginning lineno from original log file
        4) DEVDIEID, if found, is noted in the *.log file with the location (which split log.txt it is in)

"""

import argparse
from common import *
import time
_start_time = time.time()
log = None

__author__ = 'Roger'

def parse_logfile(pathfn,name='',outdir=''):
    if not os.path.isdir(outdir):
        try:
            msg = "Creating new directory: "+outdir
            log.info(msg)
            os.makedirs(outdir)
        except:
            err = 'Unable to create directory: '+outdir+'\n'
            err += 'Check file read/write permissions\n'
            err += 'You might also try closing all editors and explorer windows with a view in this directory.\n'
            print err
            log.error(err)
            raise IOError
    path, fn = os.path.split(pathfn)
    msg = 'Parsing log file: {} .....'.format(fn)
    print msg
    log.info(msg)
    lineno = 0
    beg_started,end_started = False,False
    fn = 'log_1.txt'
    msg = '\tCreating log: '+fn
    print msg
    log.info(msg)
    fp = open(os.path.join(outdir, fn),'w')
    diePat = re.compile(r'DEVDIEID\=(?P<devdieid>\S+)')
    with open(pathfn) as logfile:
        for line in logfile:
            lineno+=1
            newlog = False
            if not beg_started:
                if not end_started and -1 != line.find('] Init_framework ('):
                    # found beginning of a section
                    beg_started = True
                    newlog = True
            else:
                if -1 != line.find('] bin_disconnect ('):
                    # found the beginning of the end .... mmmmmwwwwahahahahahaha
                    end_started = True
                elif end_started:
                    # This IS the end !
                    beg_started = False
                    end_started = False
                else:
                    dieObj = diePat.search(line)
                    if dieObj:
                        log.info('\t\t'+ fn + ' : ' + dieObj.group('devdieid'))
            if newlog:
                # close the old file pointer and start a new one
                fp.close()
                fn = 'log_'+str(lineno+1)+'.txt'
                msg = '\tCreating log: '+fn
                print msg
                log.info(msg)
                fp = open(os.path.join(outdir, fn),'w')
            fp.write(line)
    fp.close()

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

    parse_logfile(args.log_file,args.name,args.output_dir)

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
