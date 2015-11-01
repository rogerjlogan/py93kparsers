__author__ = 'Roger'

# modified to True if certain sections are found
isUTMBased = False

import pyparsing as pp
import sys
from pprint import *
import re

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

# FROM TestflowParser.cpp: BinaryAdd = str_p("+") | "-"  ;
BinaryAdd = PLUS | MINUS

# FROM TestflowParser.cpp: BinaryMult = str_p("*") | "/"  ;
BinaryMult = MULT | DIV

# FROM TestflowParser.cpp: BinaryRel = str_p("==") |  "!="  | "<="  | ">="  | "<"   | ">";
BinaryRel = EQEQ | NOTEQ | LE | GE | LT | GT

# FROM TestflowParser.cpp: BinaryLogic = str_p("or") | "and" ;
BinaryLogic = pp.Keyword("or") | pp.Keyword("and")

# FROM TestflowParser.cpp: Unary = str_p("!") | "-"  | "not";
Unary = NOT | DASH | Not

# FROM TestflowParser.cpp: BinaryRelTerm = Term >> *(BinaryRel >> BinaryRelTerm);
BinaryRelTerm = pp.Forward()

# FROM TestflowParser.cpp: BinaryLogicTerm = BinaryRelTerm >> *(BinaryLogic >> BinaryRelTerm);
BinaryLogicTerm = BinaryRelTerm + pp.ZeroOrMore(BinaryLogic + BinaryRelTerm)

# FROM TestflowParser.cpp: BinaryMultTerm = BinaryLogicTerm >> *(BinaryMult >> BinaryLogicTerm);
BinaryMultTerm = BinaryLogicTerm + pp.ZeroOrMore(BinaryMult + BinaryLogicTerm)

# FROM TestflowParser.cpp: BinaryAddTerm = BinaryMultTerm >> *(BinaryAdd >> BinaryMultTerm);
BinaryAddTerm = BinaryMultTerm + pp.ZeroOrMore(BinaryAdd + BinaryMultTerm)

# FROM TestflowParser.cpp: Expression = BinaryAddTerm[Expression.expression = construct_<string>(arg1, arg2)];
Expression = pp.Combine(BinaryAddTerm,joinString=' ',adjacent=False)

# FROM TestflowParser.cpp: NumberFunction  = str_p("pass") | "fail" | "has_run" | "has_not_run" | "tf_result" |"tf_pin_result" | "spst_timing" |
# FROM TestflowParser.cpp:                         "spst_level" | "svlr_timing" | "svlr_level" | "wsus" | "bsus" | "lsus" | "tsus"          ;
NumberFunction = (pp.Keyword("pass") | pp.Keyword("fail") | pp.Keyword("has_run") | pp.Keyword("has_not_run") |
                  pp.Keyword("tf_result") | pp.Keyword("tf_pin_result") | pp.Keyword("spst_timing") |
                  pp.Keyword("spst_level") | pp.Keyword("svlr_timing") | pp.Keyword("svlr_level") |
                  pp.Keyword("wsus") | pp.Keyword("bsus") | pp.Keyword("lsus") | pp.Keyword("tsus"))

# FROM TestflowParser.cpp: StringFunction = str_p("burstfirst") | "burstnext";
StringFunction = pp.Keyword("burstfirst") | pp.Keyword("burstnext")

# FROM TestflowParser.cpp: Number = real_p | int_p;
Number = Float | integer

# FROM TestflowParser.cpp: End = str_p("end");
End = (pp.Keyword("end") + pp.ZeroOrMore(DASH)).suppress()

# FROM TestflowParser.cpp: Identifier = lexeme_d[(*((alnum_p | ch_p('_')))) - (str_p("end"))];
Identifier = pp.Word(pp.alphanums + '_')

# FROM TestflowParser.cpp: TestsuiteFlag = ch_p('@') >> (Identifier >> "." >> Identifier)[TestsuiteFlag.varName = construct_<string>(arg1, arg2)];
TestsuiteFlag = ATtok + (Identifier + DOTtok + Identifier)

# FROM TestflowParser.cpp: Variable = str_p("@") >> (Identifier)[Variable.varName = construct_<string>(arg1, arg2)] |
# FROM TestflowParser.cpp:                  "@{" >> (Identifier)[Variable.varName = construct_<string>(arg1, arg2)] >> "}";
Variable = pp.Combine((ATtok + Identifier) | ("@{" + Identifier + "}"))

# FROM TestflowParser.cpp: String = (alnum_p - ch_p('!')) >> *(alnum_p | "_");
String = pp.Combine(pp.Word(pp.alphanums,excludeChars='!') + pp.ZeroOrMore(pp.Word(pp.alphanums) | UNDER))

# FROM TestflowParser.cpp: QuotedString << ch_p('"') >> lexeme_d[(*(lex_escape_ch_p - ch_p('"')))]
# FROM TestflowParser.cpp:                [QuotedString.noQuotes = construct_<string>(arg1, arg2)] >> ch_p('"') >> !QuotedString;
QuotedString = pp.Forward()

QuotedString << pp.Combine(pp.QuotedString(unquoteResults=False, quoteChar='"', escChar='\\',multiline=True) + pp.Optional(QuotedString))

# FROM TestflowParser.cpp: Literal = Number | TestsuiteFlag | Variable | QuotedString | String;
Literal = Number | TestsuiteFlag | Variable | QuotedString | String

# FROM TestflowParser.cpp: Term = "(" >> Expression >> ")" | NumberFunction >>  "(" >> !((Expression) >> *( "," >> (Expression))) >> ")"
# FROM TestflowParser.cpp: | StringFunction >>  "(" >> !((Expression) >> *( "," >> (Expression))) >> ")" | Unary >> Term | Literal;
Term = pp.Forward()
# Term = (LPAR + Expression + RPAR | NumberFunction + LPAR + pp.Optional(Expression + pp.ZeroOrMore(COMMA + Expression))
#         + RPAR | StringFunction + LPAR + pp.Optional(Expression + pp.ZeroOrMore(COMMA + Expression))
#         + RPAR | Unary + Term | Literal)
Term = (LPARtok + Expression + RPARtok | NumberFunction + LPARtok + pp.Optional(Expression + pp.ZeroOrMore(COMMAtok + Expression))
        + RPARtok | StringFunction + LPARtok + pp.Optional(Expression + pp.ZeroOrMore(COMMAtok + Expression))
        + RPARtok | Unary + Term | Literal)

BinaryRelTerm << Term + pp.ZeroOrMore(BinaryRel + BinaryRelTerm)

# FROM TestflowParser.cpp: QualifiedIdentifier = Variable[QualifiedIdentifier.varName = arg1] |
# FROM TestflowParser.cpp:     Identifier[QualifiedIdentifier.varName = construct_<string>(arg1, arg2)];
QualifiedIdentifier = Variable | Identifier

# FROM TestflowParser.cpp: TestsuiteFlag = ch_p('@') >> (Identifier >> "." >> Identifier)[TestsuiteFlag.varName = construct_<string>(arg1, arg2)];
TestsuiteFlag = AT + (Identifier + DOT + Identifier)

# FROM TestflowParser.cpp: Type = str_p("double")[Type.type = ::xoc::tapi::ZTestflowVariableType_DOUBLE] |
# FROM TestflowParser.cpp:      str_p("string")[Type.type = ::xoc::tapi::ZTestflowVariableType_STRING];
Type = pp.Keyword("double") | pp.Keyword("string")

# FROM TestflowParser.cpp: OptFileHeader = !str_p("hp93000,testflow,0.1");
OptFileHeader = (pp.Optional(pp.Keyword("hp93000,testflow,0.1")))("OptFileHeader")

class ParseOptFileHeader(object):
    def __init__(self,toks):
        self.section_name = "OptFileHeader"
        self.header = toks[0]
    def __str__(self):
        return self.header

OptFileHeader.setParseAction(ParseOptFileHeader)

# FROM TestflowParser.cpp: OptRevision = !(str_p("language_revision") >> ch_p('=') >> int_p >> ch_p(';'));
OptRevision = (pp.Optional(pp.Keyword("language_revision")).suppress() + EQ + pp.Word(pp.nums) + SEMI)("OptRevision")

def create_OptRevision(lang):
    return "language_revision" + ' = ' + lang + ';\n'

class ParseOptRevision(object):
    def __init__(self,toks):
        self.section_name = "OptRevision"
        self.language_revision = toks[0]
    def __str__(self):
        return create_OptRevision(self.language_revision)

OptRevision.setParseAction(ParseOptRevision)

# FROM TestflowParser.cpp: EmptySection = ch_p(';');
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

# FROM TestflowParser.cpp: DeviceName = str_p("device_name") >> '=' >> (QuotedString)[bind(&SetDeviceName)(arg1)] >> ';';
DeviceName = pp.Keyword("device_name").suppress() + EQ + QuotedString("SetDeviceName") + SEMI

# FROM TestflowParser.cpp: DeviceRevision = str_p("device_revision") >> '=' >> QuotedString[bind(&SetDeviceRevision)(arg1)] >> ';';
DeviceRevision = pp.Keyword("device_revision").suppress() + EQ + QuotedString("SetDeviceRevision") + SEMI

# FROM TestflowParser.cpp: TestRevision = str_p("test_revision") >> '=' >> QuotedString[bind(&SetTestRevision)(arg1)] >> ';';
TestRevision = pp.Keyword("test_revision").suppress() + EQ + QuotedString("SetTestRevision") + SEMI

# FROM TestflowParser.cpp: Description = str_p("description") >> '=' >> QuotedString[bind(&SetDescription)(arg1)] >> ';';
Description = pp.Keyword("description").suppress() + EQ + QuotedString("SetDescription") + SEMI

# FROM TestflowParser.cpp: Application = str_p("application") >> '=' >> QuotedString[bind(&SetApplication)(arg1)] >> ';';
Application = pp.Keyword("application").suppress() + EQ + QuotedString("SetApplication") + SEMI

# FROM TestflowParser.cpp: Temperature = str_p("temperature") >> '=' >> real_p[bind(&SetTemperature)] >> ';';
Temperature = pp.Keyword("temperature").suppress() + EQ + Float("SetTemperature") + SEMI

# FROM TestflowParser.cpp: InformationElements = *(DeviceName | DeviceRevision | TestRevision | Description | Application | Temperature);
InformationElements = pp.Group(pp.ZeroOrMore(DeviceName | DeviceRevision | TestRevision | Description | Application | Temperature))

# FROM TestflowParser.cpp: InformationSection = str_p("information") >> InformationElements >> End;
InformationSection = (pp.Keyword("information").suppress() + InformationElements + End)("InformationSection")

def create_InformationSection(dev_name='',dev_rev='',test_rev='',descr='',app='',temp=''):
    rstr = 'information\n'
    if len(dev_name):
        rstr += 'device_name = ' + dev_name + ';\n'
    if len(dev_rev):
        rstr += 'device_revision = ' + dev_rev + ';\n'
    if len(test_rev):
        rstr += 'test_revision = ' + test_rev + ';\n'
    if len(descr):
        rstr += 'description = ' + descr + ';\n'
    if len(app):
        rstr += 'application = ' + app + ';\n'
    if len(temp):
        rstr += 'temperature = ' + temp + ';\n'
    rstr += EndStr
    return rstr

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
        return create_InformationSection(self.SetDeviceName,self.SetDeviceRevision,self.SetTestRevision,
                                         self.SetDescription,self.SetApplication,self.SetTemperature)

InformationSection.setParseAction(ParseInformationSection)

# -------------------------------------------------------------------------------------------
# BEGIN ImplicitDeclarationSection
# -------------------------------------------------------------------------------------------

# FROM TestflowParser.cpp: Declaration = (Variable[Declaration.varName = arg1] >> ':' >> Type[Declaration.varType = arg1] >> ';' )
# FROM TestflowParser.cpp:                [bind(&CreateImplicitVariable)(Declaration.varName, Declaration.varType)];
Declaration = pp.Group(Variable + COLON + Type + SEMI)

