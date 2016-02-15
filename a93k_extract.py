import util
import v93k_utils
import sys
import logging
import os
import re
import argparse
from pprint import pformat
import py93kParsers.ti_binning
from py93kParsers.TestflowParser import Testflow
from py93kParsers.testprog_parser import ProgFile
from py93kParsers.testtable_parser import TestTable, VALID_LIM_HEADERS
from py93kParsers.ti_binning import identify_ti_csv_files, parse_special_csv, \
    gather_all_testsuites_bins, find_actual_binning, create_ti_binning_csv, create_flowaudit_csv, \
    create_softbinaudit_csv, create_hardbinaudit_csv, create_cat_issues_csv, init_logging, callcounted, \
    categories_file, bin_groups_file, bin_groups, bin_groups_exist, speed_sort_groups_file, test_name_type_file, \
    PARTIAL_BINNING_METHOD, test_type_to_check, binning_csv_file, OTHER_BIN, category_tests, testflow_binning, \
    testflow_bin_defs, speed_sort_groups
__author__ = "Jacob"


def setUpLogging(debug=True, outputDir=os.path.curdir, outputName="", maxLogs=1):
    """sets up logging object that generates INFO and DEBUG logs
    :rtype: log, logging
    :param debug, boolean defaults to True, provides more logging with DEBUG flag applied to logging object
    :param outputDir, directory path output files are created in
    :param outputName, file name tag used for all output files generated from logging event
    :param maxLogs, number of log files to create, defaults to 1
    :return log, an instance of logging object
    """

    if debug:
        logLevel = logging.DEBUG
    else:
        logLevel = logging.INFO
    if hasattr(sys.modules[__name__], "__file__"):
        scriptName = os.path.basename(sys.modules[__name__].__file__)
    else:
        scriptName = "scratch.py"
    logger_name, outdir = init_logging(scriptname=scriptName, outdir=outputDir, name=outputName,
                                       maxlogs=maxLogs, level=logLevel)
    log = logging.getLogger(logger_name)
    log.warning=callcounted(log.warning)
    log.error=callcounted(log.error)
    msg = 'Running ' + scriptName + '...'
    print msg
    log.info(msg)
    return(log)


def parseArguments(defaultArgsDict=None):
    if sys.modules[__name__].__doc__:
        doc = "Description: " +sys.modules[__name__].__doc__
    else:
        doc = "V93k Audit"
    parser = argparse.ArgumentParser(description=doc)
    parser.add_argument('-name','--name',required=False,default='',help='Optional name used for output files/logs.')
    parser.add_argument('-d','--debug',action='store_true',help='Print a lot of debug stuff to dlog')
    parser.add_argument('-out','--output_dir',required=True,default='', help='Directory to place output files/logs.')
    parser.add_argument('-max','--maxlogs',type=int,default=1,required=False, help='(0=OFF:log data to stdout). Set to 1 to keep only one log (subsequent runs will overwrite).')
    parser.add_argument('-r','--renumber',action='store_true',help='Re-number "Test number" column across all STANDARD csv testtables')
    parser.add_argument('-s','--split',action='store_true',help='Split image files into top level groups (USE THIS OPTION FOR REALLY LARGE TESTFLOW FILES!')
    parser.add_argument('-tf','--testflow_file',required=False,default='', help='Name of testflow file (Example: Final_RPC_flow(.tf or .mfh)\
                        WARNING: THIS GOES WITH -tt (--testtable_file), BUT NOT WITH -tp (--testprog_file)')
    parser.add_argument('-tt','--testtable_file',required=False,default='', help='Name of testtable file type csv file (Example: Kepler_TestNameTypeList.csv)\
                        WARNING: THIS GOES WITH -tf (--testflow_file), BUT NOT WITH -tp (--testprog_file)')
    parser.add_argument('-tp','--testprog_file',required=False,default='', help='Name of testprog file (Example: F791857_Final_RPC.tpg)\
                        WARNING: THIS DOES NOT GO WITH -tt (--testtable_file) OR WITH -tf (--testflow_file)')
    parser.add_argument('-ignore','--ignore_suites',required=False, help='Ignore testsuites file. Place testsuites (\'\\n\' separated) in this text file to suppress in csv output')
    parser.add_argument('-bin','--binning_csv',default='',required=False, help='Path to binning csv file (Example: BinningKepler.csv (use only with -c option to use categories)')
    parser.add_argument('-tt2c','--test_type_to_check',required=False,default='', help='Check this test type against binning groups (use only with -c option to use categories)')
    parser.add_argument('-pic','--pic_type',required=False,default='png',help='Type of pic desired for output (valid options: png[default], none)')
    parser.add_argument('-c','--categories',action='store_true',help='Add this option to use binning categories')
    if __name__ == "__main__" and defaultArgsDict:
        parser.set_defaults(**defaultArgsDict)

    return (parser)
