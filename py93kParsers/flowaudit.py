#!/usr/bin/env python
"""
The script creates a flowaudit.csv

"""

import csv
import argparse
from common import *
from testprog_parser import ProgFile
from TestflowParser import Testflow
from testtable_parser import TestTable
import time
_start_time = time.time()
log = None

__author__ = 'Roger'

# global constants below here in CAPS

testflow = None
testflow_file = None
testtable = None

# control variables below here (boolean)

# data collection variables below here

testflow_binning = {}

testflow_bin_defs = {}

hard_bins = {}
import xlwt
from genOut import titleStyle, bodyStyle, titleLeft, bodyLeft, _addTitle

def addFlowAuditSheet(wkBook, levels):
    headers = ['Suite name','Levels','TimSet','TimSpecSet',
               'Testmethods','Mpb', 'Test name','Pins','Test number',
               'Bin_s_num','Bin_s_name','Bin_h_num','Bin_h_name']
    ignoreMeths = {'"ti_tml.Misc.Binning"','"miscellaneous_tml.TestControl.Disconnect"'}

    assert isinstance(wkBook, xlwt.Workbook)
    sheet = wkBook.add_sheet("TEST_NAMES")
    sheet.col(1).width = 256*40
    _addTitle(sheet, headers)
    currRow = 1
    for node in testflow.newick_tree.traverse('preorder'):
        try:
            nodeId = int(node.name.split('-')[-1])
        except:
            continue
        if testflow.nodeData[nodeId]['type'] in ['RunStatement', 'RunAndBranchStatement']:
            suiteName = node.name.split('-')[0]
            if suiteName in testflow.bypassed_testsuites:
                continue
        else:
            continue
        ts = suiteName
        v = testflow.testsuite_data[ts]

        nid = int(testflow.testsuite_nodeids[ts])
        # pprint(v)
        # sys.exit()

        if 'Testmethods' in testflow.testsuite_data[ts] and 'Class' in testflow.testsuite_data[ts]['Testmethods']:
            testmethod = testflow.testsuite_data[ts]['Testmethods']['Class'].strip(' "')
            if testmethod in ignoreMeths:
                continue
        else:
            testmethod = ''

        if 'TestsuiteLevEquSet' in testflow.testsuite_data[ts]:
            TestsuiteLevEquSet = testflow.testsuite_data[ts]['TestsuiteLevEquSet'].strip(' "')
            eqSetName =  levels["EQN"][int(TestsuiteLevEquSet)]['eq_name']
        else:
            TestsuiteLevEquSet = ''
            eqSetName = ''

        if 'TestsuiteLevSet' in testflow.testsuite_data[ts]:
            TestsuiteLevSet = testflow.testsuite_data[ts]['TestsuiteLevSet'].strip(' "')
            TestsuiteLevSet += ":" + levels["EQN"][int(TestsuiteLevEquSet)]['LEVELSET'][int(TestsuiteLevSet)]['name']
        else:
            TestsuiteLevSet = ''

        if 'TestsuiteLevSpecSet' in testflow.testsuite_data[ts]:
            TestsuiteLevSpecSet = testflow.testsuite_data[ts]['TestsuiteLevSpecSet'].strip(' "')
            TestsuiteLevSpecSet += ":"+ levels["SPS"][int(TestsuiteLevEquSet)]['SPECSET'][int(TestsuiteLevSpecSet)]['specset_name']
        else:
            TestsuiteLevSpecSet = ''
        if eqSetName:
            levelsAll = TestsuiteLevEquSet+':' + eqSetName + ',' + TestsuiteLevSet + ',' + TestsuiteLevSpecSet
        else:
            levelsAll = ''

        if 'TestsuiteSequencerLabel' in testflow.testsuite_data[ts]:
            TestsuiteSequencerLabel = testflow.testsuite_data[ts]['TestsuiteSequencerLabel'].strip(' "')
        else:
            TestsuiteSequencerLabel = ''

        if 'TestsuiteTimSet' in testflow.testsuite_data[ts]:
            TestsuiteTimSet = testflow.testsuite_data[ts]['TestsuiteTimSet'].strip(' "')
        else:
            TestsuiteTimSet = ''

        if 'TestsuiteTimSpecSet' in testflow.testsuite_data[ts]:
            TestsuiteTimSpecSet = testflow.testsuite_data[ts]['TestsuiteTimSpecSet'].strip(' "')
        else:
            TestsuiteTimSpecSet = ''
        sheet.row(currRow).write(0, ts, style = bodyLeft)
        sheet.row(currRow).write(1, levelsAll, style = bodyLeft)
        sheet.row(currRow).write(2, TestsuiteTimSet, style = bodyLeft)
        sheet.row(currRow).write(3, TestsuiteTimSpecSet, style = bodyLeft)
        sheet.row(currRow).write(4, testmethod, style = bodyLeft)
        sheet.row(currRow).write(5, TestsuiteSequencerLabel, style = bodyLeft)

        if ts in testtable.testsuite_data:
            for row in testtable.testsuite_data[ts]:
                sheet.row(currRow).write(6, row['Test name'], style = bodyLeft)
                sheet.row(currRow).write(7, row['Pins'], style = bodyLeft)
                sheet.row(currRow).write(8, row['Test number'], style = bodyLeft)
                sheet.row(currRow).write(9, row['Bin_s_num'], style = bodyLeft)
                sheet.row(currRow).write(10, row['Bin_s_name'], style = bodyLeft)
                sheet.row(currRow).write(11, row['Bin_h_num'], style = bodyLeft)
                sheet.row(currRow).write(12, row['Bin_h_name'], style = bodyLeft)
                currRow +=1
            if not testtable.testsuite_data[ts]:
                currRow += 1
        else:
            currRow +=1
