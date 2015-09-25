#! /usr/local/bin/python2.7

import sys
import pyparsing as pp
from generic_parsers import *
from print_debug import *

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


character = pp.alphanums

# <color> := an integer number (where 0 = black, 1 = white, 2 = red,
# 3 = yellow, 4 = green, 5 = cyan, 6 = blue, 7 = magenta),
# or the name of the color in lower case.
color = pp.Word(pp.alphanums)

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

expression = pp.Word(pp.printables, excludeChars='";')

# TODO: complete string_with_vars definition
# string_with_vars = "[[<chars>] \@<var_name> ]... [<chars>]"
string_with_vars = String

# <major_bin> := <character>[<character>]
major_bin = character + pp.Optional(character)

# <minor_bin> := <string_with_vars>
minor_bin = string_with_vars

# <evaluation_limit> := <integer>
evaluation_limit = Int

# <consideration window> := <integer>
consideration_window = Int

# <action_limit> := <integer>
action_limit = Int

# <message> := <string> given as report warning or
# stop message
message = String

# <OOC_rule> := [OOC_warning = <evaluation_limit>
# <consideration window> <action_limit> <message>]
# [OOC_stop = <evaluation_limit>
# <consideration window> <action_limit> <message>]
OOC_rule = pp.Optional(pp.Keyword("OOC_warning") + EQ + evaluation_limit + consideration_window + action_limit + message) +\
           pp.Optional(pp.Keyword("OOC_stop")    + EQ + evaluation_limit + consideration_window + action_limit + message)

physical_bin = Int

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
var_name = pp.Optional(label |\
                       flag_name |\
                       pp.Group(test_suite + POINT + ts_flag) |\
                       pp.Group(test_suite + POINT + pp.Keyword("ffc_on_fail"))\
                       )

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

# test_suite_entry = test_suite + COLON +\
#                    pp.ZeroOrMore(
#                        pp.Keyword("datasets") + EQ + dataset_label + SEMI |
#                        pp.Keyword("tests") + EQ + test_label + SEMI |
#                        pp.Keyword("test_level") + EQ + test_level + SEMI |
#                        pp.Keyword("local_flags") + EQ + ts_flag + pp.Regex("[, ...]") + SEMI |
#                        pp.ZeroOrMore(pp.Keyword("ffc_on_fail") + EQ + ffc_count + SEMI) |
#                        pp.Keyword("override") + EQ + Bool + SEMI |
#                        pp.Keyword("override_dpsset") + EQ + expression + SEMI |
#                        pp.Keyword("override_levset") + EQ + expression + SEMI |
#                        pp.Keyword("override_seqlbl") + EQ + expression + SEMI |
#                        pp.Keyword("override_timset") + EQ + expression + SEMI |
#                        pp.ZeroOrMore(pp.Keyword("override_wvfset") + EQ + expression + SEMI) |
#                        pp.Keyword("override_testf") + EQ + label + SEMI |
#                        pp.Keyword("site_match") + EQ + Bool + SEMI |
#                        pp.Keyword("site_control") + EQ + site_control_info + SEMI
#                    )
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
assignment  =  var_name + EQ + (String | expression)

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

# this line is necessary if "statement" is going to be nested,
# then statement must use "<<" instead of "="
statement = pp.Forward()
run_statement = pp.Keyword("run") + LPAR + test_suite + RPAR
run_and_branch_statement = pp.Keyword("run_and_branch") + LPAR + test_suite + RPAR + pp.Keyword("then") +\
                 statement + pp.Optional(pp.Keyword("else") + statement)
print_statement = pp.Keyword("print") + print_expression
print_dl_statement = pp.Keyword("print_dl") + print_expression
if_statement = pp.Keyword("if") + expression + pp.Keyword("then") + statement + pp.Optional(pp.Keyword("else") + statement)
while_statement = pp.Keyword("while") + expression + pp.Keyword("do") + statement
for_statement = pp.Keyword("for") + assignment + SEMI + expression + SEMI + assignment + SEMI + pp.Keyword("do") + statement
repeat_statement = pp.Keyword("repeat") + statement + SEMI + pp.Keyword("until") + expression
group_statement = LCURL + statement + pp.ZeroOrMore(SEMI + statement) + RCURL + \
                  pp.Optional(pp.Optional(compound_state) + COMMA +\
                                pp.Optional(compound_label) + COMMA +\
                                pp.Optional(compound_description))
stop_bin_statement = pp.Keyword("stop_bin") + LCURL + major_bin + minor_bin +\
                     pp.Optional(OOC_rule) + good_flag + reprobe_flag + color +\
                     physical_bin + pp.Optional(COMMA + over_on_flag)
statement << ( #assignment|\
              run_statement|\
              run_and_branch_statement|\
              print_statement|\
              print_dl_statement|\
              if_statement|\
              while_statement|\
              for_statement|\
              repeat_statement|\
              group_statement|\
              stop_bin_statement).setResultsName("statement")

test_flow_section = pp.Group(pp.Keyword("test_flow").suppress() + pp.OneOrMore(statement) + END)\
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
# oocrule_section = pp.Optional(OOC_rule)
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
section = header + language_revision +\
            pp.ZeroOrMore(
                information_section                     |\
                declarations_section                    |\
                implicit_declarations_section           |\
                flags_section                           |\
                testmethodparameters                    |\
                testmethodlimits                        |\
                testmethods                             |\
                tests_section                           |\
                testfunction_section                    |\
                dataset_section                         |\
                test_suites_section                     |\
                bin_disconnect                          |\
                download_section                        |\
                initialize_section                      |\
                pause_section                           |\
                abort_section                           |\
                reset_section                           |\
                exit_section                            |\
                bin_disconnect_section                  |\
                multi_bin_decision_section              |\
                binning_section                         |\
                context_section                         |\
                oocrule_section                         |\
                setup_section                           |\
                hardware_bin_descriptions_section
            ) +\
            test_flow_section +\
            pp.ZeroOrMore(
                information_section                     |\
                declarations_section                    |\
                implicit_declarations_section           |\
                flags_section                           |\
                testmethodparameters                    |\
                testmethodlimits                        |\
                testmethods                             |\
                tests_section                           |\
                testfunction_section                    |\
                dataset_section                         |\
                test_suites_section                     |\
                bin_disconnect                          |\
                download_section                        |\
                initialize_section                      |\
                pause_section                           |\
                abort_section                           |\
                reset_section                           |\
                exit_section                            |\
                bin_disconnect_section                  |\
                multi_bin_decision_section              |\
                binning_section                         |\
                context_section                         |\
                oocrule_section                         |\
                setup_section                           |\
                hardware_bin_descriptions_section
            )



class parse_TestFlow(object):
    def __init__(self, toks):
        self.parse_test_flow_section(toks["test_flow_section"])

    def parse_test_flow_section(self, content):
        print2file(content)

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
