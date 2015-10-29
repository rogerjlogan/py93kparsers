__author__ = 'Roger'

# modified to True if certain sections are found
isUTMBased = False

import pyparsing as pp
from print_debug import *
import sys
import re
from common import *

debug = True

SEMI = pp.Literal(';').suppress()
AT = pp.Literal('@').suppress()
ATtok = pp.Literal('@')
COLON = pp.Literal(':').suppress()
COLONtok = pp.Literal(':')
COMMA = pp.Literal(',').suppress()
COMMAtok = pp.Literal(',')
UNDER = pp.Literal('_')
DOT = pp.Literal('.').suppress()
PERIOD = DOT
DOTtok = pp.Literal('.')
PERIODtok = DOTtok
EQ = pp.Literal('=').suppress()
EQtok = pp.Literal('=')
DASH = pp.Literal('-')
MINUS = DASH
PLUS = pp.Literal('+')
MULT = pp.Literal('*')
DIV = pp.Literal('/')
NOT = pp.Literal('!')
Not = pp.Keyword("not")
EQEQ = pp.Literal('==')
NOTEQ = pp.Literal('!=')
LE = pp.Literal('<=')
GE = pp.Literal('>=')
LT = pp.Literal('<')
GT = pp.Literal('>')
LCURL = pp.Literal('{').suppress()
RCURL = pp.Literal('}').suppress()
LPAR = pp.Literal('(').suppress()
RPAR = pp.Literal(')').suppress()
LPARtok = pp.Literal('(')
RPARtok = pp.Literal(')')

# common output strings
EndStr = "end\n-----------------------------------------------------------------"

E = pp.CaselessLiteral("E")
number = pp.Word(pp.nums)
plusorminus = PLUS | MINUS
integer = pp.Combine(pp.Optional(plusorminus) + number)
Float = pp.Combine(integer + pp.Optional('.' + pp.Optional(number)) + pp.Optional(E + integer))
Bool = pp.Literal('0') | '1'

# BinaryAdd = str_p("+") | "-"  ;
BinaryAdd = PLUS | MINUS

# BinaryMult = str_p("*") | "/"  ;
BinaryMult = MULT | DIV

# BinaryRel = str_p("==") |  "!="  | "<="  | ">="  | "<"   | ">";
BinaryRel = EQEQ | NOTEQ | LE | GE | LT | GT

# BinaryLogic = str_p("or") | "and" ;
BinaryLogic = pp.Keyword("or") | pp.Keyword("and")

# Unary = str_p("!") | "-"  | "not";
Unary = NOT | DASH | Not

# BinaryRelTerm = Term >> *(BinaryRel >> BinaryRelTerm);
BinaryRelTerm = pp.Forward()

# BinaryLogicTerm = BinaryRelTerm >> *(BinaryLogic >> BinaryRelTerm);
BinaryLogicTerm = BinaryRelTerm + pp.ZeroOrMore(BinaryLogic + BinaryRelTerm)

# BinaryMultTerm = BinaryLogicTerm >> *(BinaryMult >> BinaryLogicTerm);
BinaryMultTerm = BinaryLogicTerm + pp.ZeroOrMore(BinaryMult + BinaryLogicTerm)

# BinaryAddTerm = BinaryMultTerm >> *(BinaryAdd >> BinaryMultTerm);
BinaryAddTerm = BinaryMultTerm + pp.ZeroOrMore(BinaryAdd + BinaryMultTerm)

# Expression = BinaryAddTerm[Expression.expression = construct_<string>(arg1, arg2)];
Expression = pp.Combine(BinaryAddTerm,joinString=' ',adjacent=False)

# NumberFunction  = str_p("pass") | "fail" | "has_run" | "has_not_run" | "tf_result" |"tf_pin_result" | "spst_timing" |
#                         "spst_level" | "svlr_timing" | "svlr_level" | "wsus" | "bsus" | "lsus" | "tsus"          ;
NumberFunction = (pp.Keyword("pass") | pp.Keyword("fail") | pp.Keyword("has_run") | pp.Keyword("has_not_run") |
                  pp.Keyword("tf_result") | pp.Keyword("tf_pin_result") | pp.Keyword("spst_timing") |
                  pp.Keyword("spst_level") | pp.Keyword("svlr_timing") | pp.Keyword("svlr_level") |
                  pp.Keyword("wsus") | pp.Keyword("bsus") | pp.Keyword("lsus") | pp.Keyword("tsus"))

# StringFunction = str_p("burstfirst") | "burstnext";
StringFunction = pp.Keyword("burstfirst") | pp.Keyword("burstnext")

# Number = real_p | int_p;
Number = Float | integer

# End = str_p("end");
End = (pp.Keyword("end") + pp.ZeroOrMore(DASH)).suppress()

# Identifier = lexeme_d[(*((alnum_p | ch_p('_')))) - (str_p("end"))];
Identifier = pp.Word(pp.alphanums + '_')

# TestsuiteFlag = ch_p('@') >> (Identifier >> "." >> Identifier)[TestsuiteFlag.varName = construct_<string>(arg1, arg2)];
TestsuiteFlag = ATtok + (Identifier + DOTtok + Identifier)

# Variable = str_p("@") >> (Identifier)[Variable.varName = construct_<string>(arg1, arg2)] |
#                  "@{" >> (Identifier)[Variable.varName = construct_<string>(arg1, arg2)] >> "}";
Variable = pp.Combine((ATtok + Identifier) | ("@{" + Identifier + "}"))

# String = (alnum_p - ch_p('!')) >> *(alnum_p | "_");
String = pp.Combine(pp.Word(pp.alphanums,excludeChars='!') + pp.ZeroOrMore(pp.Word(pp.alphanums) | UNDER))

# QuotedString << ch_p('"') >> lexeme_d[(*(lex_escape_ch_p - ch_p('"')))]
#                [QuotedString.noQuotes = construct_<string>(arg1, arg2)] >> ch_p('"') >> !QuotedString;
QuotedString = pp.Forward()

QuotedString << pp.Combine(pp.QuotedString(unquoteResults=False, quoteChar='"', escChar='\\',multiline=True) + pp.Optional(QuotedString))

# Literal = Number | TestsuiteFlag | Variable | QuotedString | String;
Literal = Number | TestsuiteFlag | Variable | QuotedString | String

# Term = "(" >> Expression >> ")" | NumberFunction >>  "(" >> !((Expression) >> *( "," >> (Expression))) >> ")"
# | StringFunction >>  "(" >> !((Expression) >> *( "," >> (Expression))) >> ")" | Unary >> Term | Literal;
Term = pp.Forward()
# Term = (LPAR + Expression + RPAR | NumberFunction + LPAR + pp.Optional(Expression + pp.ZeroOrMore(COMMA + Expression))
#         + RPAR | StringFunction + LPAR + pp.Optional(Expression + pp.ZeroOrMore(COMMA + Expression))
#         + RPAR | Unary + Term | Literal)
Term = (LPARtok + Expression + RPARtok | NumberFunction + LPARtok + pp.Optional(Expression + pp.ZeroOrMore(COMMAtok + Expression))
        + RPARtok | StringFunction + LPARtok + pp.Optional(Expression + pp.ZeroOrMore(COMMAtok + Expression))
        + RPARtok | Unary + Term | Literal)

BinaryRelTerm << Term + pp.ZeroOrMore(BinaryRel + BinaryRelTerm)

# QualifiedIdentifier = Variable[QualifiedIdentifier.varName = arg1] |
#     Identifier[QualifiedIdentifier.varName = construct_<string>(arg1, arg2)];
QualifiedIdentifier = Variable | Identifier

# TestsuiteFlag = ch_p('@') >> (Identifier >> "." >> Identifier)[TestsuiteFlag.varName = construct_<string>(arg1, arg2)];
TestsuiteFlag = AT + (Identifier + DOT + Identifier)

# Type = str_p("double")[Type.type = ::xoc::tapi::ZTestflowVariableType_DOUBLE] |
#      str_p("string")[Type.type = ::xoc::tapi::ZTestflowVariableType_STRING];
Type = pp.Keyword("double") | pp.Keyword("string")

# OptFileHeader = !str_p("hp93000,testflow,0.1");
OptFileHeader = (pp.Optional(pp.Keyword("hp93000,testflow,0.1")))("OptFileHeader")

class ParseOptFileHeader(object):
    def __init__(self,toks):
        self.section_name = "OptFileHeader"
        self.header = toks[0]
    def __str__(self):
        return self.header

OptFileHeader.setParseAction(ParseOptFileHeader)

# OptRevision = !(str_p("language_revision") >> ch_p('=') >> int_p >> ch_p(';'));
OptRevision = (pp.Optional(pp.Keyword("language_revision")).suppress() + EQ + pp.Word(pp.nums) + SEMI)("OptRevision")

class ParseOptRevision(object):
    def __init__(self,toks):
        self.section_name = "OptRevision"
        self.language_revision = toks[0]
    def __str__(self):
        return "language_revision" + ' = ' + self.language_revision + ';\n'

OptRevision.setParseAction(ParseOptRevision)

# EmptySection = ch_p(';');
EmptySection = pp.Group(pp.Literal(';'))("EmptySection")

class ParseEmptySection(object):
    def __init__(self,toks):
        self.section_name = ""
        self.empty_section = toks
    def __str__(self):
        return ';'

EmptySection.setParseAction(ParseEmptySection)

# -------------------------------------------------------------------------------------------
# BEGIN InformationSection
# -------------------------------------------------------------------------------------------

# DeviceName = str_p("device_name") >> '=' >> (QuotedString)[bind(&SetDeviceName)(arg1)] >> ';';
DeviceName = pp.Keyword("device_name").suppress() + EQ + QuotedString("SetDeviceName") + SEMI

# DeviceRevision = str_p("device_revision") >> '=' >> QuotedString[bind(&SetDeviceRevision)(arg1)] >> ';';
DeviceRevision = pp.Keyword("device_revision").suppress() + EQ + QuotedString("SetDeviceRevision") + SEMI

# TestRevision = str_p("test_revision") >> '=' >> QuotedString[bind(&SetTestRevision)(arg1)] >> ';';
TestRevision = pp.Keyword("test_revision").suppress() + EQ + QuotedString("SetTestRevision") + SEMI

# Description = str_p("description") >> '=' >> QuotedString[bind(&SetDescription)(arg1)] >> ';';
Description = pp.Keyword("description").suppress() + EQ + QuotedString("SetDescription") + SEMI

# Application = str_p("application") >> '=' >> QuotedString[bind(&SetApplication)(arg1)] >> ';';
Application = pp.Keyword("application").suppress() + EQ + QuotedString("SetApplication") + SEMI

# Temperature = str_p("temperature") >> '=' >> real_p[bind(&SetTemperature)] >> ';';
Temperature = pp.Keyword("temperature").suppress() + EQ + Float("SetTemperature") + SEMI

# InformationElements = *(DeviceName | DeviceRevision | TestRevision | Description | Application | Temperature);
InformationElements = pp.Group(pp.ZeroOrMore(DeviceName | DeviceRevision | TestRevision | Description | Application | Temperature))

# InformationSection = str_p("information") >> InformationElements >> End;
InformationSection = (pp.Keyword("information").suppress() + InformationElements + End)("InformationSection")

class ParseInformationSection(object):
    def __init__(self,toks):
        self.section_name = "information"
        self.SetDeviceName = toks[0].SetDeviceName
        self.SetDeviceRevision = toks[0].SetDeviceRevision
        self.SetTestRevision = toks[0].SetTestRevision
        self.SetDescription = toks[0].SetDescription
        self.SetApplication = toks[0].SetApplication
        self.SetTemperature = toks[0].SetTemperature
    def __str__(self):
        rstr = self.section_name + "\n"
        for k,v in self.__dict__.items():
            if k == "section_name":
                pass
            elif k == "SetDeviceName" and len(v):
                rstr += "device_name = \"" + v + "\";\n"
            elif k == "SetDeviceRevision" and len(v):
                rstr += "device_revision = \"" + v + "\";\n"
            elif k == "SetTestRevision" and len(v):
                rstr += "test_revision = \"" + v + "\";\n"
            elif k == "SetDescription" and len(v):
                rstr += "description = \"" + v + "\";\n"
            elif k == "SetApplication" and len(v):
                rstr += "application = \"" + v + "\";\n"
            elif k == "SetTemperature" and len(v):
                rstr += "temperature = " + v + ";\n"
            else:
                pass
        rstr += EndStr
        return rstr