# FROM TestflowParser.cpp: ImplicitDeclarations = (*Declaration);
ImplicitDeclarations = pp.ZeroOrMore(Declaration)

# FROM TestflowParser.cpp: ImplicitDeclarationSection = str_p("implicit_declarations") >> ImplicitDeclarations >> End;
ImplicitDeclarationSection = (pp.Keyword("implicit_declarations").suppress() + ImplicitDeclarations + End)("ImplicitDeclarationSection")

def create_ImplicitDeclarationSection(declarations):
    rstr = 'implicit_declarations\n'
    for varName,varType in declarations.iteritems():
        rstr += varName + ' : ' + varType + ';\n'
    rstr += EndStr
    return rstr

class ParseImplicitDeclarationSection(object):
    def __init__(self,toks):
        self.section_name = "implicit_declarations"
        self.Declarations = {}
        for tok in toks:
            self.Declarations[tok[0]] = tok[1]
    def __str__(self):
        return create_ImplicitDeclarationSection(self.Declarations)

ImplicitDeclarationSection.setParseAction(ParseImplicitDeclarationSection)

# -------------------------------------------------------------------------------------------
# BEGIN DeclarationSection
# -------------------------------------------------------------------------------------------

# FROM TestflowParser.cpp: variables = (Variable[variables.varName = arg1] >> '=' >> Expression[variables.value = arg1] >> ';')
# FROM TestflowParser.cpp:              [bind(&CreateVariable)(variables.varName, variables.value)];
# variables = (Variable + EQ + Expression + SEMI)
Definition = pp.Group(Variable + EQ + Expression + SEMI)

# FROM TestflowParser.cpp: Declarations = (*variables);
Declarations = pp.ZeroOrMore(Definition)

# FROM TestflowParser.cpp: DeclarationSection = str_p("declarations") >> Declarations >> End;
DeclarationSection = (pp.Keyword("declarations").suppress() + Declarations + End)("DeclarationSection")

def create_DeclarationSection(variables):
    rstr = 'declarations\n'
    for varName,value in variables.iteritems():
        rstr += varName + ' = ' + value + ';\n'
    rstr += EndStr
    return rstr

class ParseDeclarationSection(object):
    def __init__(self,toks):
        self.section_name = "declarations"
        self.variables = {}
        for tok in toks:
            self.variables[tok[0]] = tok[1]
    def __str__(self):
        return create_DeclarationSection(self.variables)

DeclarationSection.setParseAction(ParseDeclarationSection)

# -------------------------------------------------------------------------------------------
# BEGIN FlagSection
# -------------------------------------------------------------------------------------------

# FROM TestflowParser.cpp: SystemFlag = *(alnum_p | ch_p('_')) >> '=' >> *(alnum_p | '-') >> ';';
SystemFlag = pp.Group(pp.Word(pp.alphanums + '_') + EQ + pp.Word(pp.alphanums + '-') + SEMI)

# FROM TestflowParser.cpp: UserFlag = (str_p("user") >> (alpha_p >> *(alnum_p | '_'))[UserFlag.varName = construct_<string>(arg1, arg2)]
# FROM TestflowParser.cpp:            >> '=' >> Expression[UserFlag.value = arg1] >> ';')
# FROM TestflowParser.cpp:            [bind(&CreateUserVariable)(UserFlag.varName, UserFlag.value)];
UserFlag = pp.Group(pp.Keyword("user") + pp.Word(pp.alphas,pp.alphanums + '_') + EQ + Expression + SEMI)

# FROM TestflowParser.cpp: //Systemflags are ignored for now, as they are still handled by the flag_ui
# FROM TestflowParser.cpp: Flags = *(UserFlag | SystemFlag);
Flags = pp.ZeroOrMore(UserFlag | SystemFlag)

# FROM TestflowParser.cpp: FlagSection = str_p("flags") >> Flags >> End;
FlagSection = (pp.Keyword("flags").suppress() + Flags + End)("FlagSection")

def create_FlagSection(user_flags,sys_flags):
    rstr = 'flags\n'
    for varName,value in sys_flags.iteritems():
        rstr += varName + ' = ' + value + ';\n'
    for varName,value in user_flags.iteritems():
        rstr += 'user ' + varName + ' = ' + value + ';\n'
    rstr += EndStr
    return rstr

class ParseFlagSection(object):
    def __init__(self,toks):
        self.section_name = "flags"
        self.UserFlags = {}
        self.SystemFlags = {}
        for tok in toks:
            if len(tok) == 3:
                self.UserFlags[tok[1]] = tok[2]
            elif len(tok) == 2:
                self.SystemFlags[tok[0]] = tok[1]
            else:
                sys.exit("ERROR!!! Unknown element in 'flags' section! Exiting ...")
    def __str__(self):
        return create_FlagSection(self.UserFlags,self.SystemFlags)

FlagSection.setParseAction(ParseFlagSection)

# -------------------------------------------------------------------------------------------
# BEGIN TestfunctionSection
# -------------------------------------------------------------------------------------------

# FROM TestflowParser.cpp: TestfunctionDescription = str_p("testfunction_description") >> '=' >> QuotedString[Testfunction.description = arg1] >> ';';
TestfunctionDescription = pp.Group(pp.Keyword("testfunction_description")("testfunction_description") + EQ + QuotedString + SEMI)

# FROM TestflowParser.cpp: TestfunctionParameter = str_p("testfunction_parameters")  >> '=' >> QuotedString[Testfunction.parameters = arg1] >> ';';
TestfunctionParameter = pp.Group(pp.Keyword("testfunction_parameters")("testfunction_parameters") + EQ + QuotedString + SEMI)

# FROM TestflowParser.cpp: TestfunctionDefinition = ((TestfunctionDescription >> TestfunctionParameter) | (TestfunctionParameter >> TestfunctionDescription));
TestfunctionDefinition = ((TestfunctionDescription + TestfunctionParameter) | (TestfunctionParameter + TestfunctionDescription))

# FROM TestflowParser.cpp: Testfunction = ((Identifier)[Testfunction.identifier = construct_<string>(arg1, arg2)] >> ':'>> TestfunctionDefinition)
# FROM TestflowParser.cpp:                [bind(&CreateTestfunction)(Testfunction.identifier, Testfunction.description, Testfunction.parameters)];
Testfunction = pp.Group(Identifier + COLON + TestfunctionDefinition)

# FROM TestflowParser.cpp: Testfunctions = *(Testfunction) >> End;
Testfunctions = pp.ZeroOrMore(Testfunction) + End

# FROM TestflowParser.cpp: TestfunctionSection = str_p("testfunctions") >> Testfunctions;
TestfunctionSection = (pp.Keyword("testfunctions").suppress() + Testfunctions)("TestfunctionSection")

def create_TestfunctionSection(test_funcs):
    rstr = 'testfunctions\n'
    for tm_id in test_funcs:
        rstr += tm_id + ':\n'
        for k,v in test_funcs[tm_id].iteritems():
            rstr += '  ' + k + ' = ' + v + ';\n'
    rstr += EndStr
    return rstr

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
        return create_TestfunctionSection(self.Testfunctions)

TestfunctionSection.setParseAction(ParseTestfunctionSection)

# -------------------------------------------------------------------------------------------
# BEGIN TestmethodParameterSection
# -------------------------------------------------------------------------------------------

# FROM TestflowParser.cpp: TestmethodParameter = ((Identifier)[bind(&StartTestmethod)(construct_<string>(arg1, arg2))] >> ch_p(':') >>
# FROM TestflowParser.cpp:                       *((QuotedString[TestmethodParameter.name = arg1] >> '=' >> QuotedString[TestmethodParameter.value = arg1])
# FROM TestflowParser.cpp:                       [bind(&AddTestmethodParameter)(TestmethodParameter.name, TestmethodParameter.value)] >> ';'))
# FROM TestflowParser.cpp:                       [bind(&SetTestmethodParameters)()];
TestmethodParameter = pp.Group(Identifier + COLON + pp.ZeroOrMore(pp.Group(QuotedString + EQ + QuotedString + SEMI)))

# FROM TestflowParser.cpp: UTMTestmethodParameters = *(TestmethodParameter);
UTMTestmethodParameters = pp.ZeroOrMore(TestmethodParameter)

# FROM TestflowParser.cpp: TestmethodParameterSection = str_p("testmethodparameters")[Start.isUTMBased = true]
# FROM TestflowParser.cpp:     #if NOUTM
# FROM TestflowParser.cpp:         >> Error
# FROM TestflowParser.cpp:     #else
# FROM TestflowParser.cpp:         >> UTMTestmethodParameters
# FROM TestflowParser.cpp:         >> End
# FROM TestflowParser.cpp:     #endif
# FROM TestflowParser.cpp:     ;
TestmethodParameterSection = (pp.Keyword("testmethodparameters").suppress() + UTMTestmethodParameters + End)("TestmethodParameterSection")

def create_TestmethodParameterSection(utm_tm_params):
    rstr = 'testmethodparameters\n'
    for tm_id in utm_tm_params:
        rstr += tm_id + ':\n'
        for k,v in utm_tm_params[tm_id].iteritems():
            rstr += '  ' + k + ' = ' + v + ';\n'
    rstr += EndStr
    return rstr

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
        return create_TestmethodParameterSection(self.UTMTestmethodParameters)

TestmethodParameterSection.setParseAction(ParseTestmethodParameterSection)

# -------------------------------------------------------------------------------------------
# BEGIN TestmethodLimitSection
# -------------------------------------------------------------------------------------------

# FROM TestflowParser.cpp: LowLimitSymbol = ch_p('"') >> (str_p("NA")[TestmethodLimit.loSym = ::xoc::tapi::ZLimitSymbol_DONT_CARE] |
# FROM TestflowParser.cpp:                                str_p("GT")[TestmethodLimit.loSym = ::xoc::tapi::ZLimitSymbol_GREATER] |
# FROM TestflowParser.cpp:                                str_p("GE")[TestmethodLimit.loSym = ::xoc::tapi::ZLimitSymbol_GREATER_EQUAL])
# FROM TestflowParser.cpp:                            >> ch_p('"');
LowLimitSymbol = pp.Combine(pp.Literal('"') + (pp.Keyword("NA") | pp.Keyword("GT") | pp.Keyword("GE")) + pp.Literal('"'))

# FROM TestflowParser.cpp: HighLimitSymbol = ch_p('"') >> (str_p("NA")[TestmethodLimit.loSym = ::xoc::tapi::ZLimitSymbol_DONT_CARE] |
# FROM TestflowParser.cpp:                                 str_p("LT")[TestmethodLimit.loSym = ::xoc::tapi::ZLimitSymbol_LESSER] |
# FROM TestflowParser.cpp:                                 str_p("LE")[TestmethodLimit.loSym = ::xoc::tapi::ZLimitSymbol_LESSER_EQUAL])
# FROM TestflowParser.cpp:                             >> ch_p('"');
HighLimitSymbol = pp.Combine(pp.Literal('"') + (pp.Keyword("NA") | pp.Keyword("LT") | pp.Keyword("LE")) + pp.Literal('"'))

