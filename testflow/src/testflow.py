#! /usr/local/bin/python2.7

import sys
import pyparsing as pp
from pprint import pprint

class Node(object):
    def __init__(self, toks=None):
        if toks:
            self.val = toks[0]
            self.repr = str(toks[0])
        else:
            self.val = None
            self.repr = ''

    def eval(self, env=None):
        pass

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.repr

    def __eq__(self, other):
        try:
            return self.__dict__ == other.__dict__
        except AttributeError:
            return False


class DecEval(Node):
    def __init__(self, toks):
        """ :rtype : str, hash, self
            :param toks:
        """
        super(DecEval, self).__init__()
        self.val = int(toks[0])

    def __str__(self):
        return str(self.val)

    def __hash__(self):
        return hash(self.val)

    def eval(self, env=None):
        return self

        # def __add__(self, other):
        #     if isinstance(other, floatEval):
        #         return other + self
        #     try:
        #         return DecEval([str(self.val + other.val)])
        #     except AttributeError:
        #         return DecEval([str(self.val + other)])
        #
        # def __neg__(self):
        #     out = copy.deepcopy(self)
        #     out.val  = -out.val
        #     return out
        #
        # def __abs__(self):
        #     if self.val < 0:
        #         return -self
        #     return copy.deepcopy(self)
        #
        # def __mod__(self, other):
        #     try:
        #         return DecEval([str(self.val % other.val)])
        #     except AttributeError:
        #         return DecEval([str(self.val % other)])
        # def __pow__(self, other):
        #     try:
        #         return DecEval([str(self.val ** other.val)])
        #     except AttributeError:
        #         return DecEval([str(self.val ** other)])
        #
        # def _convert(self, other):
        #     if hasattr(other, 'val'):
        #         return other
        #     elif isinstance(other, float):
        #         return floatEval([str(other).upper()])
        #     return DecEval([str(other).upper()])
        #
        # def __mul__(self,other):
        #     if isinstance(other, floatEval):
        #         return other * self
        #     other = self._convert(other)
        #     return DecEval([str(self.val*other.val)])
        # def __radd__(self, other):
        #     return self.__add__(other)
        # def __rmul__(self,other):
        #     return self.__mul__(other)
        #
        # def __div__(self,other):
        #     if isinstance(other, floatEval):
        #         return other.__rdiv__(self)
        #     other = self._convert(other)
        #     try:
        #         return DecEval([str(self.val/other.val)])
        #     except ZeroDivisionError:
        #         print 'Warning!!: division by zero!!!'
        #         return DecEval(['0'])
        #
        # def __rdiv__(self,other):
        #     try:
        #         return DecEval([str(other/self.val).upper()])
        #     except ZeroDivisionError:
        #         print 'Warning!!: division by zero!!!'
        #         return DecEval(['0'])
        # def __sub__(self,other):
        #     if isinstance(other, floatEval):
        #         return (-other) + self
        #     other = self._convert(other)
        #     return DecEval([str(self.val - other.val)])
        # def __lshift__(self,other):
        #     other = self._convert(other)
        #     return DecEval([str(self.val << other.val)])
        # def __rshift__(self,other):
        #     other = self._convert(other)
        #     return DecEval([str(self.val >> other.val)])
        # def __or__(self,other):
        #     other = self._convert(other)
        #     return DecEval([str(self.val | other.val)])
        # def __and__(self,other):
        #     other = self._convert(other)
        #     return DecEval([str(self.val & other.val)])
        # def __xor__(self,other):
        #     other = self._convert(other)
        #     return DecEval([str(self.val ^ other.val)])
        # def __invert__(self):
        #     return DecEval([str(~self.val)])
        # def __cmp__(self,other):
        #     try:
        #         return cmp(self.val, other.val)
        #     except AttributeError:
        #         return cmp(self.val, other)
        # def __nonzero__(self):
        #     return self.val !=0