InformationSection.setParseAction(ParseInformationSection)

# -------------------------------------------------------------------------------------------
# BEGIN ImplicitDeclarationSection
# -------------------------------------------------------------------------------------------

# Declaration = (Variable[Declaration.varName = arg1] >> ':' >> Type[Declaration.varType = arg1] >> ';' )
#                [bind(&CreateImplicitVariable)(Declaration.varName, Declaration.varType)];
Declaration = pp.Group(Variable + COLON + Type + SEMI)

# ImplicitDeclarations = (*Declaration);
ImplicitDeclarations = pp.ZeroOrMore(Declaration)

# ImplicitDeclarationSection = str_p("implicit_declarations") >> ImplicitDeclarations >> End;
ImplicitDeclarationSection = (pp.Keyword("implicit_declarations").suppress() + ImplicitDeclarations + End)("ImplicitDeclarationSection")

class ParseImplicitDeclarationSection(object):
    def __init__(self,toks):
        self.section_name = "implicit_declarations"
        self.Declaration = {}
        for tok in toks:
            self.Declaration[tok[0]] = tok[1]
    def __str__(self):
        rstr = self.section_name + "\n"
        for varName,varType in self.Declaration.iteritems():
            rstr += varName + ' : ' + varType + ';\n'
        rstr += EndStr
        return rstr

ImplicitDeclarationSection.setParseAction(ParseImplicitDeclarationSection)

# -------------------------------------------------------------------------------------------
# BEGIN DeclarationSection
# -------------------------------------------------------------------------------------------

# variables = (Variable[variables.varName = arg1] >> '=' >> Expression[variables.value = arg1] >> ';')
#              [bind(&CreateVariable)(variables.varName, variables.value)];
# variables = (Variable + EQ + Expression + SEMI)
Definition = pp.Group(Variable + EQ + Expression + SEMI)

# Declarations = (*variables);
Declarations = pp.ZeroOrMore(Definition)

# DeclarationSection = str_p("declarations") >> Declarations >> End;
DeclarationSection = (pp.Keyword("declarations").suppress() + Declarations + End)("DeclarationSection")

class ParseDeclarationSection(object):
    def __init__(self,toks):
        self.section_name = "declarations"
        self.variables = {}
        for tok in toks:
            self.variables[tok[0]] = tok[1]
    def __str__(self):
        rstr = self.section_name + "\n"
        for varName,value in self.variables.iteritems():
            rstr += varName + ' = ' + value + ';\n'
        rstr += EndStr
        return rstr

DeclarationSection.setParseAction(ParseDeclarationSection)

# -------------------------------------------------------------------------------------------
# BEGIN FlagSection
# -------------------------------------------------------------------------------------------

# SystemFlag = *(alnum_p | ch_p('_')) >> '=' >> *(alnum_p | '-') >> ';';
SystemFlag = pp.Group(pp.Word(pp.alphanums + '_') + EQ + pp.Word(pp.alphanums + '-') + SEMI)

# UserFlag = (str_p("user") >> (alpha_p >> *(alnum_p | '_'))[UserFlag.varName = construct_<string>(arg1, arg2)]
#            >> '=' >> Expression[UserFlag.value = arg1] >> ';')
#            [bind(&CreateUserVariable)(UserFlag.varName, UserFlag.value)];
UserFlag = pp.Group(pp.Keyword("user") + pp.Word(pp.alphas,pp.alphanums + '_') + EQ + Expression + SEMI)

# //Systemflags are ignored for now, as they are still handled by the flag_ui
# Flags = *(UserFlag | SystemFlag);
Flags = pp.ZeroOrMore(UserFlag | SystemFlag)

# FlagSection = str_p("flags") >> Flags >> End;
FlagSection = (pp.Keyword("flags").suppress() + Flags + End)("FlagSection")

class ParseFlagSection(object):
    def __init__(self,toks):
        self.section_name = "flags"
        self.UserFlag = {}
        self.SystemFlag = {}
        for tok in toks:
            if len(tok) == 3:
                self.UserFlag[tok[1]] = tok[2]
            elif len(tok) == 2:
                self.SystemFlag[tok[0]] = tok[1]
            else:
                sys.exit("ERROR!!! Unknown element in 'flags' section! Exiting ...")
    def __str__(self):
        rstr = self.section_name + "\n"
        for varName,value in self.SystemFlag.iteritems():
            rstr += varName + ' = ' + value + ';\n'
        for varName,value in self.UserFlag.iteritems():
            rstr += "user " + varName + ' = ' + value + ';\n'
        rstr += EndStr
        return rstr

FlagSection.setParseAction(ParseFlagSection)

# -------------------------------------------------------------------------------------------
# BEGIN TestfunctionSection
# -------------------------------------------------------------------------------------------

# TestfunctionDescription = str_p("testfunction_description") >> '=' >> QuotedString[Testfunction.description = arg1] >> ';';
TestfunctionDescription = pp.Group(pp.Keyword("testfunction_description")("testfunction_description") + EQ + QuotedString + SEMI)

# TestfunctionParameter = str_p("testfunction_parameters")  >> '=' >> QuotedString[Testfunction.parameters = arg1] >> ';';
TestfunctionParameter = pp.Group(pp.Keyword("testfunction_parameters")("testfunction_parameters") + EQ + QuotedString + SEMI)

# TestfunctionDefinition = ((TestfunctionDescription >> TestfunctionParameter) | (TestfunctionParameter >> TestfunctionDescription));
TestfunctionDefinition = ((TestfunctionDescription + TestfunctionParameter) | (TestfunctionParameter + TestfunctionDescription))

# Testfunction = ((Identifier)[Testfunction.identifier = construct_<string>(arg1, arg2)] >> ':'>> TestfunctionDefinition)
#                [bind(&CreateTestfunction)(Testfunction.identifier, Testfunction.description, Testfunction.parameters)];
Testfunction = pp.Group(Identifier + COLON + TestfunctionDefinition)

# Testfunctions = *(Testfunction) >> End;
Testfunctions = pp.ZeroOrMore(Testfunction) + End

# TestfunctionSection = str_p("testfunctions") >> Testfunctions;
TestfunctionSection = (pp.Keyword("testfunctions").suppress() + Testfunctions)("TestfunctionSection")

class ParseTestfunctionSection(object):
    def __init__(self,toks):
        self.section_name = "testfunctions"
        self.Testfunctions = {}
        for tok in toks:
            tm_id = tok.pop(0)
            self.Testfunctions[tm_id] = {}
            if "testfunction_description" in tok[0] and "testfunction_parameters" in tok[1]:
                self.Testfunctions[tm_id]["testfunction_description"] = tok[0][1]
                self.Testfunctions[tm_id]["testfunction_parameters"] = tok[1][1]
            elif "testfunction_description" in tok[1] and "testfunction_parameters" in tok[0]:
                self.Testfunctions[tm_id]["testfunction_description"] = tok[1][1]
                self.Testfunctions[tm_id]["testfunction_parameters"] = tok[0][1]
    def __str__(self):
        rstr = self.section_name + "\n"
        for tm_id in self.Testfunctions:
            rstr += tm_id + ":\n"
            for k,v in self.Testfunctions[tm_id].iteritems():
                rstr += "  " + k + " = \"" + v + "\";\n"
        rstr += EndStr
        return rstr

TestfunctionSection.setParseAction(ParseTestfunctionSection)

# -------------------------------------------------------------------------------------------
# BEGIN TestmethodParameterSection
# -------------------------------------------------------------------------------------------

# TestmethodParameter = ((Identifier)[bind(&StartTestmethod)(construct_<string>(arg1, arg2))] >> ch_p(':') >>
#                       *((QuotedString[TestmethodParameter.name = arg1] >> '=' >> QuotedString[TestmethodParameter.value = arg1])
#                       [bind(&AddTestmethodParameter)(TestmethodParameter.name, TestmethodParameter.value)] >> ';'))
#                       [bind(&SetTestmethodParameters)()];
TestmethodParameter = pp.Group(Identifier + COLON + pp.ZeroOrMore(pp.Group(QuotedString + EQ + QuotedString + SEMI)))

# UTMTestmethodParameters = *(TestmethodParameter);
UTMTestmethodParameters = pp.ZeroOrMore(TestmethodParameter)

# TestmethodParameterSection = str_p("testmethodparameters")[Start.isUTMBased = true]
#     #if NOUTM
#         >> Error
#     #else
#         >> UTMTestmethodParameters
#         >> End
#     #endif
#     ;
TestmethodParameterSection = (pp.Keyword("testmethodparameters").suppress() + UTMTestmethodParameters + End)("TestmethodParameterSection")

class ParseTestmethodParameterSection(object):
    def __init__(self,toks):
        global isUTMBased
        isUTMBased = True
        self.section_name = "testmethodparameters"
        self.UTMTestmethodParameters = {}
        for tok in toks:
            self.UTMTestmethodParameters[tok[0]] = {}
            for t in tok[1:]:
                self.UTMTestmethodParameters[tok[0]][t[0]] = t[1]
    def __str__(self):
        rstr = self.section_name + '\n'
        for tm_id in self.UTMTestmethodParameters:
            rstr += tm_id + ':\n'
            for k,v in self.UTMTestmethodParameters[tm_id].iteritems():
                rstr += '  ' + k + ' = ' + v + ';\n'
        rstr += EndStr
        return rstr

TestmethodParameterSection.setParseAction(ParseTestmethodParameterSection)

# -------------------------------------------------------------------------------------------
# BEGIN TestmethodLimitSection
# -------------------------------------------------------------------------------------------

# LowLimitSymbol = ch_p('"') >> (str_p("NA")[TestmethodLimit.loSym = ::xoc::tapi::ZLimitSymbol_DONT_CARE] |
#                                str_p("GT")[TestmethodLimit.loSym = ::xoc::tapi::ZLimitSymbol_GREATER] |
#                                str_p("GE")[TestmethodLimit.loSym = ::xoc::tapi::ZLimitSymbol_GREATER_EQUAL])
#                            >> ch_p('"');
LowLimitSymbol = pp.Combine(pp.Literal('"').suppress() + (pp.Keyword("NA") | pp.Keyword("GT") | pp.Keyword("GE")) + pp.Literal('"').suppress())

# HighLimitSymbol = ch_p('"') >> (str_p("NA")[TestmethodLimit.loSym = ::xoc::tapi::ZLimitSymbol_DONT_CARE] |
#                                 str_p("LT")[TestmethodLimit.loSym = ::xoc::tapi::ZLimitSymbol_LESSER] |
#                                 str_p("LE")[TestmethodLimit.loSym = ::xoc::tapi::ZLimitSymbol_LESSER_EQUAL])
#                             >> ch_p('"');
HighLimitSymbol = pp.Combine(pp.Literal('"').suppress() + (pp.Keyword("NA") | pp.Keyword("LT") | pp.Keyword("LE")) + pp.Literal('"').suppress())

# TestmethodLimit = ((Identifier)[bind(&StartTestmethod)(construct_<string>(arg1, arg2))] >> ch_p(':') >>
#  *(
#    (
#     QuotedString[TestmethodLimit.name = arg1]
#     >> '='
#     >> QuotedString[TestmethodLimit.loVal = arg1] >> ':'
#     >> LowLimitSymbol >> ':'
#     >> QuotedString[TestmethodLimit.hiVal = arg1] >> ':'
#     >> HighLimitSymbol >> ':'
#     >> QuotedString[TestmethodLimit.unit = arg1] >> ':'
#     >> QuotedString[TestmethodLimit.numOffset = arg1] >> ':'
#     >> QuotedString[TestmethodLimit.numInc = arg1] >> ';')
#    [bind(&AddTestmethodLimit)(TestmethodLimit.name,
#                   TestmethodLimit.loVal,
#                   TestmethodLimit.loSym,
#                   TestmethodLimit.hiVal,
#                   TestmethodLimit.hiSym,
#                   TestmethodLimit.unit,
#                   TestmethodLimit.numOffset,
#                   TestmethodLimit.numInc)]
#    )
#  )[bind(&SetTestmethodLimits)()]
#    | Error
# ;
TestmethodLimit = pp.Group(Identifier("StartTestmethod")
                           + COLON + pp.ZeroOrMore((QuotedString("name") + EQ
                                                    + QuotedString("loVal") + COLON
                                                    + LowLimitSymbol("LowLimitSymbol") + COLON
                                                    + QuotedString("hiVal") + COLON
                                                    + HighLimitSymbol("HighLimitSymbol") + COLON
                                                    + QuotedString("unit") + COLON
                                                    + QuotedString("numOffset") + COLON
                                                    + QuotedString("numInc") + SEMI)))