# FROM TestflowParser.cpp: TestmethodLimit = ((Identifier)[bind(&StartTestmethod)(construct_<string>(arg1, arg2))] >> ch_p(':') >>
# FROM TestflowParser.cpp:  *(
# FROM TestflowParser.cpp:    (
# FROM TestflowParser.cpp:     QuotedString[TestmethodLimit.name = arg1]
# FROM TestflowParser.cpp:     >> '='
# FROM TestflowParser.cpp:     >> QuotedString[TestmethodLimit.loVal = arg1] >> ':'
# FROM TestflowParser.cpp:     >> LowLimitSymbol >> ':'
# FROM TestflowParser.cpp:     >> QuotedString[TestmethodLimit.hiVal = arg1] >> ':'
# FROM TestflowParser.cpp:     >> HighLimitSymbol >> ':'
# FROM TestflowParser.cpp:     >> QuotedString[TestmethodLimit.unit = arg1] >> ':'
# FROM TestflowParser.cpp:     >> QuotedString[TestmethodLimit.numOffset = arg1] >> ':'
# FROM TestflowParser.cpp:     >> QuotedString[TestmethodLimit.numInc = arg1] >> ';')
# FROM TestflowParser.cpp:    [bind(&AddTestmethodLimit)(TestmethodLimit.name,
# FROM TestflowParser.cpp:                   TestmethodLimit.loVal,
# FROM TestflowParser.cpp:                   TestmethodLimit.loSym,
# FROM TestflowParser.cpp:                   TestmethodLimit.hiVal,
# FROM TestflowParser.cpp:                   TestmethodLimit.hiSym,
# FROM TestflowParser.cpp:                   TestmethodLimit.unit,
# FROM TestflowParser.cpp:                   TestmethodLimit.numOffset,
# FROM TestflowParser.cpp:                   TestmethodLimit.numInc)]
# FROM TestflowParser.cpp:    )
# FROM TestflowParser.cpp:  )[bind(&SetTestmethodLimits)()]
# FROM TestflowParser.cpp:    | Error
# FROM TestflowParser.cpp: ;
TestmethodLimit = pp.Group(Identifier("StartTestmethod")
                           + COLON + pp.ZeroOrMore((QuotedString("name") + EQ
                                                    + QuotedString("loVal") + COLON
                                                    + LowLimitSymbol("LowLimitSymbol") + COLON
                                                    + QuotedString("hiVal") + COLON
                                                    + HighLimitSymbol("HighLimitSymbol") + COLON
                                                    + QuotedString("unit") + COLON
                                                    + QuotedString("numOffset") + COLON
                                                    + QuotedString("numInc") + SEMI)))
# FROM TestflowParser.cpp: UTMTestmethodLimits = *(TestmethodLimit);
UTMTestmethodLimits = pp.ZeroOrMore(TestmethodLimit)

# FROM TestflowParser.cpp: TestmethodLimitSection = str_p("testmethodlimits")[Start.isUTMBased = true, bind(&SetUTMBased)()]
# FROM TestflowParser.cpp: #if NOUTM
# FROM TestflowParser.cpp:   >> Error
# FROM TestflowParser.cpp: #else
# FROM TestflowParser.cpp:   >> UTMTestmethodLimits
# FROM TestflowParser.cpp:   >> End
# FROM TestflowParser.cpp: #endif
# FROM TestflowParser.cpp: ;
TestmethodLimitSection = (pp.Keyword("testmethodlimits").suppress() + UTMTestmethodLimits + End)("TestmethodLimitSection")

def create_TestmethodLimitSection(utm_tm_limits):
        rstr = 'testmethodlimits\n'
        for tm_id in utm_tm_limits:
            rstr += tm_id + ':\n  '
            rstr += utm_tm_limits[tm_id]['name'] + ' = '
            rstr += utm_tm_limits[tm_id]['loVal'] + ':'
            rstr += utm_tm_limits[tm_id]['LowLimitSymbol'] + ':'
            rstr += utm_tm_limits[tm_id]['hiVal'] + ':'
            rstr += utm_tm_limits[tm_id]['HighLimitSymbol'] + ':'
            rstr += utm_tm_limits[tm_id]['unit'] + ':'
            rstr += utm_tm_limits[tm_id]['numOffset'] + ':'
            rstr += utm_tm_limits[tm_id]['numInc'] + ';\n'
        rstr += EndStr
        return rstr

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
        return create_TestmethodLimitSection(self.UTMTestmethodLimits)
        
TestmethodLimitSection.setParseAction(ParseTestmethodLimitSection)

# -------------------------------------------------------------------------------------------
# BEGIN TestmethodSection
# -------------------------------------------------------------------------------------------

# FROM TestflowParser.cpp: UTMTestmethodClass = str_p("testmethod_class") >> '=' >> QuotedString[Testmethod.Class = arg1] >> ';';
UTMTestmethodClass = pp.Keyword("testmethod_class").suppress() + EQ + QuotedString("Class") + SEMI

# FROM TestflowParser.cpp: TestmethodClass = str_p("testmethod_class") >> '=' >> QuotedString[Testmethod.Class = arg1] >> ';';
TestmethodClass = pp.Keyword("testmethod_class").suppress() + EQ + QuotedString("Class") + SEMI

# FROM TestflowParser.cpp: TestmethodId = str_p("testmethod_id") >> '=' >> (String[Testmethod.methodId = construct_<string>(arg1, arg2)] |
# FROM TestflowParser.cpp:                QuotedString[Testmethod.methodId = arg1]) >> ';';
TestmethodId = pp.Keyword("testmethod_id").suppress() + EQ + (String | QuotedString)("methodId") + SEMI

# FROM TestflowParser.cpp: TestmethodParameters = str_p("testmethod_parameters") >> '=' >> QuotedString[Testmethod.parameter = arg1] >> ';';
TestmethodParameters = pp.Keyword("testmethod_parameters").suppress() + EQ + QuotedString("parameter") + SEMI

# FROM TestflowParser.cpp: TestmethodLimits = str_p("testmethod_limits") >> '=' >> QuotedString[Testmethod.limits = arg1] >> ';';
TestmethodLimits = pp.Keyword("testmethod_limits").suppress() + EQ + QuotedString("limits") + SEMI

# FROM TestflowParser.cpp: TestmethodName = str_p("testmethod_name") >> '=' >> QuotedString[Testmethod.name = arg1] >> ';';
TestmethodName = pp.Keyword("testmethod_name").suppress() + EQ + QuotedString("name") + SEMI

# FROM TestflowParser.cpp: TestmethodDefinition = (TestmethodClass | TestmethodId | TestmethodParameters | TestmethodLimits | TestmethodName ) >> !TestmethodDefinition;
TestmethodDefinition = pp.Forward()
TestmethodDefinition << (TestmethodClass | TestmethodId | TestmethodParameters | TestmethodLimits | TestmethodName) + pp.Optional(TestmethodDefinition)

# FROM TestflowParser.cpp: Testmethod = ((Identifier)[
# FROM TestflowParser.cpp:              Testmethod.identifier = construct_<string>(arg1, arg2),
# FROM TestflowParser.cpp:              Testmethod.Class = "",
# FROM TestflowParser.cpp:              Testmethod.methodId = "",
# FROM TestflowParser.cpp:              Testmethod.parameter = "",
# FROM TestflowParser.cpp:              Testmethod.limits = "",
# FROM TestflowParser.cpp:              Testmethod.name = ""]
# FROM TestflowParser.cpp:  >> ':' >>
# FROM TestflowParser.cpp:  if_p(Start.isUTMBased)
# FROM TestflowParser.cpp:  [
# FROM TestflowParser.cpp:   UTMTestmethodClass[bind(&CreateUTMTestmethod)(Testmethod.identifier, Testmethod.Class)]
# FROM TestflowParser.cpp:   ]
# FROM TestflowParser.cpp:  .else_p[
# FROM TestflowParser.cpp:      TestmethodDefinition[bind(&CreateTestmethod)(Testmethod.identifier, Testmethod.Class, Testmethod.methodId, Testmethod.parameter, Testmethod.limits, Testmethod.name)]
# FROM TestflowParser.cpp:  ]
# FROM TestflowParser.cpp:  )
# FROM TestflowParser.cpp: ;
if isUTMBased:
    Testmethod = pp.Group(Identifier("tm_id") + COLON + UTMTestmethodClass)
else:
    Testmethod = pp.Group(Identifier("tm_id") + COLON + TestmethodDefinition)

# FROM TestflowParser.cpp: Testmethods = *(Testmethod) >> End;
Testmethods = pp.ZeroOrMore(Testmethod) + End

# FROM TestflowParser.cpp: TestmethodSection = str_p("testmethods") >> Testmethods;
TestmethodSection = (pp.Keyword("testmethods").suppress() + Testmethods)("TestmethodSection")

def create_TestmethodSection(test_methods,utm_based=True):
    rstr = "testmethods\n"
    for tm_id in test_methods:
        rstr += tm_id + ':\n  '
        rstr += 'testmethod_class = ' + test_methods[tm_id]['Class'] + ';\n'
        if not utm_based:
            rstr += 'testmethod_id = ' + test_methods[tm_id]['methodId'] + ';\n'
            rstr += 'testmethod_parameters = ' + test_methods[tm_id]['parameter'] + ';\n'
            rstr += 'testmethod_limits = ' + test_methods[tm_id]['limits'] + ';\n'
            rstr += 'testmethod_name = ' + test_methods[tm_id]['name'] + ';\n'
    rstr += EndStr
    return rstr

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
        return create_TestmethodSection(self.Testmethods)
        
TestmethodSection.setParseAction(ParseTestmethodSection)

# -------------------------------------------------------------------------------------------
# BEGIN UserprocedureSection
# -------------------------------------------------------------------------------------------

# FROM TestflowParser.cpp: Userprocedure = ((Identifier)[Userprocedure.identifier = construct_<string>(arg1, arg2)] >> ':' >>
# FROM TestflowParser.cpp:                 str_p("user_procedure") >> '=' >> QuotedString[Userprocedure.commandline = arg1] >> ';')
# FROM TestflowParser.cpp:                 [bind(&CreateUserprocedure)(Userprocedure.identifier, Userprocedure.commandline)];
Userprocedure = pp.Group(Identifier("tm_id") + COLON + pp.Keyword("user_procedure").suppress() + EQ + QuotedString("commandline") + SEMI)

# FROM TestflowParser.cpp: Userprocedures = *(Userprocedure) >> End;
Userprocedures = pp.ZeroOrMore(Userprocedure) + End

# FROM TestflowParser.cpp: UserprocedureSection = str_p("tests") >> Userprocedures;
UserprocedureSection = (pp.Keyword("tests").suppress() + Userprocedures)("UserprocedureSection")

def create_UserprocedureSection(user_procs):
    rstr = 'tests\n'
    for tm_id in user_procs:
        rstr += tm_id + ':\n  '
        rstr += 'user_procedure = ' + user_procs[tm_id] + ';\n'
    rstr += EndStr
    return rstr
    

class ParseUserprocedureSection(object):
    def __init__(self,toks):
        self.section_name = "tests"
        self.Userprocedures = {}
        for tok in toks:
            self.Userprocedures[tok[0]] = tok[1]
    def __str__(self):
        return create_UserprocedureSection(self.Userprocedures)

UserprocedureSection.setParseAction(ParseUserprocedureSection)

# -------------------------------------------------------------------------------------------
# BEGIN TestsuiteSection
# -------------------------------------------------------------------------------------------

# FROM TestflowParser.cpp: TestsuiteName = Identifier >> *ch_p(' ') >> ':';
TestsuiteName = Identifier + COLON

# FROM TestflowParser.cpp: TestsuiteTest = (str_p("override_testf") >> '=' >> Identifier[bind(&SetTestsuiteTest)(construct_<string>(arg1, arg2))] >>';') |
# FROM TestflowParser.cpp:                 (str_p("tests") >> '=' >> Identifier[bind(&SetTestsuiteTest)(construct_<string>(arg1, arg2))] >> ';');
TestsuiteTest = pp.Group((pp.Keyword("override_testf") + EQ + Identifier + SEMI) | (pp.Keyword("tests") + EQ + Identifier + SEMI))("TestsuiteTest")

# FROM TestflowParser.cpp: TestsuiteOverride = str_p("override") >> '=' >> int_p >> ';';
TestsuiteOverride = pp.Group(pp.Keyword("override").suppress() + EQ + integer + SEMI)("TestsuiteOverride")

# FROM TestflowParser.cpp: TestsuiteTimEquSet = str_p("override_tim_equ_set") >> '=' >> Expression[bind(&SetTestsuiteTimEquSet)(arg1)] >> ';';
TestsuiteTimEquSet = pp.Group(pp.Keyword("override_tim_equ_set").suppress() + EQ + Expression + SEMI)("TestsuiteTimEquSet")

