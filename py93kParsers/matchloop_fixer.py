#!/db/kepler_pe/93k/anaconda_ete/bin/python
"""
    Dynamically modifies the RPTV counts to find the first passing condition of an LED pattern.
    Considers the fact that these patterns have multiple ports and the modulo behavior needs to be preserved for LMAP.
"""
import time
from common import *
import argparse
import sys

_start_time = time.time()
log = None

__author__ = 'Roger'
__script__ = os.path.basename(sys.modules[__name__].__file__)


# ---------------------------------------------------------
# GLOBAL CONSTANTS/VARS

_all_ = False
_pats_to_modify_ = []
_burst_ = ''
_ports_ = []
_xmodes_ = {}

# ---------------------------------------------------------
# FUNCTIONS


def pr(print_msg, level='info'):
    print_pre_msg = ''
    if level.lower() == 'info':
        print_pre_msg = "INFO: "
        log.info(print_msg)
    elif level.lower() == 'debug':
        print_pre_msg = "DEBUG: "
        log.debug(print_msg)
    elif level.lower() == 'warn':
        print_pre_msg = "WARNING: "
        log.debug(print_msg)
    elif level.lower() == 'error':
        print_pre_msg = "ERROR (continuing): "
        log.error(print_msg)
    elif level.lower() == 'critical':
        log.error(print_msg)
        sys.exit(print_msg)
    print print_pre_msg+print_msg


def fwc(cmd, escape=False):
    if escape:
        return os.popen("echo '" + cmd + "' | /opt/hp93000/soc/fw/bin/hpt -q").read()
    else:
        return os.popen("echo '"+cmd+"' | /opt/hp93000/soc/fw/bin/hpt -q 2>/dev/null").read()


def get_pats_to_modify(pathfn):
    global _pats_to_modify_
    for line in open(pathfn).readlines():
        pat = line.strip()
        if not len(pat):
            continue
        _pats_to_modify_.append(pat)


def sqsl():
    global _burst_, _ports_
    sqsl_ptn = re.compile(r'sqsl \"(?P<burst>[^"]+)\",MPBU,\((?P<ports>[^\)]+)\)', re.IGNORECASE)
    sqsl_rslt = fwc("sqsl? type;", escape=True)
    sqsl_obj = sqsl_ptn.search(sqsl_rslt)
    if not sqsl_obj:
        pr("no pattern defined in the primaries, are you trying to fool me?  aborting...", 'critical')
    else:
        _burst_ = sqsl_obj.group("burst")
        _ports_ = sqsl_obj.group("ports").split(',')
    sqsl_msg = "current primary pattern = '" + _burst_ + "': " + ','.join(_ports_)
    log.debug(sqsl_msg)
    print sqsl_msg


def ftst(pat2run):
    ftst_msg = "Running functional test '"+pat2run+"'..."
    log.debug(ftst_msg)
    print ftst_msg
    fwc("Dcrm ovem,lmap,,(@@);")
    ftst_ptn = re.compile(r'ftst p', re.IGNORECASE)
    ftst_rslt = fwc("ftst?;")
    ftst_obj = ftst_ptn.search(ftst_rslt)
    if ftst_obj:
        ret = True
    else:
        ret = False
    pr("Func test: '" + pat2run + "': " + ("PASSED" if ret else "FAILED"))
    fwc("Sqgb acff,0; ")
    return ret