# UTMTestmethodLimits = *(TestmethodLimit);
UTMTestmethodLimits = pp.ZeroOrMore(TestmethodLimit)

# TestmethodLimitSection = str_p("testmethodlimits")[Start.isUTMBased = true, bind(&SetUTMBased)()]
# #if NOUTM
#   >> Error
# #else
#   >> UTMTestmethodLimits
#   >> End
# #endif
# ;
TestmethodLimitSection = (pp.Keyword("testmethodlimits").suppress() + UTMTestmethodLimits + End)("TestmethodLimitSection")

class ParseTestmethodLimitSection(object):
    def __init__(self,toks):
        global isUTMBased
        isUTMBased = True
        self.section_name = "testmethodlimits"
        self.UTMTestmethodLimits = {}
        for tok in toks:
            tm_id = tok["StartTestmethod"]
            if tm_id not in self.UTMTestmethodLimits:
                self.UTMTestmethodLimits[tm_id] = {}
            self.UTMTestmethodLimits[tm_id]["name"] = tok["name"]
            self.UTMTestmethodLimits[tm_id]["loVal"] = tok["loVal"]
            self.UTMTestmethodLimits[tm_id]["LowLimitSymbol"] = tok["LowLimitSymbol"]
            self.UTMTestmethodLimits[tm_id]["hiVal"] = tok["hiVal"]
            self.UTMTestmethodLimits[tm_id]["HighLimitSymbol"] = tok["HighLimitSymbol"]
            self.UTMTestmethodLimits[tm_id]["unit"] = tok["unit"]
            self.UTMTestmethodLimits[tm_id]["numOffset"] = tok["numOffset"]
            self.UTMTestmethodLimits[tm_id]["numInc"] = tok["numInc"]
    def __str__(self):
        rstr = self.section_name + "\n"
        for tm_id in self.UTMTestmethodLimits:
            rstr += tm_id + ":\n  "
            rstr += self.UTMTestmethodLimits[tm_id]["name"] + ' = '
            rstr += self.UTMTestmethodLimits[tm_id]["loVal"] + ':'
            rstr += self.UTMTestmethodLimits[tm_id]["LowLimitSymbol"] + ':'
            rstr += self.UTMTestmethodLimits[tm_id]["hiVal"] + ':'
            rstr += self.UTMTestmethodLimits[tm_id]["HighLimitSymbol"] + ':'
            rstr += self.UTMTestmethodLimits[tm_id]["unit"] + ':'
            rstr += self.UTMTestmethodLimits[tm_id]["numOffset"] + ':'
            rstr += self.UTMTestmethodLimits[tm_id]["numInc"] + ';\n'
        rstr += EndStr
        return rstr
TestmethodLimitSection.setParseAction(ParseTestmethodLimitSection)

# -------------------------------------------------------------------------------------------
# BEGIN TestmethodSection
# -------------------------------------------------------------------------------------------

# UTMTestmethodClass = str_p("testmethod_class") >> '=' >> QuotedString[Testmethod.Class = arg1] >> ';';
UTMTestmethodClass = pp.Keyword("testmethod_class").suppress() + EQ + QuotedString("Class") + SEMI

# TestmethodClass = str_p("testmethod_class") >> '=' >> QuotedString[Testmethod.Class = arg1] >> ';';
TestmethodClass = pp.Keyword("testmethod_class").suppress() + EQ + QuotedString("Class") + SEMI

# TestmethodId = str_p("testmethod_id") >> '=' >> (String[Testmethod.methodId = construct_<string>(arg1, arg2)] |
#                QuotedString[Testmethod.methodId = arg1]) >> ';';
TestmethodId = pp.Keyword("testmethod_id").suppress() + EQ + (String | QuotedString)("methodId") + SEMI

# TestmethodParameters = str_p("testmethod_parameters") >> '=' >> QuotedString[Testmethod.parameter = arg1] >> ';';
TestmethodParameters = pp.Keyword("testmethod_parameters").suppress() + EQ + QuotedString("parameter") + SEMI

# TestmethodLimits = str_p("testmethod_limits") >> '=' >> QuotedString[Testmethod.limits = arg1] >> ';';
TestmethodLimits = pp.Keyword("testmethod_limits").suppress() + EQ + QuotedString("limits") + SEMI

# TestmethodName = str_p("testmethod_name") >> '=' >> QuotedString[Testmethod.name = arg1] >> ';';
TestmethodName = pp.Keyword("testmethod_name").suppress() + EQ + QuotedString("name") + SEMI

# TestmethodDefinition = (TestmethodClass | TestmethodId | TestmethodParameters | TestmethodLimits | TestmethodName ) >> !TestmethodDefinition;
TestmethodDefinition = pp.Forward()
TestmethodDefinition << (TestmethodClass | TestmethodId | TestmethodParameters | TestmethodLimits | TestmethodName) + pp.Optional(TestmethodDefinition)

# Testmethod = ((Identifier)[
#              Testmethod.identifier = construct_<string>(arg1, arg2),
#              Testmethod.Class = "",
#              Testmethod.methodId = "",
#              Testmethod.parameter = "",
#              Testmethod.limits = "",
#              Testmethod.name = ""]
#  >> ':' >>
#  if_p(Start.isUTMBased)
#  [
#   UTMTestmethodClass[bind(&CreateUTMTestmethod)(Testmethod.identifier, Testmethod.Class)]
#   ]
#  .else_p[
#      TestmethodDefinition[bind(&CreateTestmethod)(Testmethod.identifier, Testmethod.Class, Testmethod.methodId, Testmethod.parameter, Testmethod.limits, Testmethod.name)]
#  ]
#  )
# ;
if isUTMBased:
    Testmethod = pp.Group(Identifier("tm_id") + COLON + UTMTestmethodClass)
else:
    Testmethod = pp.Group(Identifier("tm_id") + COLON + TestmethodDefinition)

# Testmethods = *(Testmethod) >> End;
Testmethods = pp.ZeroOrMore(Testmethod) + End

# TestmethodSection = str_p("testmethods") >> Testmethods;
TestmethodSection = (pp.Keyword("testmethods").suppress() + Testmethods)("TestmethodSection")

class ParseTestmethodSection(object):
    def __init__(self,toks):
        self.section_name = "testmethods"
        self.isUTMBased = isUTMBased
        self.Testmethods = {}
        for tok in toks:
            tm_id = tok["tm_id"]
            if tm_id not in self.Testmethods:
                self.Testmethods[tm_id] = {}
                self.Testmethods[tm_id]["Class"] = tok["Class"]
                if not self.isUTMBased:
                    self.Testmethods[tm_id]["methodId"] = tok["methodId"]
                    self.Testmethods[tm_id]["parameter"] = tok["parameter"]
                    self.Testmethods[tm_id]["limits"] = tok["limits"]
                    self.Testmethods[tm_id]["name"] = tok["name"]
    def __str__(self):
        rstr = self.section_name + "\n"
        for tm_id in self.Testmethods:
            rstr += tm_id + ':\n  '
            rstr += 'testmethod_class = ' + self.Testmethods[tm_id]["Class"] + ';\n'
            if not self.isUTMBased:
                rstr += '"testmethod_id = ' + self.Testmethods[tm_id]["methodId"] + ';\n'
                rstr += 'testmethod_parameters = ' + self.Testmethods[tm_id]["parameter"] + ';\n'
                rstr += 'testmethod_limits = ' + self.Testmethods[tm_id]["limits"] + ';\n'
                rstr += 'testmethod_name = ' + self.Testmethods[tm_id]["name"] + ';\n'
        rstr += EndStr
        return rstr
TestmethodSection.setParseAction(ParseTestmethodSection)

# -------------------------------------------------------------------------------------------
# BEGIN UserprocedureSection
# -------------------------------------------------------------------------------------------

# Userprocedure = ((Identifier)[Userprocedure.identifier = construct_<string>(arg1, arg2)] >> ':' >>
#                 str_p("user_procedure") >> '=' >> QuotedString[Userprocedure.commandline = arg1] >> ';')
#                 [bind(&CreateUserprocedure)(Userprocedure.identifier, Userprocedure.commandline)];
Userprocedure = pp.Group(Identifier("tm_id") + COLON + pp.Keyword("user_procedure").suppress() + EQ + QuotedString("commandline") + SEMI)

# Userprocedures = *(Userprocedure) >> End;
Userprocedures = pp.ZeroOrMore(Userprocedure) + End

# UserprocedureSection = str_p("tests") >> Userprocedures;
UserprocedureSection = (pp.Keyword("tests").suppress() + Userprocedures)("UserprocedureSection")

class ParseUserprocedureSection(object):
    def __init__(self,toks):
        self.section_name = "tests"
        self.Userprocedure = {}
        for tok in toks:
            self.Userprocedure[tok[0]] = tok[1]
    def __str__(self):
        rstr = self.section_name + "\n"
        for tm_id in self.Userprocedure:
            rstr += tm_id + ":\n  "
            rstr += "user_procedure = \"" + self.Userprocedure[tm_id] + "\";\n"
        rstr += EndStr
        return rstr

UserprocedureSection.setParseAction(ParseUserprocedureSection)

# -------------------------------------------------------------------------------------------
# BEGIN TestsuiteSection
# -------------------------------------------------------------------------------------------

# TestsuiteName = Identifier >> *ch_p(' ') >> ':';
TestsuiteName = Identifier + COLON

# TestsuiteTest = (str_p("override_testf") >> '=' >> Identifier[bind(&SetTestsuiteTest)(construct_<string>(arg1, arg2))] >>';') |
#                 (str_p("tests") >> '=' >> Identifier[bind(&SetTestsuiteTest)(construct_<string>(arg1, arg2))] >> ';');
TestsuiteTest = pp.Group((pp.Keyword("override_testf") + EQ + Identifier + SEMI) | (pp.Keyword("tests") + EQ + Identifier + SEMI))("TestsuiteTest")

# TestsuiteOverride = str_p("override") >> '=' >> int_p >> ';';
TestsuiteOverride = pp.Group(pp.Keyword("override").suppress() + EQ + integer + SEMI)("TestsuiteOverride")

# TestsuiteTimEquSet = str_p("override_tim_equ_set") >> '=' >> Expression[bind(&SetTestsuiteTimEquSet)(arg1)] >> ';';
TestsuiteTimEquSet = pp.Group(pp.Keyword("override_tim_equ_set").suppress() + EQ + Expression + SEMI)("TestsuiteTimEquSet")

# TestsuiteLevEquSet = str_p("override_lev_equ_set") >> '=' >> Expression[bind(&SetTestsuiteLevEquSet)(arg1)] >> ';';
TestsuiteLevEquSet = pp.Group(pp.Keyword("override_lev_equ_set").suppress() + EQ + Expression + SEMI)("TestsuiteLevEquSet")

# TestsuiteTimSpecSet = str_p("override_tim_spec_set") >> '=' >> Expression[bind(&SetTestsuiteTimSpecSet)(arg1)] >> ';';
TestsuiteTimSpecSet = pp.Group(pp.Keyword("override_tim_spec_set").suppress() + EQ + Expression + SEMI)("TestsuiteTimSpecSet")

# TestsuiteLevSpecSet = str_p("override_lev_spec_set") >> '=' >> Expression[bind(&SetTestsuiteLevSpecSet)(arg1)] >> ';';
TestsuiteLevSpecSet = pp.Group(pp.Keyword("override_lev_spec_set").suppress() + EQ + Expression + SEMI)("TestsuiteLevSpecSet")

# TestsuiteTimSet = str_p("override_timset") >> '=' >> Expression[bind(&SetTestsuiteTimSet)(arg1)] >> ';';
TestsuiteTimSet = pp.Group(pp.Keyword("override_timset").suppress() + EQ + Expression + SEMI)("TestsuiteTimSet")

# TestsuiteLevSet = str_p("override_levset") >> '=' >> Expression[bind(&SetTestsuiteLevSet)(arg1)] >> ';';
TestsuiteLevSet = pp.Group(pp.Keyword("override_levset").suppress() + EQ + Expression + SEMI)("TestsuiteLevSet")