# FROM TestflowParser.cpp: TestsuiteLevEquSet = str_p("override_lev_equ_set") >> '=' >> Expression[bind(&SetTestsuiteLevEquSet)(arg1)] >> ';';
TestsuiteLevEquSet = pp.Group(pp.Keyword("override_lev_equ_set").suppress() + EQ + Expression + SEMI)("TestsuiteLevEquSet")

# FROM TestflowParser.cpp: TestsuiteTimSpecSet = str_p("override_tim_spec_set") >> '=' >> Expression[bind(&SetTestsuiteTimSpecSet)(arg1)] >> ';';
TestsuiteTimSpecSet = pp.Group(pp.Keyword("override_tim_spec_set").suppress() + EQ + Expression + SEMI)("TestsuiteTimSpecSet")

# FROM TestflowParser.cpp: TestsuiteLevSpecSet = str_p("override_lev_spec_set") >> '=' >> Expression[bind(&SetTestsuiteLevSpecSet)(arg1)] >> ';';
TestsuiteLevSpecSet = pp.Group(pp.Keyword("override_lev_spec_set").suppress() + EQ + Expression + SEMI)("TestsuiteLevSpecSet")

# FROM TestflowParser.cpp: TestsuiteTimSet = str_p("override_timset") >> '=' >> Expression[bind(&SetTestsuiteTimSet)(arg1)] >> ';';
TestsuiteTimSet = pp.Group(pp.Keyword("override_timset").suppress() + EQ + Expression + SEMI)("TestsuiteTimSet")

# FROM TestflowParser.cpp: TestsuiteLevSet = str_p("override_levset") >> '=' >> Expression[bind(&SetTestsuiteLevSet)(arg1)] >> ';';
TestsuiteLevSet = pp.Group(pp.Keyword("override_levset").suppress() + EQ + Expression + SEMI)("TestsuiteLevSet")

# FROM TestflowParser.cpp: TestsuiteSequencerLabel = str_p("override_seqlbl") >> '=' >> Expression[bind(&SetTestsuiteSequencerLabel)(arg1)] >> ';';
TestsuiteSequencerLabel = pp.Group(pp.Keyword("override_seqlbl").suppress() + EQ + Expression + SEMI)("TestsuiteSequencerLabel")

# FROM TestflowParser.cpp: //Ignore this for now, because flag_ui handles the flags
# FROM TestflowParser.cpp: TestsuiteFlags = str_p("local_flags") >> '=' >> list_p(Identifier[bind(&SetTestsuiteFlag)(construct_<string>(arg1, arg2))], ch_p(',')) >> ';';
TestsuiteFlags = pp.Group(pp.Keyword("local_flags").suppress() + EQ + pp.ZeroOrMore(Identifier + COMMA) + Identifier + SEMI)("TestsuiteFlags")

# FROM TestflowParser.cpp: SiteControlExpression = (str_p("\"serial:\"")[SiteControlExpression.type = ::xoc::tapi::ZSiteSequenceType_SERIAL] |
# FROM TestflowParser.cpp:                          str_p("\"parallel:\"")[SiteControlExpression.type = ::xoc::tapi::ZSiteSequenceType_PARALLEL] |
# FROM TestflowParser.cpp:                         (str_p("\"semiparallel:")[SiteControlExpression.type = ::xoc::tapi::ZSiteSequenceType_SEMIPARALLEL] >>
# FROM TestflowParser.cpp:                          int_p[bind(&NewSiteControlArgument)(arg1)] >> ':' >> int_p[bind(&NewSiteControlArgument)(arg1)] >> !ch_p(':') >> '"')|
# FROM TestflowParser.cpp:                         (str_p("\"other:")[SiteControlExpression.type = ::xoc::tapi::ZSiteSequenceType_OTHER] >>
# FROM TestflowParser.cpp:                          list_p.direct(int_p[bind(&NewSiteControlArgument)(arg1)], ch_p(':')) >> !ch_p(':') >> ch_p('"')))
# FROM TestflowParser.cpp:                         [bind(&SetTestsuiteSiteControl)(SiteControlExpression.type)];
SiteControlExpression = pp.Combine(pp.Keyword("\"serial:\"") | pp.Keyword("\"parallel:\"") |
                                   (pp.Keyword("\"semiparallel:") + integer + COLON + integer + pp.Optional(COLON) + pp.Literal('"')) |
                                   (pp.Keyword("\"other:") + pp.Optional(integer + COLON) + pp.Optional(COLON) + pp.Literal('"')))

# FROM TestflowParser.cpp: TestsuiteSiteControl = str_p("site_control")[bind(&ClearSiteControlArguments)()] >> '=' >> SiteControlExpression >> ';';
TestsuiteSiteControl = pp.Group(pp.Keyword("site_control").suppress() + EQ + SiteControlExpression + SEMI)("TestsuiteSiteControl")

# FROM TestflowParser.cpp: TestsuiteFFCCount = str_p("ffc_on_fail") >> '=' >> int_p[bind(&SetTestsuiteFFCCount)(arg1)] >> ';';
TestsuiteFFCCount = pp.Group(pp.Keyword("ffc_on_fail").suppress() + EQ + integer + SEMI)("TestsuiteFFCCount")

# FROM TestflowParser.cpp: TestsuiteTestLevel = str_p("test_level") >> '=' >> int_p[bind(&SetTestsuiteTestLevel)(arg1)] >> ';';
TestsuiteTestLevel = pp.Group(pp.Keyword("test_level").suppress() + EQ + integer + SEMI)("TestsuiteTestLevel")

# FROM TestflowParser.cpp: TestsuiteDPSSet = str_p("override_dpsset") >> '=' >> Expression[bind(&SetTestsuiteDPSSet)(arg1)] >> ';';
TestsuiteDPSSet = pp.Group(pp.Keyword("override_dpsset").suppress() + EQ + Expression + SEMI)("TestsuiteDPSSet")

# FROM TestflowParser.cpp: TestsuiteTestNumber = str_p("override_test_number") >> '=' >> Expression[bind(&SetTestsuiteTestNumber)(arg1)] >> ';';
TestsuiteTestNumber = pp.Group(pp.Keyword("override_test_number").suppress() + EQ + Expression + SEMI)("TestsuiteTestNumber")

# FROM TestflowParser.cpp: TestsuiteAnalogSet = str_p("override_anaset") >> '=' >> Expression[bind(&SetTestsuiteAnalogSet)(arg1)] >> ';';
TestsuiteAnalogSet = pp.Group(pp.Keyword("override_anaset").suppress() + EQ + Expression + SEMI)("TestsuiteAnalogSet")

# FROM TestflowParser.cpp: TestsuiteSiteMatch = str_p("site_match") >> '=' >> int_p[bind(&SetTestsuiteSiteMatch)(arg1)] >> ';';
TestsuiteSiteMatch = pp.Group(pp.Keyword("site_match").suppress() + EQ + integer + SEMI)("TestsuiteSiteMatch")

# FROM TestflowParser.cpp: TestsuiteWaveformSet = str_p("override_wvfset") >> '=' >> Expression[bind(&SetTestsuiteWaveformSet)(arg1)] >> ';';
TestsuiteWaveformSet = pp.Group(pp.Keyword("override_wvfset").suppress() + EQ + Expression + SEMI)("TestsuiteWaveformSet")

# FROM TestflowParser.cpp: TestsuiteComment = str_p("comment") >> '=' >> QuotedString[bind(&SetTestsuiteComment)(arg1)] >> ';';
TestsuiteComment = pp.Group(pp.Keyword("comment").suppress() + EQ + QuotedString + SEMI)("TestsuiteComment")

# FROM TestflowParser.cpp: TestsuiteDefinition = (TestsuiteTest |
# FROM TestflowParser.cpp:                        TestsuiteOverride |
# FROM TestflowParser.cpp:                        TestsuiteTimEquSet |
# FROM TestflowParser.cpp:                        TestsuiteLevEquSet |
# FROM TestflowParser.cpp:                        TestsuiteTimSpecSet |
# FROM TestflowParser.cpp:                        TestsuiteLevSpecSet |
# FROM TestflowParser.cpp:                        TestsuiteTimSet |
# FROM TestflowParser.cpp:                        TestsuiteLevSet |
# FROM TestflowParser.cpp:                        TestsuiteSequencerLabel |
# FROM TestflowParser.cpp:                        TestsuiteFlags |
# FROM TestflowParser.cpp:                        TestsuiteSiteControl |
# FROM TestflowParser.cpp:                        TestsuiteFFCCount |
# FROM TestflowParser.cpp:                        TestsuiteTestLevel |
# FROM TestflowParser.cpp:                        TestsuiteDPSSet |
# FROM TestflowParser.cpp:                        TestsuiteTestNumber |
# FROM TestflowParser.cpp:                        TestsuiteAnalogSet |
# FROM TestflowParser.cpp:                        TestsuiteSiteMatch |
# FROM TestflowParser.cpp:                        TestsuiteWaveformSet |
# FROM TestflowParser.cpp:                        TestsuiteComment |
# FROM TestflowParser.cpp:                        Error ) >> !TestsuiteDefinition;
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

# FROM TestflowParser.cpp: Testsuite = (TestsuiteName [bind(&StartTestsuite)(construct_<string>(arg1, arg2-1))]) >> TestsuiteDefinition;
Testsuite = pp.Group(TestsuiteName("TestsuiteName") + TestsuiteDefinition("TestsuiteDefinition"))

# FROM TestflowParser.cpp: Testsuites = *(Testsuite);
Testsuites = pp.ZeroOrMore(Testsuite)

# FROM TestflowParser.cpp: TestsuiteSection = str_p("test_suites") >> Testsuites  >> End;
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

def create_TestsuiteSection(testsuites):
    rstr = "test_suites\n"
    for ts_name in testsuites:
        rstr += ts_name + ":\n"
        rstr += format_testsuite_def(ts_name,testsuites)
    rstr += EndStr
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
        return create_TestsuiteSection(self.Testsuites)

TestsuiteSection.setParseAction(ParseTestsuiteSection)

# -------------------------------------------------------------------------------------------
# BEGIN TestflowSection
# -------------------------------------------------------------------------------------------

FlowStatements = pp.Forward()

class Statement(object):
    """
        Super class to contain common methods/data for XXXXStatement classes (children)
    """
    __id = -1 # unique node_id for each instance of child class
    node_id = -1
    _nodeData = {}
    _nodeMap = []
    testsuites = {}

    @staticmethod
    def getNodeId():
        Statement.__id += 1
        return Statement.__id

    def _nodes(self):
        return self.node_id

# FROM TestflowParser.cpp: RunStatement = (str_p("run") >> ch_p('(') >> Identifier[RunStatement.testsuite = construct_<string>(arg1, arg2)] >> ')' >> ';')
# FROM TestflowParser.cpp:                [bind(&CreateRunStatement)(RunStatement.testsuite)];
RunStatement = (pp.Keyword("run").suppress() + LPAR + Identifier("testsuite") + RPAR + SEMI)

def create_RunStatement(testsuite):
    return 'run(' + testsuite + ');\n'

class ParseRunStatement(Statement):
    def __init__(self,toks):
        self.node_id = self.getNodeId()
        self.type = 'RunStatement'
        self.testsuite = toks.testsuite
        self.toks = toks
        self._nodeData[self.node_id] = {
            'type' : self.type,
            'testsuite' : self.testsuite
        }
        self.testsuites[self.testsuite] = self.node_id
    def __repr__(self):
        return create_RunStatement(self.testsuite)

RunStatement.setParseAction(ParseRunStatement)

