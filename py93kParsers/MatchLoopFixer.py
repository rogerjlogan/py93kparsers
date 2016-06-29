#!/db/kepler_pe/93k/anaconda_ete/bin/python
"""
    Dynamically modifies the RPTV counts to find the first passing condition of an MATCHLOOP flattened pattern.
    Considers the fact that these patterns have multiple ports and the modulo behavior needs to be preserved for LMAP.
"""
import time
from common import *
import argparse
import sys
import Firmware as fw
from pprint import pprint

_start_time = time.time()
log = None

__author__ = 'Roger'
__script__ = os.path.basename(sys.modules[__name__].__file__)


# ---------------------------------------------------------
# GLOBAL CONSTANTS/VARS

_COMM_SRCH_STR_ = 'turn strobe(s) back on for final loop cycle'


# def set_final_values(focuspat):
#
#     # based on rptv0, rptv1 which are global
#     my $lfocuspat=shift;
#     #die "internal error - no value" unless (length($lfocuspat));
#
#     my $pnoload_pd = &get_pclk("pNOLOAD"); # hard coded, I know
#
#     my $pnoload_steps_total  = int ((${last_rptv1} - 0 )/$mod{"pNOLOAD"}) ;
#     my $steps_to_move_up  = ceil($pnoload_steps_total*($margin_multiplier));
#     $steps_to_move_up= &roundup_to_next_mod2 ($steps_to_move_up);
#     my $percentage = $margin_multiplier*100;
#
#     &prd("there are $pnoload_steps_total pnoload steps, so if I take the ceiling of ${percentage} % of that, I get $steps_to_move_up steps I have to move up",3);
#
#     my ${rptv1_toset}=    ${last_rptv1}+ ($steps_to_move_up *  $mod{"@vPorts[1]"});
#     my ${rptv0_toset}=    ${last_rptv0}+ ($steps_to_move_up *  $mod{"@vPorts[0]"});
#
#     my $net_time_savings = ($pnoload_pd * ( $rptv1 - $rptv1_toset ) )  / 1000 / 1000 ;  # convert to ms
#
#     &prd("$lfocuspat: !FOUND TRANSITION! with ${current_rptv0} on port '@vPorts[0]' and ${current_rptv1} on port '@vPorts[1]'  with net time savings of $net_time_savings  ms",0);
#     &prd("$lfocuspat: margin multiplier is ${margin_multiplier}, final values will be changed  $rptv0 --> ${rptv0_toset} @ '@vPorts[0]', $rptv1 --> ${rptv1_toset} @ '@vPorts[1]'",0);
#
#     &prd("\tsetting final rptv for port '@vPorts[0]' to ${rptv0_toset}...",1);
#     &fwc("Sqpg ${idx0},rptv,1,${rptv0_toset},,(@vPorts[0]);");
#
#     &prd("\tsetting final rptv for port '@vPorts[1]' to ${rptv1_toset}...",1);
#     &fwc("Sqpg ${idx1},rptv,1,${rptv1_toset},,(@vPorts[1]);");
#
#     &change_revision_comment("$lfocuspat");
#
#
#     $processed++;
#
#     &prd("done with label '$lfocuspat'.",3);


# def change_revision_comment(label):
#
#     for port in ports:
#
#         pr("changing pattern revision for pattern '"+label+"', port '"+port+"'...", 'debug', debug=debug, log=log)
#
#         # TODO: Construct full label with port and xmode
#         fwc('tstl "${lpat}_$lport",($lport)')
#
#         $_=&fwc("tcmt? 0,1")
#         chop
#         s/tcmt 0,\"//ig
#         s/\"//g
#         my $origStr = $_
#         s/\|.*//g
#         (my $rev)=/(REVISION.*=.*)/
#         newRev = "${rev}R"
#         $_=$origStr
#         s/$rev/$newRev/g
#         newStr = $_
#
#         if len($newStr)>250):
#             pr("string length for comment for pattern '${lpat}_$lport' is >250, truncating the end of the string...")
#             newStr=substr(newStr,250)
#
#         pr("changing revision from '$rev' to '$newRev' for pattern '${lpat}_$lport'...", 'debug')
#         my $newCmd = "Tcmt 0,\"$newStr\""
#         &prd("running Cmd: $newCmd",3)
#         &fwc("$newCmd")




# def mk_mpbu():
#     my $ploadpat=shift
#     my $pnoloadpat=shift
#     my $mpbu_name=shift
#
#     &prd("making a multiport burst with pat '$ploadpat'    @vPorts[0], '$pnoloadpat'    @ vPorts[1] named '$mpbu_name'",2)
#
#     &fwc("saof app")
#     &fwc("dmas sqpg,sm,2,(@vPorts[0])")
#     &fwc("sqlb \"$mpbu_name\",mpbu,0,1,,(@vPorts[0])")
#     &fwc("sqpg 0,call,,\"$ploadpat\",,(@vPorts[0])")
#     &fwc("sqpg 1,bend,,,,(@vPorts[0])")
#     &fwc("saof zero")
#
#     &fwc("saof app")
#     &fwc("dmas sqpg,sm,2,(@vPorts[1])")
#     &fwc("sqlb \"$mpbu_name\",mpbu,0,1,,(@vPorts[1])")
#     &fwc("sqpg 0,call,,\"$pnoloadpat\",,(@vPorts[1])")
#     &fwc("sqpg 1,bend,,,,(@vPorts[1])")
#     &fwc("saof zero")
#
#     pr("done making '$mpbu_name'",'debug')


