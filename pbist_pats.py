#!/usr/bin/env python
"""
    This script splits a BIST mpb into many mpb's.
"""
import os
import sys
import re
import gzip
import shutil
import csv
import time
import logging as log
from pprint import *
from common import humanize_time,init_logging,myOpen,replace
import argparse
_start_time = time.time()

__author__ = 'Roger'

VECTOR_OPTFILE_HEADER = 'hp93000,vector,0.1'

MBIST_CTLR_FILE = 'memBistCtlr.csv'

class PbistPats(object):

    total_count = ''
    port = ''
    mpb_name = ''
    start = 0
    stop = 1
    wavetable = ''
    seqDict = {}
    skip_labels = []

    # define regex for seaches
    dmasPat = re.compile(r'DMAS SQPG,SM,(?P<total_count>[0-9]+),\((?P<port>\S+)\)')
    sqlbPat = re.compile(r'SQLB "(?P<mpb_name>[^"]+)",MPBU,(?P<start>\S+),(?P<stop>[0-9]+),"",\((?P<port>[^\)]+)\)')
    sqpgPat = re.compile(r'SQPG (?P<address>[0-9]+),CALL,,"(?P<label>[^"]+)",,\((?P<port>\S+)\)')
    wvtPat = re.compile(r'SQLB "(?P<label_name>[^"]+)",MAIN,(?P<start>[0-9]+),(?P<stop>[0-9]+),"(?P<wavetable>[^"]+)",\((?P<port>[^\)]+)\)')
    stopPat = re.compile(r'SQPG (?P<address>[0-9]+),STOP,,,,\((?P<port>\S+)\)')

    def getSeqInstrPerPat(self,pathfn):
        """

        :param pathfn:
        :return:
        """

        with open(pathfn) as csvFile:

            ctlr_num = 0

            numDiag_found = False

            numDiags = {}
            """contains num diags for each VC_ field"""

            pat_idx = {}
            """index of pattern base name to index location"""

            # strip headers of ws before iterating
            headers = [h.strip() for h in csvFile.next().split(',')]
            for i,line in enumerate(csv.DictReader(csvFile,fieldnames=headers)):

                if line['CtlrNum'].strip() != ctlr_num:
                    # starting a new section
                    ctlr_num = line['CtlrNum'].strip()
                    # reset bool
                    numDiag_found = False
                    numDiags.clear()
                    pat_idx.clear()
                    continue

                else:

                    if line['CtlrField'].strip() == 'numDiag':
                        numDiag_found = True
                        for header in line:
                            if header[:3] == 'VC_':
                                # this header is a corner, so lets assign the numDiag for that corner
                                numDiags[header] = int(line[header].strip())
                        continue

                    if numDiag_found and line['CtlrField'].strip() == 'diagPSN':
                        # populate pat_idx = { pat : { corner : numDiag } }
                        patnum = int(line['PatNum'].strip())
                        for corner in numDiags:
                            numDiag = numDiags[corner]
                            pat = line[corner].strip()
                            if patnum <= numDiag:
                                if pat in pat_idx:
                                    if corner in pat_idx[pat]:
                                        if patnum != pat_idx[pat][corner]:
                                            err = 'Duplicate controls (in bist controller file): "PatNum" = '+str(patnum)+' for the same pattern: '+pat
                                            print err
                                            log.error(err)
                                pat_idx[pat] = {corner:patnum}

                    elif line['CtlrField'].strip() == 'diagMaxFails':
                        # populate self.seqDict = { pat : { corner : maxfails } }
                        for pat in pat_idx:
                            corner = pat_idx[pat].keys()[0]
                            patnum = pat_idx[pat][corner]
                            if patnum == int(line['PatNum'].strip()):
                                self.seqDict[pat] = {corner : line[corner].strip()}

    def __init__(self,args,outdir):
        """

        :param args:
        :param outdir:
        :return:
        """

        self.getSeqInstrPerPat(args.memBistCtlr_csv)

        outdir = args.output_dir
        hdr_found = False
        dmas_found = False
        sqlb_found = False
        self.path, self.fn = os.path.split(args.MEM_BIST_MPB)
        for line in myOpen(args.MEM_BIST_MPB):
            if not hdr_found:
                if -1 != line.find(VECTOR_OPTFILE_HEADER):
                    hdr_found = True
            elif not dmas_found:
                dmasObj = re.search(self.dmasPat,line)
                if dmasObj:
                    self.total_count = dmasObj.group('total_count')
                    self.port = dmasObj.group('port')
                    dmas_found = True
            elif not sqlb_found:
                sqlbObj = re.search(self.sqlbPat,line)
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
                sqpgObj = re.search(self.sqpgPat,line)
                if sqpgObj:
                    self.setup_files(sqpgObj.group('label'),sqpgObj.group('port'),outdir)
        return

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
        for line in myOpen(orig_file):
            wvtObj = re.search(self.wvtPat,line)
            if wvtObj:
                self.wavetable = wvtObj.group('wavetable')
                # we got what we came for so jump out
                break
        if not len(self.wavetable):
            err = 'No Wavetable found in original orig_label: ' + orig_label
            log.critical(err)
            sys.exit(err)

        def seqStr(start_count,maxfails,port):
            ostr = 'SQPG '+str(start_count)+',JSUB,,"jsub_arp_CheckForDoneOrPass_1p9sec",,('+port+')\n'
            ostr += 'SQPG '+str(start_count+1)+',JSUB,,"jsub_arp_strobePassH",,('+port+')\n'
            ostr += 'SQPG '+str(start_count+2)+',JSUB,,RETC,ON_PASS,RSTE,,('+port+')\n'
            ostr += 'SQPG '+str(start_count+3)+',LBGN,'+str(maxfails)+',,,('+port+')\n'
            ostr += 'SQPG '+str(start_count+4)+',JSUB,,"logout_single",,('+port+')\n'
            ostr += 'SQPG '+str(start_count+5)+',RETC,ON_PASS,RSTE,,('+port+')\n'
            ostr += 'SQPG '+str(start_count+6)+',JMPE, "jsub_arp_empty", "jsub_arp_empty",,('+port+')\n'
            ostr += 'SQPG '+str(start_count+7)+',LEND,,,,('+port+')\n'
            ostr += 'SQPG '+str(start_count+8)+',RSUB,,,,('+port+')\n'
            return ostr

        with myOpen(orig_file) as orig:
            stop = False
            dmas = False
            for line in orig:
                if dmas and not stop:
                    stopObj = re.search(self.stopPat,line)
                    if stopObj:
                        stop = True
                        start_count = int(stopObj.group('address').strip())
                        if port != stopObj.group('port').strip():
                            err = 'Port change in pattern ports: '+port+','+stopObj.group('port').strip()+' in pat:'+orig_file
                            log.error(err)
                            sys.exit(err)
                        stopStr = stopObj.group(0)
                        try:
                            corner = self.seqDict[base_label].keys()[0]
                            maxfails = self.seqDict[base_label][corner]
                            log.info('Label: %s WAS found in %s',base_label,MBIST_CTLR_FILE)
                        except:
                            log.warning('Label: %s WAS NOT found in %s -- Skipping this label for all processes....',base_label,MBIST_CTLR_FILE)
                            self.skip_labels.append(base_label)
                            return
                        stopStr_repl = seqStr(start_count,maxfails,port)
                        break
                else:
                    dmasObj = re.search(self.dmasPat,line)
                    if dmasObj:
                        dmas = True
                        total_count = int(dmasObj.group('total_count').strip())
                        port = dmasObj.group('port').strip()
                        dmasStr = dmasObj.group(0)
                        dmasStr_repl = 'DMAS SQPG,SM,'+str(total_count+8)+',('+port+')'
                    # don't break, continue searching for STOP
            if not stop:
                err = 'No STOP sequencer found: "SQPG nn,STOP,,,,(<port>)" in pat:'+orig_file
                log.error(err)
                sys.exit(err)
            if not dmas:
                err = 'No DMAS sequencer found: "DMAS SQPG,SM,nn,(<port>)" in pat:'+orig_file
                log.error(err)
                sys.exit(err)

        # let's copy orig_label to jsub2_label
        try:
            shutil.copy(orig_file,jsub2_file)
        except:
            raise IOError

        replace(jsub2_file,orig_label,jsub2_label)
        replace(jsub2_file,dmasStr,dmasStr_repl)
        replace(jsub2_file,stopStr,stopStr_repl)

        # let's create the MPB (and overwrite if already exists)
        mpb = self.create_open_file(mpb_file)
        mpb.write('DMAS SQPG,SM,2,('+port+')\n')
        mpb.write('SQLB "'+mpb_label+'",MPBU,0,1,"",('+port+')\n')
        mpb.write('SQPG 0,CALL,,"'+jsub_label+'",,('+port+')\n')
        mpb.write('SQPG 1,BEND,,,,('+port+')\n')
        mpb.close()

        # let's create the jsub call pattern (and overwrite if already exists)
        jsub = self.create_open_file(jsub_file)
        jsub.write('DMAS SQPG,SM,4,('+port+')\n')
        jsub.write('SQLB "'+jsub_label+'",MAIN,0,3,"'+self.wavetable+'",('+port+')\n')
        jsub.write('SQLB LBL,"'+jsub_label+'","PARA_MEM=SHMEM,SCAN_MEM=NONE,PARA_MCTX=DEFAULT",('+port+')\n')
        jsub.write('SQPG 0,STVA,0,,,('+port+')\n')
        jsub.write('SQPG 1,STSA,,,,('+port+')\n')
        jsub.write('SQPG 2,JSUB,,"'+jsub2_label+'",,('+port+')\n')
        jsub.write('SQPG 3,STOP,,,,('+port+')\n')
        jsub.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description: "+sys.modules[__name__].__doc__)
    parser.add_argument('-mpb','--MEM_BIST_MPB',required=True, help='Path to FULL bist MPB file that you want to split')
    parser.add_argument('-csv','--memBistCtlr_csv',required=True, help='Path to memBistCtlr.csv file')
    parser.add_argument('-d','--debug',action='store_true',help='print a lot of debug stuff to dlog')
    parser.add_argument('-out','--output_dir',required=False,default='',help='Directory to place log file(s).')
    parser.add_argument('-n','--name',required=False,default='',help='Optional name used for output files/logs.')
    parser.add_argument('-max','--maxlogs',type=int,default=10,required=False, help='(0=OFF:log data to stdout). Set to 1 to keep only one log (subsequent runs will overwrite).')
    args = parser.parse_args()

    outdir = init_logging(scriptname=os.path.basename(sys.modules[__name__].__file__),args=args)

    PbistPats(args,outdir)

    time = time.time()-_start_time
    msg = 'Script took ' + str(round(time,3)) + ' seconds (' + humanize_time(time) + ')'
    log.info(msg)
    print '\n' + msg
