#!/usr/bin/env python
"""
    First access script to get program file and it's dependencies.
"""

import logging as log
import sys
import os
import re
import argparse
import time
from common import humanize_time

_start_time = time.time()

__author__ = 'Roger Logan'
__verbose__ = False

OPTFILE_HEADER = 'hp93000,testprog,0.1'

# log.basicConfig(filename='example.log',format='%(levelname)s: %(message)s', level=log.DEBUG)
log.basicConfig(format='%(levelname)s: %(message)s', level=log.DEBUG)

class ProgFile(object):

    contents = {}
    path, fn = '',''

    def __init__(self, pathfn):
        self.path, self.fn = os.path.split(pathfn)
        log.info('Parsing '+self.fn+' .....')
        progPat = re.compile(r'(?P<key>.*):(?P<value>.*)')
        for line in open(pathfn).readlines():
            obj = re.search(progPat,line)
            if obj:
                self.contents[obj.group('key').strip()] = obj.group('value').strip()

    def __str__(self):
        rstr = OPTFILE_HEADER + '\n'
        for k,v in self.contents.iteritems():
            rstr += k + ' : ' + v + '\n'
        return rstr

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description: "+sys.modules[__name__].__doc__)
    parser.add_argument('-p','--path_to_progfile',required=True, help='Full path to program file located in program directory')
    parser.add_argument('-v','--verbose',action='store_true',help='print a lot of stuff')
    args = parser.parse_args()
    __verbose__ = args.verbose

    tp = ProgFile(args.path_to_progfile)
    time = time.time()-_start_time
    print '\nScript took',round(time,3),'seconds','('+humanize_time(time)+')'
