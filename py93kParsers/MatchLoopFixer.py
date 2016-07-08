#!/db/kepler_pe/93k/anaconda_ete/bin/python
"""
    Dynamically modifies the RPTV counts to find the first passing condition of an MATCHLOOP flattened pattern.
    Considers the fact that these patterns have multiple ports and the modulo behavior needs to be preserved for LMAP.
    Doesn't hurt BFLM either.
"""
import time
from common import *
import argparse
import sys
import firmware as fw
from pprint import pprint
import math
from collections import OrderedDict

_start_time = time.time()
log = None
# USE_XOC_SESSION = True

__author__ = 'Roger'
__script__ = os.path.basename(sys.modules[__name__].__file__)


# ---------------------------------------------------------
# GLOBAL CONSTANTS/VARS

_COMM_SRCH_STR_ = 'turn strobe(s) back on for final loop cycle'


def roundup_rptv(val, mod):
    """
    Round up to nearest modulus integer
    :param val: int RPTV value
    :param mod: int modulus for that port
    :return: int updated RPTV value
    """
    return int(math.ceil(val / mod) * mod)


def get_labelname_parts(label, port):
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
    xmode = 1  # default value when no xmode found at end of label name
    if end != port:
        raw_xmode_str = end[end.find('_X'):]
        if len(raw_xmode_str) - len(port) > 3:
            pr("Invalid end: {} in label name: '{}'".format(end, label), 'fatal', log=log)
        else:
            xmode = int(raw_xmode_str[-1:])
    return tdl_name, xmode