import xlwt
def parseTestFlow(args):
    # v93kProgPath = r"C:\work\Projects\TI\Shiva\1171shivatipi\SHIVAI03\SHIVAI03" #SHIVA
    # argsTfFile = os.path.join(v93kProgPath, "testflow", "Final_flow.mfh") #SHIVA
    # argsTtFile = os.path.join(v93kProgPath, "testtable", "Final_limits.csv.mfh") #SHIVA
    # argsTestProgFile = "" #SHIVA

    log = setUpLogging(debug=args.debug, outputDir=args.output_dir, outputName=args.name, maxLogs=args.maxlogs)
    py93kParsers.ti_binning.log = log
    if args.ignore_suites is not None:
        if os.path.isfile(args.ignore_suites):
            ignore_file = args.ignore_suites
        else:
            ignore_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),args.ignore_suites)
        try:
            with open(ignore_file, 'r') as f:
                ignore_suites = [x.strip() for x in f.readlines()]
        except:
            err = '{} is NOT a valid ignore file. Skipping your ignore file. (check permissions of file also)'.format(args.ignore_suites)
            print 'ERROR!!! '+err
            log.error(err)
            raise IOError
        ignore_str = '\n\t'.join(ignore_suites)
        msg = 'IGNORING THE FOLLOWING TESTSUITES:\n\t'+ignore_str
        # print msg
        log.info(msg)

    if len(args.testprog_file):
        if len(args.testflow_file) or len(args.testtable_file):
            err = 'INPUT ERROR!!! testprog_file (-tp) already provided.  Cannot provide testflow_file (-tf) and/or testtable_file (-tt) also! Exiting ...'
            log.error(err)
            sys.exit(err)
        tp = ProgFile(pathfn=args.testprog_file, debug=args.debug, progname=args.name,
                      maxlogs=args.maxlogs, outdir=args.output_dir)
        testflow_file = os.path.join(tp.progdir,'testflow',tp.contents['Testflow'])
        testtable_file = os.path.join(tp.progdir,'testtable',tp.contents['Testtable'])
        args.testflow_file, args.testtable_file = testflow_file, testtable_file
    elif (len(args.testflow_file) > 0) and (len(args.testtable_file) > 0):
        testflow_file = args.testflow_file
        testtable_file = args.testtable_file
    else:
        err = 'UNSTABLE INPUT: Must provide either testprog_file (-tp) OR both testflow_file (-tf) AND testtable_file (-tt) BUT not all 3! Exiting ...'
        log.error(err)
        sys.exit(err)
    # need to set global variable in ti_binning.py
    py93kParsers.ti_binning.testflow_file = testflow_file

    # need this global for easy access
    use_cats = args.categories
    py93kParsers.ti_binning.use_cats = use_cats  # making a global in ti_binning, don't want to edit that while Roger
    # is making changes
    if use_cats:
        if not len(args.test_type_to_check):
            err = 'ILLEGAL ARGUMENT COMBINATION: You\'ve chosen TO USE category binning (-c option passed) but HAVE NOT SUPPLIED the test type to check (-tt2c).'
            log.error(err)
            sys.exit(err)
        else:
            test_type_to_check = args.test_type_to_check
        if not len(args.binning_csv)>0:
            err = 'ILLEGAL ARGUMENT COMBINATION: You\'ve chosen TO USE category binning (-c option passed) but HAVE NOT SUPPLIED the binning csv file (-bin).'
            log.error(err)
            sys.exit(err)
        else:
            # silently ignoring path (in case the user was being silly).  We already have the path
            binning_csv_file = os.path.basename(args.binning_csv)
    elif len(args.test_type_to_check):
        err = 'ILLEGAL ARGUMENT COMBINATION: You\'ve chosen NOT TO USE category binning (-c option passed) but HAVE SUPPLIED the test type to check (-tt2c).'
        log.error(err)
        sys.exit(err)
    elif len(args.binning_csv):
        err = 'ILLEGAL ARGUMENT COMBINATION: You\'ve chosen NOT TO USE category binning (-c option passed) but HAVE NOT SUPPLIED the binning csv file (-bin).'
        log.error(err)
        sys.exit(err)
    else:
        test_type_to_check = None
        binning_csv_file = None
    # set the globals in ti_binning
    py93kParsers.ti_binning.test_type_to_check = test_type_to_check
    py93kParsers.ti_binning.binning_csv_file = binning_csv_file

    tf = Testflow(tf_file=testflow_file, debug=args.debug, split=args.split, progname=args.name, maxlogs=args.maxlogs,
                  outdir=args.output_dir, partial_bin_method=PARTIAL_BINNING_METHOD, pic_type=args.pic_type)
    # need to set global instance of testflow in ti_binning module
    py93kParsers.ti_binning.testflow = tf
    testtable = TestTable(pathfn=testtable_file, renum=args.renumber, debug=args.debug, progname=args.name,
                          maxlogs=args.maxlogs, outdir=args.output_dir, ignore_csv_files=[args.binning_csv])
    py93kParsers.ti_binning.testtable = testtable


    if use_cats:
        identify_ti_csv_files(testtable.special_testtables)
        categories_file = py93kParsers.ti_binning.categories_file
        ti_binning_file = os.path.join(os.path.dirname(categories_file),binning_csv_file)

        parse_special_csv(ti_binning_file, csv_type='ti_binning')
        bin_groups_file = py93kParsers.ti_binning.bin_groups_file
        if bin_groups_file is not None:
            parse_special_csv(bin_groups_file, csv_type='bin_groups')
            bin_groups_exist = True
            py93kParsers.ti_binning.bin_groups_exist = bin_groups_exist

        speed_sort_groups_file = py93kParsers.ti_binning.speed_sort_groups_file
        test_name_type_file = py93kParsers.ti_binning.test_name_type_file
        parse_special_csv(speed_sort_groups_file,csv_type='speed_sort_groups')
        parse_special_csv(test_name_type_file,csv_type='test_name_type')
        parse_special_csv(categories_file,csv_type='categories')

    gather_all_testsuites_bins()
    find_actual_binning()

    if hasattr(sys.modules[__name__], "__file__"):
        scriptName = os.path.basename(getattr(sys.modules[__name__],"__file__"))
    else:
        scriptName = "scratch.py"
    py93kParsers.ti_binning.log = log
    wkBook  = xlwt.Workbook();
    py93kParsers.ti_binning.addSoftBinSheet(wkBook)
    py93kParsers.ti_binning.addHBins(wkBook)
    py93kParsers.ti_binning.addFlowAuditSheet(wkBook)
    py93kParsers.ti_binning.addTiBinningSheet(wkBook)
    if args.categories:
        py93kParsers.ti_binning.addCatIssues(wkBook)

    if OTHER_BIN in testtable.sbin_nums:
        err = '"#define sOtherBin \'13\'" defined in Binning_helper.cpp conflicts with standard testtable(s): "{}"' \
            .format(','.join(testtable.sbin_files[OTHER_BIN]))
        print 'ERROR!!! '+err
        log.error(err)
    ti_binning = py93kParsers.ti_binning.ti_binning
    if OTHER_BIN not in ti_binning:
        err = 'No softbin 13 defined in: "{}"'.format(binning_csv_file)
        print 'ERROR!!! '+err
        log.error(err)

    # For debug and future development, list this module's data containers and their contents
    from py93kParsers.ti_binning import  bin_groups_exist, bin_groups, category_defs, categories_extra_tests, \
        testflow_extra_tests,test_name_type
    binDict = {
        "ti_binning": ti_binning, "bin_groups": bin_groups, "speed_sort_groups": speed_sort_groups,
        "test_name_type": test_name_type, "category_defs": category_defs, "category_tests": category_tests,
        "categories_extra_tests": categories_extra_tests, "testflow_extra_tests": testflow_extra_tests,
        "testflow_binning": testflow_binning, "testflow_bin_defs": testflow_bin_defs
    }
    log.debug('ti_binning:\n' + pformat(ti_binning,indent=4))
    log.debug('bin_groups:\n' + pformat(bin_groups,indent=4))
    log.debug('speed_sort_groups:\n' + pformat(speed_sort_groups,indent=4))
    log.debug('test_name_type:\n' + pformat(test_name_type,indent=4))
    log.debug('category_defs:\n' + pformat(category_defs,indent=4))
    log.debug('category_tests:\n' + pformat(category_tests,indent=4))
    log.debug('categories_extra_tests:\n' + pformat(categories_extra_tests,indent=4))
    log.debug('testflow_extra_tests:\n' + pformat(testflow_extra_tests,indent=4))
    log.debug('testflow_binning:\n' + pformat(testflow_binning, indent=4))
    log.debug('testflow_bin_defs:\n' + pformat(testflow_bin_defs, indent=4))

    log.info('ARGUMENTS:\n\t'+'\n\t'.join(['--'+k+'='+str(v) for k,v in args.__dict__.iteritems()]))
    msg = 'Number of WARNINGS for "{}": {}'.format(os.path.basename(scriptName),log.warning.counter)
    print msg
    log.info(msg)
    msg = 'Number of ERRORS for "{}": {}'.format(os.path.basename(scriptName),log.error.counter)
    print msg
    log.info(msg)
    return (args, tf, binDict,testtable,wkBook)


