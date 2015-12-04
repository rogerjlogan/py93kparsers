#!/usr/bin/env python
"""
    First access script to get program file and it's dependencies.
"""

import logging
import sys
import os
import re
import argparse
from pprint import pprint
import time
from common import *
log = None

_start_time = time.time()

__author__ = 'Roger Logan'

TESTPROG_OPTFILE_HEADER = 'hp93000,testprog,0.1'

def get_file_contents(infile,strip_comments=True):
    """
    Gets contents of file passed and (if strip_comments=True) also
    stripped of comments that start with '#' (and no double quotes in comments)
    :param infile: testprog file name
    :param strip_comments: bool to decide whether to strip single line comments or not
                           ('only supports single line comments that begin with '#')
    :return: str contents of file
    """
    if '.mfh' == infile.strip()[-4:]:
        err = 'Testflow file is an ".mfh" file. This is NOT supported yet! Exiting ...'
        log.critical(err)
        sys.exit(err)
    _f = open(infile)
    contents = '\n'.join(_f.read().splitlines())
    _f.close()
    if strip_comments:
        # string comments before parsing
        contents = re.sub(re.compile(r'#[^"]*?\n') ,'' ,contents)
    return contents


class ProgFile(object):

    contents = {}
    path, fn = '',''
    progdir = ''

    def __init__(self,pathfn,debug=False,progname='',maxlogs=1,outdir=os.path.dirname(os.path.realpath(__file__))):
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
        print msg
        log.info(msg)

        self.path, self.fn = os.path.split(pathfn)
        self.progdir = self.path[:-len('testprog')]
        msg = 'Parsing testprog file: '+self.fn+' .....'
        print msg
        log.info(msg)

        progPat = re.compile(r'(?P<key>.*):(?P<value>.*)')

        hdr_found = False
        for line in get_file_contents(pathfn).split('\n'):
            if not hdr_found:
                if -1 != line.find(TESTPROG_OPTFILE_HEADER):
                    hdr_found = True
            else:
                obj = re.search(progPat,line)
                if obj:
                    self.contents[obj.group('key').strip()] = obj.group('value').strip()
        if not hdr_found:
            err = 'ERROR!!! OptFileHeader ('+TESTPROG_OPTFILE_HEADER+') not found'
            log.critical(err)
            sys.exit(err)

        log.info(pformat(self.contents,indent=4))

        msg = 'Number of WARNINGS for "{}": {}'.format(os.path.basename(sys.modules[__name__].__file__),log.warning.counter)
        print msg
        log.info(msg)
        msg = 'Number of ERRORS for "{}": {}'.format(os.path.basename(sys.modules[__name__].__file__),log.error.counter)
        print msg
        log.info(msg)

    def __str__(self):
        rstr = TESTPROG_OPTFILE_HEADER + '\n'
        for k,v in self.contents.iteritems():
            rstr += k + ' : ' + v + '\n'
        return rstr

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description: "+sys.modules[__name__].__doc__)
    parser.add_argument('-name','--name',required=False,default='',help='Optional name used for output files/logs.')
    parser.add_argument('-d','--debug',action='store_true',help='print a lot of debug stuff to dlog')
    parser.add_argument('-out','--output_dir',required=False,default='', help='Directory to place log file(s).')
    parser.add_argument('-max','--maxlogs',type=int,default=1,required=False, help='(0=OFF:log data to stdout). Set to 1 to keep only one log (subsequent runs will overwrite).')
    parser.add_argument('-tp','--progfile',required=True, help='Path to testprog file')
    args = parser.parse_args()

    tp = ProgFile(pathfn=args.progfile,debug=args.debug,progname=args.name,maxlogs=args.maxlogs,outdir=args.output_dir)

    time = time.time()-_start_time
    msg = 'Script took ' + str(round(time,3)) + ' seconds (' + humanize_time(time) + ')'
    log.info(msg)
    print msg