class hexEval(DecEval):
    def __init__(self, toks):
        super(hexEval, self).__init__(toks)
        self.val = int(toks[0], 16)
        self.repr = str(self.val)

# special chars
COMMA = pp.Literal(',').suppress()
POINT = pp.Literal('.')
AT = pp.Literal('@')

# delimiters
LCURL = pp.Literal('{').suppress()
RCURL = pp.Literal('}').suppress()
LPAR = pp.Literal("(").suppress()
RPAR = pp.Literal(")").suppress()
String = pp.QuotedString('"', escChar="\\", multiline=True)
COLON = pp.Literal(':').suppress()
SEMI = pp.Literal(';').suppress()
END = pp.Keyword("end").suppress() + pp.ZeroOrMore(pp.Regex('[\-]+')).suppress()

# math operators
LT = pp.Literal('<').suppress()
LTE = pp.Literal('<=').suppress()
GT = pp.Literal('>').suppress()
GTE = pp.Literal('>=').suppress()
PLUS = pp.Literal("+").suppress()
MINUS = pp.Literal("-").suppress()
MULT = pp.Literal("*").suppress()
DIV = pp.Literal("/").suppress()
E = pp.CaselessLiteral("E").suppress()
EQ = pp.Literal("=").suppress()
EQEQ = pp.Literal("==").suppress()

# data types
plus = pp.Literal('+').setName('add')
minus = pp.Literal('-').setName('sub')
plusorminus = plus ^ minus
# Int =  pp.Combine(pp.Word("+-"+pp.nums,pp.nums))

# Float = pp.Combine( pp.Word(pp.nums) + POINT + pp.Word(pp.nums) )
number = pp.Word(pp.nums)

decNumber = pp.Combine(pp.Optional(plusorminus) + number)
hexNumber = pp.Combine(pp.CaselessLiteral('0X').suppress() + pp.Word(pp.hexnums)).setParseAction(hexEval)

Int = decNumber.setParseAction(DecEval) ^ hexNumber
Int.parseWithTabs()

Float = pp.Combine(decNumber +
                   pp.Optional(POINT + pp.Optional(number)) +
                   pp.Optional(E + Int))
Bool = pp.Literal("0") | pp.Literal("1")

# must start with a letter
# label = pp.Word(pp.srange("[A-Za-z]") + pp.alphas)
label = pp.Word(pp.alphas + pp.printables, excludeChars='"')


# ---------------------------------------
# SAMPLE CODE ... TODO: check this out ... might be able to use
# ---------------------------------------
# nestedParens = nestedExpr('(', ')', content=enclosed)
# nestedBrackets = nestedExpr('[', ']', content=enclosed)
# nestedCurlies = nestedExpr('{', '}', content=enclosed)

# TODO: figure out expression definition
# <expression> := an arithmetic, string and/or boolean
# expression with operators:
# +
# -
# *
# /
# >
# >=
# <
# <=
# ==
# !=
# (
# )
# and
# or
# not
# and operands:
# pass(<test_suite>)
# fail(<test_suite>)
# tf_result(<test_suite>,<result_index>)
# has_run(<test_suite>)
# has_not_run(<test_suite>)
# * wsus()
# tsus()
# lsus()
# dsus()
# bsus()
# ( expression )

# expression parsing, uses built-in operator precedence.
expr = pp.Forward()

expression = pp.Word(pp.printables, excludeChars='";')

# TODO: complete string_with_vars definition
# string_with_vars = "[[<chars>] \@<var_name> ]... [<chars>]"
string_with_vars = String


ts_flag = pp.Keyword("bypass") |\
          pp.Keyword("set_pass") |\
          pp.Keyword("set_fail") |\
          pp.Keyword("hold") |\
          pp.Keyword("hold_on_fail") |\
          pp.Keyword("output_on_pass") |\
          pp.Keyword("output_on_fail") |\
          pp.Keyword("value_on_pass") |\
          pp.Keyword("value_on_fail") |\
          pp.Keyword("per_pin_on_pass") |\
          pp.Keyword("per_pin_on_fail")