def determineSetups(testflow_file):
    """
    get levels and timing file reference(s) from setups in testflow file
    :param testflow_file"""
    # testflow section fields
    tfSectionFields = [
        "information", "declarations", "implicit_declarations", "flags", "testmethodparameters",
        "testmethodlimits", "testmethods", "test_suites", "bin_disconnect", "test_flow", "binning",
        "context", "hardware_bin_descriptions"
    ]
    contextDirDict = {
        "context_config_file": "configuration", "context_levels_file": "levels", "context_timing_file": "timing",
        "context_vector_file": "vectors", "context_analog_control_file": "analog_control",
        "context_routing_file": "routing", "context_testtable_file": "testtable",
        "context_channel_attrib_file": "ch_attributes"
    }
    testflowPath = os.path.dirname(testflow_file)
    devicePath = testflowPath.rpartition(os.path.sep)[0]
    f = util.FileUtils(args.testflow_file, True)
    setupIndex = util.find_index(f.contents, "^\s*setup\s*:\s*[\.\\/\w]+")
    setupsDict = {}
    if setupIndex>-1:
        setupFn = os.path.join(testflowPath,f.contents[setupIndex].split(":")[-1].strip())
        f = util.FileUtils(setupFn, True)
        startPt = util.find_index(f.contents, "^\s*context\\b")
        stopPt = startPt + util.find_index(f.contents[startPt:], "^\s*end\\b")
        chkList = [
            ",".join([aWord.strip() for aWord in aRow.strip().split("=")]).replace(";","").replace('"','')
            for aRow in f.contents[startPt:stopPt] if util.in_string(aRow, "=")
        ]
        setupsDict = dict([tuple(aRow.split(",")) for aRow in chkList])
        for k,v in setupsDict.iteritems():
            setupsDict[k] = os.path.join(devicePath, contextDirDict[k], v)
    return setupsDict