# FROM TestflowParser.cpp: RunAndBranchStatement = (str_p("run_and_branch") >> ch_p('(') >> Identifier[RunAndBranchStatement.testsuite = construct_<string>(arg1, arg2)] >> ')'
# FROM TestflowParser.cpp:                         >> str_p("then"))[bind(&CreateRunAndBranchStatement)(RunAndBranchStatement.testsuite)] >> str_p("{") [bind(&EnterSubBranch)(0)]
# FROM TestflowParser.cpp:                         >> FlowStatements >> str_p("}") [bind(&LeaveSubBranch)()] >> !(str_p("else")
# FROM TestflowParser.cpp:                         >> str_p("{") [bind(&EnterSubBranch)(1)] >> FlowStatements >> str_p("}") [bind(&LeaveSubBranch)()]);
RunAndBranchStatement = pp.Group(pp.Keyword("run_and_branch").suppress() + LPAR + Identifier("testsuite") + RPAR
                                 + pp.Keyword("then").suppress() + LCURL + pp.Group(FlowStatements)("RB_PASS") + RCURL
                                 + pp.Optional(pp.Keyword("else").suppress() + LCURL + pp.Group(FlowStatements)("RB_FAIL") + RCURL))

def create_RunAndBranchStatement(testsuite,rb_pass,rb_fail):
    rb_pass_str = '\n'.join([str(x) for x in rb_pass])
    rb_fail_str = '\n'.join([str(x) for x in rb_fail])
    rstr = 'run_and_branch(' + testsuite + ')\n'
    rstr += 'then\n'
    rstr += '{\n'
    if len(rb_pass_str):
        rstr += rb_pass_str + '\n'
    rstr += '}\n'
    rstr += 'else\n'
    rstr += '{\n'
    if len(rb_fail_str):
        rstr += rb_fail_str + '\n'
    rstr += '}\n'
    return rstr

class ParseRunAndBranchStatement(Statement):
    def __init__(self,toks):
        self.node_id = self.getNodeId()
        self.type = 'RunAndBranchStatement'
        self.testsuite = toks[0].testsuite
        self.rb_pass = toks[0].RB_PASS[:]
        self.rb_fail = toks[0].RB_FAIL[:]
        self.toks = toks
        self._nodeData[self.node_id] = {
            'type' : self.type,
            'testsuite' : self.testsuite
        }
        self.testsuites[self.testsuite] = self.node_id
    def __repr__(self):
        return create_RunAndBranchStatement(self.testsuite,self.rb_pass,self.rb_fail)
    def _nodes(self):
        return [self.node_id ,[x._nodes() for x in self.rb_pass],[x._nodes() for x in self.rb_fail]]

RunAndBranchStatement.setParseAction(ParseRunAndBranchStatement)

# FROM TestflowParser.cpp: IfStatement = (str_p("if") >> Expression[IfStatement.condition = arg1] >> str_p("then") )
# FROM TestflowParser.cpp:               [bind(&CreateIfStatement)(IfStatement.condition)]
# FROM TestflowParser.cpp:               >> (str_p("{")) [bind(&EnterSubBranch)(0)] >> FlowStatements >> (str_p("}")) [bind(&LeaveSubBranch)()]
# FROM TestflowParser.cpp:               >> !(str_p("else") >> (str_p("{")) [bind(&EnterSubBranch)(1)] >> FlowStatements >> (str_p("}")) [bind(&LeaveSubBranch)()]);
IfStatement = pp.Group(pp.Keyword("if").suppress() + Expression("condition")
                       + pp.Keyword("then").suppress() + LCURL + pp.Group(FlowStatements)("IF_TRUE") + RCURL
                       + pp.Optional(pp.Keyword("else").suppress() + LCURL + pp.Group(FlowStatements)("IF_FALSE") + RCURL))

def create_IfStatement(condition,if_true,if_false):
    if_true_str = '\n'.join([str(x) for x in if_true]).strip()
    if_false_str = '\n'.join([str(x) for x in if_false]).strip()
    rstr = 'if ' + condition + ' then\n'
    rstr += '{\n'
    rstr += if_true_str + '\n'
    rstr += '}\n'
    if len(if_false_str):
        rstr += 'else\n'
        rstr += '{\n'
        rstr += if_false_str + '\n'
        rstr += '}\n'
    return rstr

class ParseIfStatement(Statement):
    def __init__(self,toks):
        self.node_id = self.getNodeId()
        self.type = 'IfStatement'
        self.condition = toks[0].condition
        self.if_true = toks[0].IF_TRUE[:]
        self.if_false = toks[0].IF_FALSE[:]
        self.toks = toks
        self._nodeData[self.node_id] = {
            'type' : self.type,
            'condition' : self.condition
        }
    def __repr__(self):
        return create_IfStatement(self.condition,self.if_true,self.if_false)
    def _nodes(self):
        return [self.node_id ,[x._nodes() for x in self.if_true],[x._nodes() for x in self.if_false]]
IfStatement.setParseAction(ParseIfStatement)

# FROM TestflowParser.cpp: GroupBypass = str_p("groupbypass") >> ',';
GroupBypass = pp.Keyword("groupbypass")("SetGroupBypass") + COMMA

# FROM TestflowParser.cpp: GroupStatement = str_p("{") [bind(&CreateGroupStatement)(), bind(&EnterSubBranch)(0)]
# FROM TestflowParser.cpp:                  >> FlowStatements >> str_p("}") [bind(&LeaveSubBranch)()] >> ','
# FROM TestflowParser.cpp:                  >> (GroupBypass[bind(&SetGroupBypass)()] |
# FROM TestflowParser.cpp:                 str_p("")[bind(&SetGroupNoBypass)()]) >> (str_p("open")[bind(&SetGroupOpen)()] |
# FROM TestflowParser.cpp:                 str_p("closed")[bind(&SetGroupClosed)()]) >> ',' >> (QuotedString) [bind(&SetGroupLabel)(arg1)]
# FROM TestflowParser.cpp:                 >> ',' >> (QuotedString) [bind(&SetGroupDescription)(arg1)];
GroupStatement = pp.Group(LCURL + pp.Group(FlowStatements)("GR_SUB") + RCURL + COMMA + pp.Optional(GroupBypass)
                          + (pp.Keyword("open") | pp.Keyword("closed"))("SetGroupOpen") + COMMA
                          + QuotedString("SetGroupLabel") + COMMA + QuotedString("SetGroupDescription"))

def create_GroupStatement(gr_sub,gr_open,gr_label,gr_desc,gr_bypass_cond=''):
        gr_sub_str = '\n'.join([str(x) for x in gr_sub]).strip()
        rstr = '{\n'
        rstr += gr_sub_str + '\n'
        rstr += '},'
        if len(gr_bypass_cond):
            rstr += gr_bypass_cond + ','
        rstr += gr_open + ',' + gr_label + ',' + gr_desc + '\n'
        return rstr

class ParseGroupStatement(Statement):
    def __init__(self,toks):
        self.node_id = self.getNodeId()
        self.type = 'GroupStatement'
        self.gr_bypass_cond = toks[0].SetGroupBypass
        self.gr_sub = toks[0].GR_SUB[:]
        self.gr_open = toks[0].SetGroupOpen
        self.gr_label = toks[0].SetGroupLabel
        self.gr_desc = toks[0].SetGroupDescription
        self.toks = toks
        self._nodeData[self.node_id] = {
            'type' : self.type,
            'gr_bypass_cond' : self.gr_bypass_cond,
            'gr_open' : self.gr_open,
            'gr_label' : self.gr_label,
            'gr_desc' : self.gr_desc
        }
    def __repr__(self):
        return create_GroupStatement(self.gr_sub,self.gr_open,self.gr_label,self.gr_desc,self.gr_bypass_cond)
    def _nodes(self):
        return [self.node_id , [x._nodes() for x in self.gr_sub]]
GroupStatement.setParseAction(ParseGroupStatement)

# FROM TestflowParser.cpp: AssignmentStatement = (( TestsuiteFlag[AssignmentStatement.varName = arg1] |  Variable[AssignmentStatement.varName = arg1])
# FROM TestflowParser.cpp:                       >> '=' >> (Expression[AssignmentStatement.value = arg1] | TestsuiteFlag[AssignmentStatement.value = arg1])
# FROM TestflowParser.cpp:                       >> ';') [bind(&CreateAssignmentStatement)(AssignmentStatement.varName, AssignmentStatement.value)];
# AssignmentStatement = ((TestsuiteFlag | Variable) + EQ + (Expression | TestsuiteFlag) + SEMI)("AssignmentStatement")
AssignmentStatement = pp.Group((TestsuiteFlag | Variable) + EQtok + (Expression | TestsuiteFlag) + SEMI)

def create_AssignmentStatement(assignment):
    return assignment + '\n'

class ParseAssignmentStatement(Statement):
    def __init__(self,toks):
        self.node_id = self.getNodeId()
        self.type = 'AssignmentStatement'
        self.assignment = ' '.join(toks[0]) + ';'
        self.toks = toks
        self._nodeData[self.node_id] = {
            'type' : self.type,
            'assignment' : self.assignment
        }
    def __repr__(self):
        return create_AssignmentStatement(self.assignment)

AssignmentStatement.setParseAction(ParseAssignmentStatement)

# FROM TestflowParser.cpp: OOCRule = !(str_p("oocwarning") >> '=' >> int_p >> int_p >> int_p >> QuotedString) >> !(str_p("oocstop") >> '=' >> int_p >> int_p >> int_p >> QuotedString);
OOCRule = (pp.Group(pp.Optional(pp.Keyword("oocwarning")("oocwarning") + EQ + integer + integer + integer + QuotedString))
           + pp.Group(pp.Optional(pp.Keyword("oocstop")("oocstop") + EQ + integer + integer + integer + QuotedString)))

# FROM TestflowParser.cpp: Quality = str_p("good") [BinDefinition.quality = true] | str_p("bad")[BinDefinition.quality = false];
Quality = pp.Keyword("good") | pp.Keyword("bad")

# FROM TestflowParser.cpp: Reprobe = str_p("reprobe") [BinDefinition.reprobe = true] | str_p("noreprobe") [BinDefinition.reprobe = false];
Reprobe = pp.Keyword("reprobe") | pp.Keyword("noreprobe")

# FROM TestflowParser.cpp: Color = int_p [BinDefinition.color = static_cast_< ::xoc::tapi::ZBinColor >(arg1)]
# FROM TestflowParser.cpp:     | str_p("black") [BinDefinition.color = ::xoc::tapi::ZBinColor_BLACK]
# FROM TestflowParser.cpp:     | str_p("white") [BinDefinition.color = ::xoc::tapi::ZBinColor_WHITE]
# FROM TestflowParser.cpp:     | str_p("red") [BinDefinition.color = ::xoc::tapi::ZBinColor_RED]
# FROM TestflowParser.cpp:     | str_p("yellow") [BinDefinition.color = ::xoc::tapi::ZBinColor_YELLOW]
# FROM TestflowParser.cpp:     | str_p("green") [BinDefinition.color = ::xoc::tapi::ZBinColor_GREEN]
# FROM TestflowParser.cpp:     | str_p("cyan") [BinDefinition.color = ::xoc::tapi::ZBinColor_CYAN]
# FROM TestflowParser.cpp:     | str_p("blue") [BinDefinition.color = ::xoc::tapi::ZBinColor_BLUE]
# FROM TestflowParser.cpp:     | str_p("magenta") [BinDefinition.color = ::xoc::tapi::ZBinColor_MAGENTA];
Color = (integer | pp.Keyword("black") | pp.Keyword("white") | pp.Keyword("red") | pp.Keyword("yellow") |
         pp.Keyword("green") | pp.Keyword("cyan") | pp.Keyword("blue") | pp.Keyword("magenta"))

# FROM TestflowParser.cpp: BinNumber = int_p [BinDefinition.binNumber = arg1];
BinNumber = integer

# FROM TestflowParser.cpp: Overon = str_p("over_on") [BinDefinition.overon = true] | str_p("not_over_on") [BinDefinition.overon = false];
Overon = pp.Keyword("over_on") | pp.Keyword("not_over_on")

