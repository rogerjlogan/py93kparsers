#!/db/kepler_pe/93k/anaconda_ete/bin/python
"""
    Dynamically modifies the RPTV counts to find P/F location of matchloops (flattened into masked repeat blocks).
    Currently does not support LMAP generated patterns (BFLM only) even though there is a switch to choose LMAP (for later use).
    Expections:
        1. There are corresponding repeats across all ports (except ignored ports).  If no repeat is found at the same point in
            time (calculated from commment port) then an attempt is made to find the closest repeat.  The period for that port
            is then adjusted (aligned) for all future calculations in the script.  This is necessary to limit the size of the LCM
            of all port periods. The LCM of all port periods is used to find the step size in units of time for each port.
        2. The comment port has the correct repeat block size.  If other repeat blocks are smaller (in time units),
            then the port which has the smallest repeat block will limit the reduction attempt.
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
logfn = None

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
    memory = {}
    margin = 0.1
    bin = False
    burst = ''
    periods = {}
    aligned_periods = {}
    labels_by_port = {}
    labels_wtih_srchstr = {}
    ports = []
    match_rptv_data = {}
    rptv_data = {}
    match_rptv_times = []
    beg_cycle_count = {}
    end_cycle_count = {}
    search_str = ''
    mod = {}
    step_size_t = 0.0  # init same value for every port
    step_size_n = {}  # init unique value for every port

    @staticmethod
    def setup_logger(logger_name):
        """
        Setup logger with decorators for warning and error so we can count how
        many times they were called.
        :param logger_name: string name of logger used for retrieval
        """
        global log
        log = logging.getLogger(logger_name)
        log.warning = callcounted(log.warning)
        log.error = callcounted(log.error)

    def find_commport_match_rpt_vec_no(self):
        """
        This function searches each vector comment (on comment port only) for srch_str, if provided.
        :param srch_str: string string to search for in comments
        :return dict vector addresses that had the comment per label
        """
        log.info("Running tcmt()... (This may take a few minutes!)")
        tcmt_ptn = re.compile(r'tcmt (?P<vec_addr>\d+),"(?P<comment>[^"]+)"', re.IGNORECASE)

        for label in self.labels_by_port[self.comment_port]:
            log.info("\tGetting comments for label: '{}'".format(label))
            # set focus to label for this port before quering comments
            fw.tstl(label, self.comment_port, log=log)
            # okay, now we query comments
            for tcmt_rslt in fw.tcmt_q(0, log=log).split('\n'):
                tcmt_obj = tcmt_ptn.search(tcmt_rslt)
                if tcmt_obj:
                    vec_addr = int(tcmt_obj.group('vec_addr'))
                    comment = tcmt_obj.group('comment').strip()
                    if len(self.search_str) and self.search_str in comment:
                        if label not in self.labels_wtih_srchstr:
                            self.labels_wtih_srchstr[label] = []
                        self.labels_wtih_srchstr[label].append(vec_addr)
        if not self.labels_wtih_srchstr:
            log.critical("Search string not found on comment port: {}".format(self.comment_port))
            sys.exit(1)
        return self.labels_wtih_srchstr

    def get_labels(self, port):
        """
        Get all labels for each port in current burst.  Also need to get type of memory being used (SM/SHMEM)
        :param port: string name of port to get labels for using firmware
        :return list all labels found in port given
        """
        labels = []
        getl_ptn = re.compile(r'getl (?P<idx>\d+),\"(?P<label>.*)\",(?P<start>\d+),(?P<stop>\d+),\(', re.IGNORECASE)
        sqla_ptn = re.compile(r'sqla lbl,\"(?P<label>[^\"]+)\",\"PARA_MEM=(?P<memory>[^\"]+)\"', re.IGNORECASE)
        for getl_rslt in fw.getl_q(0, port, log=log).split('\n'):
            if not len(getl_rslt):
                continue
            getl_obj = getl_ptn.search(getl_rslt)
            if not getl_obj:
                log.critical("Unable to parse GETL result: " + getl_rslt)
                sys.exit(1)
            label = getl_obj.group('label').strip()
            labels.append(label)
            sqla_obj = sqla_ptn.search(fw.sqla_q(label, log=log))
            if sqla_obj:
                self.memory[label] = sqla_obj.group('memory')
            else:
                log.critical("Unable to get type of memory(SM/SHMEM) for label: '{}'".format(label))
                sys.exit(1)
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
                        log.debug("Match RPTV found on vec/cyc: '{}/{}' with per(ns): '{}' for comment port: '{}'"
                           .format(rptv_data['start_vector'], rptv_data['start_cycle'],
                                   self.periods[self.comment_port], self.comment_port))
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
        for getv_rslt in fw.getv_q(0, 100000000000, port, log=log).strip().split('\n'):
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
            sqlb_rslt = fw.sqlb_q(label, log=log)
            sqlb_obj = sqlb_ptn.search(sqlb_rslt)
            if sqlb_obj:
                start = int(sqlb_obj.group('start'))
                stop = int(sqlb_obj.group('stop'))
                # okay, now that we have the range, we can run SQPG? and get all the seq instructions for the port
                for sqpg_rslt in fw.sqpg_q(port, start, stop, log=log).split('\n'):
                    # search each result for all RPTV commands keeping track of the count, since that is a key that was
                    # started with GETV? earlier.  The cmd_No will allow us to modify the correct repeat later
                    sqpg_obj = sqpg_ptn.search(sqpg_rslt)
                    if sqpg_obj:
                        rptv_no += 1
                        self.rptv_data[port][rptv_no]['cmd_no'] = int(sqpg_obj.group('cmd_no'))

    @staticmethod
    def get_cyc2num(port, rptv_data):
        """
        Get the rptv number (order found in burst for given port) indexed by the start cycle of that rptv
        :param port: string name of port
        :param rptv_data: dict all the relevant data for every repeat (gleaned from SQPG? and GETV?)
        :return: dict repeat number by start cycle
        """
        return {this_rptv_data['start_cycle']: rptv_no for rptv_no, this_rptv_data in rptv_data[port].iteritems()}

    @staticmethod
    def get_closest_rptv_num(cyc2num, ideal_rptv_cyc):
        """
        Get the closest rptv number that coincides with the ideal_rptv_cyc
        :param cyc2num: dict repeat number by start cycle
        :param ideal_rptv_cyc: the start_cycle of the rptv if the vectors were correctly aligned
        :return: int rptv number closest to ideal_rptv_cyc passed
        """
        return cyc2num.get(ideal_rptv_cyc, cyc2num[min(cyc2num.keys(), key=lambda x: abs(x-ideal_rptv_cyc))])

    def find_corr_match_rptv_data(self):
        """
        Uses the matchloop repeats found in the control port (comment_port) to find the corresponding
        match repeats on the other ports.  Does this by calcalating the time (time = cycle * period) where the repeat
        starts and uses that in the other ports to find the correct cycle (cycle = time / period).
        If no repeat is found on that cycle, then it looks for the closest repeat in either direction and gives warning
        that vectors are not aligned. Also gives you the current period for that port and what the period would be to
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
                    log.debug("closest_rptv_cyc: {}".format(closest_rptv_cyc))
                    log.debug("ideal_rptv_cyc: {}".format(ideal_rptv_cyc))
                    log.debug("m_rptv_time: {}".format(m_rptv_time))
                    aligned_period = round(m_rptv_time / (closest_rptv_cyc+1), 4)
                    if aligned_period not in aligned_periods[port]:
                        aligned_periods[port].append(aligned_period)
                    delta = abs(closest_rptv_cyc-ideal_rptv_cyc)
                    log.warning("Vector misalignment at matchloop repeat on port: '{}' label: '{}'\n"
                                "\t(Assuming aligned period for all future calculations in this script).\n"
                                "\tCycle deviation from actual to aligned cycle is: '{} cycles'\n"
                                "\tActual period: '{} ns' Aligned period: '{} ns'\n"
                                "\t(You may want to change the period on this port to the aligned value)."
                                .format(port, self.rptv_data[port][closest_rptv_num]['label'], delta,
                                        self.periods[port], aligned_period))
                # deliver the payload
                if m_rptv_time not in self.match_rptv_data:
                    self.match_rptv_data[m_rptv_time] = {}
                self.match_rptv_data[m_rptv_time][port] = self.rptv_data[port][closest_rptv_num]
        # average all the periods and round to nearest 2 decimal places
        # if a matchloop had no mis-aligned periods on any port, then just use period
        for port, periods in aligned_periods.iteritems():
            if len(periods):
                per = round(np.mean(periods), 2)
            else:
                per = self.periods[port]
            self.aligned_periods[port] = per
        log.debug(self.match_rptv_data)

    def calc_step_size(self, m_rptv_data):
        """
        Calculate min step size in time and number of steps for all ports.  Must have calculated aligned periods first.
        :param m_rptv_data: dict all the relevant data for match repeats (gleaned from SQPG? and GETV?)
        """
        log.info("Formula for calculating step size for each port: int(ceil(step_size_t / (period / no_of_vectors)))")
        log.info("Aligned period (which may differ from actual) is used for calculating step size.")
        if not self.aligned_periods:
            log.critical("Can't calculate step size until Aligned periods have been calculated!")
        self.step_size_t = max([self.aligned_periods[p] / data['no_of_vectors'] for p, data in m_rptv_data.iteritems()])
        log.debug("Step size (time) for all ports: %r ns" % (self.step_size_t,))

        for port in self.ports:
            no_of_vectors = m_rptv_data[port]['no_of_vectors']
            self.step_size_n[port] = int(math.ceil(self.step_size_t / (self.aligned_periods[port] / no_of_vectors)))
            log.debug("Port: '{}' Aligned Period: '{} ns' no_of_vectors: '{}' Step size (for no_of_repeats) : '{}'"
                      .format(port, self.aligned_periods[port], no_of_vectors, self.step_size_n[port]))

    def set_final_values(self, m_rptv_data, original_rptv, current_rptv):
        """
        Adds margin to last passing rptv value and sets final rptv repeat values for all ports
        :param m_rptv_data: dict all the relevant data for match repeats (gleaned from SQPG? and GETV?)
        :param original_rptv: dict original rptv values for each port
        :param current_rptv: dict latest rptv value for each port
        """
        failed = False
        for port in self.ports:
            total_steps = original_rptv[port] - current_rptv[port]
            start_cycle_t = self.aligned_periods[port]*current_rptv[port]
            log.debug("Total steps traversed: {} for port: '{}'".format(total_steps, port))
            log.debug("Last pass for port/cycle(time): {}/{}({})".format(port, current_rptv[port], start_cycle_t))
            log.debug("Step size (time)    used: {}".format(self.step_size_t))
            log.debug("Step size (repeats) used: {}".format(self.step_size_n[port]))
            log.debug("Margin set to: {}".format(self.margin))

            # adding margin
            new_rptv = int(round(current_rptv[port] * (1 + self.margin)))

            if new_rptv >= original_rptv[port]:
                # Margin above Fail location would make the repeat increase, so abort
                failed = True
                new_rptv = original_rptv[port]
                log.warning("Not enough room to add margin (set to {}). Restoring label: '{}'. Setting RPTV back to: {} from {}"
                            .format(self.margin, m_rptv_data[port]['label'], original_rptv[port], current_rptv[port]))
                break
            # okay, let's go modify the label with the new rptv value with margin added (or set back to original)
            self.update_port_label("FINAL (if all other ports okay) update to label", port, m_rptv_data, new_rptv)
        if failed:
            for port in self.ports:
                self.update_port_label("RESETTING update to label", port, m_rptv_data, original_rptv[port])

    def get_port_repeat(self, original_rptv, cport_midpt, port):
        """
        Calculate repeats for port passed in based on control port's repeat count
        :param original_rptv: dict original repeat value per port
        :param cport_midpt: int repeat count which is current midpoint for control (comment) port
        :param port: string name of port
        :return: int updated rptv value which is equivalent to control (comment) port's value
        """
        # get num steps traversed (decreased) by comment port
        unit_steps_delta = (original_rptv[self.comment_port] - cport_midpt) / self.step_size_n[self.comment_port]
        log.debug("Units steps delta from original (factoring out step size): {}".format(unit_steps_delta))
        if port == self.comment_port:
            new_rptv = cport_midpt
        else:
            # calculate number of cycles to decrease based on comment port change
            new_rptv = original_rptv[port] - unit_steps_delta * self.step_size_n[port]
        log.debug("New RPTV value on port: {} is: {}".format(port, new_rptv))
        return new_rptv

    def update_port_label(self, msg, port, m_rptv_data, new_repeat):
        """
        Download the updated rptv info to the tester for given port. Also calculates reduction achieved so far.
        :param msg: string message to prepended to log message
        :param port: string name of port
        :param m_rptv_data: dict all the relevant data for match repeats (gleaned from SQPG? and GETV?)
        :param new_repeat: int value of updated repeat count for this port
        """
        label = m_rptv_data[port]['label']
        start_vector = m_rptv_data[port]['start_vector']
        no_of_vectors = m_rptv_data[port]['no_of_vectors']
        no_of_repeats = m_rptv_data[port]['no_of_repeats']
        cmd_no = m_rptv_data[port]['cmd_no']
        log.debug("{msg}: '{label}' on Port: '{port}' at vector: '{vector}' beging changed to 'RPTV {new_num},{new_rep}'"
                  "(orig: RPTV {old_num}, {old_rep} with stepsize={step})"
                 .format(msg=msg, label=label, port=port, vector=start_vector, new_num=no_of_vectors, old_num=no_of_vectors,
                         old_rep=no_of_repeats, new_rep=new_repeat, step=self.step_size_n[port]))
        fw.sqpg(cmd_no=cmd_no, instr='rptv', param_1=no_of_vectors, param_2=new_repeat,
                memory=self.memory[label], port=port, log=log)

    def do_parametric_ftest(self):
        """
        Linear or Binary search of P/F for rptv values changed
        """
        # iterate through each matchloop repeat across all ports found earlier
        for m_rptv_time, m_rptv_data in sorted(self.match_rptv_data.iteritems()):
            log.info("START Repeat modification search for burst: '{}'".format(self.burst))

            # go get the step size in time for all ports and the step repeat num for each port
            self.calc_step_size(m_rptv_data)

            # re-organize for quicker access
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
                    skip_func = False
                    log.info("Trying next repeat (count={})".format(count))
                    # calculate midpoint: average and then round up to nearest repeat step size
                    cport_midpt = roundup2mod((cport_upper + cport_lower) / 2, self.step_size_n[self.comment_port])
                    log.debug("New midpoint for comment port({}): {} (original repeat={})"
                              .format(self.comment_port, cport_midpt, original_rptv[self.comment_port]))

                    for port in self.ports:
                        current_rptv[port] = self.get_port_repeat(original_rptv, cport_midpt, port)
                        if current_rptv[port] < self.step_size_n[port]:
                            # consider this a fail, search top half
                            log.warning("Repeat block for port: {} smaller (in time units) than comment port: {}"
                                        .format(port, self.comment_port))
                            skip_func = True
                        else:
                            self.update_port_label("BINARY search change to label", port, m_rptv_data, current_rptv[port])
                    if not skip_func and fw.ftst_q(self.burst, log=log):
                        # passed at midpoint, search bottom half (not far enough)
                        cport_upper = cport_midpt
                        last_passing_rptv = deepcopy(current_rptv)
                    else:
                        # failed at midpoint, search top half (too far)
                        cport_lower = cport_midpt
                if not last_passing_rptv:
                    log.warning("NO PASS FOUND FOR BURST: '{}'!".format(self.burst))
                    for port in self.ports:
                        self.update_port_label("No Pass found!  Resetting repeats back to original values.", port, m_rptv_data, original_rptv[port])
                else:
                    log.debug(last_passing_rptv)
                    self.set_final_values(m_rptv_data, original_rptv, last_passing_rptv)

            else:  # linear search
                passed = 0
                keep_going = True
                while keep_going:
                    # keep going until functional test fails
                    if not fw.ftst_q(self.burst, log=log):
                        if passed == 0:
                            log.critical("Did not pass at least at once")
                            sys.exit(1)
                        self.set_final_values(m_rptv_data, original_rptv, current_rptv)
                        keep_going = False
                        log.debug("Found P/F transition on burst: '{}' at t(ns) = {}".format(self.burst, m_rptv_time))
                    else:
                        passed += 1
                        log.info("Trying next repeat (count={})".format(passed))
                        for port in self.ports:
                            current_rptv[port] -= self.step_size_n[port]
                            if current_rptv[port] < self.step_size_n[port]:
                                keep_going = False
                            else:
                                self.update_port_label("LINEAR search change to label", port, m_rptv_data, current_rptv[port])
                if passed == 0:
                    log.warning("NO PASS FOUND FOR BURST: '{}'!".format(self.burst))
                    for port in self.ports:
                        self.update_port_label("No Pass found!  Resetting repeats back to original values.", port, m_rptv_data, original_rptv[port])

            if not fw.ftst_q(self.burst, log=log):
                for port in self.ports:
                    self.update_port_label("Post Search Func Test Failed!  "
                                           "Resetting repeats back to original values.", port, m_rptv_data, original_rptv[port])

    def show_reduction(self):
        """
        Display statistics of differences between total cycle count for each port before/after RPTV modification
        """
        log.info("Showing Reduction Achieved for Burst: '{}' ...".format(self.burst))
        for port in self.ports:
            beg = self.beg_cycle_count[port]
            end = self.end_cycle_count[port]
            reduction = 100 - round(float(end)/float(beg)*100, 4)
            difference = beg - end
            time_saved = difference * self.periods[port] / 1000 / 1000  # ms
            log.info("\t{:>15}: Beg Cyc Count: {:>10} End Cyc Count: {:>10} Differece: {:<10} Reduction: {:>7} % Time Saved: {:>7} ms"
                     .format(port, beg, end, difference, reduction, time_saved))
        log.info("Search String was: '{}'".format(self.search_str))
        log.info("Labels found with Search String (and their vector numbers) ...")
        log.debug(self.labels_wtih_srchstr)
        for label, vectors in self.labels_wtih_srchstr.iteritems():
            log.info("\tLabel with Search String: '{}' Vectors: {}".format(label, ','.join([str(v) for v in vectors])))

    def get_cycle_count(self):
        """
        Uses GETV? to get all vector data per port and looks at last vector to get total cycle count
        :return: dict total cycle count (int) for each port
        """
        getv_ptn = re.compile(r'getv (?P<start_cycle>\d+),(?P<no_of_cycles>\d+),', re.IGNORECASE)
        total_cyc = {}
        for port in self.ports:
            total_cyc[port] = 0  # init
            # get last vector data only
            getv_rslt = fw.getv_q(0, 100000000000, port,
                                  debug_output_char_limit=0, log=log).strip().split('\n')[-1]
            if len(getv_rslt):
                getv_obj = getv_ptn.search(getv_rslt)
                if getv_obj:
                    last_vec_start_cyc = int(getv_obj.group('start_cycle'))
                    no_of_cycles = int(getv_obj.group('no_of_cycles'))
                    total_cyc[port] = last_vec_start_cyc + no_of_cycles
            if total_cyc[port] == 0:
                log.critical("Unable to get Cycle Count for Port: '{}'".format(port))
                sys.exit(1)
        return total_cyc

    def __init__(self, debug=False, progname='', outdir=os.path.dirname(os.path.realpath(__file__)),
                 offset=0, srchstr='', comment_port='', lmap=False, marg=0.1, binary=False, ignore=''):
        """
        Init for MatchLoopFixer
        :param debug: bool determines whether to print/log 'debug' statements in pr() functions
        :param progname: string used for appending to output file names and output directory
        :param outdir: string destination of all output files.  if not exist, it will be created
        :param offset: int vector comment address offset from matchloop.
        :param srchstr: string string to search for in comments
        :param comment_port: string
        :param lmap: bool patterns were generated with LMAP (true) or BFLM (false)
        """
        global logfn
        self.debug = debug
        self.lmap = lmap
        self.comment_port = comment_port
        self.margin = marg
        self.binary = binary
        self.search_str = srchstr
        if self.debug:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
        logger_name, outdir, logfn = init_logging(scriptname=os.path.basename(sys.modules[__name__].__file__),
                                                  outdir=outdir, name=progname, level=log_level)
        self.setup_logger(logger_name)
        log.info('Running ' + os.path.basename(sys.modules[__name__].__file__) + '...')

        if self.lmap:
            log.critical("Currently does not support LMAP mode!  Please re-generate your patterns with BFLM and remove switch")
            sys.exit(1)

        # get burst name and ports
        self.burst, self.ports = fw.sqsl_q(log=log)

        if len(ignore):
            # remove ignored ports before continuing
            for port in [p.strip() for p in ignore.split(',')]:
                if port == self.comment_port:
                    log.critical("Comment port: '{}' can not be in ignore port list: '{}'".format(port, ignore))
                    sys.exit(1)
                log.debug("Removing port: '{}'".format(port))
                self.ports.remove(port)

        # execute functional test
        if not args.skip_func and not fw.ftst_q(self.burst, lmap=self.lmap, log=log):
            log.info("this may be normal, especially if there are flaky patterns as they are not considered here")
            time.sleep(1)

        for port in self.ports:
            self.periods[port] = fw.pclk_q(port, log=log)
            self.labels_by_port[port] = self.get_labels(port)
            self.rptv_data[port] = self.get_rptv_from_getv(port)
            self.get_rptv_cmd_no_from_sqpg(port)

        # get the vector number for the comment port vector
        self.commport_match_rpt_vec_no = self.find_commport_match_rpt_vec_no()

        # get the absolute time for the match repeats on the comment port only
        self.find_match_rptv_time(offset)

        # use the absolute time found above to find corresponding match repeats for all the ports now
        self.find_corr_match_rptv_data()

        # get cycle count BEFORE RPTV MODIFICATION for statistics at end
        self.beg_cycle_count = self.get_cycle_count()

        # modify match repeats and continually check for P/F
        self.do_parametric_ftest()

        # get cycle count AFTER RPTV MODIFICATION for statistics at end
        self.end_cycle_count = self.get_cycle_count()

        self.show_reduction()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description: "+sys.modules[__name__].__doc__)
    parser.add_argument('-name', '--name', required=False, default='', help='Optional name used for output files/logs.')
    parser.add_argument('-d', '--debug', action='store_true', help='print a lot of debug stuff to dlog')
    parser.add_argument('-out', '--output_dir', required=False, default='', help='Directory to place log file(s).')
    parser.add_argument('-comm_port', '--comment_port', required=True, default='',
                        help='Port that has the search comments (just give one port, even if others have the string.')
    parser.add_argument('-cmt_offst', '--comment_offset', type=int, default=1, required=False,
                        help='Vector comment address offset from matchloop. '
                             '(0=comm_srch_str is on matchloop repeat vector; '
                             '-1=comm_srch_str is one vector BEFORE matchloop START; '
                             ' 1=comm_srch_str is one vector AFTER matchloop END)')
    parser.add_argument('-comm_srch_str', '--comment_search_string', required=False,
                        default='turn strobe(s) back on for final loop cycle',
                        help='String to search for in comments (USE DOUBLE QUOTES)')
    parser.add_argument('-ignore', '--ignore_ports', required=False, default='',
                        help='Comma separated string of ports to ignore for this script (useful for Asynchronous ports; USE DOUBLE QUOTES)')
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
                         offset=args.comment_offset,
                         srchstr=args.comment_search_string,
                         comment_port=args.comment_port,
                         lmap=args.lmap,
                         marg=args.margin,
                         binary=args.bin,
                         ignore=args.ignore_ports)

    log.info('ARGS PASSED TO THIS SCRIPT:\n\t'+'\n\t'.join(['--'+k+'='+str(v) for k, v in args.__dict__.iteritems()]))
    num_warns = log.warning.counter
    num_errors = log.error.counter
    if num_warns:
        log.warning('Number of WARNINGS for "{}": {} (You should read these!)'.format(__script__, num_warns))
    else:
        log.warning('Yay! No WARNINGNS for "{}"!'.format(__script__))
    if num_errors:
        log.error('Number of ERRORS for "{}": {} (You should really ready these!)'.format(__script__, num_errors))
    else:
        log.error('Yay! No ERRORS for "{}"!'.format(__script__))

    time = time.time()-_start_time
    log.info('Script took ' + str(round(time, 3)) + ' seconds (' + humanize_time(time) + ')')
    log.info('Everything printed here was also printed to your log file in the output directory.')
    log.info('Log file: {}'.format(logfn))

    if logfn is not None:
        # hack to remove color code characters from log file. couldn't figure out how to prevent
        # colors from being sent to log file that were meant for console
        string = open(logfn).read()
        new_str = re.sub(r'(\033|\x1b)\[\d+m', '', string)
        open(logfn, 'w').write(new_str)