# TestsuiteSequencerLabel = str_p("override_seqlbl") >> '=' >> Expression[bind(&SetTestsuiteSequencerLabel)(arg1)] >> ';';
TestsuiteSequencerLabel = pp.Group(pp.Keyword("override_seqlbl").suppress() + EQ + Expression + SEMI)("TestsuiteSequencerLabel")

# //Ignore this for now, because flag_ui handles the flags
# TestsuiteFlags = str_p("local_flags") >> '=' >> list_p(Identifier[bind(&SetTestsuiteFlag)(construct_<string>(arg1, arg2))], ch_p(',')) >> ';';
TestsuiteFlags = pp.Group(pp.Keyword("local_flags").suppress() + EQ + pp.ZeroOrMore(Identifier + COMMA) + Identifier + SEMI)("TestsuiteFlags")

# SiteControlExpression = (str_p("\"serial:\"")[SiteControlExpression.type = ::xoc::tapi::ZSiteSequenceType_SERIAL] |
#                          str_p("\"parallel:\"")[SiteControlExpression.type = ::xoc::tapi::ZSiteSequenceType_PARALLEL] |
#                         (str_p("\"semiparallel:")[SiteControlExpression.type = ::xoc::tapi::ZSiteSequenceType_SEMIPARALLEL] >>
#                          int_p[bind(&NewSiteControlArgument)(arg1)] >> ':' >> int_p[bind(&NewSiteControlArgument)(arg1)] >> !ch_p(':') >> '"')|
#                         (str_p("\"other:")[SiteControlExpression.type = ::xoc::tapi::ZSiteSequenceType_OTHER] >>
#                          list_p.direct(int_p[bind(&NewSiteControlArgument)(arg1)], ch_p(':')) >> !ch_p(':') >> ch_p('"')))
#                         [bind(&SetTestsuiteSiteControl)(SiteControlExpression.type)];
SiteControlExpression = pp.Combine(pp.Keyword("\"serial:\"") | pp.Keyword("\"parallel:\"") |
                                   (pp.Keyword("\"semiparallel:") + integer + COLON + integer + pp.Optional(COLON) + pp.Literal('"')) |
                                   (pp.Keyword("\"other:") + pp.Optional(integer + COLON) + pp.Optional(COLON) + pp.Literal('"')))

# TestsuiteSiteControl = str_p("site_control")[bind(&ClearSiteControlArguments)()] >> '=' >> SiteControlExpression >> ';';
TestsuiteSiteControl = pp.Group(pp.Keyword("site_control").suppress() + EQ + SiteControlExpression + SEMI)("TestsuiteSiteControl")

# TestsuiteFFCCount = str_p("ffc_on_fail") >> '=' >> int_p[bind(&SetTestsuiteFFCCount)(arg1)] >> ';';
TestsuiteFFCCount = pp.Group(pp.Keyword("ffc_on_fail").suppress() + EQ + integer + SEMI)("TestsuiteFFCCount")

# TestsuiteTestLevel = str_p("test_level") >> '=' >> int_p[bind(&SetTestsuiteTestLevel)(arg1)] >> ';';
TestsuiteTestLevel = pp.Group(pp.Keyword("test_level").suppress() + EQ + integer + SEMI)("TestsuiteTestLevel")

# TestsuiteDPSSet = str_p("override_dpsset") >> '=' >> Expression[bind(&SetTestsuiteDPSSet)(arg1)] >> ';';
TestsuiteDPSSet = pp.Group(pp.Keyword("override_dpsset").suppress() + EQ + Expression + SEMI)("TestsuiteDPSSet")

# TestsuiteTestNumber = str_p("override_test_number") >> '=' >> Expression[bind(&SetTestsuiteTestNumber)(arg1)] >> ';';
TestsuiteTestNumber = pp.Group(pp.Keyword("override_test_number").suppress() + EQ + Expression + SEMI)("TestsuiteTestNumber")

# TestsuiteAnalogSet = str_p("override_anaset") >> '=' >> Expression[bind(&SetTestsuiteAnalogSet)(arg1)] >> ';';
TestsuiteAnalogSet = pp.Group(pp.Keyword("override_anaset").suppress() + EQ + Expression + SEMI)("TestsuiteAnalogSet")

# TestsuiteSiteMatch = str_p("site_match") >> '=' >> int_p[bind(&SetTestsuiteSiteMatch)(arg1)] >> ';';
TestsuiteSiteMatch = pp.Group(pp.Keyword("site_match").suppress() + EQ + integer + SEMI)("TestsuiteSiteMatch")

# TestsuiteWaveformSet = str_p("override_wvfset") >> '=' >> Expression[bind(&SetTestsuiteWaveformSet)(arg1)] >> ';';
TestsuiteWaveformSet = pp.Group(pp.Keyword("override_wvfset").suppress() + EQ + Expression + SEMI)("TestsuiteWaveformSet")

# TestsuiteComment = str_p("comment") >> '=' >> QuotedString[bind(&SetTestsuiteComment)(arg1)] >> ';';
TestsuiteComment = pp.Group(pp.Keyword("comment").suppress() + EQ + QuotedString + SEMI)("TestsuiteComment")

# TestsuiteDefinition = (TestsuiteTest |
#                        TestsuiteOverride |
#                        TestsuiteTimEquSet |
#                        TestsuiteLevEquSet |
#                        TestsuiteTimSpecSet |
#                        TestsuiteLevSpecSet |
#                        TestsuiteTimSet |
#                        TestsuiteLevSet |
#                        TestsuiteSequencerLabel |
#                        TestsuiteFlags |
#                        TestsuiteSiteControl |
#                        TestsuiteFFCCount |
#                        TestsuiteTestLevel |
#                        TestsuiteDPSSet |
#                        TestsuiteTestNumber |
#                        TestsuiteAnalogSet |
#                        TestsuiteSiteMatch |
#                        TestsuiteWaveformSet |
#                        TestsuiteComment |
#                        Error ) >> !TestsuiteDefinition;
TestsuiteDefinition = pp.Forward()
TestsuiteDefinition << (TestsuiteTest |
                        TestsuiteOverride |
                        TestsuiteTimEquSet |
                        TestsuiteLevEquSet |
                        TestsuiteTimSpecSet |
                        TestsuiteLevSpecSet |
                        TestsuiteTimSet |
                        TestsuiteLevSet |
                        TestsuiteSequencerLabel |
                        TestsuiteFlags |
                        TestsuiteSiteControl |
                        TestsuiteFFCCount |
                        TestsuiteTestLevel |
                        TestsuiteDPSSet |
                        TestsuiteTestNumber |
                        TestsuiteAnalogSet |
                        TestsuiteSiteMatch |
                        TestsuiteWaveformSet |
                        TestsuiteComment) + pp.Optional(TestsuiteDefinition)

# Testsuite = (TestsuiteName [bind(&StartTestsuite)(construct_<string>(arg1, arg2-1))]) >> TestsuiteDefinition;
Testsuite = pp.Group(TestsuiteName("TestsuiteName") + TestsuiteDefinition("TestsuiteDefinition"))

# Testsuites = *(Testsuite);
Testsuites = pp.ZeroOrMore(Testsuite)

# TestsuiteSection = str_p("test_suites") >> Testsuites  >> End;
TestsuiteSection = (pp.Keyword("test_suites").suppress() + Testsuites + End)("TestsuiteSection")

def parse_testsuite_def(ts_name,ts_def):
    """
        Used by ParseTestsuiteSection and also ParseSpecialTestsuiteSection
    """
    testsuites = {}
    if ts_name not in testsuites:
        testsuites[ts_name] = {}
    if "TestsuiteTest" in ts_def:
        testsuites[ts_name]["TestsuiteTest"] = {}
        testsuites[ts_name]["TestsuiteTest"][ts_def["TestsuiteTest"][0]] = ts_def["TestsuiteTest"][1]
        testsuites[ts_name]["TestsuiteOverride"] = ts_def["TestsuiteOverride"][0]
    if "TestsuiteTimEquSet" in ts_def:
        testsuites[ts_name]["TestsuiteTimEquSet"] = ts_def["TestsuiteTimEquSet"][0]
    if "TestsuiteLevEquSet" in ts_def:
        testsuites[ts_name]["TestsuiteLevEquSet"] = ts_def["TestsuiteLevEquSet"][0]
    if "TestsuiteTimSpecSet" in ts_def:
        testsuites[ts_name]["TestsuiteTimSpecSet"] = ts_def["TestsuiteTimSpecSet"][0]
    if "TestsuiteLevSpecSet" in ts_def:
        testsuites[ts_name]["TestsuiteLevSpecSet"] = ts_def["TestsuiteLevSpecSet"][0]
    if "TestsuiteTimSet" in ts_def:
        testsuites[ts_name]["TestsuiteTimSet"] = ts_def["TestsuiteTimSet"][0]
    if "TestsuiteLevSet" in ts_def:
        testsuites[ts_name]["TestsuiteLevSet"] = ts_def["TestsuiteLevSet"][0]
    if "TestsuiteSequencerLabel" in ts_def:
        testsuites[ts_name]["TestsuiteSequencerLabel"] = ts_def["TestsuiteSequencerLabel"][0]
    if "TestsuiteFlags" in ts_def:
        testsuites[ts_name]["TestsuiteFlags"] = []
        for flag in ts_def["TestsuiteFlags"]:
            testsuites[ts_name]["TestsuiteFlags"].append(flag)
    if "TestsuiteSiteControl" in ts_def:
        testsuites[ts_name]["TestsuiteSiteControl"] = ts_def["TestsuiteSiteControl"][0]
    if "TestsuiteFFCCount" in ts_def:
        testsuites[ts_name]["TestsuiteFFCCount"] = ts_def["TestsuiteFFCCount"][0]
    if "TestsuiteTestLevel" in ts_def:
        testsuites[ts_name]["TestsuiteTestLevel"] = ts_def["TestsuiteTestLevel"][0]
    if "TestsuiteDPSSet" in ts_def:
        testsuites[ts_name]["TestsuiteDPSSet"] = ts_def["TestsuiteDPSSet"][0]
    if "TestsuiteTestNumber" in ts_def:
        testsuites[ts_name]["TestsuiteTestNumber"] = ts_def["TestsuiteTestNumber"][0]
    if "TestsuiteAnalogSet" in ts_def:
        testsuites[ts_name]["TestsuiteAnalogSet"] = ts_def["TestsuiteAnalogSet"][0]
    if "TestsuiteSiteMatch" in ts_def:
        testsuites[ts_name]["TestsuiteSiteMatch"] = ts_def["TestsuiteSiteMatch"][0]
    if "TestsuiteWaveformSet" in ts_def:
        testsuites[ts_name]["TestsuiteWaveformSet"] = ts_def["TestsuiteWaveformSet"][0]
    if "TestsuiteComment" in ts_def:
        testsuites[ts_name]["TestsuiteComment"] = ts_def["TestsuiteComment"][0]
    return testsuites

