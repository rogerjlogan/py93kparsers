#!/db/kepler_pe/93k/anaconda_ete/bin/python
"""
    Dynamically modifies the RPTV counts to find the first passing condition of an MATCHLOOP flattened pattern.
    Considers the fact that these patterns have multiple ports and the modulo behavior needs to be preserved for LMAP.
    Doesn't hurt BFLM either.
"""
import time
from common import *
import sys
import firmware as fw
import math
from collections import OrderedDict
from copy import deepcopy
import numpy as np

_start_time = time.time()
log = None

__author__ = 'Roger'
__script__ = os.path.basename(sys.modules[__name__].__file__)


# ---------------------------------------------------------
# GLOBAL CONSTANTS/VARS

_COMM_SRCH_STR_ = 'turn strobe(s) back on for final loop cycle'
_MIN_MARGIN_RATIO_ = 5


class MatchLoopFixer(object):
    """
    Class to fix matchloop after Jazz converted to a set repeat (RPTV).
    """
    debug = False
    comment_port = ''
    commport_match_rpt_vec_no = {}
    memory = 'SH'
    margin = 0.1
    bin = False
    burst = ''
    periods = {}
    aligned_periods = {}
    labels_by_port = {}
    ports = []
    match_rptv_data = {}
    rptv_data = {}
    match_rptv_times = []
    mod = {}
    step_size_t = 0.0  # init same value for every port
    step_size_n = {}  # init unique value for every port

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

    def get_labels(self, port):
        """
        Get all labels for each port in current burst
        There is only a query version of this command, so no need for 'get_'
        """
        labels = []
        getl_ptn = re.compile(r'getl (?P<idx>\d+),\"(?P<label>.*)\",(?P<start>\d+),(?P<stop>\d+),\(', re.IGNORECASE)
        for getl_rslt in fw.getl_q(0, port, debug=self.debug, log=log).split('\n'):
            if not len(getl_rslt):
                continue
            getl_obj = getl_ptn.search(getl_rslt)
            if not getl_obj:
                pr("Unable to parse GETL result: " + getl_rslt, 'fatal', log=log)
            label = getl_obj.group('label').strip()
            labels.append(label)
        return labels

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
        Since we couldn't get everything we wanted from GETV, we need to use SQPG? to get cmd_no.
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

    @staticmethod
    def get_cyc2num(port, rptv_data):
        return {this_rptv_data['start_cycle']: rptv_no for rptv_no, this_rptv_data in rptv_data[port].iteritems()}

    @staticmethod
    def get_closest_rptv_num(cyc2num, ideal_rptv_cyc):
        return cyc2num.get(ideal_rptv_cyc, cyc2num[min(cyc2num.keys(), key=lambda x: abs(x-ideal_rptv_cyc))])

    def find_corr_match_rptv_data(self):
        """
        This routine uses the matchloop repeats found in the control port (comment_port) to find the corresponding
        match repeats on the other ports.  It does this by calcalating the time (time = cycle * period) where the repeat
        starts and uses that in the other ports to find the correct cycle (cycle = time / period).
        If no repeat is found on that cycle, then it looks for the closest repeat in either direction and gives warning
        that vectors are not aligned. It also gives you the current period for that port and what the period would be to
        align the vectors.
        """
        aligned_periods = {}  # keep this local until we can compare with original periods
        for port in self.ports:
            if port not in aligned_periods:
                aligned_periods[port] = []
            # create a simple dictionary on this port to map cycles to rptv_no for easier access below
            cyc2num = self.get_cyc2num(port, self.rptv_data)

            for m_rptv_time in self.match_rptv_times:
                ideal_rptv_cyc = int(m_rptv_time / self.periods[port])
                # Find the rptv_no that has the closest 'start_cycle' to our ideal 'start_cycle' which is really just
                # this port's equivalent to the 'start_cycle' in our control port (comment_port)
                closest_rptv_num = self.get_closest_rptv_num(cyc2num, ideal_rptv_cyc)
                closest_rptv_cyc = self.rptv_data[port][closest_rptv_num]['start_cycle']
                if closest_rptv_cyc != ideal_rptv_cyc:
                    # okay, we're not aligned, so we need to generate a warning
                    aligned_period = round(m_rptv_time / closest_rptv_cyc, 4)
                    if aligned_period not in aligned_periods[port]:
                        aligned_periods[port].append(aligned_period)
                    delta = abs(closest_rptv_cyc-ideal_rptv_cyc)
                    pr("Vector misalignment at matchloop repeat on port: '{}' label: '{}'\n"
                       "\t(Assuming aligned period for all future calculations in this script).\n"
                       "\tCycle deviation from actual to aligned cycle is: '{} cycles'\n"
                       "\tActual period: '{} ns' Aligned period: '{} ns'\n"
                       "\t(You may want to change the period on this port to the aligned value)."
                       .format(port, self.rptv_data[port][closest_rptv_num]['label'], delta,
                               self.periods[port], aligned_period), 'warn', log=log)
                # deliver the payload
                if m_rptv_time not in self.match_rptv_data:
                    self.match_rptv_data[m_rptv_time] = {}
                self.match_rptv_data[m_rptv_time][port] = self.rptv_data[port][closest_rptv_num]
        for port, periods in aligned_periods.iteritems():
            if len(periods):
                per = round(np.mean(periods), 2)
            else:
                per = self.periods[port]
            self.aligned_periods[port] = per
        pr(self.match_rptv_data, 'debug', self.debug, log=log)

    def calc_step_size(self, m_rptv_data):
        """
        Calculate min step size in time for all ports.  Must have calculated aligned periods first.
        :param m_rptv_data:
        :return:
        """
        pr("Formula for calculating step size for each port: int(ceil(step_size_t / (period / no_of_vectors)))", log=log)
        pr("Aligned period (which may differ from actual) is used for calculating step size.", log=log)
        if not self.aligned_periods:
            pr("Can't calculate step size until Aligned periods have been calculated!", 'fatal', log=log)
        self.step_size_t = max([self.aligned_periods[p] / data['no_of_vectors'] for p, data in m_rptv_data.iteritems()])
        pr("Step size (time) for all ports: %r ns" % (self.step_size_t,), 'debug', self.debug, log=log)

        for port in self.ports:
            no_of_vectors = m_rptv_data[port]['no_of_vectors']
            self.step_size_n[port] = int(math.ceil(self.step_size_t / (self.aligned_periods[port] / no_of_vectors)))
            pr("Port: '{}' Aligned Period: '{} ns' no_of_vectors: '{}' Step size (for no_of_repeats) : '{}'"
               .format(port, self.aligned_periods[port], no_of_vectors, self.step_size_n[port]), 'debug', self.debug, log=log)

    def set_final_values(self, m_rptv_data, original_rptv, current_rptv):
        all_new_rptv = {}
        for port in self.ports:
            total_steps = original_rptv[port] - current_rptv[port]
            start_cycle_t = self.aligned_periods[port]*current_rptv[port]
            pr("Total steps traversed: {} for port: '{}'".format(total_steps, port), 'debug', debug=self.debug, log=log)
            pr("Last pass for port/cycle(time): {}/{}({})"
               .format(port, current_rptv[port], start_cycle_t), 'debug', debug=self.debug, log=log)

            pr("Step size (time)    used: {}".format(self.step_size_t), 'debug', debug=self.debug, log=log)
            pr("Step size (repeats) used: {}".format(self.step_size_n[port]), 'debug', debug=self.debug, log=log)
            pr("Margin set to: {}".format(self.margin), 'debug', self.debug, log=log)

            # adding margin
            new_rptv = current_rptv[port] * (1 + self.margin)

            if new_rptv < original_rptv[port]:
                # let's only go down for now
                all_new_rptv[port] = new_rptv
                rptv_t = new_rptv * self.aligned_periods[port]
                pr("For port: {} New RPTV value: {} (amount of time: {})"
                   .format(port, new_rptv, rptv_t), 'debug', self.debug, log=log)

                pr("First Fail at: {}  Setting with margin to: {}"
                   .format(current_rptv[port], new_rptv), 'debug', debug=self.debug, log=log)
                net_time_savings = (self.aligned_periods[port]*(original_rptv[port]-new_rptv))/1000/1000  # ms
                pr("Final update to label: '{}' Setting RPTV to: {} from {} (with net time savings: {})"
                   .format(m_rptv_data[port]['label'], new_rptv, original_rptv[port], net_time_savings))
            else:
                # Margin above Fail location would make the repeat increase, so abort
                new_rptv = original_rptv[port]
                pr("Not enough room to add margin (set to {}). Restoring label: '{}'. Setting RPTV back to: {} from {}"
                   .format(self.margin, m_rptv_data[port]['label'], original_rptv[port], current_rptv[port]),
                   'warn', log=log)

            # okay, let's go modify the label with the new rptv value with margin added (or set back to original)
            self.update_port_label("FINAL update to label", port, m_rptv_data, new_rptv)

        # sanity check for debug mode only after final modification
        if self.debug:
            for p, rptv in all_new_rptv.iteritems():
                rptv_t = rptv * self.aligned_periods[p]
                pr("For port: {} New RPTV value: {} (amount of time: {})"
                   .format(p, rptv, rptv_t), 'debug', self.debug, log=log)

    def get_port_repeat(self, original_rptv, cport_midpt, port):
        """
        Calculate repeats for port passed in based on control port's repeat count
        """
        # get num steps traversed (decreased) by comment port
        unit_steps_delta = (original_rptv[self.comment_port] - cport_midpt) / self.step_size_n[self.comment_port]
        pr("Units steps delta from original (factoring out step size): {}".format(unit_steps_delta), 'debug', self.debug, log=log)
        if port == self.comment_port:
            new_rptv = cport_midpt
        else:
            # calculate number of cycles to decrease based on comment port change
            new_rptv = original_rptv[port] - unit_steps_delta * self.step_size_n[port]
        pr("New RPTV value on port: {} is: {}".format(port, new_rptv), 'debug', self.debug, log=log)
        return new_rptv

    def update_port_label(self, msg, port, m_rptv_data, new_repeat):
        label = m_rptv_data[port]['label']
        start_vector = m_rptv_data[port]['start_vector']
        no_of_vectors = m_rptv_data[port]['no_of_vectors']
        no_of_repeats = m_rptv_data[port]['no_of_repeats']
        cmd_no = m_rptv_data[port]['cmd_no']
        pr("{msg}: '{label}' on Port: '{port}' at vector: '{vector}' beging changed to 'RPTV {new_num},{new_rep}'"
           "(orig: RPTV {old_num}, {old_rep} with stepsize={step})"
           .format(msg=msg, label=label, port=port, vector=start_vector, new_num=no_of_vectors, old_num=no_of_vectors,
                   old_rep=no_of_repeats, new_rep=new_repeat, step=self.step_size_n[port]), log=log)
        fw.sqpg(cmd_no=cmd_no, instr='rptv', param_1=no_of_vectors, param_2=new_repeat,
                memory=self.memory, port=port, debug=self.debug, log=log)

    def do_parametric_ftest(self):

        # iterate through each matchloop repeat across all ports found earlier
        for m_rptv_time, m_rptv_data in sorted(self.match_rptv_data.iteritems()):
            pr("START Repeat modification search for burst: '{}'".format(self.burst), log=log)

            self.calc_step_size(m_rptv_data)
            original_rptv = {port: data['no_of_repeats'] for port, data in m_rptv_data.iteritems()}
            current_rptv = deepcopy(original_rptv)  # init
            last_passing_rptv = {}

            if self.binary:  # binary search

                # init upper/lower boundaries for RPTV(no_of_repeats) for control port (comment port)
                cport_upper = original_rptv[self.comment_port]
                cport_lower = self.step_size_n[self.comment_port]

                count = 0
                while (cport_upper-cport_lower) > self.step_size_n[self.comment_port]:
                    count += 1
                    pr("Trying next repeat (count={})".format(count), log=log)
                    # calculate midpoint: average and then round up to nearest repeat step size
                    cport_midpt = roundup2mod((cport_upper + cport_lower) / 2, self.step_size_n[self.comment_port])
                    pr("New midpoint for comment port({}): {} (original repeat={})"
                       .format(self.comment_port, cport_midpt, original_rptv[self.comment_port]), 'debug', debug=self.debug, log=log)

                    for port in self.ports:
                        current_rptv[port] = self.get_port_repeat(original_rptv, cport_midpt, port)
                        self.update_port_label("BINARY search change to label", port, m_rptv_data, current_rptv[port])
                    if fw.ftst_q(self.burst, debug=self.debug, log=log):
                        # passed at midpoint, search bottom half
                        cport_upper = cport_midpt
                        last_passing_rptv = deepcopy(current_rptv)
                    else:
                        # failed at midpoint, search top half
                        cport_lower = cport_midpt
                if not last_passing_rptv:
                    pr("NO PASS FOUND FOR BURST: '{}'!".format(self.burst), 'warn', log=log)
                    self.update_port_label("No Pass found!  Resetting repeats back to original values.", port, m_rptv_data, current_rptv[port])
                else:
                    pr(last_passing_rptv, 'debug', debug=self.debug, log=log)
                    self.set_final_values(m_rptv_data, original_rptv, last_passing_rptv)

            else:  # linear search
                passed = 0
                keep_going = True
                while keep_going:
                    # keep going until functional test fails
                    if not fw.ftst_q(self.burst, debug=self.debug, log=log):
                        if passed == 0:
                            pr("Did not pass at least at once", 'fatal', log=log)
                        self.set_final_values(m_rptv_data, original_rptv, current_rptv)
                        keep_going = False
                        pr("Found P/F transition on burst: '{}' at t(ns) = {}"
                           .format(self.burst, m_rptv_time), 'debug', debug=self.debug, log=log)
                    else:
                        passed += 1
                        pr("Trying next repeat (count={})".format(passed), log=log)
                        for port in self.ports:
                            label = m_rptv_data[port]['label']
                            current_rptv[port] -= self.step_size_n[port]
                            if current_rptv[port] < 0:
                                pr("Unable to find P/F threshold for label: '{}'".format(label), 'fatal', log=log)
                            self.update_port_label("LINEAR search change to label", port, m_rptv_data, current_rptv[port])
            if not fw.ftst_q(self.burst, debug=self.debug, log=log):
                pr("Failed Func test after final modification to burst", 'fatal', log=log)

    def __init__(self, debug=False, progname='', maxlogs=1, outdir=os.path.dirname(os.path.realpath(__file__)),
                 offset=0, srchstr='', comment_port='', memory='SH', lmap=False, marg=0.1, binary=False):
        """
        Constructor for MatchLoopFixer
        :param debug: bool determines whether to print/log 'debug' statements in pr() functions
        :param progname: string used for appending to output file names and output directory
        :param maxlogs: int determines whether to have 1 log file per module or just 1 overall (default)
        :param outdir: string destination of all output files.  if not exist, it will be created
        :param offset:
        :param srchstr:
        :param comment_port:
        :param lmap:
        """
        global log
        self.debug = debug
        self.lmap = lmap
        self.comment_port = comment_port
        self.memory = memory
        self.margin = marg
        self.binary = binary
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

        if self.lmap:
            pr("Currently does not support LMAP mode!  Please re-generate your patterns with BFLM and remove switch",
               'fatal', log=log)

        # get burst name and ports
        self.burst, self.ports = fw.sqsl_q(debug=self.debug, log=log)

        # execute functional test
        if not args.skip_func and not fw.ftst_q(self.burst, lmap=self.lmap, debug=self.debug, log=log):
            pr("this may be normal, especially if there are flaky patterns as they are not considered here", log=log)
            time.sleep(1)

        for port in self.ports:
            self.periods[port] = fw.pclk_q(port, debug=self.debug, log=log)
            self.labels_by_port[port] = self.get_labels(port)
            self.rptv_data[port] = self.get_rptv_from_getv(port)
            self.get_rptv_cmd_no_from_sqpg(port)

        # get the vector number for the comment port vector
        self.commport_match_rpt_vec_no = self.find_commport_match_rpt_vec_no(srch_str=srchstr)

        # get the absolute time for the match repeats on the comment port only
        self.find_match_rptv_time(offset)

        # use the absolute time found above to find corresponding match repeats for all the ports now
        self.find_corr_match_rptv_data()

        # modify match repeats and continually check for P/F
        self.do_parametric_ftest()

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
    parser.add_argument('-mem', '--memory', required=False,
                        default='SH',
                        help="Set to 'SH' or 'SHMEM'")
    # parser.add_argument('-keep_temp_burst', '--keep_temp_burst', required=False,
    #                     help='Do not delete the temporary burst at the end of the script exeuction (not the default)')
    parser.add_argument('-skip_func', '--skip_func', action='store_true', required=False,
                        help='Do not run an initial functional test... not the default !')
    parser.add_argument('-bin', '--bin', action='store_true', required=False,
                        help='Use binary method to search P/F (default=Linear) !')
    parser.add_argument('-lmap', '--lmap', action='store_true',
                        help='Patterns were generated with LMAP (not supported at this time. BFLM is default)')
    parser.add_argument('-marg', '--margin', type=restricted_float, default=0.1, required=False,
                        help='Decimal margin to allow for padding above P/F location'
                             'Set to 1 to keep only one log (subsequent runs will overwrite).')
    args = parser.parse_args()

    fw.check_xoc_session(log)

    mlf = MatchLoopFixer(progname=args.name,
                         debug=args.debug,
                         outdir=args.output_dir,
                         maxlogs=args.maxlogs,
                         offset=args.comment_offset,
                         srchstr=args.comment_search_string,
                         comment_port=args.comment_port,
                         memory=args.memory,
                         lmap=args.lmap,
                         marg=args.margin,
                         binary=args.bin)

    pr('ARGUMENTS:\n\t'+'\n\t'.join(['--'+k+'='+str(v) for k, v in args.__dict__.iteritems()]), log=log)
    pr('Number of WARNINGS for "{}": {}'.format(__script__, log.warning.counter, log=log), log=log)
    pr('Number of ERRORS for "{}": {}'.format(__script__, log.error.counter), log=log)

    time = time.time()-_start_time
    pr('Script took ' + str(round(time, 3)) + ' seconds (' + humanize_time(time) + ')', log=log)
    pr('Everything printed here was also printed to your log file(s) in the output directory.')
    new_files = os.popen('ls -lrt {}'.format(args.output_dir)).read()
    pr("Displaying Output Directory: {}\n\tContents: \n\t\t{}"
       .format(args.output_dir, '\n\t\t'.join(new_files.split('\n'))))