tflow_flag = pp.Keyword("set pass level") |\
             pp.Keyword("set fail level") |\
             pp.Keyword("bypass level") |\
             pp.Keyword("hold on fail") |\
             pp.Keyword("global_hold") |\
             pp.Keyword("debug mode") |\
             pp.Keyword("site_match_mode")

system_flag = pp.Keyword("datalog_formatter") |\
              pp.Keyword("datalog_sample_size") |\
              pp.Keyword("graphic_result_displ") |\
              pp.Keyword("state_display") |\
              pp.Keyword("print_wafermap") |\
              pp.Keyword("ink wafer") |\
              pp.Keyword("max_reprobes") |\
              pp.Keyword("temp_monitor") |\
              pp.Keyword("calib_age_monitor") |\
              pp.Keyword("diag_monitor") |\
              pp.Keyword("current_monitor")

test_suite = label

# <flag_name> := {<tflow_flag> | <system_flag> }
flag_name = tflow_flag | system_flag

user_flag_name = label

flag_value = Int | Bool

# <var_name> := {<label> |
# <flag_name> |
# <test_suite>.<ts_flag>|
# * <test_suite>.ffc_on_fail}
var_name = label |\
           flag_name |\
           (test_suite + '.' + ts_flag) |\
           pp.ZeroOrMore((test_suite + '.' + pp.Keyword("ffc_on_fail")))

# ----------------------
# hp93000,testflow,0.1
# ----------------------
header = (pp.Keyword("hp93000").suppress() + COMMA + pp.Keyword("testflow").suppress() + COMMA + Float)\
         .setResultsName("header")


# ----------------------
# language_revision = 1;
# ----------------------
language_revision = (pp.Keyword("language_revision").suppress() + EQ + pp.Word(pp.nums) + SEMI)\
                    .setResultsName("language_revision")

# ----------------------
# information_section
# ----------------------
infospec = \
    pp.Keyword("description").suppress() + EQ + String + SEMI +\
    pp.Keyword("device_name").suppress() + EQ + String + SEMI +\
    pp.Keyword("device_revision").suppress() + EQ + String + SEMI +\
    pp.Keyword("test_revision").suppress() + EQ + String + SEMI
information_section = (pp.Keyword("information") + pp.ZeroOrMore(infospec) + END)\
                      .setResultsName("information_section")


# ----------------------
# declarations_section
# ----------------------
# <declaration> := {@<var_name> = <expression> |
# @<var_name> = <string> }
declaration = pp.Combine(AT + var_name) + EQ + (String | expression) + SEMI
# TODO: need to debug the "expression"
declarations_section = (pp.Keyword("declarations") + pp.ZeroOrMore(declaration) + END)\
                       .setResultsName("declarations_section")


# ----------------------
# implicit_declarations_section
# ----------------------
# <implicit_declaration> := {@<var_name> = <expression> |
# @<var_name> = <string> }
implicit_declaration = pp.Combine(AT + var_name) + EQ + (String | expression) + SEMI
# TODO: need to debug the "expression"
implicit_declarations_section = (pp.Keyword("implicit_declarations") + pp.ZeroOrMore(implicit_declaration) + END)\
                                .setResultsName("implicit_declarations_section")


# ----------------------
# flags_section
# ----------------------
flag_spec = (flag_name + EQ + flag_value + SEMI) |\
            (pp.Keyword("user") + user_flag_name + EQ + flag_value + SEMI)
# TODO: need to debug the "expression"
# flags_section = (pp.Keyword("flags") + pp.ZeroOrMore( flag_spec ) + END)\
flags_section = (pp.Keyword("flags") + pp.SkipTo(END) + END)\
                .setResultsName("flags_section")


# ----------------------
# testmethodparameters
# ----------------------
testmethodparameters = (pp.Keyword("testmethodparameters") + pp.SkipTo(END) + END)\
                       .setResultsName("testmethodparameters")


