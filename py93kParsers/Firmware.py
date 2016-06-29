"""
This modules file is for scripts that need to run firmware commands on the 93k tester
"""

from common import *
import os
import re
import math


def get_labelname_parts(label, port, debug=False, log=None):
    """
    Assumption: labels are named with port name and xmode at end (if not xmode, then xmode is x1)
    Example:
        some_label_pASYNC1    => port: pASYNC1 and xmode: x1
        other_label_pOTHER_X2 => port: pOTHER  and xmode: x2
        scan_label_pSCANIN_X4 => port: pSCANIN and xmode: x4

    :param label: string name of label to parse
    :param port: string name of port to find delimiter of tdl_name and xmode (if not x1)
    :param debug: determines print level
    :param log:
    :return: string tdl_name, int (1-9) xmode
    """
    if port not in label:
        pr('Incongruent port: {} for label: {}'.format(port, label), 'fatal', log=log)
    tdl_name = label[:label.find(port) - 1]
    # clever slicing to get xmode after port name if found
    end = label[label.find(port):]
    xmode = 1 # default value when no xmode found at end of label name
    if end != port:
        raw_xmode_str = end[end.find('_X'):]
        if len(raw_xmode_str) - len(port) > 3:
            pr("Invalid end: {} in label name: '{}'".format(end, label), 'fatal', log=log)
        else:
            xmode = int(raw_xmode_str[-1:])
    return tdl_name, xmode


def fwc(cmd, escape=False, suppress_result_output=False, debug=False, log=None):
    """
    Execute FW command.  Must have SmarTest loaded and primaries set (run func test before running script)
    :param cmd: string FW command to be run
    :param escape: bool but not sure the eficacy of this but preserving it from Kozma's original script
    :param suppress_result_output:
    :param debug: determines print level
    :param log:
    :return: string rslt from command line if any
    """
    if escape:
        rslt = os.popen("echo '" + cmd + "' | /opt/hp93000/soc/fw/bin/hpt -q").read()
    else:
        rslt = os.popen("echo '"+cmd+"' | /opt/hp93000/soc/fw/bin/hpt -q 2>/dev/null").read()
    pr("FW COMMAND: "+cmd, 'debug', debug=debug, log=log)
    if not suppress_result_output:
        pr("FW  RESULT: "+rslt, 'debug', debug=debug, log=log)
    else:
        pr("FW  RESULT: {suppressed}", 'debug', debug=debug, log=log)
    return rslt


def get_sqsl(debug=False, log=None):
    """
    Get the current mpb burst name and the ports it uses.
    This is the query version of the command, hence the 'get_'
    :param debug: determines print level
    :param log:
    """
    sqsl_ptn = re.compile(r'sqsl \"(?P<burst>[^"]+)\",MPBU,\((?P<ports>[^\)]+)\)', re.IGNORECASE)
    sqsl_rslt = fwc("sqsl? type;", escape=True, debug=debug, log=log)
    sqsl_obj = sqsl_ptn.search(sqsl_rslt)
    if not sqsl_obj:
        pr("no pattern defined in the primaries, are you trying to fool me?  aborting...", 'fatal', log=log)
    else:
        burst = sqsl_obj.group("burst")
        ports = sqsl_obj.group("ports").split(',')
        pr("current primary pattern = '" + burst + "': " + ','.join(ports), 'debug', debug=debug, log=log)
        return burst, ports


def ftst(mpb, debug=False, log=None):
    """
    Run functional test on current primaries set.
    :param mpb: string name of mpb.  Not really needed except for print statement to show which MPB func was just run.
    :param debug: determines print level
    :param log:
    :return: bool True if func test passed, False if func test failed
    """
    pr("Running functional test '{}'...".format(mpb), log=log)
    fwc("Dcrm ovem,lmap,,(@@);", debug=debug, log=log)
    ftst_ptn = re.compile(r'ftst p', re.IGNORECASE)
    ftst_rslt = fwc("ftst?;", debug=debug, log=log)
    ftst_obj = ftst_ptn.search(ftst_rslt)
    if ftst_obj:
        ret = True
    else:
        ret = False
    pr("Func test: '" + mpb + "': " + ("PASSED" if ret else "FAILED"), 'debug', debug=debug, log=log)
    fwc("Sqgb acff,0; ", debug=debug, log=log)
    return ret


def getl(ports, debug=False, log=None):
    """
    Get all labels for each port in current burst
    There is only a query version of this command, so no need for 'get_'
    :param ports:
    :param debug: determines print level
    :param log:
    :return:
    """
    labels_by_port = {}
    xmodes_by_port = {}
    ports_by_tdl = {}
    getl_ptn = re.compile(r'getl (?P<idx>\d+),\"(?P<label>.*)\",(?P<start>\d+),(?P<stop>\d+),\(', re.IGNORECASE)
    for port in ports:
        if port not in labels_by_port:
            labels_by_port[port] = []
        for getl_rslt in fwc("getl? 0,100000,("+port+");", debug=debug, log=log).split('\n'):
            if not len(getl_rslt):
                continue
            getl_obj = getl_ptn.search(getl_rslt)
            if not getl_obj:
                pr("Unable to parse GETL result: " + getl_rslt, 'fatal', log=log)
            label = getl_obj.group('label').strip()
            if port not in label:
                pr("Invalid label: '{}' port: {} combination".format(label, port), 'fatal', log=log)
            else:
                labels_by_port[port].append(label)
                tdl, xmode = get_labelname_parts(label, port, debug=debug, log=log)
                if tdl not in ports_by_tdl:
                    ports_by_tdl[tdl] = []
                ports_by_tdl[tdl].append(port)
                xmodes_by_port[port] = xmode

    return labels_by_port, ports_by_tdl, xmodes_by_port