class MatchLoopFixer(object):
    """
    Class to fix matchloop after Jazz converted to a set repeat (RPTV).
    """
    debug = False
    comment_port = ''
    burst = ''
    periods = {}
    labels_by_port = {}
    xmodes = {}
    ports = []
    match_rptv_data_lst = {}
    rptv_data = {}
    match_rptv_times = []
    mod = {}

    def find_commport_match_rpt_vec_no(self, srch_str):
        """
        This function searches each vector comment for srch_str, if provided.
        """
        pr("Running tcmt()... (This may take a few minutes!)", log=log)
        tcmt_ptn = re.compile(r'tcmt (?P<vec_addr>\d+),"(?P<comment>[^"]+)"', re.IGNORECASE)
        srch_rslts = {}

        for label in self.labels_by_port[self.comment_port]:
            pr("\tGetting comments for label: '{}'".format(label), log=log)
            # set focus to label for this port before quering comments
            fw.tstl(label, self.comment_port, debug=self.debug, log=log)
            # okay, now we query comments
            for tcmt_rslt in fw.tcmt_q(0, debug=self.debug, log=log).split('\n'):
                tcmt_obj = tcmt_ptn.search(tcmt_rslt)
                if tcmt_obj:
                    vec_addr = int(tcmt_obj.group('vec_addr'))
                    comment = tcmt_obj.group('comment').strip()
                    if len(srch_str) and srch_str in comment:
                        if label not in srch_rslts:
                            srch_rslts[label] = []
                        srch_rslts[label].append(vec_addr)
        return srch_rslts

    def get_labels_xmodes(self, port):
        """
        Get all labels for each port in current burst
        There is only a query version of this command, so no need for 'get_'
        """
        labels = []
        prev_xmode, xmode = None, None
        getl_ptn = re.compile(r'getl (?P<idx>\d+),\"(?P<label>.*)\",(?P<start>\d+),(?P<stop>\d+),\(', re.IGNORECASE)
        for getl_rslt in fw.getl_q(0, port, debug=self.debug, log=log).split('\n'):
            if not len(getl_rslt):
                continue
            getl_obj = getl_ptn.search(getl_rslt)
            if not getl_obj:
                pr("Unable to parse GETL result: " + getl_rslt, 'fatal', log=log)
            label = getl_obj.group('label').strip()
            labels.append(label)
            tdl, xmode = get_labelname_parts(label, port)
            if prev_xmode is not None and xmode != prev_xmode:
                pr("Unbalanced xmodes: ({} and {}) from label names on port: {}"
                   .format(prev_xmode, xmode, port), 'fata', log=log)
        return labels, xmode

    def set_mod(self):
        """
        Set modification for each port based on the xmode setting for that port keeping to an 8-byte boundary
        """
        xmodes_lst = [xmode for port, xmode in self.xmodes.iteritems()]

        # we need to find the LCM of all xmodes (for each port) times 8 bytes
        dividend = 8*lcmm(*set(xmodes_lst))
        for port in self.ports:
            self.mod[port] = dividend / self.xmodes[port]
            pr("Setting port: '{}' to mod: '{}' due to xmode: '{}'"
               .format(port, self.mod[port], self.xmodes[port]), 'info', debug=self.debug, log=log)

    def find_match_rptv_time(self, offset=0):
        """
        This function gets the absolute time of the match repeat start(s) for the comment port that was given.
        Must have already found the vector number(s) containing the comment which we can use to locate the
        correct repeat block(s) depending on the offset value(s).  The absolute time(s) will later be used to find the
        corresponding match repeat(s) on other ports.
        The absolute time is the only value that stays the same across ports.
        (or should.. we'll generate a warning if they do not)
        FORMULAS:
            absolute time = cycle num * period
                cycle num = absolute time / period
        :param offset: int vector distance of comment vector from match repeat vector. positive numbers must include the
                           size of the repeat block
        """
        # go through each label that had the search string in the comments on at least one vector
        for comment_label, comment_vectors in self.commport_match_rpt_vec_no.iteritems():
            # go through each vector number that contained the search string for this label
            for comm_vec in comment_vectors:
                # now compare the comment vector number against all the repeat data on this port and look for a match
                for rptv_no, rptv_data in self.rptv_data[self.comment_port].iteritems():
                    if offset > 0:
                        # if positive then we need to add the number of vectors to the start vector to include the
                        # whole repeat block
                        possible_comm_vec = rptv_data['start_vector'] + (rptv_data['no_of_vectors']-1) + offset
                    else:
                        # either there is no offset (default) or it is negative,
                        # so we can disregard the size of the repeat block
                        possible_comm_vec = rptv_data['start_vector'] + offset
                    if possible_comm_vec == comm_vec:
                        pr("Match RPTV found on vec/cyc: '{}/{}' with per(ns): '{}' for comment port: '{}'"
                           .format(rptv_data['start_vector'], rptv_data['start_cycle'],
                                   self.periods[self.comment_port], self.comment_port),
                           'debug', debug=self.debug, log=log)
                        self.match_rptv_times.append(rptv_data['start_cycle'] * self.periods[self.comment_port])

    def get_rptv_from_getv(self, port):
        """
        We need all the repeat info from GETV? since that will give us most of what we want except for cmd_no.  For that
        we will need to use SQPG? in another function.
        :param port: string name of given port to get info on
        :return: dict rptv_data for given port
        """
        # need to preserve order for this dictionary
        getv_rptv_data = OrderedDict()
        getv_ptn = re.compile(r'getv (?P<start_cycle>\d+),(?P<no_of_cycles>\d+),(?P<start_vector>\d+),'
                              r'(?P<no_of_vectors>\d+),(?P<seq_status>[^,]+),"(?P<label>[^"]+)",,\((?:.*?)\)',
                              re.IGNORECASE)
        rptv_num = 0  # init
        # for GETV we must give a dummy really big number to get everything for this port
        # (let's hope no label has that many)
        for getv_rslt in fw.getv_q(0, 100000000000, port, debug=self.debug, log=log).split('\n'):
            if len(getv_rslt):
                getv_obj = getv_ptn.search(getv_rslt)
                if getv_obj and getv_obj.group('seq_status').strip().lower() == 'rptv':
                    rptv_num += 1
                    start_cycle = int(getv_obj.group('start_cycle'))
                    no_of_cycles = int(getv_obj.group('no_of_cycles'))
                    start_vector = int(getv_obj.group('start_vector'))
                    no_of_vectors = int(getv_obj.group('no_of_vectors'))
                    no_of_repeats = no_of_cycles/no_of_vectors
                    label = getv_obj.group('label')
                    getv_rptv_data[rptv_num] = {
                        'start_cycle': start_cycle,
                        'no_of_cycles': no_of_cycles,
                        'start_vector': start_vector,
                        'no_of_vectors': no_of_vectors,
                        'no_of_repeats': no_of_repeats,
                        'label': label
                    }
        return getv_rptv_data

    def get_rptv_cmd_no_from_sqpg(self, port):
        """
        Since couldn't get everything we wanted from GETV, we need to use SQPG? to get cmd_no.
        We will modify the data structure "self.rptv_data" that should already be started from GETV?
        :param port: string name of given port to get info on
        """
        sqlb_ptn = re.compile(r'sqlb "(?:[^"]*)",main,(?P<start>\d+),(?P<stop>\d+),"(?:[^"]*)",\(', re.IGNORECASE)
        sqpg_ptn = re.compile(r'sqpg (?P<cmd_no>\d+),rptv,(?P<num_vectors>\d+),(?P<repeats>\d+),,', re.IGNORECASE)
        rptv_no = 0  # re-init
        for label in self.labels_by_port[port]:
            # need to get the range of seq instructions from SQLB? which SQPG? needs
            sqlb_rslt = fw.sqlb_q(label, debug=self.debug, log=log)
            sqlb_obj = sqlb_ptn.search(sqlb_rslt)
            if sqlb_obj:
                start = int(sqlb_obj.group('start'))
                stop = int(sqlb_obj.group('stop'))
                # okay, now that we have the range, we can run SQPG? and get all the seq instructions for the port
                for sqpg_rslt in fw.sqpg_q(port, start, stop, debug=self.debug, log=log).split('\n'):
                    # search each result for all RPTV commands keeping track of the count, since that is a key that was
                    # started with GETV? earlier.  The cmd_No will allow us to modify the correct repeat later
                    sqpg_obj = sqpg_ptn.search(sqpg_rslt)
                    if sqpg_obj:
                        rptv_no += 1
                        self.rptv_data[port][rptv_no]['cmd_no'] = int(sqpg_obj.group('cmd_no'))

    def find_corr_match_rptv_data(self):
        """
        This routine uses the matchloop repeats found in the control port (comment_port) to find the corresponding
        match repeats on the other ports.  It does this by calcalating the time (time = cycle * period) where the repeat
        starts and uses that in the other ports to find the correct cycle (cycle = time / period).  If no repeat is
        found on that cycle, then it looks for the closest repeat in either direction and gives warning that vectors are
        not aligned. It also gives you the current per for that port and what the per would be to align the vectors.
        """
        for port in self.ports:
            # create a simple dictionary on this port to map cycles to rptv_no for easier access below
            cyc2num = {this_rptv_data['start_cycle']: rptv_no
                       for rptv_no, this_rptv_data in self.rptv_data[port].iteritems()}
            for m_rptv_time in self.match_rptv_times:
                ideal_rptv_cyc = int(m_rptv_time / self.periods[port])
                # Find the rptv_no that has the closest 'start_cycle' to our ideal 'start_cycle' which is really just
                # this port's equivalent to the 'start_cycle' in our control port (comment_port)
                closest_rptv_num = cyc2num.get(ideal_rptv_cyc,
                                               cyc2num[min(cyc2num.keys(), key=lambda x: abs(x-ideal_rptv_cyc))])
                closest_rptv_cyc = self.rptv_data[port][closest_rptv_num]['start_cycle']
                if closest_rptv_cyc != ideal_rptv_cyc:
                    # okay, we're not aligned, so we need to generate a warning
                    aligned_period = round(m_rptv_time / closest_rptv_cyc,4)
                    delta = abs(closest_rptv_cyc-ideal_rptv_cyc)
                    pr("Vector misalignment at matchloop repeat on port: '{}' label: '{}'\n"
                       "\t(Assuming aligned period in order to find corresponding match repeat on this port).\n"
                       "\tCycle deviation from actual to aligned cycle is: '{} cycles'\n"
                       "\tActual period: '{} ns' Aligned period: '{} ns'\n"
                       "\t(You may want to change the period on this port to the aligned value)."
                       .format(port, self.rptv_data[port][closest_rptv_num]['label'], delta,
                               self.periods[port], aligned_period), 'warn', log=log)
                # deliver the payload
                if port not in self.match_rptv_data_lst:
                    self.match_rptv_data_lst[port] = []
                self.match_rptv_data_lst[port].append(self.rptv_data[port][closest_rptv_num])
        pr(self.match_rptv_data_lst, 'debug', self.debug, log=log)

    def __init__(self, debug=False, progname='', maxlogs=1,
                 outdir=os.path.dirname(os.path.realpath(__file__)), offset=0, srchstr='', comment_port=''):
        """
        Constructor for MatchLoopFixer
        :param debug: bool determines whether to print/log 'debug' statements in pr() functions
        :param progname: string used for appending to output file names and output directory
        :param maxlogs: int determines whether to have 1 log file per module or just 1 overall (default)
        :param outdir: string destination of all output files.  if not exist, it will be created
        """
        global log
        self.debug = debug
        self.comment_port = comment_port
        if self.debug:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
        logger_name, outdir = init_logging(scriptname=os.path.basename(sys.modules[__name__].__file__),
                                           outdir=outdir, name=progname, maxlogs=maxlogs, level=log_level)
        log = logging.getLogger(logger_name)
        log.warning = callcounted(log.warning)
        log.error = callcounted(log.error)
        pr('Running ' + os.path.basename(sys.modules[__name__].__file__) + '...', log=log)

        # get burst name and ports
        self.burst, self.ports = fw.sqsl_q(debug=debug, log=log)

        # execute functional test
        if not args.skip_func and not fw.ftst_q(self.burst, debug=debug, log=log):
            pr("this may be normal, especially if there are flaky patterns as they are not considered here", log=log)
            time.sleep(1)

        for port in self.ports:
            self.periods[port] = fw.pclk_q(port, debug=debug, log=log)
            self.labels_by_port[port], self.xmodes[port] = self.get_labels_xmodes(port)
            self.rptv_data[port] = self.get_rptv_from_getv(port)
            self.get_rptv_cmd_no_from_sqpg(port)

        self.set_mod()

        self.commport_match_rpt_vec_no = self.find_commport_match_rpt_vec_no(srch_str=srchstr)

        # get the absolute time for the match repeats on the comment port only
        self.find_match_rptv_time(offset)

        # use the absolute time found above to find match repeats for all the ports now
        self.find_corr_match_rptv_data()

        for label in self.labels_by_port[self.comment_port]:
            print label
        sys.exit()


        # curr_rptv, last_rptv = {}, {}  # init
        #
        #                     curr_rptv[tdl][label] = rptv - self.mod[port]
        #                     last_rptv[tdl][label] = rptv
        #     keep_going = True
        #     while keep_going:
        #         for port in self.ports:
        #             for label, rptv in curr_rptv.iteritems():
        #                 pr("\tSetting RPTV for port: '{}' to '{}'".format(port,))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description: "+sys.modules[__name__].__doc__)
    parser.add_argument('-name', '--name', required=False, default='', help='Optional name used for output files/logs.')
    parser.add_argument('-d', '--debug', action='store_true', help='print a lot of debug stuff to dlog')
    parser.add_argument('-out', '--output_dir', required=False, default='', help='Directory to place log file(s).')
    parser.add_argument('-max', '--maxlogs', type=int, default=1, required=False,
                        help='(0=OFF:log data to stdout).'
                             'Set to 1 to keep only one log (subsequent runs will overwrite).')
    parser.add_argument('-comm_port', '--comment_port', required=True, default='',
                        help='Port that has the search comments (just give one port, even if others have the string.')
    parser.add_argument('-cmt_offst', '--comment_offset', type=int, default=1, required=False,
                        help='Vector comment address offset from matchloop. '
                             '(0=comm_srch_str is on matchloop repeat vector; '
                             '-1=comm_srch_str is one vector BEFORE matchloop START; '
                             ' 1=comm_srch_str is one vector AFTER matchloop END)')
    parser.add_argument('-comm_srch_str', '--comment_search_string', required=False,
                        default='turn strobe(s) back on for final loop cycle',
                        help='String to search for in comments')
    parser.add_argument('-keep_temp_burst', '--keep_temp_burst', required=False,
                        help='Do not delete the temporary burst at the end of the script exeuction (not the default)')
    parser.add_argument('-skip_func', '--skip_func', action='store_true', required=False,
                        help='Do not run an initial functional test... not the default !')
    parser.add_argument('-bin', '--bin', action='store_true', required=False,
                        help='Dse a binary search algorithm instead of linear... not the default !')
    args = parser.parse_args()

    fw.check_xoc_session(log)

    mlf = MatchLoopFixer(progname=args.name,
                         debug=args.debug,
                         outdir=args.output_dir,
                         maxlogs=args.maxlogs,
                         offset=args.comment_offset,
                         srchstr=args.comment_search_string,
                         comment_port=args.comment_port)

    pr('ARGUMENTS:\n\t'+'\n\t'.join(['--'+k+'='+str(v) for k, v in args.__dict__.iteritems()]), log=log)
    pr('Number of WARNINGS for "{}": {}'.format(__script__, log.warning.counter, log=log), log=log)
    pr('Number of ERRORS for "{}": {}'.format(__script__, log.error.counter), log=log)

    time = time.time()-_start_time
    pr('Script took ' + str(round(time, 3)) + ' seconds (' + humanize_time(time) + ')', log=log)
    pr('Everything printed here was also printed to your log file(s) in the output directory.')
    new_files = os.popen('ls -lrt {}'.format(args.output_dir)).read()
    pr("Displaying Output Directory: {}\n\tContents: \n\t\t{}"
       .format(args.output_dir, '\n\t\t'.join(new_files.split('\n'))))