class MatchLoopFixer(object):
    """
    Class to fix matchloop after Jazz converted to a set repeat (RPTV).
    """
    burst = ''
    labels_by_port = {}
    ports_by_tdl = {}
    xmodes_by_port = {}
    ports = []
    rptv_address = {}
    match_rptv_addr = {}
    # first vector after matchloop per port

    def build_matchloop_dict(self, debug=False, log=None):
        # need to iterate through once just to build the skip tdl list
        skip_tdls = []
        for port in self.ports:
            for label in self.labels_by_port[port]:
                tdl, xmode = fw.get_labelname_parts(label, port, debug=debug, log=log)
                if xmode != self.xmodes_by_port[port]:
                    pr("Invalid xmode: {} found in label: '{}'".format(xmode, label))
                else:
                    if label not in self.rptv_data and tdl not in skip_tdls:
                        skip_tdls.append(tdl)

        # now that we have our skip tdl list, let's build our matchloop RPTV addresses
        for port in self.ports:
            for label in self.labels_by_port[port]:
                tdl, xmode = fw.get_labelname_parts(label, port, debug=debug, log=log)
                if tdl not in skip_tdls:
                    if label not in self.vec_comm_srch_rslts:
                        # this label didn't have`have the search string so we need to use the last RPTV
                        self.match_rptv_addr[label] = max([x for x in self.rptv_data[label]])
                    else:
                        # Search comment vector should be 1 vector after matchloop
                        srch_comm_addr = self.vec_comm_srch_rslts[label]
                        if srch_comm_addr-1 not in self.rptv_data[label]:
                            pr("Invalid RPTV / Search Comment results", 'fatal', log=log)
                        else:
                            self.match_rptv_addr[label] = self.vec_comm_srch_rslts[label]

    def __init__(self, debug=False, progname='', maxlogs=1, outdir=os.path.dirname(os.path.realpath(__file__))):
        """
        Constructor for MatchLoopFixer
        :param debug: bool determines print level
        :param progname: string used for appending to output file names and output directory
        :param maxlogs: int determines whether to have 1 log file per module or just 1 overall
        :param outdir: string destination of all output files.  if not exist, it will be created
        """
        global log
        if debug:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
        logger_name, outdir = init_logging(scriptname=os.path.basename(sys.modules[__name__].__file__),
                                           outdir=outdir, name=progname, maxlogs=maxlogs, level=log_level)
        log = logging.getLogger(logger_name)
        log.warning = callcounted(log.warning)
        log.error = callcounted(log.error)
        pr('Running ' + os.path.basename(sys.modules[__name__].__file__) + '...', log=log)

        # execute functional test
        if not args.ftst_no and not fw.ftst(self.burst, debug=debug, log=log):
            pr("this may be normal, especially if there are flaky patterns as they are not considered here", log=log)
            time.sleep(1)

        # get burst name and ports
        self.burst, self.ports = fw.get_sqsl(debug=debug, log=log)

        # get label info for each port in the current burst
        self.labels_by_port, self.ports_by_tdl, self.xmodes_by_port = fw.getl(self.ports, debug=debug, log=log)

        self.rptv_data = fw.get_rptv(self.ports)

        # get comments and search results (not keeping comments, just the search results, hence the 'dummy')
        dummy, self.vec_comm_srch_rslts = fw.get_tcmt(self.labels_by_port,
                                                      srch_str=_COMM_SRCH_STR_,
                                                      exit_after_srch=True,
                                                      debug=debug, log=log)

        self.build_matchloop_dict(debug=debug, log=log)

        pprint(self.match_rptv_addr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description: "+sys.modules[__name__].__doc__)
    parser.add_argument('-name', '--name', required=False, default='', help='Optional name used for output files/logs.')
    parser.add_argument('-d', '--debug', action='store_true', help='print a lot of debug stuff to dlog')
    parser.add_argument('-out', '--output_dir', required=False, default='', help='Directory to place log file(s).')
    parser.add_argument('-max', '--maxlogs', type=int, default=1, required=False,
                        help='(0=OFF:log data to stdout).'
                             'Set to 1 to keep only one log (subsequent runs will overwrite).')
    parser.add_argument('-keep_temp_burst', '--keep_temp_burst', required=False,
                        help='do not delete the temporary burst at the end of the script exeuction (not the default)')
    parser.add_argument('-ftst_no', '--ftst_no', action='store_true', required=False,
                        help='do not run an initial functional test... not the default !')
    parser.add_argument('-bin', '--bin', action='store_true', required=False,
                        help='use a binary search algorithm instead of linear... not the default !')
    args = parser.parse_args()

    mlf = MatchLoopFixer(progname=args.name, debug=args.debug, outdir=args.output_dir, maxlogs=args.maxlogs,)

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