def create_flowaudit_csv(scriptname=os.path.basename(sys.modules[__name__].__file__), outdir='', fn='', maxlogs=1):
    csv_file,outdir,info_msg,warn_msg = get_valid_file(scriptname=scriptname, name=fn, outdir=outdir, maxlogs=maxlogs, ext='.csv')
    for msg in warn_msg:
        print 'WARNING!!! ',msg
        log.warning(msg)
    for msg in info_msg:
        log.info(msg)

    headers = ['node_id','Bypassed','Suite name','Test name','Pins','Test number',\
               'Bin_s_num','Bin_s_name','Bin_h_num','Bin_h_name','Levels','TimSet','TimSpecSet',\
               'Testmethods','Mpb']
    with open(csv_file,'wb') as csvFile:
        writer = csv.DictWriter(csvFile,fieldnames=headers)
        writer.writeheader()
        for ts,v in testflow.testsuite_data.iteritems():
            nid = int(testflow.testsuite_nodeids[ts])
            # pprint(v)
            # sys.exit()

            if 'Testmethods' in testflow.testsuite_data[ts] and 'Class' in testflow.testsuite_data[ts]['Testmethods']:
                testmethod = testflow.testsuite_data[ts]['Testmethods']['Class'].strip(' "')
            else:
                testmethod = ''

            if 'TestsuiteLevEquSet' in testflow.testsuite_data[ts]:
                TestsuiteLevEquSet = testflow.testsuite_data[ts]['TestsuiteLevEquSet'].strip(' "')
            else:
                TestsuiteLevEquSet = ''

            if 'TestsuiteLevSet' in testflow.testsuite_data[ts]:
                TestsuiteLevSet = testflow.testsuite_data[ts]['TestsuiteLevSet'].strip(' "')
            else:
                TestsuiteLevSet = ''

            if 'TestsuiteLevSpecSet' in testflow.testsuite_data[ts]:
                TestsuiteLevSpecSet = testflow.testsuite_data[ts]['TestsuiteLevSpecSet'].strip(' "')
            else:
                TestsuiteLevSpecSet = ''

            levels = TestsuiteLevEquSet + ',' + TestsuiteLevSet + ',' + TestsuiteLevSpecSet

            if 'TestsuiteSequencerLabel' in testflow.testsuite_data[ts]:
                TestsuiteSequencerLabel = testflow.testsuite_data[ts]['TestsuiteSequencerLabel'].strip(' "')
            else:
                TestsuiteSequencerLabel = ''

            if 'TestsuiteTimSet' in testflow.testsuite_data[ts]:
                TestsuiteTimSet = testflow.testsuite_data[ts]['TestsuiteTimSet'].strip(' "')
            else:
                TestsuiteTimSet = ''

            if 'TestsuiteTimSpecSet' in testflow.testsuite_data[ts]:
                TestsuiteTimSpecSet = testflow.testsuite_data[ts]['TestsuiteTimSpecSet'].strip(' "')
            else:
                TestsuiteTimSpecSet = ''

            if ts in testtable.testsuite_data:
                for row in testtable.testsuite_data[ts]:
                    writer.writerow({'node_id' : int(nid),
                                     'Bypassed' : 'Y' if ts in testflow.bypassed_testsuites else '',
                                     'Suite name' : ts,
                                     'Test name' : row['Test name'],
                                     'Pins' : row['Pins'],
                                     'Test number' : row['Test number'],
                                     'Bin_s_num' : row['Bin_s_num'],
                                     'Bin_s_name' : row['Bin_s_name'],
                                     'Bin_h_num' : row['Bin_h_num'],
                                     'Bin_h_name' : row['Bin_h_name'],
                                     'Levels' : levels,
                                     'TimSet' : TestsuiteTimSet,
                                     'TimSpecSet' : TestsuiteTimSpecSet,
                                     'Testmethods' : testmethod,
                                     'Mpb' : TestsuiteSequencerLabel
                                     })

            else:
                writer.writerow({'node_id' : int(nid),
                                 'Bypassed' : 'Y' if ts in testflow.bypassed_testsuites else '',
                                 'Suite name' : ts,
                                 'Test name' : '',
                                 'Pins' : '',
                                 'Test number' : '',
                                 'Bin_s_num' : '',
                                 'Bin_s_name' : '',
                                 'Bin_h_num' : '',
                                 'Bin_h_name' : '',
                                 'Levels' : levels,
                                 'TimSet' : TestsuiteTimSet,
                                 'TimSpecSet' : TestsuiteTimSpecSet,
                                 'Testmethods' : testmethod,
                                 'Mpb' : TestsuiteSequencerLabel
                                 })