def evaluateLevels(setups_dict, spec_levels_groups, pin_list, pin_group_dict):
    """
    go through all levels objects, and build a dictionary with the following structure:
    levels_dict = {"EQN":{}, "SPS":{}}
        "EQN" = {<int eqnset A>:{}, <int eqnset B>:{},....<int eqnset N>:{}}
            <int eqnset> = {"LEVELSET":{}, "DPSPINS":{}, "SPECS":{}, "EQUATIONS":{},
                            "eq_name":<eqnset string name>, "sub_sections":[]}
                "sub_sections" = [list of sections found in equation set, i.e. "LEVELSET, SPECS, DPSPINS, etc"]
                "LEVELSET" = {<int levelset A>:{}, <int levelset B>:{},....<int levelset N>:{}}
                    <int levelset> = {"name":<levelset name string>, <int pins 0>:{}, <int pins 1>:{},...
                                      <int pins N>:{}}
                        <int pins> = {"pin_list":[], "fields_dict":{}}
                            "pin_list" = list of pins after expanding pin groups and removing any -( <pins> } groups
                            "fields_dict" = {"field":"<equation>",...."vih":"VIH_Iddq_LVDS-DCF_COMP"....}
                "DPSPINS" = {<int dpspins A>:{}, <int dpspins B>:{},....<int dpspins N>:{}}
                    <int dpspins> = {"pin_list":[], "fields_dict":[]}
                        "pin_list" = [<power supply pins, mode DFPS>]
                        "fields_dict" = {"field":"<value>",....,"vout":"VDDDR_PS+(SCF_DPS128*ENABLE_SCF)"....}
                "SPECS" = {"specnameA":"units", "specnameB":"units",...,"specnameN":"units"}
                    "specname" = string name of spec in SPECS section of EQNSET object
                    "units" = string of units, i.e. V, mA, etc.  empty string if no units
                "EQUATIONS" = {"eqn A":"<equation>", "eqn B":"<equation>",...,"eqn N":"<equation>"}
                    "eqn" = <equation>, i.e. "VOL_Spec": "0.45-CCF_PS1600"
        "SPS" = {<int eqnset A>:{}, <int eqnset B>:{},....<int eqnset N>:{}}
            <int eqnset> = {"eq_name":"equation set string name", "SPECSET":{}, "sub_sections":[]}
                "SPECSET" = {<int  specset A>:{}, <int specset B>:{},....,<int specset N>:{}}
                    <int specset> = {"SPECS":{}, "specset_name":"string name of specset"}
                        "SPECS" = {"specnameA":{}, "specnameB":{},...."specnameN":{}}
                            "specname" = {"actual":"value", "maximimum":"value", "minimum":"value", "units":"<units>"}
                                "value|units" is an empty string if nothing there, i.e. usually maximum and minimum
                                              would be empty
    :param setups_dict:
    :param spec_levels_groups:
    :param pin_list:
    :param pin_group_dict:
    :return: levels_dict
    """
    ref_file_regexp = "^\s*(?P<ref_type>(?:EQNSET|WAVETABLE|MULTIPORT_SPEC))\s+(?P<ref_name>[\"\w]+)\s*:"
    ref_dict = v93k_utils.parseMFH(setups_dict[setups_keys["levels"]], ref_file_regexp, ["EQNSET"])
    levels_dict = {"EQN": {}, "SPS": {}}
    for ref,fn in ref_dict["EQNSET"].iteritems():
        a_dict = v93k_utils.getLevels(fn, spec_levels_groups, pin_list, pin_group_dict)
        for eq_set, eq_dict in a_dict["EQN"].iteritems():
            levels_dict["EQN"][eq_set] = eq_dict
        for eq_set, eq_dict in a_dict["SPS"].iteritems():
            levels_dict["SPS"][eq_set] = eq_dict
    return levels_dict