def get_tcmt(ports_dict, srch_str='' ,exit_after_srch=False , debug=False, log=None):
    """
    This function gets all the comments for each label on each port in the active burst keyed by vector address.
    Also searches each vector comment for srch_str, if provided.
    This is the query version of the command, hence the 'get_'
    :param ports_dict:
    :param srch_str:
    :param exit_after_srch:
    :param debug:
    :param log:
    :return:
    """
    pr("Running tcmt()... (This may take a few minutes!)", log=log)
    tcmt_ptn = re.compile(r'tcmt (?P<vec_addr>\d+),"(?P<comment>[^"]+)"', re.IGNORECASE)
    tcmt_dict = {}
    srch_rslts = {}

    for port, label_lst in ports_dict.iteritems():
        for label in label_lst:
            pr("\tGetting comments for label: '{}'".format(label), log=log)
            if not exit_after_srch and label not in tcmt_dict:
                tcmt_dict[label] = {}
            # set focus to label for this port before quering comments
            fwc('tstl "{}", ({});'.format(label, port), debug=debug, log=log)
            # okay, now we query comments
            for tcmt_rslt in fwc('tcmt? 0, 1000000000', suppress_result_output=True, debug=debug, log=log).split('\n'):
                tcmt_obj = tcmt_ptn.search(tcmt_rslt)
                if tcmt_obj:
                    vec_addr = int(tcmt_obj.group('vec_addr'))
                    comment = tcmt_obj.group('comment').strip()
                    if not exit_after_srch:
                        tcmt_dict[label][vec_addr] = comment
                    if len(srch_str) and srch_str in comment:
                        if label in srch_rslts:
                            pr("Unsupported multiple matchloops in label: '{}'", 'fatal', log=log)
                        srch_rslts[label] = vec_addr
                        if exit_after_srch:
                            break
    return tcmt_dict, srch_rslts


def get_rptv(ports, debug=False, log=None):
    rptv_data = {}
    rptv_ptn = re.compile(r'getv (?:\d+),(?P<cycles>\d+),(?P<vec_addr>\d+),'
                          r'(?P<num_vectors>\d+),rptv,"(?P<label>[^"]+)",,\((?:.*?)\)', re.IGNORECASE)
    for port in ports:
        for getv_rslt in fwc('getv? 0,100000000000,({});'.format(port), debug=debug, log=log).split('\n'):
            if not len(getv_rslt):
                continue
            rptv_obj = rptv_ptn.search(getv_rslt)
            if not rptv_obj:
                continue
            else:
                cycles = int(rptv_obj.group('cycles'))
                vec_addr = int(rptv_obj.group('vec_addr'))
                num_vectors = int(rptv_obj.group('num_vectors'))
                label = rptv_obj.group('label')
                if label not in rptv_data:
                    rptv_data[label] = {}
                if vec_addr not in rptv_data[label]:
                    rptv_data[label][vec_addr] = {
                        'cycles': cycles,
                        'num_vectors': num_vectors
                    }
    return rptv_data


def roundup_rptv(val, mod, debug=False, log=None):
    """
        Round up to nearest modulus integer
    :param val: int RPTV value
    :param mod: int modulus for that port
    :param debug: determines print level
    :param log:
    :return: int updated RPTV value
    """
    rslt = int(math.ceil(val/mod)*mod)
    pr('Running roundup_rptv(): val={}\t mod={}\t rslt(ceil(val/mod)*mod)={}'
       .format(val, mod, rslt), 'debug', debug=debug, log=log)
    return rslt


def get_pclk(port, debug=False, log=None):
    """
    Get absolute period for given port in current primaries
    This is the query version of the command, hence the 'get_'
    :param port: string port name
    :param debug: determines print level
    :param log:
    :return: float per (period) for given port
    """
    pclk_ptn = re.compile(r'pclk "(?P<wset>[^"]+)",(?P<tset>\d+),(?P<per>\d+),\((?P<port>.+?)\)', re.IGNORECASE)
    pclk_fwc = 'pclk? prm,1,('+port+');'
    pclk_rslt = fwc(pclk_fwc, debug=debug, log=log)
    pclk_obj = pclk_ptn.search(pclk_rslt)
    if not pclk_obj:
        pr("get_pclk() fwc failed: "+pclk_fwc, 'fatal', log=log)
    wset = pclk_obj.group('wset')
    tset = int(pclk_obj.group('tset'))
    per = int(pclk_obj.group('per'))
    pr("Results of get_pclk() for port={}: wset='{}'\t tset={}\t per={}\t"
       .format(port, wset, tset, per), 'debug', debug=debug, log=log)
    return per


def dlts(label, debug=False, log=None):
    """
    Delete label for all ports.
    There is no query version of this commmand.
    :param debug: determines print level
    :param log:
    :param label: string
    """
    fwc('diag 20;', debug=debug, log=log)
    fwc('dlts "'+label+'";',escape=True, debug=debug, log=log)
    fwc('diag -20;', debug=debug, log=log)


