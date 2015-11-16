#!/usr/bin/env python
"""
    First access script to get program file and it's dependencies.
"""

import logging as log
import sys
import os
import re
import argparse
import pyparsing as pp
from pprint import pprint
import time
from common import humanize_time,init_logging

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

    def __init__(self, pathfn):
        self.path, self.fn = os.path.split(pathfn)
        log.info('Parsing '+self.fn+' .....')

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

    def __str__(self):
        rstr = TESTPROG_OPTFILE_HEADER + '\n'
        for k,v in self.contents.iteritems():
            rstr += k + ' : ' + v + '\n'
        return rstr

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description: "+sys.modules[__name__].__doc__)
    parser.add_argument('-tp','--path_to_progfile',required=True, help='Path to testprog file')
    parser.add_argument('-out','--output_dir',required=False,default='', help='Directory to place log file(s).')
    parser.add_argument('-v','--verbose',action='store_true',help='print a lot of stuff')
    parser.add_argument('-max','--maxlogs',type=int,default=10,required=False, help='(0=OFF:log data to stdout). Set to 1 to keep only one log (subsequent runs will overwrite).')
    args = parser.parse_args()

    init_logging(args.verbose, scriptname=os.path.split(sys.modules[__name__].__file__)[1], logDir=args.output_dir, args=args)

    tp = ProgFile(args.path_to_progfile)

    time = time.time()-_start_time
    msg = 'Script took ' + str(round(time,3)) + ' seconds (' + humanize_time(time) + ')'
    log.info(msg)
    print msg