def evaluateTiming(setups_dict, spec_timing_groups, pin_list, pin_group_dict):
    """
    parse through all timing objects, build and return dictionary timing_dict.
    timing_dict = {"EQN":{}, "SPS":{}, "WVT":{}}
        "EQN" = {<int eqnset A>:{}, <int eqnset B>:{},....,<int eqnset N>:{}}
            <int eqnset> = {"eq_name":"str eqn name", "TIMINGSET":{}, "sub_sections":[], "DEFINES": [<pin list>],
                            "SPECS":{}, "EQUATIONS":{}}
                "SPECS" = {"specnameA":"units", "specnameB":"units",...,"specnameN":"units"}
                    "specname" = string name of spec in SPECS section of EQNSET object
                    "units" = string of units, i.e. nS, MHz, etc.  empty string if no units
                "EQUATIONS" = {"eqn A":"<equation>", "eqn B":"<equation>",...,"eqn N":"<equation>"}
                    "eqn" = <equation>, i.e. "GBper": "1000/GBfreq"
                "TIMINGSET" = {<int timingset A>:{}, <int timingset B>:{},....,<int timingset N>:{}}
                    <int timingset> = {"name":"str timingset name", "period":"period expression",
                                       <int pins 1>:{}, <int pins 2>:{},....,<int pins N>:{}}
                        <int pins> = {"pin_list":[], "fields_dict":{}}
                            "pin_list" = list of pins after expanding pin groups and removing any -( <pins> } groups
                            "fields_dict" = {"field":"<equation>",...."d1":"0.5*GBper"....}
        "SPS" = {<str specificationName A>:{}, <str specificationName B>:{},...,<str specificationName N>:{}}
            <str specificationName> = {<int eqnset A>:{}, <int eqnset B>:{},.....,<int eqnset N>:{}}
                <int eqnset> = {"PORT":[<port(s) list>], "WAVETBL":"str wavetable reference", "name":"str eqn name",
                                "sub_sections":["PORT", "WAVETBL", "name", "SPECS"],
                                "SPECS":{}
                                }
                    "SPECS" = {"specnameA":{}, "specnameB":{},...."specnameN":{}}
                            "specname" = {"actual":"value", "maximimum":"value", "minimum":"value", "units":"<units>"}
                                "value|units" is an empty string if nothing there, i.e. usually maximum and minimum
                                              would be empty
        "WVT" = NOT IMPLEMENTED AT THIS TIME
    :param setups_dict:
    :param spec_timing_groups:
    :param pin_list:
    :param pin_group_dict:
    :return:
    """
    ref_file_types = ["EQNSET", "WAVETABLE", "MULTIPORT_SPEC"]
    ref_file_regexp = "^\s*(?P<ref_type>(?:{0}))\s+(?P<ref_name>[\"\w\s]+)\s*:".format("|".join(ref_file_types))
    ref_dict = v93k_utils.parseMFH(setups_dict[setups_keys["timing"]], ref_file_regexp, ref_file_types)
    timing_dict = {"EQN":{}, "SPS":{}, "WVT":{}}
    file_list = []
    for type in ref_file_types:
        file_list += list(ref_dict[type].itervalues())

    for fn in file_list:
        a_dict = v93k_utils.getTiming(fn, spec_timing_groups, pin_list, pin_group_dict)
        for eq_set, eq_dict in a_dict["EQN"].iteritems():
            timing_dict["EQN"][eq_set] = eq_dict
        for eq_set, eq_dict in a_dict["SPS"].iteritems():
            timing_dict["SPS"][eq_set] = eq_dict
    return timing_dict

import py93kParsers.parseUtils as parseUtils
def createEnv(inp):
    out = {}
    for spec in inp['SPECS']:
        try:
            out[spec] = float(inp['SPECS'][spec]['actual'])
        except ValueError:
            continue
    return out
def addEquEnv(envi, eqs):
    """ since equations are in a dictionary, they are not always evaluated in order, so need a complicated while loop"""
    retry = True
    tryVals = eqs.items()
    while(retry and tryVals):
        newTries = tryVals
        tryVals =[]
        retry = False
        for val, expr in newTries:
            try:
                exp = parseUtils.valueExpr.parseString(expr)[0]
                envi[val] = parseUtils.getVal(exp, envi)
                retry = True
            except KeyError:
                tryVals.append((val,expr))



def evalPeriods(tims):
    out = {}
    for spec in tims['SPS']:
        out[spec]= {}
        for ind in tims['SPS'][spec]:
            assert len(tims['SPS'][spec][ind]['PORT']) == 1
            port = tims['SPS'][spec][ind]['PORT'][0]
            envi = createEnv(tims['SPS'][spec][ind])
            out[spec][port] = {}
            if 'EQUATIONS' in tims['EQN'][ind]:
                addEquEnv(envi, tims['EQN'][ind]['EQUATIONS'])
            for timeset in tims['EQN'][ind]['TIMINGSET']:
                perExpr = parseUtils.valueExpr.parseString(tims['EQN'][ind]['TIMINGSET'][timeset]['period'])[0]
                try:
                    out[spec][port][timeset] = parseUtils.getVal(perExpr, envi)
                except KeyError:
                    out[spec][port][timeset] = -1e7
    return out
from genOut import titleLeft, titleStyle, bodyLeft, bodyStyle, _addTitle
def addPeriodSheet(wkBook, pers):
    allPortLs = sum((x.keys() for x in pers.values()),[])
    allPorts = set(allPortLs)
    assert isinstance(wkBook, xlwt.Workbook)
    sheet = wkBook.add_sheet("PERIODS")
    sheet.row(0).write(0, 'Spec Names', style = titleStyle)
    sheet.col(0).width = 256*60
    sheet.write_merge(0,0, 1, len(allPorts), 'PORTS', style = titleStyle)
    allPorts = sorted(allPorts, key = lambda x: -allPortLs.count(x))
    portCols = dict((port, ii+1) for ii, port in enumerate(allPorts))
    for port, ind in portCols.items():
        sheet.row(1).write(ind, port, style = titleStyle)
        sheet.col(ind).width = 256*20
    currRow = 2
    for spec, portDict in pers.items():
        sheet.row(currRow).write(0, spec, style = bodyLeft)
        for port in allPorts:
            if port in portDict:
                periods = portDict[port]
                perDict = defaultdict(list)
                for ind, period in periods.items():
                    perDict[period].append(ind)
                if len(perDict) == 1:
                    period = str(perDict.keys()[0])
                else:
                    period = str(dict(perDict))
            else:
                period = ''
            sheet.row(currRow).write(portCols[port], period, style = bodyLeft)
        currRow += 1



