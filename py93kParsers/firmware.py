"""
This modules file is for scripts that need to run firmware commands on the 93k tester
"""

from common import *
import os
import re
import time


def check_xoc_session(log=None):
    """
    Check XOC_SESSION environmental variable.  This must be set prior to executing this script.
    Setting it in the Python code is not possible since the parent shell is no longer accessible.
    By the time the script is run, python only has a copy of the parent environment and therefore can't change it.
    """
    session_finder = '/opt/hp93000/soc/system/bin/sessionfinder.ksh'
    if os.path.exists(session_finder):
        get_session_cmd = session_finder + ' 2>/dev/null'
        session = os.popen(get_session_cmd).read().strip()
        if os.environ.get('XOC_SESSION') != session:
            log.warning("XOC_SESSION env variable not set! Should be set to '{}' to drastically increase speed of script!".format(session))
            time.sleep(5)


def fwc(cmd, suppress_error=False, debug_output_char_limit=None, log=None):
    """
    Execute FW command.  Must have SmarTest loaded and primaries set (run func test before running script)
    """
    hpt_cmd = "/opt/hp93000/soc/fw/bin/hpt -q"
    if suppress_error:
        hpt_cmd += " 2>/dev/null"
    echo_cmd = "echo '{}'".format(cmd)
    command = "{} | {}".format(echo_cmd, hpt_cmd)
    rslt = os.popen(command).read()
    log.debug("FW COMMAND: {}".format(cmd))
    if debug_output_char_limit is None:
        log.debug("FW  RESULT: {}".format(rslt.strip()))
    else:
        log.debug("FW  RESULT[maxchars={}]: {}".format(debug_output_char_limit, rslt[:debug_output_char_limit].strip()))
    return rslt


def sqpg(port, cmd_no, instr, param_1='', param_2='', memory='', log=None):
    return fwc('sqpg {}, {}, {}, {},{},({});'
               .format(cmd_no, instr, param_1, param_2, memory, port), log=log)


def sqlb_q(label, log=None):
    return fwc('sqlb? "{}",all,(@@);'.format(label), log=log)


def sqpg_q(portlist, cmd_no_a, cmd_no_b=None, log=None):
    if cmd_no_b is None:
        return fwc('sqpg? {},({});'.format(cmd_no_a, portlist), log=log)
    else:
        return fwc('sqpg? "{},{}",({});'.format(cmd_no_a, cmd_no_b, portlist), log=log)


def sqsl_q(log=None):
    """
    Get the current mpb burst name and the ports it uses.
    :param debug: determines print level
    :param log: object logger used for writing to log file(s)
    """
    sqsl_ptn = re.compile(r'sqsl \"(?P<burst>[^"]+)\",MPBU,\((?P<ports>[^\)]+)\)', re.IGNORECASE)
    sqsl_rslt = fwc("sqsl? type;", suppress_error=True, log=log)
    sqsl_obj = sqsl_ptn.search(sqsl_rslt)
    if not sqsl_obj:
        log.critical("no pattern defined in the primaries, are you trying to fool me?  aborting...")
        sys.exit(1)
    else:
        burst = sqsl_obj.group("burst")
        ports = sqsl_obj.group("ports").split(',')
        log.debug("current primary pattern = '" + burst + "': " + ','.join(ports))
        return burst, ports


def ftst_q(mpb, lmap=False, log=None):
    """
    Run functional test on current primaries set.
    :param mpb: string name of mpb.  Not really needed except for print statement to show which MPB func was just run.
    :param lmap:
    :param debug: determines print level
    :param log:
    :return: bool True if func test passed, False if func test failed
    """
    log.info("Running functional test '{}'...".format(mpb))
    if lmap:
        fwc("Dcrm ovem,lmap,,(@@);", log=log)
    ftst_ptn = re.compile(r'ftst p', re.IGNORECASE)
    ftst_rslt = fwc("ftst?;", log=log)
    ftst_obj = ftst_ptn.search(ftst_rslt)
    if ftst_obj:
        ret = True
    else:
        ret = False
    log.debug("Func test: '" + mpb + "': " + ("PASSED" if ret else "FAILED"))
    fwc("Sqgb acqf,0; ", log=log)
    return ret


def getl_q(index_first_call, pin_or_port, number_of_calls=0, log=None):
    if number_of_calls == 0:
        number_of_calls = ''
    return fwc('getl? {},{},({});'.format(index_first_call, number_of_calls, pin_or_port), log=log)


def tstl(label, port, log=None):
    fwc('tstl "{}",({});'.format(label, port), log=log)


def tcmt_q(vect_addr, vect_length=0, debug_output_char_limit=100, log=None):
    if vect_length == 0:
        vect_length = ''
    return fwc('tcmt? {}, {};'.format(vect_addr, vect_length),
               debug_output_char_limit=debug_output_char_limit, log=log)


def sqla_q(label, attr_key='para_mem', log=None):
    return fwc('sqla?,"{}","{}";'.format(label, attr_key), log=log)


def getv_q(start_cycle, no_of_cycles, pinlist, debug_output_char_limit=100, log=None):
    return fwc('getv? {},{},({});'.format(start_cycle, no_of_cycles, pinlist),
               debug_output_char_limit=debug_output_char_limit, log=log)


def pclk_q(port, log=None):
    """
    Get absolute period for given port in current primaries
    :param port: string port name
    :param debug: determines print level
    :param log:
    :return: float per (period) for given port
    """
    pclk_ptn = re.compile(r'pclk "(?:[^"]+)",(?:\d+),(?P<per>[-+]?\d*\.\d+|\d+),\((?:.+?)\)', re.IGNORECASE)
    pclk_rslt = fwc('pclk? prm,1,({});'.format(port), log=log)
    pclk_obj = pclk_ptn.search(pclk_rslt)
    per = float(pclk_obj.group('per'))
    return per


def dlts(label, log=None):
    """
    Delete label for all ports.
    There is no query version of this commmand.
    :param debug: determines print level
    :param log:
    :param label: string
    """
    fwc('diag 20;', log=log)
    fwc('dlts "{}";'.format(label), suppress_error=True, log=log)
    fwc('diag -20;', log=log)
