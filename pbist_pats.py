#!/usr/bin/env python
"""
    This script splits a BIST mpb into many mpb's.
"""
import os
import sys
import re
import gzip
import shutil
import time
import logging as log
from pprint import *
from common import humanize_time,init_logging,myOpen,replace
import argparse
_start_time = time.time()

__author__ = 'Roger'

VECTOR_OPTFILE_HEADER = 'hp93000,vector,0.1'

class PbistPats(object):

    total_count = ''
    port = ''
    mpb_name = ''
    start = 0
    stop = 1
    wavetable = ''

    def __init__(self,args,outdir):
        """

        :param args:
        :param outdir:
        :return:
        """
        outdir = args.output_dir
        dmasPat = re.compile('^\s*DMAS\s+SQPG\s*,\s*SM\s*,(?P<total_count>[0-9]+)\s*,\s*\(\s*(?P<port>\S+)\s*\)\s*$')
        sqlbPat = re.compile('^\s*SQLB\s+"\s*(?P<mpb_name>\S+)\s*"\s*,\s*MPBU\s*,\s*(?P<start>\S+)\s*,\s*(?P<stop>\S+)\s*,\s*""\s*,\(\s*(?P<port>\S+)\s*\)\s*$')
        sqpgPat = re.compile('^\s*SQPG\s+(?P<address>[0-9]+)\s*,\s*CALL\s*,\s*,\s*"\s*(?P<label>\S+)\s*"\s*,\s*,\(\s*(?P<port>\S+)\s*\)\s*$')
        hdr_found = False
        dmas_found = False
        sqlb_found = False
        self.path, self.fn = os.path.split(args.path_to_PBIST_MPB)
        for line in myOpen(args.path_to_PBIST_MPB):
            if not hdr_found:
                if -1 != line.find(VECTOR_OPTFILE_HEADER):
                    hdr_found = True
            elif not dmas_found:
                dmasObj = re.search(dmasPat,line)
                if dmasObj:
                    self.total_count = dmasObj.group('total_count')
                    self.port = dmasObj.group('port')
                    dmas_found = True
            elif not sqlb_found:
                sqlbObj = re.search(sqlbPat,line)
                if sqlbObj:
                    self.mpb_name = sqlbObj.group('mpb_name')
                    self.start = int(sqlbObj.group('start'))
                    self.stop = int(sqlbObj.group('stop'))
                    if sqlbObj.group('port') != self.port:
                        err = 'Multiple ports found in MPB: '+sqlbObj.group('port')+' and '+self.port+'.  Exiting ...'
                        log.error(err)
                        sys.exit(err)
                    sqlb_found = True
            else:
                sqpgObj = re.search(sqpgPat,line)
                if sqpgObj:
                    self.setup_files(sqpgObj.group('label'),sqpgObj.group('port'),outdir)

    def create_open_file(self,pathfn):
        """
        Let's create and then open the new mpb/label (make sure to close it!)
        :param pathfn: full path to new file
        :return: fp (file pointer)
        """
        if os.path.isfile(pathfn):
            log.warning(pathfn + ' already exists! Clobbering ...')
        try:
            fp = gzip.open(pathfn,'wb')
            fp.write(VECTOR_OPTFILE_HEADER+'\n')
        except:
            raise IOError
        return fp


    def setup_files(self, orig_label, port, outdir):
        """
        Create   new MPB: <base_label>_arp_MPB.binl.gz
                contains: CALL <base_label>_<port>_arp.binl.gz
                          END
        Create new orig_label: <base_label>_<port>_arp.binl.gz
                contains: JSUB jsub2_<base_label>_<port>_arp
                          END
        Move  orig orig_label: FROM <orig_label>.binl.gz TO: jsub2_<base_label>_<port>_arp.binl.gz

        :param orig_label: main name of original pattern label
        :param port: should be pNONASYNC1
        :param outdir: should be 'ARPv7' somewhere
        :return: NULL
        """

        base_label = orig_label.split('_' + port)[0]

        mpb_label = base_label+'_arp_MPB'
        mpb_file = os.path.join(outdir,mpb_label+'.binl.gz')

        jsub_label = base_label+'_'+port+'_arp'
        jsub_file = os.path.join(outdir,jsub_label+'.binl.gz')

        jsub2_label = 'jsub2_'+base_label+'_'+port+'_arp'
        jsub2_file = os.path.join(outdir,jsub2_label+'.binl.gz')

        orig_file = os.path.join(self.path, orig_label + '.binl.gz')

        # get the wavetable name
        wvtPat = re.compile('SQLB "(?P<label_name>[^"]+)",MAIN,(?P<start>[0-9]+),(?P<stop>[0-9]+),"(?P<wavetable>[^"]+)",\((?P<port>[^\)]+)\)')
        for line in myOpen(orig_file):
            wvtObj = re.search(wvtPat,line)
            if wvtObj:
                self.wavetable = wvtObj.group('wavetable')
                # we got what we came for so jump out
                break
        if not len(self.wavetable):
            err = 'No Wavetable found in original orig_label: ' + orig_label
            log.critical(err)
            sys.exit(err)

        # let's copy orig_label to jsub2_label
        try:
            shutil.copy(orig_file,jsub2_file)
            replace(jsub2_file,orig_label,jsub2_label)
        except:
            raise IOError

        # let's create the MPB (and overwrite if already exists)
        out = self.create_open_file(mpb_file)
        out.write('DMAS SQPG,SM,2,('+port+')\n')
        out.write('SQLB "'+mpb_label+'",MPBU,0,1,"",('+port+')\n')
        out.write('SQPG 0,CALL,,"'+jsub_label+'",,('+port+')\n')
        out.write('SQPG 1,BEND,,,,('+port+')\n')
        out.close()

        # let's create the jsub call pattern (and overwrite if already exists)
        out = self.create_open_file(jsub_file)
        out.write('DMAS SQPG,SM,4,('+port+')\n')
        out.write('SQLB "'+jsub_label+'",MAIN,0,3,"'+self.wavetable+'",('+port+')\n')
        out.write('SQLB LBL,"'+jsub_label+'","PARA_MEM=SHMEM,SCAN_MEM=NONE,PARA_MCTX=DEFAULT",('+port+')\n')
        out.write('SQPG 0,STVA,0,,,('+port+')\n')
        out.write('SQPG 1,STSA,,,,('+port+')\n')
        out.write('SQPG 2,JSUB,,"'+jsub2_label+'",,('+port+')\n')
        out.write('SQPG 3,STOP,,,,('+port+')\n')
        out.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description: "+sys.modules[__name__].__doc__)
    parser.add_argument('-mpb','--path_to_PBIST_MPB',required=True, help='Path to FULL pbist MPB file that you want to split')
    parser.add_argument('-v','--verbose',action='store_true',help='print a lot of stuff')
    parser.add_argument('-out','--output_dir',required=False,default='',help='Directory to place log file(s).')
    parser.add_argument('-max','--maxlogs',type=int,default=10,required=False, help='(0=OFF:log data to stdout). Set to 1 to keep only one log (subsequent runs will overwrite).')
    args = parser.parse_args()

    outdir = init_logging(scriptname=os.path.split(sys.modules[__name__].__file__)[1],args=args)

    pbist = PbistPats(args,outdir)

    time = time.time()-_start_time
    msg = 'Script took ' + str(round(time,3)) + ' seconds (' + humanize_time(time) + ')'
    log.info(msg)
    print '\n' + msg