def evalSupplies(levs):
    out = {}
    for eqInd in levs['EQN']:
        eqKey = (eqInd, levs['EQN'][eqInd]['eq_name'])
        out[eqKey] = {}
        dspExprs = {}
        for pinInd in levs['EQN'][eqInd]['DPSPINS']:
            dspExprs[tuple(levs['EQN'][eqInd]['DPSPINS'][pinInd]['pin_list'])] = \
                    py93kParsers.parseUtils.valueExpr.parseString(levs['EQN'][eqInd]['DPSPINS'][pinInd]['fields_dict']['vout'])[0]

        for specInd in levs['SPS'][eqInd]['SPECSET']:
            specKey = (specInd, levs['SPS'][eqInd]['SPECSET'][specInd]['specset_name'])
            out[eqKey][specKey] = {}
            envi = createEnv(levs['SPS'][eqInd]['SPECSET'][specInd])
            if 'EQUATIONS' in levs['EQN'][eqInd]:
                addEquEnv(envi, levs['EQN'][eqInd]['EQUATIONS'])
            for pin in dspExprs:
                try:
                    out[eqKey][specKey][pin] = parseUtils.getVal(dspExprs[pin], envi)
                except KeyError as err:
                    print 'For Eq:', eqKey, ", spec ", specKey, 'pin:', pin
                    print str(dspExprs[pin]), 'could not be evaluated'
                    print 'Value of ', err, 'unknown'
                    out[eqKey][specKey][pin] = -1e7
    return out
def addSupplySheet(wkBook, pows):
    assert isinstance(wkBook, xlwt.Workbook)
    sheet = wkBook.add_sheet("SUPPLY_LEVELS")
    allSups = sum((x.values()[0].keys() for x in pows.values()),[])
    allSups = sorted(set(sum(allSups,())))
    supDict = dict((sup,ii+2) for ii, sup in enumerate(allSups))
    headers = ["EQNSET", "SPECSET"] + allSups
    _addTitle(sheet, headers)
    currRow = 1
    for key, specDict in sorted(pows.items()):
        sheet.write_merge(currRow, currRow+len(specDict)-1, 0,0, str(key[0]) + ':' +key[1], style=bodyStyle)
        rowIter = 0
        for specKey, supVals in sorted(specDict.items()):
            sheet.row(currRow+rowIter).write(1, str(specKey[0])+ ':' + specKey[1], style = bodyStyle)
            for suplies, val in supVals.items():
                for sup in suplies:
                    sheet.row(currRow+rowIter).write(supDict[sup], str(val), style = bodyLeft)
            rowIter += 1
        currRow += len(specDict)


def analyzeTestFlow(tf):
    # data structures to pull out information such as test suite name, limits, primaries, test parameters, and such
    tsData = tf.testsuite_data
    primaryLevelKeys = ["TestsuiteLevEquSet", "TestsuiteLevSet", "TestsuiteLevSpecSet"]
    primaryTimingKeys = ["TestsuiteTimEquSet", "TestsuiteTimSet", "TestsuiteTimSpecSet"]
    tsNodeIds = tf.testsuite_nodeids
    tsNodeData = tf.nodeData
    hashTableNodeAndTestsuite = ["{0}:{1}".format(k, v["testsuite"]) for k,v in tsNodeData.iteritems() if "testsuite" in v]