# ----------------------
# testmethodlimits
# ----------------------
testmethodlimits = (pp.Keyword("testmethodlimits") + pp.SkipTo(END) + END)\
                   .setResultsName("testmethodlimits")


# ----------------------
# testmethods
# ----------------------
testmethods = (pp.Keyword("testmethods") + pp.SkipTo(END) + END)\
              .setResultsName("testmethods")

# ----------------------
# tests_section
# ----------------------
user_procedure = String
test_label = label
test_spec = test_label + COLON + pp.ZeroOrMore(user_procedure)
tests_section = (pp.Keyword("tests_section") + pp.ZeroOrMore(test_spec) + END)\
                .setResultsName("tests_section")


# ----------------------
# testfunction_section
# ----------------------
testfunction_identifier = label
testfunction = testfunction_identifier + COLON +\
               pp.Keyword("testfunction_description") + EQ + String + SEMI +\
               pp.Keyword("testfunction_parameters") + EQ + String + SEMI
testfunction_section = (pp.Keyword("testfunctions") + pp.ZeroOrMore(testfunction) + END)\
                       .setResultsName("testfunction_section")


# ----------------------
# dataset_section
# ----------------------
dataset_label = label
dataset_file = "the name of a V93000 dataset file"
dataset_spec = dataset_label + COLON + pp.ZeroOrMore(pp.Keyword("file") + EQ + dataset_file + SEMI)
dataset_section = (pp.Keyword("datasets") + pp.ZeroOrMore(dataset_spec) + END)\
                  .setResultsName("dataset_section")


# ----------------------
# test_suites_section
# ----------------------
# <site_control_info>:= <sequence_type>: [<sequence_info>]
# (<sequence_info> is omitted if
# <sequence_type> = serial or parallel)
# <sequence_type> := {serial|parallel|semiparallel|other}
# <sequence_info> := {<size>:<cycle>:|<sequence_order>}
# (If <sequence_type> = semiparallel,
# <size>:<cycle>: is used.
# If <sequence_type> = other,
# <sequence_order> is used.)
# <size> := an integer number (where 0 = undefined)
# <cycle> := an integer number (where 0 = undefined),
# or -1 for "unbouded"
# <sequence_order> := <sequence_order_element>:
# [<sequence_order_element>:]
# <sequence_order_element> := an integer number
# (where, 0 = undefined, or
# a pogitive integer = test order)
# site_control = "<site_control_info>";
# TODO: translate BNF info above instead of line below
site_control_info = String

test_level = Int
ffc_count = Int

test_suite_entry = test_suite + COLON +\
                   pp.ZeroOrMore(
                       pp.Keyword("datasets") + EQ + dataset_label + SEMI |
                       pp.Keyword("tests") + EQ + test_label + SEMI |
                       pp.Keyword("test_level") + EQ + test_level + SEMI |
                       pp.Keyword("local_flags") + EQ + ts_flag + pp.Regex("[, ...]") + SEMI |
                       pp.ZeroOrMore(pp.Keyword("ffc_on_fail") + EQ + ffc_count + SEMI) |
                       pp.Keyword("override") + EQ + Bool + SEMI |
                       pp.Keyword("override_dpsset") + EQ + expression + SEMI |
                       pp.Keyword("override_levset") + EQ + expression + SEMI |
                       pp.Keyword("override_seqlbl") + EQ + expression + SEMI |
                       pp.Keyword("override_timset") + EQ + expression + SEMI |
                       pp.ZeroOrMore(pp.Keyword("override_wvfset") + EQ + expression + SEMI) |
                       pp.Keyword("override_testf") + EQ + label + SEMI |
                       pp.Keyword("site_match") + EQ + Bool + SEMI |
                       pp.Keyword("site_control") + EQ + site_control_info + SEMI
                   )
# test_suites_section = pp.Keyword("test_suites") + pp.ZeroOrMore(test_suite_entry) + END
test_suites_section = (pp.Keyword("test_suites") + pp.SkipTo(END) + END)\
                      .setResultsName("test_suites_section")