def format_testsuite_def(ts_name,testsuites):
    rstr = ''
    if "TestsuiteTest" in testsuites[ts_name]:
        for k,v in testsuites[ts_name]["TestsuiteTest"].iteritems():
            rstr += "  " + k + " = " + v + ";\n"
    if "TestsuiteOverride" in testsuites[ts_name]:
        rstr += "  override = " + testsuites[ts_name]["TestsuiteOverride"] + ";\n"
    if "TestsuiteTimEquSet" in testsuites[ts_name]:
        rstr += "  override_tim_equ_set = " + testsuites[ts_name]["TestsuiteTimEquSet"] + ";\n"
    if "TestsuiteLevEquSet" in testsuites[ts_name]:
        rstr += "  override_lev_equ_set = " + testsuites[ts_name]["TestsuiteLevEquSet"] + ";\n"
    if "TestsuiteTimSpecSet" in testsuites[ts_name]:
        rstr += "  override_tim_spec_set = " + testsuites[ts_name]["TestsuiteTimSpecSet"] + ";\n"
    if "TestsuiteLevSpecSet" in testsuites[ts_name]:
        rstr += "  override_lev_spec_set = " + testsuites[ts_name]["TestsuiteLevSpecSet"] + ";\n"
    if "TestsuiteTimSet" in testsuites[ts_name]:
        rstr += "  override_timset = " + testsuites[ts_name]["TestsuiteTimSet"] + ";\n"
    if "TestsuiteLevSet" in testsuites[ts_name]:
        rstr += "  override_levset = " + testsuites[ts_name]["TestsuiteLevSet"] + ";\n"
    if "TestsuiteSequencerLabel" in testsuites[ts_name]:
        rstr += "  override_seqlbl = " + testsuites[ts_name]["TestsuiteSequencerLabel"] + ";\n"
    if "TestsuiteFlags" in testsuites[ts_name]:
        rstr += "  local_flags = " + ','.join(testsuites[ts_name]["TestsuiteFlags"]) + ";\n"
    if "TestsuiteSiteControl" in testsuites[ts_name]:
        rstr += "  site_control = " + testsuites[ts_name]["TestsuiteSiteControl"] + ";\n"
    if "TestsuiteFFCCount" in testsuites[ts_name]:
        rstr += "  ffc_on_fail = " + testsuites[ts_name]["TestsuiteFFCCount"] + ";\n"
    if "TestsuiteTestLevel" in testsuites[ts_name]:
        rstr += "  test_level = " + testsuites[ts_name]["TestsuiteTestLevel"] + ";\n"
    if "TestsuiteDPSSet" in testsuites[ts_name]:
        rstr += "  override_dpsset = " + testsuites[ts_name]["TestsuiteDPSSet"] + ";\n"
    if "TestsuiteTestNumber" in testsuites[ts_name]:
        rstr += "  override_test_number = " + testsuites[ts_name]["TestsuiteTestNumber"] + ";\n"
    if "TestsuiteAnalogSet" in testsuites[ts_name]:
        rstr += "  override_anaset = " + testsuites[ts_name]["TestsuiteAnalogSet"] + ";\n"
    if "TestsuiteSiteMatch" in testsuites[ts_name]:
        rstr += "  site_match = " + testsuites[ts_name]["TestsuiteSiteMatch"] + ";\n"
    if "TestsuiteWaveformSet" in testsuites[ts_name]:
        rstr += "  override_wvfset = " + testsuites[ts_name]["TestsuiteWaveformSet"] + ";\n"
    if "TestsuiteComment" in testsuites[ts_name]:
        rstr += "  comment = " + testsuites[ts_name]["TestsuiteComment"] + ";\n"
    return rstr

class ParseTestsuiteSection(object):
    def __init__(self,toks):
        self.section_name = "test_suites"
        self.Testsuites = {}
        for tok in toks:
            ts_name = tok["TestsuiteName"][0]
            ts_def = tok["TestsuiteDefinition"]
            self.Testsuites.update(parse_testsuite_def(ts_name,ts_def))
    def __str__(self):
        rstr = self.section_name + "\n"
        for ts_name in self.Testsuites:
            rstr += ts_name + ":\n"
            rstr += format_testsuite_def(ts_name,self.Testsuites)
        rstr += EndStr
        return rstr
TestsuiteSection.setParseAction(ParseTestsuiteSection)

# -------------------------------------------------------------------------------------------
# BEGIN TestflowSection
# -------------------------------------------------------------------------------------------

FlowStatements = pp.Forward()

class Statement(object):
    """
        Super class to contain common methods/data for XXXXStatement classes (children)
    """
    __id = -1 # unique id for each instance of child class
    parent = None
    runCond = ''
    @staticmethod
    def getId():
        Statement.__id += 1
        return Statement.__id
    def setParent(self, parent):
        self.parent = parent
    def setRunCond(self, parentRunCond):
        self.runCond = parentRunCond
    def deleteSelf(self):
        return self.parent.delete(self)
    def nestedNames(self):
        return self.type
    def nestedIdsTypes(self):
        return str(self.id)+'_'+self.type

# RunStatement = (str_p("run") >> ch_p('(') >> Identifier[RunStatement.testsuite = construct_<string>(arg1, arg2)] >> ')' >> ';')
#                [bind(&CreateRunStatement)(RunStatement.testsuite)];
RunStatement = (pp.Keyword("run").suppress() + LPAR + Identifier("testsuite") + RPAR + SEMI)
class ParseRunStatement(Statement):
    def __init__(self,toks):
        self.id = self.getId()
        self.type = 'RunStatement'
        self.testsuite = toks.testsuite
        self.toks = toks
    def __repr__(self):
        return '\nrun(' + self.testsuite + ');'

RunStatement.setParseAction(ParseRunStatement)

# RunAndBranchStatement = (str_p("run_and_branch") >> ch_p('(') >> Identifier[RunAndBranchStatement.testsuite = construct_<string>(arg1, arg2)] >> ')'
#                         >> str_p("then"))[bind(&CreateRunAndBranchStatement)(RunAndBranchStatement.testsuite)] >> str_p("{") [bind(&EnterSubBranch)(0)]
#                         >> FlowStatements >> str_p("}") [bind(&LeaveSubBranch)()] >> !(str_p("else")
#                         >> str_p("{") [bind(&EnterSubBranch)(1)] >> FlowStatements >> str_p("}") [bind(&LeaveSubBranch)()]);
RunAndBranchStatement = pp.Group(pp.Keyword("run_and_branch").suppress() + LPAR + Identifier("testsuite") + RPAR
                                 + pp.Keyword("then").suppress() + LCURL + pp.Group(FlowStatements)("RB_PASS") + RCURL
                                 + pp.Optional(pp.Keyword("else").suppress() + LCURL + pp.Group(FlowStatements)("RB_FAIL") + RCURL))
class ParseRunAndBranchStatement(Statement):
    def __init__(self,toks):
        self.id = self.getId()
        self.type = 'RunAndBranchStatement'
        self.testsuite = toks[0].testsuite
        self.rb_pass = toks[0].RB_PASS[:]
        self.rb_fail = toks[0].RB_FAIL[:]
        self.toks = toks
    def __repr__(self):
        rstr = '\nrun_and_branch(' + self.testsuite + ')\n'
        rstr += 'then\n{\n' + '\n'.join([str(x) for x in self.rb_pass]) + '\n}'
        rstr += '\nelse\n{\n' + '\n'.join([str(x) for x in self.rb_fail]) + '\n}'
        return rstr
    def insert(self,data,branch=True):
        if branch:
            self.rb_pass.insert(data)
        else:
            self.rb_fail.insert(data)
    def setParent(self, parent):
        self.parent = parent
        for elem in self.rb_pass:
            elem.setParent(self)
        for elem in self.rb_fail:
            elem.setParent(self)
    def setRunCond(self, parentRunCond):
        self.runCond = parentRunCond
        for elem in self.rb_pass:
            elem.setRunCond(parentRunCond + " AND PASS(" + self.testsuite + ")")
        for elem in self.rb_fail:
            elem.setRunCond(parentRunCond + " AND FAIL(" + self.testsuite + ")")
    def delete(self, elem):
        try:
            ind = self.rb_fail.index(elem)
            del self.rb_fail[ind]
            return ind
        except IndexError:
            ind = self.rb_pass.index(elem)
            del self.rb_pass[ind]
            return ind
    def nestedNames(self):
        return [self.testsuite ,[x.nestedNames() for x in self.rb_pass],[x.nestedNames() for x in self.rb_fail]]
    def nestedIdsTypes(self):
        return [str(self.id)+'_'+self.type ,[x.nestedIdsTypes() for x in self.rb_pass],[x.nestedIdsTypes() for x in self.rb_fail]]

RunAndBranchStatement.setParseAction(ParseRunAndBranchStatement)

# IfStatement = (str_p("if") >> Expression[IfStatement.condition = arg1] >> str_p("then") )
#               [bind(&CreateIfStatement)(IfStatement.condition)]
#               >> (str_p("{")) [bind(&EnterSubBranch)(0)] >> FlowStatements >> (str_p("}")) [bind(&LeaveSubBranch)()]
#               >> !(str_p("else") >> (str_p("{")) [bind(&EnterSubBranch)(1)] >> FlowStatements >> (str_p("}")) [bind(&LeaveSubBranch)()]);
IfStatement = pp.Group(pp.Keyword("if").suppress() + Expression("condition")
                       + pp.Keyword("then").suppress() + LCURL + pp.Group(FlowStatements)("IF_TRUE") + RCURL
                       + pp.Optional(pp.Keyword("else").suppress() + LCURL + pp.Group(FlowStatements)("IF_FALSE") + RCURL))
class ParseIfStatement(Statement):
    def __init__(self,toks):
        self.id = self.getId()
        self.type = 'IfStatement'
        self.condition = toks[0].condition
        self.if_true = toks[0].IF_TRUE[:]
        self.if_false = toks[0].IF_FALSE[:]
        self.toks = toks
    def __repr__(self):
        rstr = '\nif ' + self.condition + '\n'
        rstr += 'then\n{\n' + '\n'.join([str(x) for x in self.if_true]) + '\n}'
        if len(self.if_false):
            rstr += '\nelse\n{\n' + '\n'.join([str(x) for x in self.if_false]) + '\n}'
        return rstr
    def insert(self,data,branch=True):
        if branch:
            self.if_true.insert(data)
        else:
            self.if_false.insert(data)
    def setParent(self, parent):
        self.parent = parent
        for elem in self.if_true:
            elem.setParent(self)
        for elem in self.if_false:
            elem.setParent(self)
    def setRunCond(self, parentRunCond):
        self.runCond = parentRunCond
        for elem in self.if_true:
            elem.setRunCond(parentRunCond + " AND TRUE(" + self.condition + ")")
        for elem in self.if_false:
            elem.setRunCond(parentRunCond + " AND FALSE(" + self.condition + ")")
    def delete(self, elem):
        try:
            ind = self.if_true.index(elem)
            del self.if_false[ind]
            return ind
        except IndexError:
            ind = self.if_true.index(elem)
            del self.if_false[ind]
            return ind
    def nestedNames(self):
        return [self.condition ,[x.nestedNames() for x in self.if_true],[x.nestedNames() for x in self.if_false]]
    def nestedIdsTypes(self):
        return [str(self.id)+'_'+self.type ,[x.nestedIdsTypes() for x in self.if_true],[x.nestedIdsTypes() for x in self.if_false]]
IfStatement.setParseAction(ParseIfStatement)

# GroupBypass = str_p("groupbypass") >> ',';
GroupBypass = pp.Keyword("groupbypass")("SetGroupBypass") + COMMA

# GroupStatement = str_p("{") [bind(&CreateGroupStatement)(), bind(&EnterSubBranch)(0)]
#                  >> FlowStatements >> str_p("}") [bind(&LeaveSubBranch)()] >> ','
#                  >> (GroupBypass[bind(&SetGroupBypass)()] |
#                 str_p("")[bind(&SetGroupNoBypass)()]) >> (str_p("open")[bind(&SetGroupOpen)()] |
#                 str_p("closed")[bind(&SetGroupClosed)()]) >> ',' >> (QuotedString) [bind(&SetGroupLabel)(arg1)]
#                 >> ',' >> (QuotedString) [bind(&SetGroupDescription)(arg1)];
GroupStatement = pp.Group(LCURL + pp.Group(FlowStatements)("GR_SUB") + RCURL + COMMA + pp.Optional(GroupBypass)
                          + (pp.Keyword("open") | pp.Keyword("closed"))("SetGroupOpen") + COMMA
                          + QuotedString("SetGroupLabel") + COMMA + QuotedString("SetGroupDescription"))
class ParseGroupStatement(Statement):
    def __init__(self,toks):
        self.id = self.getId()
        self.type = 'GroupStatement'
        self.gr_bypass_cond = toks[0].SetGroupBypass
        self.gr_sub = toks[0].GR_SUB[:]
        self.gr_open = toks[0].SetGroupOpen
        self.gr_label = toks[0].SetGroupLabel
        self.gr_desc = toks[0].SetGroupDescription
        self.toks = toks
    def __repr__(self):
        rstr = '\n{\n' + '\n'.join([str(x) for x in self.gr_sub]) + '\n},'
        if len(self.gr_bypass_cond):
            rstr += self.gr_bypass_cond
        rstr += self.gr_open + ',' + self.gr_label + ',' + self.gr_desc
        return rstr
    def setRunCond(self, parentRunCond):
        self.runCond = parentRunCond
        for elem in self.gr_sub:
            elem.setRunCond(parentRunCond + " AND TRUE(" + self.gr_bypass_cond + ")")
    def nestedNames(self):
        return [self.gr_label , [x.nestedNames() for x in self.gr_sub]]
    def nestedIdsTypes(self):
        return [str(self.id)+'_'+self.type , [x.nestedIdsTypes() for x in self.gr_sub]]