from collections import defaultdict
def treeWalkFlow(tf, levs,tims):
    ignoreMeths = {'"ti_tml.Misc.Binning"','"miscellaneous_tml.TestControl.Disconnect"'}
    def getGroup(nd):
        try:
            nodeId = int(nd.name.split('-')[-1])
        except ValueError:
            nodeId = int(nd.name[:-1])
        if tf.nodeData[nodeId]['type'] == 'GroupStatement':
            return nd.name.split('-')[0].rstrip('">').lstrip('<GROUP "')
        return getGroup(nd.up)

    out = defaultdict(dict)

    for node in tf.newick_tree.traverse('preorder'):
        try:
            nodeId = int(node.name.split('-')[-1])
        except:
            continue
        if tf.nodeData[nodeId]['type'] in ['RunStatement', 'RunAndBranchStatement']:
            suiteName = node.name.split('-')[0]
            if suiteName in tf.bypassed_testsuites:
                continue
            group = getGroup(node)
            if tf.nodeData[nodeId][suiteName]['Testmethods']['Class'] in ignoreMeths:
                continue
            if group not in out:
                ind = len(out)
                out[group]['_ii'] = ind
            out[group][suiteName] = {'_ii' : len(out[group]), 'LEVS': {}, 'TIM' : {}}
            out[group][suiteName]['TM'] = tf.nodeData[nodeId][suiteName]['Testmethods']['Class']
            tmp = out[group][suiteName]['LEVS']

            try:
                levEq = tf.nodeData[nodeId][suiteName]["TestsuiteLevEquSet"]
                levEqName = levs["EQN"][int(levEq)]['eq_name']
                tmp['levEq'] = (levEq,levEqName)
                levSet = tf.nodeData[nodeId][suiteName]["TestsuiteLevSet"]
                levSetName = levs["EQN"][int(levSet)]['LEVELSET'][int(levSet)]['name']
                tmp['levSet'] = (levSet,levSetName)
                levSpec = tf.nodeData[nodeId][suiteName]["TestsuiteLevSpecSet"]
                levSpecName = levs["SPS"][int(levEq)]['SPECSET'][int(levSpec)]['specset_name']
                tmp['levSpec'] = (levSpec, levSpecName)
            except KeyError:
                tmp['levEq'] = ('','')
                tmp['levSet'] = ('','')
                tmp['levSpec'] = ('','')

            tmp = out[group][suiteName]["TIM"]
            try:
                timSpec = tf.nodeData[nodeId][suiteName]["TestsuiteTimSpecSet"].strip('"')
                try:
                    int(timSpec)
                    timEq = tf.nodeData[nodeId][suiteName]["TestsuiteTimEquSet"]
                    timEqName = tims["EQN"][int(timEq)]['eq_name']

                    timSpecName = tims["SPS"][int(timEq)][int(timSpec)]['specset_name']
                    tmp['timSpec'] = (timSpec, timSpecName)
                    tmp['timEq'] = (timEq,timEqName)
                    tmp['timSet'] = tf.nodeData[nodeId][suiteName]["TestsuiteTimSet"]

                except ValueError as e:
                    tmp['timSpec'] = (timSpec,)
                    tmp['timEq'] = ('','')
                    tmp['timSet'] = tf.nodeData[nodeId][suiteName]["TestsuiteTimSet"]

            except KeyError as e:
                #print e.message, node.name
                tmp['timEq'] = ('','')
                tmp['timSpec'] = ('','')
                tmp['timSet'] = ''
                continue



    return out

if __name__ == "__main__":
    v93kProgPath = r"C:\work\scratch\v93kAudit\py93kParsers\example_progs\KEPLERI8220" # KEPLER
    argsTfFile = ""
    argsTtFile = ""
    argsTestProgFile = os.path.join(v93kProgPath, "testprog", "KEPLERI8220.tpg")
    argsDebug = False
    argsSplit = False
    argsName = "kepler_r20"
    argsRenumber = False # arg param -r, stores true, Re-number "Test number" column across all STANDARD csv testtables
    argsMaxLogs = 1
    argsOutputDir = r"c:\Temp"
    argsTestTypeToCheck = "FT_RPC_HT" # arg param -tt2c, default is ""
    # Check this test type against binning groups (use only with -c option to use categories)
    argsPicType = ""  # don't care about the graphical output rendering, just want the data container
    argsBinningCsv = "BinningKepler_pg2.csv"
    argsCategories = True # arg param -c, stores true (false if not included), option to use binning categories
    argsIgnoreSuites = r"C:\work\scratch\v93kAudit\py93kParsers\example_runs\kepler.ignore"
    argsDefault = {
        "name": "bob", "debug": False, "output_dir": r"c:\Temp", "maxlogs": 1,
        "renumber": False, "split": False, "testflow_file": "", "testtable_file": "",
        "testprog_file": "", "ignore_suites": "", "binning_csv": "", "test_type_to_check": "",
        "pic_type": "png", "categories": False
    }
    setArgsDict = {
        "--testprog_file": argsTestProgFile, "--name": argsName, "--output_dir": argsOutputDir,
        "--test_type_to_check": argsTestTypeToCheck, "--pic_type": "", "--binning_csv": argsBinningCsv,
        "--ignore_suites": argsIgnoreSuites, "--categories": True
    }
    storeTrueVars = ["--debug", "--renumber", "--split", "--categories"]
    #copySysArgV = [arg for arg in sys.argv]
    #numParameters = len(sys.argv)-1
    #for i in xrange(numParameters):
    #    sys.argv.pop(-1)