# ----------------------
# bin_disconnect
# ----------------------
bin_disconnect = (pp.Keyword("bin_disconnect") + pp.SkipTo(END) + END)\
                 .setResultsName("bin_disconnect")


# ----------------------
# initialize_section
# ----------------------
initialize_section = (pp.Keyword("initialize") + pp.SkipTo(END) + END)\
                     .setResultsName("initialize_section")


# ----------------------
# download_section
# ----------------------
download_section = (pp.Keyword("download") + pp.SkipTo(END) + END)\
                   .setResultsName("download_section")


# ----------------------
# abort_section
# ----------------------
abort_section = (pp.Keyword("abort") + pp.SkipTo(END) + END)\
                .setResultsName("abort_section")


# ----------------------
# pause_section
# ----------------------
pause_section = (pp.Keyword("pause") + pp.SkipTo(END) + END)\
                .setResultsName("pause_section")


# ----------------------
# reset_section
# ----------------------
reset_section = (pp.Keyword("reset").suppress() + pp.SkipTo(END) + END)\
                .setResultsName("reset_section")


# ----------------------
# exit_section
# ----------------------
exit_section = (pp.Keyword("exit").suppress() + pp.SkipTo(END) + END)\
               .setResultsName("exit_section")


# ----------------------
# bin_disconnect_section
# ----------------------
bin_disconnect_section = (pp.Keyword("bin_disconnect").suppress() + pp.SkipTo(END) + END)\
                         .setResultsName("bin_disconnect_section")


# ----------------------
# multi_bin_decision_section
# ----------------------
multi_bin_decision_section = (pp.Keyword("multi_bin_decision").suppress() + pp.SkipTo(END) + END)\
                         .setResultsName("multi_bin_decision_section")


# ----------------------
# test_flow_section
# ----------------------

print_expression = expression | string_with_vars

# <assignment> :={@<var_name> = <expression> |
# @<var_name> = <string>}
assignment  = var_name + EQ + (String | expression)

compound_state = (pp.Keyword("open") | pp.Keyword("closed")).setResultsName("compound_state")
compound_label = String.setResultsName("compound_label")
compound_description = String.setResultsName("compound_description")
over_on_flag = (pp.Keyword("over_on") | pp.Keyword("not_over_on")).setResultsName("over_on_flag")
good_flag = (pp.Keyword("good") | pp.Keyword("bad")).setResultsName("good_flag")
reprobe_flag = (pp.Keyword("reprobe") | pp.Keyword("noreprobe")).setResultsName("reprobe_flag")

# <statement> :=
# {
# 	<assignment> 								|
#
# 	run(<test_suite>) 							|
#
# 	run_and_branch(<test_suite>)
# 	then <statement> [else <statement>]			|
#
# 	print(<print_expression>) 					|
#
# 	print_dl(<print_expression>) 				|
#
# 	if <expression> then <statement>
# 	[else <statement>] 							|
#
# 	while <expression> do <statement> 			|
#
# 	for <assignment>;<expression>;<assignment>;
# 	do <statement> 								|
#
# 	repeat <statement>; until <expression> 		|
#
# 	'{' <statement> [;<statement>]... '}'
# 	[
# 		[<compound_state>],
# 		[<compound_label>],
# 		[<compound_description>]
# 	] 											|
#
# 	stop_bin
# 	(
# 		<major_bin>,
# 		<minor_bin>,
# 		[<OOC_rule>],
# 		<good_flag>,
# 		<reprobe_flag>,
# 		<color>,
# 		<physical_bin>
# 		[, <over_on_flag>]
# 	);
# }
# NOTE: For compatibility reasons to older versions, SmarTest saves stop_bin with a blank in between commas
#       between <minor_bin> and <good_flag>.



# <test_flow_section> := <statement>;
# [...]
#