GroupStatement.setParseAction(ParseGroupStatement)

# AssignmentStatement = (( TestsuiteFlag[AssignmentStatement.varName = arg1] |  Variable[AssignmentStatement.varName = arg1])
#                       >> '=' >> (Expression[AssignmentStatement.value = arg1] | TestsuiteFlag[AssignmentStatement.value = arg1])
#                       >> ';') [bind(&CreateAssignmentStatement)(AssignmentStatement.varName, AssignmentStatement.value)];
# AssignmentStatement = ((TestsuiteFlag | Variable) + EQ + (Expression | TestsuiteFlag) + SEMI)("AssignmentStatement")
AssignmentStatement = pp.Group((TestsuiteFlag | Variable) + EQtok + (Expression | TestsuiteFlag) + SEMI)
class ParseAssignmentStatement(Statement):
    def __init__(self,toks):
        self.id = self.getId()
        self.type = 'AssignmentStatement'
        self.assignment = '\n' + ' '.join(toks[0]) + ';'
        self.toks = toks
    def __repr__(self):
        return self.assignment
AssignmentStatement.setParseAction(ParseAssignmentStatement)

# OOCRule = !(str_p("oocwarning") >> '=' >> int_p >> int_p >> int_p >> QuotedString) >> !(str_p("oocstop") >> '=' >> int_p >> int_p >> int_p >> QuotedString);
OOCRule = (pp.Group(pp.Optional(pp.Keyword("oocwarning")("oocwarning") + EQ + integer + integer + integer + QuotedString))
           + pp.Group(pp.Optional(pp.Keyword("oocstop")("oocstop") + EQ + integer + integer + integer + QuotedString)))

# Quality = str_p("good") [BinDefinition.quality = true] | str_p("bad")[BinDefinition.quality = false];
Quality = pp.Keyword("good") | pp.Keyword("bad")

# Reprobe = str_p("reprobe") [BinDefinition.reprobe = true] | str_p("noreprobe") [BinDefinition.reprobe = false];
Reprobe = pp.Keyword("reprobe") | pp.Keyword("noreprobe")

# Color = int_p [BinDefinition.color = static_cast_< ::xoc::tapi::ZBinColor >(arg1)]
#     | str_p("black") [BinDefinition.color = ::xoc::tapi::ZBinColor_BLACK]
#     | str_p("white") [BinDefinition.color = ::xoc::tapi::ZBinColor_WHITE]
#     | str_p("red") [BinDefinition.color = ::xoc::tapi::ZBinColor_RED]
#     | str_p("yellow") [BinDefinition.color = ::xoc::tapi::ZBinColor_YELLOW]
#     | str_p("green") [BinDefinition.color = ::xoc::tapi::ZBinColor_GREEN]
#     | str_p("cyan") [BinDefinition.color = ::xoc::tapi::ZBinColor_CYAN]
#     | str_p("blue") [BinDefinition.color = ::xoc::tapi::ZBinColor_BLUE]
#     | str_p("magenta") [BinDefinition.color = ::xoc::tapi::ZBinColor_MAGENTA];
Color = (integer | pp.Keyword("black") | pp.Keyword("white") | pp.Keyword("red") | pp.Keyword("yellow") |
         pp.Keyword("green") | pp.Keyword("cyan") | pp.Keyword("blue") | pp.Keyword("magenta"))

# BinNumber = int_p [BinDefinition.binNumber = arg1];
BinNumber = integer

# Overon = str_p("over_on") [BinDefinition.overon = true] | str_p("not_over_on") [BinDefinition.overon = false];
Overon = pp.Keyword("over_on") | pp.Keyword("not_over_on")

# // the first alternate rule is an old definition format which accepts an OOCcrule
# // as third parameter without using it;
# // that way, syntax compability with older testflows is achieved
#  BinDefinition = (QuotedString [BinDefinition.swBin = arg1, BinDefinition.binNumber = -1] >> ','
#                   >> QuotedString [BinDefinition.swBinDescription = arg1] >> ',' >> !OOCRule >> ',' >> !Quality
#                   >> ','  >> !Reprobe >> ',' >> Color >> ',' >> !BinNumber >> ',' >> !Overon)
#                   [bind(&CreateBin)(BinDefinition.swBin, BinDefinition.swBinDescription, BinDefinition.quality,
#                                     BinDefinition.reprobe, BinDefinition.color, BinDefinition.binNumber, BinDefinition.overon)] |
#                   (QuotedString [BinDefinition.swBin = arg1, BinDefinition.binNumber = -1] >> ','
#                   >> QuotedString [BinDefinition.swBinDescription = arg1] >> ',' >> !Quality >> ',' >> !Reprobe >> ',' >> Color
#                   >> ',' >> !BinNumber >> ',' >> !Overon) [bind(&CreateBin)(BinDefinition.swBin, BinDefinition.swBinDescription,
#                                                                             BinDefinition.quality, BinDefinition.reprobe, BinDefinition.color,
#                                                                             BinDefinition.binNumber, BinDefinition.overon)];
BinDefinition = ((QuotedString("swBin") + COMMA + QuotedString("swBinDescription") + COMMA
                  + pp.Optional(OOCRule)("oocrule") + COMMA + pp.Optional(Quality)("quality") + COMMA
                  + pp.Optional(Reprobe)("reprobe") + COMMA + Color("color") + COMMA
                  + pp.Optional(BinNumber)("binNumber") + COMMA + pp.Optional(Overon)("overon")) |
                 (QuotedString("swBin") + COMMA + QuotedString("swBinDescription") + COMMA
                  + pp.Optional(Quality)("quality") + COMMA + pp.Optional(Reprobe)("reprobe") + COMMA
                  + Color("color") + COMMA + pp.Optional(BinNumber)("binNumber") + COMMA
                  + pp.Optional(Overon)("overon")))

# StopBinStatement = (str_p("stop_bin") >> (BinDefinition("", "", false, false, ::xoc::tapi::ZBinColor_BLACK, -1, false)) >> ';')
#                    [bind(&CreateStopBinStatement)()];
StopBinStatement = pp.Group(pp.Keyword("stop_bin") + BinDefinition("CreateStopBinStatement") + SEMI)
class ParseStopBinStatement(Statement):
    def __init__(self,toks):
        self.id = self.getId()
        self.type = 'StopBinStatement'
        self.swBin = toks[0].swBin
        self.swBinDescription = toks[0].swBinDescription
        self.oocrule = toks[0].oocrule.oocwarning + ' ' + toks[0].oocrule.oocstop
        self.quality = toks[0].quality
        self.reprobe = toks[0].reprobe
        self.color = toks[0].color
        self.binNumber = toks[0].binNumber
        self.overon = toks[0].overon
        self.toks = toks
    def __repr__(self):
        rstr = 'stop_bin ' +  self.swBin + ',' + self.swBinDescription + ','
        rstr += self.oocrule + ','
        rstr += self.quality + ',' + self.reprobe + ',' + self.color + ','
        rstr += self.binNumber + ',' + self.overon + ';'
        return rstr
StopBinStatement.setParseAction(ParseStopBinStatement)

# PrintStatement = (str_p("print") >> '(' >> Expression[PrintStatement.statement = arg1] >> ')' >> ';')
#                  [bind(&CreatePrintStatement)(PrintStatement.statement)];
PrintStatement = pp.Group(pp.Keyword("print") + LPAR + Expression("statement") + RPAR + SEMI)
class ParsePrintStatement(Statement):
    def __init__(self,toks):
        self.id = self.getId()
        self.type = 'PrintStatement'
        self.statement = toks[0].statement
        self.toks = toks
    def __repr__(self):
        rstr = ''
        if len(self.statement):
            rstr += '\nprint("' + self.statement + '");'
        return rstr
PrintStatement.setParseAction(ParsePrintStatement)

# PrintDatalogStatement = (str_p("print_dl") >> '(' >> Expression[PrintDatalogStatement.statement = arg1] >> ')' >> ';')
#                         [bind(&CreatePrintDatalogStatement)(PrintDatalogStatement.statement)];
PrintDatalogStatement = pp.Group(pp.Keyword("print_dl") + LPAR + Expression("statement") + RPAR + SEMI)
class ParsePrintDatalogStatement(Statement):
    def __init__(self,toks):
        self.id = self.getId()
        self.type = 'PrintDatalogStatement'
        self.statement = toks[0].statement
        self.toks = toks
    def __repr__(self):
        rstr = ''
        if len(self.statement):
            rstr += '\nprint_dl("' + self.statement + '");'
        return rstr
PrintDatalogStatement.setParseAction(ParsePrintDatalogStatement)

# SVLRTimingStatement = (str_p("svlr_timing_command") >> '(' >> Expression[SVLRTimingStatement.equSet = arg1] >> ','
#                       >> Expression[SVLRTimingStatement.specSet = arg1] >> ',' >> QuotedString[SVLRTimingStatement.variable = arg1]
#                       >> ',' >> Expression[SVLRTimingStatement.value = arg1] >> ')' >> ';')
#                       [bind(&CreateSVLRTimingStatement)(SVLRTimingStatement.equSet, SVLRTimingStatement.specSet,
#                                                         SVLRTimingStatement.variable, SVLRTimingStatement.value)];
SVLRTimingStatement = pp.Group(pp.Keyword("svlr_timing_command") + LPAR + Expression("equSet") + COMMA + Expression("specSet") + COMMA
                               + QuotedString("variable") + COMMA + Expression("value") + RPAR + SEMI)
class ParseSVLRTimingStatement(Statement):
    def __init__(self,toks):
        self.id = self.getId()
        self.type = 'SVLRTimingStatement'
        self.equSet = toks[0].equSet
        self.specSet = toks[0].specSet
        self.variable = toks[0].variable
        self.value = toks[0].value
        self.toks = toks
    def __repr__(self):
        rstr = '\nsvlr_timing_command(' + self.equSet + ',' + self.specSet + ',' + self.variable + ',' + self.value + ');'
        return rstr
SVLRTimingStatement.setParseAction(ParseSVLRTimingStatement)

# SVLRLevelStatement = (str_p("svlr_level_command") >> '(' >> Expression[SVLRLevelStatement.equSet = arg1] >> ',' >> Expression[SVLRLevelStatement.specSet = arg1]
#                       >> ',' >> QuotedString[SVLRLevelStatement.variable = arg1] >> ',' >> Expression[SVLRLevelStatement.value = arg1] >> ')' >> ';')
#                     [bind(&CreateSVLRLevelStatement)(SVLRLevelStatement.equSet, SVLRLevelStatement.specSet, SVLRLevelStatement.variable, SVLRLevelStatement.value)];
SVLRLevelStatement = pp.Group(pp.Keyword("svlr_level_command") + LPAR + Expression("equSet") + COMMA + Expression("specSet") + COMMA
                              + QuotedString("variable") + COMMA + Expression("value") + RPAR + SEMI)
class ParseSVLRLevelStatement(Statement):
    def __init__(self,toks):
        self.id = self.getId()
        self.type = 'SVLRLevelStatement'
        self.equSet = toks[0].equSet
        self.specSet = toks[0].specSet
        self.variable = toks[0].variable
        self.value = toks[0].value
        self.toks = toks
    def __repr__(self):
        rstr = '\nsvlr_level_command(' + self.equSet + ',' + self.specSet + ',' + self.variable + ',' + self.value + ');'
        return rstr
SVLRLevelStatement.setParseAction(ParseSVLRLevelStatement)

# TestNumLoopInc = str_p("test_number_loop_increment") >> '=' >> Expression[TestNumLoopInc.expression = arg1];
TestNumLoopInc = pp.Keyword("test_number_loop_increment") + EQ + Expression

# WhileStatement = (str_p("while") >> Expression [WhileStatement.condition = arg1, WhileStatement.testnum = construct_<string>("")] >> str_p("do")
#                  >> !(TestNumLoopInc [WhileStatement.testnum = arg1])) [bind(&CreateWhileStatement)(WhileStatement.condition, WhileStatement.testnum)]
#                  >> str_p("{") [bind(&EnterSubBranch)(0)] >> FlowStatements >> str_p("}") [bind(&LeaveSubBranch)()];
WhileStatement = pp.Group((pp.Keyword("while").suppress() + Expression("condition") + pp.Keyword("do").suppress() + pp.Optional(TestNumLoopInc)("testnum"))
                          + LCURL + pp.Group(FlowStatements)("W_TRUE") + RCURL)