#    for i,(k,v) in enumerate(setArgsDict.iteritems()):
#        sys.argv.append("{0}{1}".format(k,
#                                       "{0}".format("" if util.in_list(storeTrueVars,k) else ("={0}".format(v if len(v) else '""')))))
    parser = parseArguments()
    args = parser.parse_args()

    args, tf, bin_dict,testtable,wkBook = parseTestFlow(args)
    setups_dict = determineSetups(args.testflow_file)
    setups_keys = {
        "levels": "context_levels_file", "timing": "context_timing_file",
        "configuration": "context_config_file"
    }
    config_file = setups_dict[setups_keys["configuration"]]
    pin_list, pin_map_dict, pin_group_dict, port_dict = v93k_utils.configDict(config_file)
    # levels set keys: ^\s*EQNSET\s+\d+:\s*[\./\w]+
    # timings set keys: ^\s*(?:EQNSET|WAVETABLE|MULTIPORT_SPEC)\s+[\"\w]+:\s+[\./\w]+
    # go through EQNSET's first.  Break down by: EQNSET, subgroups: SPECS, EQUATIONS, TIMINGSET
    #    special fields: DEFAINES for multiport, for TIMINGSET, get period field
    #    within TIMINGSET, key off PINS, expand all pins from pinGroups,
    # join ^\s*{ to previous line, then do block grouping off SPECIFICATION ["\w]+ {
    spec_timing_groups = {
        "topLevel": "^\s*(?:EQSP\s+TIM\s*,\s*(?:EQN|SPS|WVT)|@)",
        "startClause": "^\s*EQSP\s+TIM\s*,\s*(?:EQN|SPS|WVT)",
        "stopClause" : "^\s*@",
        "remove": "^\s*(?:CHECK\s+all\s*|@|NOOP\s[\"\.\d]+|hp93000[\d\.]+|EQSP\s+\w+[\,#\w]+)?$",
        "EQN": {
            "remove": ["\s*#\s*.*$", "^\s*CHECK\s+all\s*"],  # remove blank lines, and all comments (# something)
            "topLevel": "^\s*EQNSET\s+\d+(?:\"[\,\w\s\-\.]\")?",
            "subSections": "^\s*(?:SPECS|EQUATIONS|DEFINES\s+[\w\s]+|TIMINGSET\s+\d+\s*[\"\w\s\.\-]*)",
            "EQUATIONS": lambda a_line: tuple(
                    "".join(a_part.strip().split()) for a_part in a_line.split("=")
            ),  # split by equals sign, get rid of white space
            "SPECS": lambda a_line: (
                a_line.split()[0].strip(),
                re.sub("[\[\]]", "", a_line.split()[-1].strip()) if len(a_line.split())>1 else ""
            ),  # strip leading whitespace and remove []'s, split off middle whitespace, (name, units)
            "TIMINGSET": "^\s*(?:PINS\s+[\w\s\-\(\)]+|period\s*=\s*[\w\s\*\+\-/]+)",
            "DEFINES" : lambda a_line: re.sub("^\s*DEFINES\s+", "", a_line).split()
        },
        "SPS": {
            "remove": [],
            "SPECIFICATION": "^\s*SPECIFICATION\s+(?:\"[\,\w\s\-\.]+\")",
            "topLevel": "^\s*EQNSET\s+\d+\s*\"?[\w\s\-\,]*\"?",
            "subSections": "^\s*(#\s+SPECNAME|(?:WAVETBL\s+\"[\s\w]+\"|PORT\s+[\w\s]+))",
            "EQNSET": "^\s*#\s+SPECNAME\s+\*+"
        },
        "WVT": {
            "remove": [],
            "topLevel": "^\s*WAVETBL\s+(?:\"[\,\w\s\-\.]\")?",
            "subSections": "^\*(?:PINS|DEFINES\s+[\w\s]+)",
            "PINS": lambda a_line: tuple(
                    "".join(a_string.strip().split())for a_string in util.my_split(a_line,"\"")
            )
        }
    }
    spec_levels_groups = {
        "topLevel": "^\s*(?:EQSP\s+LEV\s*,\s*(?:EQN|SPS)|@)",
        "startClause": "^\s*EQSP\s+LEV\s*,\s*(?:EQN|SPS)",
        "stopClause" : "^\s*@",
        "EQN": {
            "remove": ["\s*#\s*.*$"],  # remove blank lines, and all comments (# something)
            "topLevel": "^\s*EQNSET\s+\d+(?:\"[\,\w\s\-\.]\")?",
            "subSections": "^\s*(?:SPECS|EQUATIONS|DPSPINS|LEVELSET\s+\d+\s*[\"\w\s\.\-]*)",
            "EQUATIONS": lambda a_line: tuple(
                    "".join(a_part.strip().split()) for a_part in a_line.split("=")
            ),  # split by equals sign, get rid of white space
            "SPECS": lambda a_line: (
                a_line.split()[0].strip(),
                re.sub("[\[\]]", "", a_line.split()[-1].strip()) if len(a_line.split())>1 else ""
            ),  # strip leading whitespace and remove []'s, split off middle whitespace, (name, units)
            "LEVELSET": "^\s*PINS\s+[\w\s\-\(\)]+",
            "DPSPINS" : lambda a_line: tuple(
                    "".join(a_part.strip().split()) for a_part in a_line.split("=")
            ),  # split by equals sign, get rid of white space
        },
        "SPS": {
            "remove": [],
            "topLevel": "^\s*EQNSET\s+\d+(?:\"[\,\w\s\-\.]\")?",
            "subSections": "^\s*(?:SPECSET\s+\d+\s*[\"\w\s\.\-]*)",
            "SPECS": "^\s*\w+"
        },
    }
    levels_dict = evaluateLevels(setups_dict, spec_levels_groups, pin_list, pin_group_dict)
    timing_dict = evaluateTiming(setups_dict, spec_timing_groups, pin_list, pin_group_dict)
    import py93kParsers.flowaudit
    py93kParsers.flowaudit.testflow = tf
    py93kParsers.flowaudit.testtable = testtable
    #py93kParsers.flowaudit.log = log
    py93kParsers.flowaudit.addFlowAuditSheet(wkBook,levels_dict)
    period = evalPeriods(timing_dict)
    sups = evalSupplies(levels_dict)
    addPeriodSheet(wkBook, period)
    addSupplySheet(wkBook, sups)
    wkBook.save(os.path.join(args.output_dir, args.name + ".xls"))