# FROM TestflowParser.cpp: // the first alternate rule is an old definition format which accepts an OOCcrule
# FROM TestflowParser.cpp: // as third parameter without using it;
# FROM TestflowParser.cpp: // that way, syntax compability with older testflows is achieved
# FROM TestflowParser.cpp:  BinDefinition = (QuotedString [BinDefinition.swBin = arg1, BinDefinition.binNumber = -1] >> ','
# FROM TestflowParser.cpp:                   >> QuotedString [BinDefinition.swBinDescription = arg1] >> ',' >> !OOCRule >> ',' >> !Quality
# FROM TestflowParser.cpp:                   >> ','  >> !Reprobe >> ',' >> Color >> ',' >> !BinNumber >> ',' >> !Overon)
# FROM TestflowParser.cpp:                   [bind(&CreateBin)(BinDefinition.swBin, BinDefinition.swBinDescription, BinDefinition.quality,
# FROM TestflowParser.cpp:                                     BinDefinition.reprobe, BinDefinition.color, BinDefinition.binNumber, BinDefinition.overon)] |
# FROM TestflowParser.cpp:                   (QuotedString [BinDefinition.swBin = arg1, BinDefinition.binNumber = -1] >> ','
# FROM TestflowParser.cpp:                   >> QuotedString [BinDefinition.swBinDescription = arg1] >> ',' >> !Quality >> ',' >> !Reprobe >> ',' >> Color
# FROM TestflowParser.cpp:                   >> ',' >> !BinNumber >> ',' >> !Overon) [bind(&CreateBin)(BinDefinition.swBin, BinDefinition.swBinDescription,
# FROM TestflowParser.cpp:                                                                             BinDefinition.quality, BinDefinition.reprobe, BinDefinition.color,
# FROM TestflowParser.cpp:                                                                             BinDefinition.binNumber, BinDefinition.overon)];
BinDefinition = ((QuotedString("swBin") + COMMA + QuotedString("swBinDescription") + COMMA
                  + pp.Optional(OOCRule)("oocrule") + COMMA + pp.Optional(Quality)("quality") + COMMA
                  + pp.Optional(Reprobe)("reprobe") + COMMA + Color("color") + COMMA
                  + pp.Optional(BinNumber)("binNumber") + COMMA + pp.Optional(Overon)("overon")) |
                 (QuotedString("swBin") + COMMA + QuotedString("swBinDescription") + COMMA
                  + pp.Optional(Quality)("quality") + COMMA + pp.Optional(Reprobe)("reprobe") + COMMA
                  + Color("color") + COMMA + pp.Optional(BinNumber)("binNumber") + COMMA
                  + pp.Optional(Overon)("overon")))

# FROM TestflowParser.cpp: StopBinStatement = (str_p("stop_bin") >> (BinDefinition("", "", false, false, ::xoc::tapi::ZBinColor_BLACK, -1, false)) >> ';')
# FROM TestflowParser.cpp:                    [bind(&CreateStopBinStatement)()];
StopBinStatement = pp.Group(pp.Keyword("stop_bin") + BinDefinition("CreateStopBinStatement") + SEMI)

def create_StopBinStatement(swBin,swBinDescription,oocrule,quality,reprobe,color,binNumber,overon):
    rstr = 'stop_bin ' +  swBin + ',' + swBinDescription + ',' + oocrule + ','
    rstr += quality + ',' + reprobe + ',' + color + ',' + binNumber + ',' + overon + ';'
    return rstr

class ParseStopBinStatement(Statement):
    def __init__(self,toks):
        self.node_id = self.getNodeId()
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
        self._nodeData[self.node_id] = {
            'type' : self.type,
            'swBin' : self.swBin,
            'swBinDescription' : self.swBinDescription,
            'oocrule' : self.oocrule,
            'quality' : self.quality,
            'reprobe' : self.reprobe,
            'binNumber' : self.binNumber,
            'overon' : self.overon
        }
    def __repr__(self):
        return create_StopBinStatement(self.swBin,self.swBinDescription,self.oocrule,self.quality,
                                       self.reprobe,self.color,self.binNumber,self.overon)

StopBinStatement.setParseAction(ParseStopBinStatement)

# FROM TestflowParser.cpp: PrintStatement = (str_p("print") >> '(' >> Expression[PrintStatement.statement = arg1] >> ')' >> ';')
# FROM TestflowParser.cpp:                  [bind(&CreatePrintStatement)(PrintStatement.statement)];
PrintStatement = pp.Group(pp.Keyword("print") + LPAR + Expression("statement") + RPAR + SEMI)

def create_PrintStatement(statement):
    return 'print(' + statement + ');\n'

class ParsePrintStatement(Statement):
    def __init__(self,toks):
        self.node_id = self.getNodeId()
        self.type = 'PrintStatement'
        self.statement = toks[0].statement
        self.toks = toks
        self._nodeData[self.node_id] = {
            'type' : self.type,
            'statement' : self.statement
        }
    def __repr__(self):
        return create_PrintStatement(self.statement)
PrintStatement.setParseAction(ParsePrintStatement)

# FROM TestflowParser.cpp: PrintDatalogStatement = (str_p("print_dl") >> '(' >> Expression[PrintDatalogStatement.statement = arg1] >> ')' >> ';')
# FROM TestflowParser.cpp:                         [bind(&CreatePrintDatalogStatement)(PrintDatalogStatement.statement)];
PrintDatalogStatement = pp.Group(pp.Keyword("print_dl") + LPAR + Expression("statement") + RPAR + SEMI)

def create_PrintDatalogStatement(statement):
    return 'print_dl(' + statement + ');\n'

class ParsePrintDatalogStatement(Statement):
    def __init__(self,toks):
        self.node_id = self.getNodeId()
        self.type = 'PrintDatalogStatement'
        self.statement = toks[0].statement
        self.toks = toks
        self._nodeData[self.node_id] = {
            'type' : self.type,
            'statement' : self.statement
        }
    def __repr__(self):
        return create_PrintDatalogStatement(self.statement)

PrintDatalogStatement.setParseAction(ParsePrintDatalogStatement)

# FROM TestflowParser.cpp: SVLRTimingStatement = (str_p("svlr_timing_command") >> '(' >> Expression[SVLRTimingStatement.equSet = arg1] >> ','
# FROM TestflowParser.cpp:                       >> Expression[SVLRTimingStatement.specSet = arg1] >> ',' >> QuotedString[SVLRTimingStatement.variable = arg1]
# FROM TestflowParser.cpp:                       >> ',' >> Expression[SVLRTimingStatement.value = arg1] >> ')' >> ';')
# FROM TestflowParser.cpp:                       [bind(&CreateSVLRTimingStatement)(SVLRTimingStatement.equSet, SVLRTimingStatement.specSet,
# FROM TestflowParser.cpp:                                                         SVLRTimingStatement.variable, SVLRTimingStatement.value)];
SVLRTimingStatement = pp.Group(pp.Keyword("svlr_timing_command") + LPAR + Expression("equSet") + COMMA + Expression("specSet") + COMMA
                               + QuotedString("variable") + COMMA + Expression("value") + RPAR + SEMI)

def create_SVLRTimingStatement(equSet,specSet,variable,value):
        return 'svlr_timing_command(' + equSet + ',' + specSet + ',' + variable + ',' + value + ');\n'

class ParseSVLRTimingStatement(Statement):
    def __init__(self,toks):
        self.node_id = self.getNodeId()
        self.type = 'SVLRTimingStatement'
        self.equSet = toks[0].equSet
        self.specSet = toks[0].specSet
        self.variable = toks[0].variable
        self.value = toks[0].value
        self.toks = toks
        self._nodeData[self.node_id] = {
            'type' : self.type,
            'equSet' : self.equSet,
            'specSet' : self.specSet,
            'variable' : self.variable,
            'value' : self.value
        }
    def __repr__(self):
        return create_SVLRTimingStatement(self.equSet,self.specSet,self.variable,self.value)

SVLRTimingStatement.setParseAction(ParseSVLRTimingStatement)

# FROM TestflowParser.cpp: SVLRLevelStatement = (str_p("svlr_level_command") >> '(' >> Expression[SVLRLevelStatement.equSet = arg1] >> ',' >> Expression[SVLRLevelStatement.specSet = arg1]
# FROM TestflowParser.cpp:                       >> ',' >> QuotedString[SVLRLevelStatement.variable = arg1] >> ',' >> Expression[SVLRLevelStatement.value = arg1] >> ')' >> ';')
# FROM TestflowParser.cpp:                     [bind(&CreateSVLRLevelStatement)(SVLRLevelStatement.equSet, SVLRLevelStatement.specSet, SVLRLevelStatement.variable, SVLRLevelStatement.value)];
SVLRLevelStatement = pp.Group(pp.Keyword("svlr_level_command") + LPAR + Expression("equSet") + COMMA + Expression("specSet") + COMMA
                              + QuotedString("variable") + COMMA + Expression("value") + RPAR + SEMI)

def create_SVLRLevelStatement(equSet,specSet,variable,value):
        return 'svlr_level_command(' + equSet + ',' + specSet + ',' + variable + ',' + value + ');\n'

class ParseSVLRLevelStatement(Statement):
    def __init__(self,toks):
        self.node_id = self.getNodeId()
        self.type = 'SVLRLevelStatement'
        self.equSet = toks[0].equSet
        self.specSet = toks[0].specSet
        self.variable = toks[0].variable
        self.value = toks[0].value
        self.toks = toks
        self._nodeData[self.node_id] = {
            'type' : self.type,
            'equSet' : self.equSet,
            'specSet' : self.specSet,
            'variable' : self.variable,
            'value' : self.value
        }
    def __repr__(self):
        return create_SVLRLevelStatement(self.equSet,self.specSet,self.variable,self.value)

SVLRLevelStatement.setParseAction(ParseSVLRLevelStatement)

# FROM TestflowParser.cpp: TestNumLoopInc = str_p("test_number_loop_increment") >> '=' >> Expression[TestNumLoopInc.expression = arg1];
TestNumLoopInc = pp.Keyword("test_number_loop_increment") + EQtok + Expression

# FROM TestflowParser.cpp: WhileStatement = (str_p("while") >> Expression [WhileStatement.condition = arg1, WhileStatement.testnum = construct_<string>("")] >> str_p("do")
# FROM TestflowParser.cpp:                  >> !(TestNumLoopInc [WhileStatement.testnum = arg1])) [bind(&CreateWhileStatement)(WhileStatement.condition, WhileStatement.testnum)]
# FROM TestflowParser.cpp:                  >> str_p("{") [bind(&EnterSubBranch)(0)] >> FlowStatements >> str_p("}") [bind(&LeaveSubBranch)()];
WhileStatement = pp.Group((pp.Keyword("while").suppress() + Expression("condition") + pp.Keyword("do").suppress() + pp.Optional(TestNumLoopInc)("testnum"))
                          + LCURL + pp.Group(FlowStatements)("W_TRUE") + RCURL)

def create_WhileStatement(condition,testnum,w_true):
    w_true_str = '\n'.join([str(x) for x in w_true]).strip()
    rstr = 'while ' + condition + ' do\n' + testnum + '\n{\n'
    rstr += w_true_str + '\n}'
    return rstr

class ParseWhileStatement(Statement):
    def __init__(self,toks):
        self.node_id = self.getNodeId()
        self.type = 'WhileStatement'
        self.condition = toks[0].condition
        self.testnum = ' '.join(toks[0].testnum)
        self.w_true = toks[0].W_TRUE[:]
        self.toks = toks
        self._nodeData[self.node_id] = {
            'type' : self.type,
            'condition' : self.condition,
            'testnum' : self.testnum
        }
    def __repr__(self):
        return create_WhileStatement(self.condition,self.testnum,self.w_true)
    def _nodes(self):
        return [self.node_id ,[x._nodes() for x in self.w_true]]

WhileStatement.setParseAction(ParseWhileStatement)