def getl():
    """
        Assumption: labels are named with port name and xmode at end (if not xmode, then xmode is x1)
            Example:
                some_label_pASYNC1    => port: pASYNC1 and xmode: x1
                other_label_pOTHER_X2 => port: pOTHER  and xmode: x2
                scan_label_pSCANIN_X4 => port: pSCANIN and xmode: x4
    """
    global _xmodes_
    getl_ptn = re.compile(r'getl (?P<idx>\d+),\"(?P<label>.*)\",(?P<start>\d+),(?P<stop>\d+),\(', re.IGNORECASE)
    for port in _ports_:
        for getl_rslt in fwc("getl? 0,100000,("+port+");").split('\n'):
            if not len(getl_rslt):
                continue
            getl_obj = getl_ptn.search(getl_rslt)
            if not getl_obj:
                pr("Unable to parse GETL result: " + getl_rslt, 'critical')
            stop = int(getl_obj.group('stop')) + int(getl_obj.group('start')) + 800
            label = getl_obj.group('label').strip()
            if port not in _xmodes_:
                # clever slicing to get xmode after port name if found
                xmode = label[label.find(port):][-1:]
                if not len(xmode):
                    # no xmode found, must be x1
                    _xmodes_[port] = 1
                else:
                    _xmodes_[port] = int(xmode)
            if not _all_:
                pass


    # my $port = @vPorts[0];  #pload
    # my $g=&fwc("getl? 0,100000,($port);");
    # foreach  (split(/\n/, $g)) {
    #     (my $idx,my $pat, my $start, my $stop)=/getl (\d+),\"(.*)\",(\d+),(\d+),\(/i;
    #     $stop = $stop + $start + 800;
    #     if (not $all) {
    #       foreach my $lpat (@vPats) {
    #         if ("${lpat}_pLOAD" eq "$pat") {
    #             push (@vPatsmatch,$lpat);
    #             &prd("found a match with pattern '$pat', it's found in index '$idx' of the current burst '$burst'");
    #             $patIdx{$lpat}=$idx;
    #             $stopIdx_pload{$lpat}= $stop+800;
    #
    #         }
    #       }
    #     } else { #end of if not $all loop, here #all ==1
    #         $_=$pat;
    #         if (/_${port}/) {
    #             s/_${port}//g;
    #             my $lpat=$_;
    #             push (@vPatsmatch,$lpat);
    #             &prd("found a match with pattern '$lpat', it's found in index '$idx' of the current burst '$burst'");
    #             $patIdx{$lpat}=$idx;
    #             $stopIdx_pload{$lpat}= $stop+800;
    #         }
    #
    #
    #     }
    #
    #
    # }
    # $port = @vPorts[1];  #pnoload
    # $g=&fwc("getl? 0,100000,($port);");
    # foreach  (split(/\n/, $g)) {
    #     (my $idx,my $pat, my $start, my $stop)=/getl (\d+),\"(.*)\",(\d+),(\d+),\(/i;
    #     $stop = $stop + $start + 800;
    #     foreach my $lpat (@vPats) {
    #         if ("${lpat}_pNOLOAD" eq "$pat") {
    #             #push (@vPatsmatch,$lpat);
    #             #&prd("found a match with pattern '$pat', it's found in index '$idx' of the current burst '$burst'");
    #             #$patIdx{$lpat}=$idx;
    #             $stopIdx_pnoload{$lpat}= $stop+800;
    #
    #         }
    #     }
    # }

# ---------------------------------------------------------
# BEGIN

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description: "+sys.modules[__name__].__doc__)
    parser.add_argument('-name', '--name', required=False, default='', help='Optional name used for output files/logs.')
    parser.add_argument('-d', '--debug', action='store_true', help='print a lot of debug stuff to dlog')
    parser.add_argument('-out', '--output_dir', required=False, default='', help='Directory to place log file(s).')
    parser.add_argument('-max', '--maxlogs', type=int, default=1, required=False,
                        help='(0=OFF:log data to stdout).'
                             'Set to 1 to keep only one log (subsequent runs will overwrite).')
    parser.add_argument('-pats_to_modify', '--pats_to_modify', default='', required=False,
                        help='file (line-delimited) containing the patterns to be modified'
                             '(do not use with "-all" option)')
    parser.add_argument('-all', '--all', action='store_true', required=False,
                        help='do all patterns in the current burst (do not use with "-pats_to_modify" option)')
    parser.add_argument('-keep_temp_burst', '--keep_temp_burst', required=False,
                        help='do not delete the temporary burst at the end of the script exeuction (not the default)')
    parser.add_argument('-ftst_no', '--ftst_no', action='store_true', required=False,
                        help='do not run an initial functional test... not the default !')
    parser.add_argument('-bin', '--bin', action='store_true', required=False,
                        help='use a binary search algorithm instead of linear... not the default !')
    args = parser.parse_args()

    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logger_name, outdir = init_logging(scriptname=__script__,
                                       outdir=args.output_dir,
                                       name=args.name,
                                       maxlogs=args.maxlogs,
                                       level=log_level)
    log = logging.getLogger(logger_name)
    log.warning = callcounted(log.warning)
    log.error = callcounted(log.error)
    msg = 'Running ' + __script__ + '...'
    print msg
    log.info(msg)

    # ---------------------------------------------------------------------
    # PLACE CODE AND METHOD CALLS HERE

    if len(args.pats_to_modify):
        if args.all:
            pr('Both "-all" and "-pats_to_modify" passed. '
                'Ignoring "-all" and only modifying pats in pats_to_modify', 'warn')
            _all_ = False  # override
        get_pats_to_modify(args.pats_to_modify)
    else:
        _all_ = args.all

    # get burst name and ports
    sqsl()

    # get label info for current mpb
    getl()

    if not args.ftst_no and not ftst(_burst_):
        pr("this may be normal, especially if there are flaky patterns as they are not considered here")
        time.sleep(1)

        # ---------------------------------------------------------------------
    # CLEANUP

    log.info('ARGUMENTS:\n\t'+'\n\t'.join(['--'+k+'='+str(v) for k, v in args.__dict__.iteritems()]))
    msg = 'Number of WARNINGS for "{}": {}'.format(__script__, log.warning.counter)
    print msg
    log.info(msg)
    msg = 'Number of ERRORS for "{}": {}'.format(__script__, log.error.counter)
    print msg
    log.info(msg)

    time = time.time()-_start_time
    msg = 'Script took ' + str(round(time, 3)) + ' seconds (' + humanize_time(time) + ')'
    log.info(msg)
    print '\n' + msg