def main():
    global log,ignore_suites,testflow,testflow_file,testtable,bin_groups_exist,binning_csv_file,test_type_to_check,use_cats
    parser = argparse.ArgumentParser(description="Description: "+sys.modules[__name__].__doc__)
    parser.add_argument('-name','--name',required=False,default='',help='Optional name used for output files/logs.')
    parser.add_argument('-d','--debug',action='store_true',help='Print a lot of debug stuff to dlog')
    parser.add_argument('-out','--output_dir',required=True,default='', help='Directory to place output files/logs.')
    parser.add_argument('-max','--maxlogs',type=int,default=1,required=False, help='(0=OFF:log data to stdout). Set to 1 to keep only one log (subsequent runs will overwrite).')
    parser.add_argument('-r','--renumber',action='store_true',help='Re-number "Test number" column across all STANDARD csv testtables')
    parser.add_argument('-s','--split',action='store_true',help='Split image files into top level groups (USE THIS OPTION FOR REALLY LARGE TESTFLOW FILES!')
    parser.add_argument('-tp','--testprog_file',required=True,default='', help='Name of testprog file (Example: F791857_Final_RPC.tpg)\
                        WARNING: THIS DOES NOT GO WITH -tt (--testtable_file) OR WITH -tf (--testflow_file)')

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

    tp = ProgFile(pathfn=args.testprog_file,debug=args.debug,progname=args.name,maxlogs=args.maxlogs,outdir=args.output_dir)
    testflow_file = os.path.join(tp.progdir,'testflow',tp.contents['Testflow'])
    testtable_file = os.path.join(tp.progdir,'testtable',tp.contents['Testtable'])

    testflow = Testflow(tf_file=testflow_file,split=args.split,debug=args.debug,progname=args.name,
                        maxlogs=args.maxlogs,outdir=args.output_dir)
    testtable = TestTable(testtable_file, args.renumber, debug=args.debug, progname=args.name, maxlogs=args.maxlogs,
                          outdir=args.output_dir)

    create_flowaudit_csv(scriptname=os.path.basename(sys.modules[__name__].__file__), outdir=args.output_dir,
                         fn=args.name+'_ActualFlowBins', maxlogs=max(1, args.maxlogs))

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