# FROM TestflowParser.cpp: RepeatStatement = str_p("repeat") [bind(&CreateRepeatStatement)(), bind(&EnterSubBranch)(0)] >> FlowStatements >> str_p("until") [bind(&LeaveSubBranch)()]
# FROM TestflowParser.cpp:                   >> Expression [bind(&SetRepeatCondition)(arg1)] >> !(TestNumLoopInc [bind(&SetRepeatTestnum)(arg1)]);
RepeatStatement = pp.Group(pp.Keyword("repeat").suppress() + pp.Group(FlowStatements)("RPT_TRUE") + pp.Keyword("until").suppress()
                           + Expression("SetRepeatCondition") + pp.Optional(TestNumLoopInc)("SetRepeatTestnum"))

def create_RepeatStatement(condition,testnum,rpt_true):
    rpt_true_str = '\n'.join([str(x) for x in rpt_true]).strip() + '\n'
    rstr = 'repeat\n'
    rstr += rpt_true_str + 'until ' + condition + '\n' + testnum
    return rstr

class ParseRepeatStatement(Statement):
    def __init__(self,toks):
        self.node_id = self.getNodeId()
        self.type = 'RepeatStatement'
        self.rpt_true = toks[0].RPT_TRUE[:]
        self.condition = toks[0].SetRepeatCondition
        self.testnum = ' '.join(toks[0].SetRepeatTestnum)
        self._nodeData[self.node_id] = {
            'type' : self.type,
            'condition' : self.condition,
            'testnum' : self.testnum
        }
    def __repr__(self):
        return create_RepeatStatement(self.condition,self.testnum,self.rpt_true)
    def _nodes(self):
        return [self.node_id ,[x._nodes() for x in self.rpt_true]]
RepeatStatement.setParseAction(ParseRepeatStatement)

# FROM TestflowParser.cpp: ForStatement = (str_p("for")[ForStatement.testnum = construct_<string>("")] >> QualifiedIdentifier[ForStatement.assignVar = arg1]
# FROM TestflowParser.cpp:                >> '=' >> Expression[ForStatement.assignValue = arg1] >> ';' >> Expression[ForStatement.condition = arg1]
# FROM TestflowParser.cpp:                >> ';' >> QualifiedIdentifier[ForStatement.incrementVar = arg1] >> '=' >> Expression[ForStatement.incrementValue = arg1]
# FROM TestflowParser.cpp:                >> ';' >> str_p("do") >> !(TestNumLoopInc [ForStatement.testnum = arg1]))
# FROM TestflowParser.cpp:                [bind(&CreateForStatement)(ForStatement.assignVar, ForStatement.assignValue, ForStatement.condition, ForStatement.incrementVar,
# FROM TestflowParser.cpp:                                           ForStatement.incrementValue, ForStatement.testnum)]
# FROM TestflowParser.cpp:                >> str_p("{") [bind(&EnterSubBranch)(0)] >> FlowStatements >> str_p("}") [bind(&LeaveSubBranch)()];
ForStatement = pp.Group((pp.Keyword("for").suppress() + QualifiedIdentifier("assignVar") + EQ + Expression("assignValue") + SEMI
                         + Expression("condition") + SEMI + QualifiedIdentifier("incrementVar") + EQ + Expression("incrementValue")
                         + SEMI + pp.Keyword("do").suppress() + pp.Optional(TestNumLoopInc)("testnum"))
                        + LCURL + pp.Group(FlowStatements)("FOR_TRUE") + RCURL)

def create_ForStatement(assignVar,assignValue,condition,incrementVar,incrementValue,testnum,for_true):
    for_true_str = '\n'.join([str(x) for x in for_true]).strip()
    rstr = 'for ' + assignVar + ' = ' + assignValue + ';'
    rstr += condition + ';' + incrementVar + ' = ' + incrementValue + '; do\n'
    rstr += testnum + '\n{\n' + for_true_str + '\n}'
    return rstr

class ParseForStatement(Statement):
    def __init__(self,toks):
        self.node_id = self.getNodeId()
        self.type = 'ForStatement'
        self.assignVar = toks[0].assignVar
        self.assignValue = toks[0].assignValue
        self.condition = toks[0].condition
        self.incrementVar = toks[0].incrementVar
        self.incrementValue = toks[0].incrementValue
        self.testnum = ' '.join(toks[0].testnum)
        self.for_true = toks[0].FOR_TRUE[:]
        self._nodeData[self.node_id] = {
            'type' : self.type,
            'assignVar' : self.assignVar,
            'condition' : self.condition,
            'incrementVar' : self.incrementVar,
            'incrementValue' : self.incrementValue,
            'testnum' : self.testnum
        }
    def __repr__(self):
        return create_ForStatement(self.assignVar,self.assignValue,self.condition,self.incrementVar,
                                   self.incrementValue,self.testnum,self.for_true)
    def _nodes(self):
        return [self.node_id ,[x._nodes() for x in self.for_true]]
ForStatement.setParseAction(ParseForStatement)

# FROM TestflowParser.cpp: MultiBinStatement = str_p("multi_bin")[bind(&CreateMultiBinStatement)()] >> ';';
MultiBinStatement = (pp.Keyword("multi_bin") + SEMI)

def create_MultiBinStatement():
    return 'multi_bin;\n'

class ParseMultiBinStatement(Statement):
    def __init__(self,toks):
        self.node_id = self.getNodeId()
        self.type = 'MultiBinStatement'
        self._nodeData[self.node_id] = {
            'type' : self.type,
        }
    def __repr__(self):
        return create_MultiBinStatement()

MultiBinStatement.setParseAction(ParseMultiBinStatement)

# FROM TestflowParser.cpp: EmptyStatement = ch_p(';');
EmptyStatement = ';'

# FROM TestflowParser.cpp: TestflowSection = str_p("test_flow")[bind(&FlowSectionStart)()] >> FlowStatements >> End;
TestflowSection = (pp.Keyword("test_flow").suppress() + FlowStatements + End)("TestflowSection")

# FROM TestflowParser.cpp: FlowStatement = RunStatement |
# FROM TestflowParser.cpp:                 RunAndBranchStatement |
# FROM TestflowParser.cpp:                 GroupStatement |
# FROM TestflowParser.cpp:                 IfStatement |
# FROM TestflowParser.cpp:                 AssignmentStatement |
# FROM TestflowParser.cpp:                 StopBinStatement |
# FROM TestflowParser.cpp:                 PrintStatement |
# FROM TestflowParser.cpp:                 PrintDatalogStatement |
# FROM TestflowParser.cpp:                 SVLRTimingStatement |
# FROM TestflowParser.cpp:                 SVLRLevelStatement |
# FROM TestflowParser.cpp:                 WhileStatement |
# FROM TestflowParser.cpp:                 RepeatStatement |
# FROM TestflowParser.cpp:                 ForStatement |
# FROM TestflowParser.cpp:                 MultiBinStatement |
# FROM TestflowParser.cpp:                 EmptyStatement |
# FROM TestflowParser.cpp:                 Error;
FlowStatement = (RunStatement('RunStatement') |
                 RunAndBranchStatement('RunAndBranchStatement') |
                 GroupStatement('GroupStatement') |
                 IfStatement('IfStatement') |
                 AssignmentStatement('AssignmentStatement') |
                 StopBinStatement('StopBinStatement') |
                 PrintStatement('PrintStatement') |
                 PrintDatalogStatement('PrintDatalogStatement') |
                 SVLRTimingStatement('SVLRTimingStatement') |
                 SVLRLevelStatement('SVLRLevelStatement') |
                 WhileStatement('WhileStatement') |
                 RepeatStatement('RepeatStatement') |
                 ForStatement('ForStatement') |
                 MultiBinStatement('MultiBinStatement') |
                 EmptyStatement)

# FROM TestflowParser.cpp: FlowStatements = *(FlowStatement);
FlowStatements << pp.ZeroOrMore(FlowStatement)

# -------------------------------------------------------------------------------------------
# BEGIN SpecialTestsuiteSection
# -------------------------------------------------------------------------------------------

# FROM TestflowParser.cpp: DownloadTestsuite = (str_p("download")[bind(&StartTestsuite)("download")] >> TestsuiteDefinition >> End) [bind(&SetDownloadSuite)()];
DownloadTestsuite = pp.Group(pp.Keyword("download")("download") + TestsuiteDefinition + End)

# FROM TestflowParser.cpp: InitTestsuite = (str_p("initialize")[bind(&StartTestsuite)("initialize")] >> TestsuiteDefinition >> End )[bind(&SetInitSuite)()];
InitTestsuite = pp.Group(pp.Keyword("initialize")("initialize") + TestsuiteDefinition + End)

# FROM TestflowParser.cpp: PauseTestsuite = (str_p("pause")[bind(&StartTestsuite)("pause")] >> TestsuiteDefinition >> End)[bind(&SetPauseSuite)()];
PauseTestsuite = pp.Group(pp.Keyword("pause")("pause") + TestsuiteDefinition + End)

# FROM TestflowParser.cpp: AbortTestsuite = (str_p("abort")[bind(&StartTestsuite)("abort")] >> TestsuiteDefinition >> End)[bind(&SetAbortSuite)()];
AbortTestsuite = pp.Group(pp.Keyword("abort")("abort") + TestsuiteDefinition + End)

# FROM TestflowParser.cpp: ResetTestsuite = (str_p("reset")[bind(&StartTestsuite)("reset")] >> TestsuiteDefinition >> End)[bind(&SetResetSuite)()];
ResetTestsuite = pp.Group(pp.Keyword("reset")("reset") + TestsuiteDefinition + End)

# FROM TestflowParser.cpp: ExitTestsuite = (str_p("exit")[bind(&StartTestsuite)("exit")] >> TestsuiteDefinition >> End)[bind(&SetExitSuite)()];
ExitTestsuite = pp.Group(pp.Keyword("exit")("exit") + TestsuiteDefinition + End)

# FROM TestflowParser.cpp: DisconnectTestsuite = (str_p("bin_disconnect")[bind(&StartTestsuite)("bin_disconnect")] >> TestsuiteDefinition >> End)[bind(&SetDisconnectSuite)()];
DisconnectTestsuite = pp.Group(pp.Keyword("bin_disconnect")("bin_disconnect") + TestsuiteDefinition + End)

# FROM TestflowParser.cpp: MultiBinDecisionTestsuite = (str_p("multi_bin_decision")[bind(&StartTestsuite)("multi_bin_decision")] >> TestsuiteDefinition >> End)[bind(&SetMultiBinDecisionSuite)()];
MultiBinDecisionTestsuite = pp.Group(pp.Keyword("multi_bin_decision")("multi_bin_decision") + TestsuiteDefinition + End)

# FROM TestflowParser.cpp: SpecialTestsuiteSection = DownloadTestsuite| InitTestsuite| PauseTestsuite| AbortTestsuite| ResetTestsuite| ExitTestsuite| DisconnectTestsuite| MultiBinDecisionTestsuite;
# Made this section recursive because TestsuiteDefinition is recursive (otherwise, pyparsing stops after the first element in the OR list)
SpecialTestsuiteSection = pp.Forward()
SpecialTestsuiteSection << (DownloadTestsuite | InitTestsuite | PauseTestsuite | AbortTestsuite |
                            ResetTestsuite | ExitTestsuite | DisconnectTestsuite | MultiBinDecisionTestsuite)("SpecialTestsuiteSection")

def create_SpecialTestsuiteSection(special_testsuites):
    rstr = ""
    for ts_name in special_testsuites:
        rstr += ts_name + '\n'
        rstr += format_testsuite_def(ts_name,special_testsuites)
        rstr += EndStr
    return rstr

class ParseSpecialTestsuiteSection(object):
    def __init__(self,toks):
        self.section_name = ""
        self.SpecialTestsuites = {}
        for tok in toks:
            ts_name = tok.pop(0)
            ts_def = tok
            self.SpecialTestsuites.update(parse_testsuite_def(ts_name,ts_def))
    def __str__(self):
        return create_SpecialTestsuiteSection(self.SpecialTestsuites)

SpecialTestsuiteSection.setParseAction(ParseSpecialTestsuiteSection)