test_flow_section = (pp.Keyword("test_flow").suppress() + pp.SkipTo(END) + END)\
                    .setResultsName("test_flow_section")


# ----------------------
# binning_section
# ----------------------
# <binning_section> :=
# otherwise bin = <major_bin> <minor_bin>, , <good_flag>,
# <reprobe_flag>, <color>,
# <physical_bin>[, <over_on_flag>] ;
# NOTE: For compatibility reasons to older versions, SmarTest saves otherwise_bin_description with a blank in
#       between commas between <minor_bin> and <good_flag>.
binning_section = (pp.Keyword("binning").suppress() + pp.SkipTo(END) + END)\
                  .setResultsName("binning_section")


# ----------------------
# context_section
# ----------------------
context_section = (pp.Keyword("context").suppress() + pp.SkipTo(END) + END)\
                  .setResultsName("context_section")


# ----------------------
# oocrule_section
# ----------------------
# <oocrule_section> := [<OOC_rule>]
# <OOC_rule> := [OOC_warning = <evaluation_limit>
# <consideration window> <action_limit> <message>]
# [OOC_stop = <evaluation_limit>
# <consideration window> <action_limit> <message>]
oocrule_section = (pp.Keyword("oocrule").suppress() + pp.SkipTo(END) + END)\
                  .setResultsName("oocrule_section")


# ----------------------
# setup_section
# ----------------------
setup_section = (pp.Keyword("setup").suppress() + pp.SkipTo(END) + END)\
                .setResultsName("setup_section")


# ----------------------
# hardware_bin_descriptions_section
# ----------------------
hardware_bin_descriptions_section = (pp.Keyword("hardware_bin_descriptions").suppress() + pp.SkipTo(END) + END)\
                                    .setResultsName("hardware_bin_descriptions_section")


# ----------------------
# section - NOTE: This comprises ALL of the (sub)sections defined above
# ----------------------
# <section> := {information <information_section> end |
# declarations <declarations_section> end |
# flags <flags_section> end |
# tests <tests_section> end |
# testfunctions <testfunction_section> end |
# datasets <dataset_section> end |
# test_suites <test_suites_section> end |
# initialize <initialize_section> end |
# download <download_section> end |
# abort <abort_section> end |
# pause <pause_section> end |
# reset <reset_section> end |
# exit <exit_section> end |
# test_flow <test_flow_section> end |
# binning <binning_section> end |
# ooc_rule <oocrule_section> end |
# context <setup_section> end |
# hardware_bin_descriptions <hardware_bin_descriptions_section> end }
section = header                                  +\
          language_revision                       +\
          information_section                     +\
          declarations_section                    +\
          implicit_declarations_section           +\
          flags_section                           +\
          testmethodparameters                    +\
          testmethodlimits                        +\
          testmethods                             +\
          pp.Optional(tests_section)              +\
          pp.Optional(testfunction_section)       +\
          pp.Optional(dataset_section)            +\
          test_suites_section                     +\
          pp.Optional(bin_disconnect)             +\
          pp.Optional(download_section)           +\
          pp.Optional(initialize_section)         +\
          pp.Optional(pause_section)              +\
          pp.Optional(abort_section)              +\
          pp.Optional(reset_section)              +\
          pp.Optional(exit_section)               +\
          pp.Optional(bin_disconnect_section)     +\
          pp.Optional(multi_bin_decision_section) +\
          test_flow_section                       +\
          binning_section                         +\
          pp.Optional(context_section)            +\
          pp.Optional(oocrule_section)            +\
          pp.Optional(setup_section)              +\
          hardware_bin_descriptions_section


class parse_TestFlow(object):
    def __init__(self, toks):
        self.parse_test_flow_section(toks["test_flow_section"])

    def parse_test_flow_section(self, content):
        print content

section.setParseAction(parse_TestFlow)

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 1:
        print "usage: (python) testflow.py <input file>"
        exit()
    print '\n\n'

    f = open(args[0])

    result = section.parseFile(f)

    f.close()