class ParseWhileStatement(Statement):
    def __init__(self,toks):
        self.id = self.getId()
        self.type = 'WhileStatement'
        self.condition = toks[0].condition
        self.testnum = ' '.join(toks[0].testnum)
        self.w_true = toks[0].W_TRUE[:]
        self.toks = toks
    def __repr__(self):
        rstr = 'while ' + self.condition + ' do ' + self.testnum + '\n{\n'
        rstr += '\n'.join([str(x) for x in self.w_true]) + '\n}'
        return rstr
    def setRunCond(self, parentRunCond):
        self.runCond = parentRunCond
        for elem in self.w_true:
            elem.setRunCond(parentRunCond + " AND TRUE(" + self.condition + ")")
    def nestedNames(self):
        return [self.condition ,[x.nestedNames() for x in self.w_true]]
    def nestedIdsTypes(self):
        return [str(self.id)+'_'+self.type ,[x.nestedIdsTypes() for x in self.w_true]]
WhileStatement.setParseAction(ParseWhileStatement)

# RepeatStatement = str_p("repeat") [bind(&CreateRepeatStatement)(), bind(&EnterSubBranch)(0)] >> FlowStatements >> str_p("until") [bind(&LeaveSubBranch)()]
#                   >> Expression [bind(&SetRepeatCondition)(arg1)] >> !(TestNumLoopInc [bind(&SetRepeatTestnum)(arg1)]);
RepeatStatement = pp.Group(pp.Keyword("repeat").suppress() + pp.Group(FlowStatements)("RPT_TRUE") + pp.Keyword("until").suppress()
                           + Expression("SetRepeatCondition") + pp.Optional(TestNumLoopInc)("SetRepeatTestnum"))
class ParseRepeatStatement(Statement):
    def __init__(self,toks):
        self.id = self.getId()
        self.type = 'RepeatStatement'
        self.rpt_true = toks[0].RPT_TRUE[:]
        self.condition = toks[0].SetRepeatCondition
        self.testnum = ' '.join(toks[0].SetRepeatTestnum)
    def __repr__(self):
        rstr = 'repeat ' + '\n'.join([str(x) for x in self.rpt_true]) + '\nuntil ' + self.condition + ' ' + self.testnum
        return rstr
    def nestedNames(self):
        return [self.condition ,[x.nestedNames() for x in self.rpt_true]]
    def nestedIdsTypes(self):
        return [str(self.id)+'_'+self.type ,[x.nestedIdsTypes() for x in self.rpt_true]]
RepeatStatement.setParseAction(ParseRepeatStatement)

# ForStatement = (str_p("for")[ForStatement.testnum = construct_<string>("")] >> QualifiedIdentifier[ForStatement.assignVar = arg1]
#                >> '=' >> Expression[ForStatement.assignValue = arg1] >> ';' >> Expression[ForStatement.condition = arg1]
#                >> ';' >> QualifiedIdentifier[ForStatement.incrementVar = arg1] >> '=' >> Expression[ForStatement.incrementValue = arg1]
#                >> ';' >> str_p("do") >> !(TestNumLoopInc [ForStatement.testnum = arg1]))
#                [bind(&CreateForStatement)(ForStatement.assignVar, ForStatement.assignValue, ForStatement.condition, ForStatement.incrementVar,
#                                           ForStatement.incrementValue, ForStatement.testnum)]
#                >> str_p("{") [bind(&EnterSubBranch)(0)] >> FlowStatements >> str_p("}") [bind(&LeaveSubBranch)()];
ForStatement = pp.Group((pp.Keyword("for").suppress() + QualifiedIdentifier("assignVar") + EQ + Expression("assignValue") + SEMI
                         + Expression("condition") + SEMI + QualifiedIdentifier("incrementVar") + EQ + Expression("incrementValue")
                         + SEMI + pp.Keyword("do").suppress() + pp.Optional(TestNumLoopInc)("testnum"))
                        + LCURL + pp.Group(FlowStatements)("FOR_TRUE") + RCURL)
class ParseForStatement(Statement):
    def __init__(self,toks):
        self.id = self.getId()
        self.type = 'ForStatement'
        self.assignVar = toks[0].assignVar
        self.assignValue = toks[0].assignValue
        self.condition = toks[0].condition
        self.incrementVar = toks[0].incrementVar
        self.incrementValue = toks[0].incrementValue
        self.testnum = ' '.join(toks[0].testnum)
        self.for_true = toks[0].FOR_TRUE[:]
    def __repr__(self):
        rstr = 'for "' + self.assignVar + ' = ' + self.assignValue + ';'
        rstr += self.condition + ';' + self.incrementVar + ' = ' + self.incrementValue + '; do\n'
        rstr += self.testnum + '\n{\n' + '\n'.join([str(x) for x in self.for_true]) + '\n}'
        return rstr
    def nestedNames(self):
        return [self.condition ,[x.nestedNames() for x in self.for_true]]
    def nestedIdsTypes(self):
        return [str(self.id)+'_'+self.type ,[x.nestedIdsTypes() for x in self.for_true]]
ForStatement.setParseAction(ParseForStatement)

# MultiBinStatement = str_p("multi_bin")[bind(&CreateMultiBinStatement)()] >> ';';
MultiBinStatement = (pp.Keyword("multi_bin") + SEMI)
class ParseMultiBinStatement(Statement):
    def __init__(self,toks):
        self.id = self.getId()
        self.type = 'MultiBinStatement'
    def __repr__(self):
        return 'multi_bin\n'
MultiBinStatement.setParseAction(ParseMultiBinStatement)

# EmptyStatement = ch_p(';');
EmptyStatement = ';'

# TestflowSection = str_p("test_flow")[bind(&FlowSectionStart)()] >> FlowStatements >> End;
TestflowSection = (pp.Keyword("test_flow").suppress() + FlowStatements + End)("TestflowSection")

# FlowStatement = RunStatement |
#                 RunAndBranchStatement |
#                 GroupStatement |
#                 IfStatement |
#                 AssignmentStatement |
#                 StopBinStatement |
#                 PrintStatement |
#                 PrintDatalogStatement |
#                 SVLRTimingStatement |
#                 SVLRLevelStatement |
#                 WhileStatement |
#                 RepeatStatement |
#                 ForStatement |
#                 MultiBinStatement |
#                 EmptyStatement |
#                 Error;
FlowStatement = (RunStatement("RunStatement") |
                 RunAndBranchStatement("RunAndBranchStatement") |
                 GroupStatement("GroupStatement") |
                 IfStatement("IfStatement") |
                 AssignmentStatement("AssignmentStatement") |
                 StopBinStatement("StopBinStatement") |
                 PrintStatement("PrintStatement") |
                 PrintDatalogStatement("PrintDatalogStatement") |
                 SVLRTimingStatement("SVLRTimingStatement") |
                 SVLRLevelStatement("SVLRLevelStatement") |
                 WhileStatement("WhileStatement") |
                 RepeatStatement("RepeatStatement") |
                 ForStatement("ForStatement") |
                 MultiBinStatement("MultiBinStatement") |
                 EmptyStatement)

# FlowStatements = *(FlowStatement);
FlowStatements << pp.ZeroOrMore(FlowStatement)

# -------------------------------------------------------------------------------------------
# BEGIN SpecialTestsuiteSection
# -------------------------------------------------------------------------------------------

# DownloadTestsuite = (str_p("download")[bind(&StartTestsuite)("download")] >> TestsuiteDefinition >> End) [bind(&SetDownloadSuite)()];
DownloadTestsuite = pp.Group(pp.Keyword("download")("download") + TestsuiteDefinition + End)

# InitTestsuite = (str_p("initialize")[bind(&StartTestsuite)("initialize")] >> TestsuiteDefinition >> End )[bind(&SetInitSuite)()];
InitTestsuite = pp.Group(pp.Keyword("initialize")("initialize") + TestsuiteDefinition + End)

# PauseTestsuite = (str_p("pause")[bind(&StartTestsuite)("pause")] >> TestsuiteDefinition >> End)[bind(&SetPauseSuite)()];
PauseTestsuite = pp.Group(pp.Keyword("pause")("pause") + TestsuiteDefinition + End)

# AbortTestsuite = (str_p("abort")[bind(&StartTestsuite)("abort")] >> TestsuiteDefinition >> End)[bind(&SetAbortSuite)()];
AbortTestsuite = pp.Group(pp.Keyword("abort")("abort") + TestsuiteDefinition + End)

# ResetTestsuite = (str_p("reset")[bind(&StartTestsuite)("reset")] >> TestsuiteDefinition >> End)[bind(&SetResetSuite)()];
ResetTestsuite = pp.Group(pp.Keyword("reset")("reset") + TestsuiteDefinition + End)

# ExitTestsuite = (str_p("exit")[bind(&StartTestsuite)("exit")] >> TestsuiteDefinition >> End)[bind(&SetExitSuite)()];
ExitTestsuite = pp.Group(pp.Keyword("exit")("exit") + TestsuiteDefinition + End)

# DisconnectTestsuite = (str_p("bin_disconnect")[bind(&StartTestsuite)("bin_disconnect")] >> TestsuiteDefinition >> End)[bind(&SetDisconnectSuite)()];
DisconnectTestsuite = pp.Group(pp.Keyword("bin_disconnect")("bin_disconnect") + TestsuiteDefinition + End)

# MultiBinDecisionTestsuite = (str_p("multi_bin_decision")[bind(&StartTestsuite)("multi_bin_decision")] >> TestsuiteDefinition >> End)[bind(&SetMultiBinDecisionSuite)()];
MultiBinDecisionTestsuite = pp.Group(pp.Keyword("multi_bin_decision")("multi_bin_decision") + TestsuiteDefinition + End)

# SpecialTestsuiteSection = DownloadTestsuite| InitTestsuite| PauseTestsuite| AbortTestsuite| ResetTestsuite| ExitTestsuite| DisconnectTestsuite| MultiBinDecisionTestsuite;
# Made this section recursive because TestsuiteDefinition is recursive (otherwise, pyparsing stops after the first element in the OR list)
SpecialTestsuiteSection = pp.Forward()
SpecialTestsuiteSection << (DownloadTestsuite | InitTestsuite | PauseTestsuite | AbortTestsuite |
                            ResetTestsuite | ExitTestsuite | DisconnectTestsuite | MultiBinDecisionTestsuite)("SpecialTestsuiteSection")

class ParseSpecialTestsuiteSection(object):
    def __init__(self,toks):
        self.section_name = ""
        self.SpecialTestsuites = {}
        for tok in toks:
            ts_name = tok.pop(0)
            ts_def = tok
            self.SpecialTestsuites.update(parse_testsuite_def(ts_name,ts_def))
    def __str__(self):
        rstr = ""
        for ts_name in self.SpecialTestsuites:
            rstr += ts_name + "\n"
            rstr += format_testsuite_def(ts_name,self.SpecialTestsuites)
            rstr += EndStr
        return rstr
SpecialTestsuiteSection.setParseAction(ParseSpecialTestsuiteSection)

# -------------------------------------------------------------------------------------------
# BEGIN BinningSection
# -------------------------------------------------------------------------------------------

# OtherwiseBin = (str_p("otherwise bin") >> '= ' >> BinDefinition >> ';')[bind(&CreateOtherwiseBin)()];
OtherwiseBin = (pp.Keyword("otherwise bin")("otherwise") + EQ + BinDefinition + SEMI)

# BinningSection = str_p("binning") >> *(OtherwiseBin| (BinDefinition >> ';')) >> End;
BinningSection = (pp.Keyword("binning").suppress() + pp.ZeroOrMore(pp.Group(OtherwiseBin | (BinDefinition + SEMI))) + End)("BinningSection")