# -------------------------------------------------------------------------------------------
# BEGIN BinningSection
# -------------------------------------------------------------------------------------------

# FROM TestflowParser.cpp: OtherwiseBin = (str_p("otherwise bin") >> '= ' >> BinDefinition >> ';')[bind(&CreateOtherwiseBin)()];
OtherwiseBin = (pp.Keyword("otherwise bin")("otherwise") + EQ + BinDefinition + SEMI)

# FROM TestflowParser.cpp: BinningSection = str_p("binning") >> *(OtherwiseBin| (BinDefinition >> ';')) >> End;
BinningSection = (pp.Keyword("binning").suppress() + pp.ZeroOrMore(pp.Group(OtherwiseBin | (BinDefinition + SEMI))) + End)("BinningSection")

def create_BinningSection(binning):
    rstr = "binning\n"
    for bindef in binning:
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
        return create_BinningSection(self.binning)

BinningSection.setParseAction(ParseBinningSection)

# -------------------------------------------------------------------------------------------
# BEGIN SetupSection
# -------------------------------------------------------------------------------------------

# FROM TestflowParser.cpp: ConfigFile = str_p("context_config_file") >> '= ' >> QuotedString [bind(&SetConfigFile)(arg1)] >> ';';
ConfigFile = (pp.Keyword("context_config_file") + EQ + QuotedString + SEMI)

# FROM TestflowParser.cpp: LevelsFile = str_p("context_levels_file") >> '= ' >> QuotedString [bind(&SetLevelsFile)(arg1)] >> ';';
LevelsFile = (pp.Keyword("context_levels_file") + EQ + QuotedString + SEMI)

# FROM TestflowParser.cpp: TimingFile = str_p("context_timing_file") >> '= ' >> QuotedString [bind(&SetTimingFile)(arg1)] >> ';';
TimingFile = (pp.Keyword("context_timing_file") + EQ + QuotedString + SEMI)

# FROM TestflowParser.cpp: VectorFile = str_p("context_vector_file") >> '= ' >> QuotedString [bind(&SetVectorFile)(arg1)] >> ';';
VectorFile = (pp.Keyword("context_vector_file") + EQ + QuotedString + SEMI)

# FROM TestflowParser.cpp: AttribFile = str_p("context_attrib_file") >> '= ' >> QuotedString [bind(&SetAttribFile)(arg1)] >> ';';
AttribFile = (pp.Keyword("context_attrib_file") + EQ + QuotedString + SEMI)

# FROM TestflowParser.cpp: ChannelAttribFile = str_p("context_channel_attrib_file") >> '= ' >> QuotedString [bind(&SetChannelAttribFile)(arg1)] >> ';';
ChannelAttribFile = (pp.Keyword("context_channel_attrib_file") + EQ + QuotedString + SEMI)

# FROM TestflowParser.cpp: MixedSignalFile = str_p("context_mixsgl_file") >> '= ' >> QuotedString [bind(&SetMixedSignalFile)(arg1)] >> ';';
MixedSignalFile = (pp.Keyword("context_mixsgl_file") + EQ + QuotedString + SEMI)

# FROM TestflowParser.cpp: AnalogControlFile = str_p("context_analog_control_file") >> '= ' >> QuotedString [bind(&SetAnalogControlFile)(arg1)] >> ';';
AnalogControlFile = (pp.Keyword("context_analog_control_file") + EQ + QuotedString + SEMI)

# FROM TestflowParser.cpp: WaveformFile = str_p("context_waveform_file") >> '= ' >> QuotedString [bind(&SetWaveformFile)(arg1)] >> ';';
WaveformFile = (pp.Keyword("context_waveform_file") + EQ + QuotedString + SEMI)

# FROM TestflowParser.cpp: RoutingFile = str_p("context_routing_file") >> '= ' >> QuotedString [bind(&SetRoutingFile)(arg1)] >> ';';
RoutingFile = (pp.Keyword("context_routing_file") + EQ + QuotedString + SEMI)

# FROM TestflowParser.cpp: TestTableFile = str_p("context_testtable_file") >> '= ' >> QuotedString[bind(&SetTestTableFile)(arg1)] >> ';';
TestTableFile = (pp.Keyword("context_testtable_file") + EQ + QuotedString + SEMI)

# FROM TestflowParser.cpp: Protocols = str_p("context_protocols") >> '= ' >> QuotedString[bind(&SetProtocols)(arg1)] >> ';';
Protocols = (pp.Keyword("context_protocols") + EQ + QuotedString + SEMI)

# FROM TestflowParser.cpp: SetupFiles = ConfigFile| LevelsFile| TimingFile| VectorFile| AttribFile| ChannelAttribFile| MixedSignalFile| AnalogControlFile| WaveformFile| RoutingFile| TestTableFile| Protocols;
SetupFiles = pp.Group(ConfigFile | LevelsFile | TimingFile | VectorFile | AttribFile | ChannelAttribFile |
                      MixedSignalFile | AnalogControlFile | WaveformFile | RoutingFile | TestTableFile | Protocols)

# FROM TestflowParser.cpp: SetupSection = str_p("context") >> *(SetupFiles) >> End;
SetupSection = (pp.Keyword("context").suppress() + pp.ZeroOrMore(SetupFiles) + End)("SetupSection")

def create_SetupSection(setup_files):
    rstr = 'context\n'
    for k,v in setup_files.iteritems():
        rstr += k + ' = ' + v + ';\n'
    rstr += EndStr
    return rstr

class ParseSetupSection(object):
    def __init__(self,toks):
        self.section_name = "context"
        self.SetupFiles = {}
        for tok in toks:
            self.SetupFiles[tok[0]] = tok[1]
    def __str__(self):
        return create_SetupSection(self.SetupFiles)

SetupSection.setParseAction(ParseSetupSection)

# -------------------------------------------------------------------------------------------
# BEGIN OOCSection
# -------------------------------------------------------------------------------------------

# FROM TestflowParser.cpp: OOCSection = str_p("oocrule") >> OOCRule >> End;
OOCSection = (pp.Keyword("oocrule").suppress() + OOCRule + End)("OOCSection")

def create_OOCSection(ooc_rules):
    rstr = 'oocrule\n'
    for rule in ooc_rules:
        rstr += rule[0] + ' = ' + rule[1] + ' ' + rule[2] + ' ' + rule[3] + ' ' + rule[4] + '\n'
    rstr += EndStr
    return rstr

class ParseOOCSection(object):
    def __init__(self,toks):
        self.section_name = "oocrule"
        self.OOCRules = []
        for tok in toks:
            if len(tok):
                self.OOCRules.append(tok)
    def __str__(self):
        return create_OOCSection(self.OOCRules)

OOCSection.setParseAction(ParseOOCSection)

# -------------------------------------------------------------------------------------------
# BEGIN HardwareBinSection
# -------------------------------------------------------------------------------------------

# FROM TestflowParser.cpp: HardBinDescription = (int_p[HardBinDescription.hwBin =  arg1] >> '= ' >> QuotedString[HardBinDescription.description =  arg1] >> ';')[bind(&SetHardBinDescription)(HardBinDescription.hwBin, HardBinDescription.description)];
HardBinDescription = pp.Group(integer + EQ + QuotedString + SEMI)

# FROM TestflowParser.cpp: HardwareBinSection = str_p("hardware_bin_descriptions") >> *(HardBinDescription) >> End;
HardwareBinSection = (pp.Keyword("hardware_bin_descriptions").suppress() + pp.ZeroOrMore(HardBinDescription) + End)("HardwareBinSection")

def create_HardwareBinSection(hbin_descriptions):
    rstr = 'hardware_bin_descriptions\n'
    for k,v in hbin_descriptions.iteritems():
        rstr += k + ' = ' + v + ';\n'
    rstr += EndStr
    return rstr

class ParseHardwareBinSection(object):
    def __init__(self,toks):
        self.section_name = "hardware_bin_descriptions"
        self.hbin_descriptions = {}
        for tok in toks:
            self.hbin_descriptions[tok[0]] = tok[1]
    def __str__(self):
        return create_HardwareBinSection(self.hbin_descriptions)

HardwareBinSection.setParseAction(ParseHardwareBinSection)

# -------------------------------------------------------------------------------------------
# BEGIN ALL Sections collection
# -------------------------------------------------------------------------------------------

# FROM TestflowParser.cpp:   Sections =
# FROM TestflowParser.cpp: (
# FROM TestflowParser.cpp:  EmptySection
# FROM TestflowParser.cpp:  | InformationSection
# FROM TestflowParser.cpp:  | ImplicitDeclarationSection
# FROM TestflowParser.cpp:  | DeclarationSection
# FROM TestflowParser.cpp:  | FlagSection
# FROM TestflowParser.cpp:  | TestfunctionSection
# FROM TestflowParser.cpp:  | TestmethodParameterSection
# FROM TestflowParser.cpp:  | TestmethodLimitSection
# FROM TestflowParser.cpp:  | TestmethodSection
# FROM TestflowParser.cpp:  | UserprocedureSection
# FROM TestflowParser.cpp:  | TestsuiteSection
# FROM TestflowParser.cpp:  | TestflowSection
# FROM TestflowParser.cpp:  | SpecialTestsuiteSection
# FROM TestflowParser.cpp:  | BinningSection
# FROM TestflowParser.cpp:  | SetupSection
# FROM TestflowParser.cpp:  | OOCSection
# FROM TestflowParser.cpp:  | HardwareBinSection
# FROM TestflowParser.cpp:  )
# FROM TestflowParser.cpp:    >> !Sections
# FROM TestflowParser.cpp: ;
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

# FROM TestflowParser.cpp: Start = OptFileHeader[Start.isUTMBased=false] >> OptRevision >> Sections;
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
Start.setParseAction(ParseStart)

def format_tf(tf_str):
    indent_lev = 0
    indent = '  '
    rstr = ''
    for line in tf_str.split('\n'):
        line = line.strip()
        if not len(line):
            continue
        if line[0] == '}':
            indent_lev -= 1
        rstr += indent*indent_lev + line + '\n'
        if line[0] == '{':
            indent_lev += 1
    return rstr

class ParseTestflowSection(Statement):
    def __init__(self,toks):
        self.data = toks[:]
        self.section_name = "test_flow"
    def __repr__(self):
        rstr = self.section_name + '\n'
        rstr += ''.join([str(x) for x in self.data]) + '\n'
        rstr += EndStr
        return format_tf(rstr)
    def _nodes(self):
        return [x._nodes() for x in self.data]

TestflowSection.setParseAction(ParseTestflowSection)

def get_file_contents(infile,strip_comments=True):
        _f = open(infile)
        contents = '\n'.join(_f.read().splitlines())
        _f.close()
        if strip_comments:
            # string comments before parsing
            contents = re.sub(re.compile(r'--[^"]*?\n') ,'' ,contents)
        return contents

class Testflow(Statement):
    """
        usage:
            tf = Testflow(testflow_file.tf)
            print tf
            pprint(tf.showNodeMap())
            pprint(tf.testsuites)
    """
    def __init__(self,tf_file,testflow_only=False):
        contents = get_file_contents(tf_file)
        self.tf = Start.parseString(contents,1)[0]
        self._nodeMap = self.tf.TestflowSection._nodes()
    def showNodeMap(self):
        return tf.traverse_tree(self._nodeMap)

    def traverse_tree(self,obj):
        if isinstance(obj, list):
            return [self.traverse_tree(elem) for elem in obj]
        else:
            return self._nodeData[obj]
    def __str__(self):
        return str(self.tf)

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 1:
        print "usage: (python) TestflowParser.py <input file>"
        exit()
    print '\n\n'
    tf = Testflow(args[0],True)

    print tf
    # print '===================================================================================================\n'*4
    # pprint(tf.showNodeMap())
    # print '===================================================================================================\n'*4
    # pprint(tf.testsuites)

# TODO : gather all testsuite meta data
# TODO : get all parent ids/conditions so that we can add that to testsuite information