class ParseBinningSection(object):
    def __init__(self,toks):
        self.section_name = "binning"
        self.binning = []
        for tok in toks:
            tempdict = {}
            if "otherwise" in tok:
                tempdict["otherwise"] = True
            else:
                tempdict["otherwise"] = False
            tempdict["swBin"] = tok["swBin"]
            tempdict["swBinDescription"] = tok["swBinDescription"]
            if "oocrule" in tok:
                tempdict["oocrule"] = []
                for rule in tok["oocrule"]:
                    if len(rule):
                        tempdict["oocrule"].append(rule)
            if "quality" in tok:
                tempdict["quality"] = tok["quality"]
            if "reprobe" in tok:
                tempdict["reprobe"] = tok["reprobe"]
            tempdict["color"] = tok["color"]
            if "binNumber" in tok:
                tempdict["binNumber"] = tok["binNumber"]
            if "overon" in tok:
                tempdict["overon"] = tok["overon"]
            self.binning.append(tempdict)
    def __str__(self):
        rstr = self.section_name + "\n"
        for bindef in self.binning:
            if bindef["otherwise"]:
                rstr += "otherwise bin = "
            rstr += bindef["swBin"] + ','
            rstr += bindef["swBinDescription"] + ','
            if "oocrule" in bindef:
                for rule in bindef["oocrule"]:
                    rstr += rule[0] + ' = ' + rule[1] + ' ' + rule[2] + ' ' + rule[3] + ' ' + rule[4] + ' '
            rstr += ','
            if "quality" in bindef:
                rstr += bindef["quality"]
            rstr += ','
            if "reprobe" in bindef:
                rstr += bindef["reprobe"]
            rstr += ','
            rstr += bindef["color"] + ','
            if "binNumber" in bindef:
                rstr += bindef["binNumber"]
            rstr += ','
            if "overon" in bindef:
                rstr += bindef["overon"]
            rstr += ';\n'
        rstr += EndStr
        return rstr
BinningSection.setParseAction(ParseBinningSection)

# -------------------------------------------------------------------------------------------
# BEGIN SetupSection
# -------------------------------------------------------------------------------------------

# ConfigFile = str_p("context_config_file") >> '= ' >> QuotedString [bind(&SetConfigFile)(arg1)] >> ';';
ConfigFile = (pp.Keyword("context_config_file") + EQ + QuotedString + SEMI)

# LevelsFile = str_p("context_levels_file") >> '= ' >> QuotedString [bind(&SetLevelsFile)(arg1)] >> ';';
LevelsFile = (pp.Keyword("context_levels_file") + EQ + QuotedString + SEMI)

# TimingFile = str_p("context_timing_file") >> '= ' >> QuotedString [bind(&SetTimingFile)(arg1)] >> ';';
TimingFile = (pp.Keyword("context_timing_file") + EQ + QuotedString + SEMI)

# VectorFile = str_p("context_vector_file") >> '= ' >> QuotedString [bind(&SetVectorFile)(arg1)] >> ';';
VectorFile = (pp.Keyword("context_vector_file") + EQ + QuotedString + SEMI)

# AttribFile = str_p("context_attrib_file") >> '= ' >> QuotedString [bind(&SetAttribFile)(arg1)] >> ';';
AttribFile = (pp.Keyword("context_attrib_file") + EQ + QuotedString + SEMI)

# ChannelAttribFile = str_p("context_channel_attrib_file") >> '= ' >> QuotedString [bind(&SetChannelAttribFile)(arg1)] >> ';';
ChannelAttribFile = (pp.Keyword("context_channel_attrib_file") + EQ + QuotedString + SEMI)

# MixedSignalFile = str_p("context_mixsgl_file") >> '= ' >> QuotedString [bind(&SetMixedSignalFile)(arg1)] >> ';';
MixedSignalFile = (pp.Keyword("context_mixsgl_file") + EQ + QuotedString + SEMI)

# AnalogControlFile = str_p("context_analog_control_file") >> '= ' >> QuotedString [bind(&SetAnalogControlFile)(arg1)] >> ';';
AnalogControlFile = (pp.Keyword("context_analog_control_file") + EQ + QuotedString + SEMI)

# WaveformFile = str_p("context_waveform_file") >> '= ' >> QuotedString [bind(&SetWaveformFile)(arg1)] >> ';';
WaveformFile = (pp.Keyword("context_waveform_file") + EQ + QuotedString + SEMI)

# RoutingFile = str_p("context_routing_file") >> '= ' >> QuotedString [bind(&SetRoutingFile)(arg1)] >> ';';
RoutingFile = (pp.Keyword("context_routing_file") + EQ + QuotedString + SEMI)

# TestTableFile = str_p("context_testtable_file") >> '= ' >> QuotedString[bind(&SetTestTableFile)(arg1)] >> ';';
TestTableFile = (pp.Keyword("context_testtable_file") + EQ + QuotedString + SEMI)

# Protocols = str_p("context_protocols") >> '= ' >> QuotedString[bind(&SetProtocols)(arg1)] >> ';';
Protocols = (pp.Keyword("context_protocols") + EQ + QuotedString + SEMI)

# SetupFiles = ConfigFile| LevelsFile| TimingFile| VectorFile| AttribFile| ChannelAttribFile| MixedSignalFile| AnalogControlFile| WaveformFile| RoutingFile| TestTableFile| Protocols;
SetupFiles = pp.Group(ConfigFile | LevelsFile | TimingFile | VectorFile | AttribFile | ChannelAttribFile |
                      MixedSignalFile | AnalogControlFile | WaveformFile | RoutingFile | TestTableFile | Protocols)

# SetupSection = str_p("context") >> *(SetupFiles) >> End;
SetupSection = (pp.Keyword("context").suppress() + pp.ZeroOrMore(SetupFiles) + End)("SetupSection")

class ParseSetupSection(object):
    def __init__(self,toks):
        self.section_name = "context"
        self.SetupFiles = {}
        for tok in toks:
            self.SetupFiles[tok[0]] = tok[1]
    def __str__(self):
        rstr = self.section_name + "\n"
        for k,v in self.SetupFiles.iteritems():
            rstr += k + ' = ' + v + ';\n'
        rstr += EndStr
        return rstr

SetupSection.setParseAction(ParseSetupSection)

# -------------------------------------------------------------------------------------------
# BEGIN OOCSection
# -------------------------------------------------------------------------------------------

# OOCSection = str_p("oocrule") >> OOCRule >> End;
OOCSection = (pp.Keyword("oocrule").suppress() + OOCRule + End)("OOCSection")

class ParseOOCSection(object):
    def __init__(self,toks):
        self.section_name = "oocrule"
        self.OOCRule = []
        for tok in toks:
            if len(tok):
                self.OOCRule.append(tok)
    def __str__(self):
        rstr = self.section_name + "\n"
        for rule in self.OOCRule:
            rstr += rule[0] + ' = ' + rule[1] + ' ' + rule[2] + ' ' + rule[3] + ' ' + rule[4] + '\n'
        rstr += EndStr
        return rstr

OOCSection.setParseAction(ParseOOCSection)

# -------------------------------------------------------------------------------------------
# BEGIN HardwareBinSection
# -------------------------------------------------------------------------------------------

# HardBinDescription = (int_p[HardBinDescription.hwBin =  arg1] >> '= ' >> QuotedString[HardBinDescription.description =  arg1] >> ';')[bind(&SetHardBinDescription)(HardBinDescription.hwBin, HardBinDescription.description)];
HardBinDescription = pp.Group(integer + EQ + QuotedString + SEMI)

# HardwareBinSection = str_p("hardware_bin_descriptions") >> *(HardBinDescription) >> End;
HardwareBinSection = (pp.Keyword("hardware_bin_descriptions").suppress() + pp.ZeroOrMore(HardBinDescription) + End)("HardwareBinSection")

class ParseHardwareBinSection(object):
    def __init__(self,toks):
        self.section_name = "hardware_bin_descriptions"
        self.hbin_descriptions = {}
        for tok in toks:
            self.hbin_descriptions[tok[0]] = tok[1]
    def __str__(self):
        rstr = self.section_name + "\n"
        for k,v in self.hbin_descriptions.iteritems():
            rstr += k + ' = ' + v + ';\n'
        rstr += EndStr
        return rstr

HardwareBinSection.setParseAction(ParseHardwareBinSection)

# -------------------------------------------------------------------------------------------
# BEGIN ALL Sections collection
# -------------------------------------------------------------------------------------------

#   Sections =
# (
#  EmptySection
#  | InformationSection
#  | ImplicitDeclarationSection
#  | DeclarationSection
#  | FlagSection
#  | TestfunctionSection
#  | TestmethodParameterSection
#  | TestmethodLimitSection
#  | TestmethodSection
#  | UserprocedureSection
#  | TestsuiteSection
#  | TestflowSection
#  | SpecialTestsuiteSection
#  | BinningSection
#  | SetupSection
#  | OOCSection
#  | HardwareBinSection
#  )
#    >> !Sections
# ;
Sections = pp.Forward()
Sections << pp.ZeroOrMore(EmptySection |
                          InformationSection |
                          ImplicitDeclarationSection |
                          DeclarationSection |
                          FlagSection |
                          TestfunctionSection |
                          TestmethodParameterSection |
                          TestmethodLimitSection |
                          TestmethodSection |
                          UserprocedureSection |
                          TestsuiteSection |
                          TestflowSection |
                          SpecialTestsuiteSection |
                          BinningSection |
                          SetupSection |
                          OOCSection |
                          HardwareBinSection + pp.Optional(Sections))

# Start = OptFileHeader[Start.isUTMBased=false] >> OptRevision >> Sections;
Start = pp.Group(OptFileHeader + OptRevision + Sections)
class ParseStart(object):
    def __init__(self,toks):
        self.toks = toks[0]
        # pass along the objects to higher level for post parsing
        self.OptFileHeader = toks[0].OptFileHeader
        self.OptRevision = toks[0].OptRevision
        self.InformationSection = toks[0].InformationSection
        self.ImplicitDeclarationSection = toks[0].ImplicitDeclarationSection
        self.DeclarationSection = toks[0].DeclarationSection
        self.FlagSection = toks[0].FlagSection
        self.TestmethodParameterSection = toks[0].TestmethodParameterSection
        self.TestmethodLimitSection = toks[0].TestmethodLimitSection
        self.TestmethodSection = toks[0].TestmethodSection
        self.TestfunctionSection = toks[0].TestfunctionSection
        self.UserprocedureSection = toks[0].UserprocedureSection
        self.TestsuiteSection = toks[0].TestsuiteSection
        self.TestflowSection = toks[0].TestflowSection
        self.SpecialTestsuiteSection = toks[0].SpecialTestsuiteSection
        self.BinningSection = toks[0].BinningSection
        self.SetupSection = toks[0].SetupSection
        self.OOCSection = toks[0].OOCSection
        self.HardwareBinSection = toks[0].HardwareBinSection
    def __str__(self):
        return '\n'.join([str(x) for x in self.toks])
    # TODO : have str() for top level all the way down (make sure defined recursively)
Start.setParseAction(ParseStart)


class ParseTestflowSection(Statement):
    def __init__(self,toks):
        self.data = toks[:]
        self.condDict = {}
        self.section_name = "test_flow"
        self.setRunCond('TRUE')
    def __repr__(self):
        rstr = self.section_name + '\n'
        rstr += ''.join([str(x) for x in self.data]) + '\n'
        rstr += EndStr
        return rstr
    def nestedNames(self):
        return ['testflow' , [x.nestedNames() for x in self.data]]
    def nestedIdsTypes(self):
        return ['testflow' , [x.nestedIdsTypes() for x in self.data]]

    # TODO : have methods to post parse the data

TestflowSection.setParseAction(ParseTestflowSection)

def get_section(obj,str,max=1):
    section = None
    for toks,start,stop in obj.scanString(str,max):
        section = toks[start:stop]
    return section

def get_file_contents(infile,strip_comments=True):
        _f = open(infile)
        contents = _f.read()
        _f.close()
        if strip_comments:
            # string comments before parsing
            contents = re.sub(re.compile(r'--.*?\n') ,'' ,contents)
        return contents

class Testflow(object):
    def __init__(self,tf_file,debug=False):
        contents = get_file_contents(tf_file)
        self.tf = Start.parseString(contents,1)[0]


        pprint(self.tf.TestflowSection.nestedIdsTypes())

    def __str__(self):
        return str(self.tf)

    # TODO : write some methods that could be called from the instance

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 1:
        print "usage: (python) TestflowParser.py <input file>"
        exit()
    print '\n\n'
    tf = Testflow(args[0],debug=False)

    # print tf

    # --------------------------------------------------------------
    # TODO : user can access/mutate data in tf
    # --------------------------------------------------------------
    # TODO : user could write tf to file now....  fp = open(args[1]).write(str(tf))
    # --------------------------------------------------------------
