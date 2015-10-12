__author__ = 'Roger'

# modified to True if certain sections are found
isUTMBased = False

import pyparsing as pp

SEMI = pp.Literal(';').suppress()
AT = pp.Literal('@').suppress()
COLON = pp.Literal(':').suppress()
COMMA = pp.Literal(',').suppress()
UNDER = pp.Literal('_')
DOT = pp.Literal('.').suppress()
PERIOD = DOT
EQ = pp.Literal('=').suppress()
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
LCURL = pp.Literal('{')
RCURL = pp.Literal('}')
LPAR = pp.Literal('(')
RPAR = pp.Literal(')')

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
Expression = BinaryAddTerm

# NumberFunction  = str_p("pass") | "fail" | "has_run" | "has_not_run" | "tf_result" |"tf_pin_result" | "spst_timing" |
#                         "spst_level" | "svlr_timing" | "svlr_level" | "wsus" | "bsus" | "lsus" | "tsus"          ;
NumberFunction  = pp.Keyword("pass") | pp.Keyword("fail") | pp.Keyword("has_run") | pp.Keyword("has_not_run") |\
                           pp.Keyword("tf_result") | pp.Keyword("tf_pin_result") | pp.Keyword("spst_timing") |\
                           pp.Keyword("spst_level") | pp.Keyword("svlr_timing") | pp.Keyword("svlr_level") |\
                           pp.Keyword("wsus") | pp.Keyword("bsus") | pp.Keyword("lsus") | pp.Keyword("tsus")

# StringFunction = str_p("burstfirst") | "burstnext";
StringFunction = pp.Keyword("burstfirst") | pp.Keyword("burstnext")

# Number = real_p | int_p;
Number = Float | integer

# End = str_p("end");
End = (pp.Keyword("end") + pp.ZeroOrMore(DASH)).suppress()

# Identifier = lexeme_d[(*((alnum_p | ch_p('_')))) - (str_p("end"))];
Identifier = pp.Word(pp.alphanums + '_')

# TestsuiteFlag = ch_p('@') >> (Identifier >> "." >> Identifier)[TestsuiteFlag.varName = construct_<string>(arg1, arg2)];
TestsuiteFlag = AT + (Identifier + DOT + Identifier)

# Variable = str_p("@") >> (Identifier)[Variable.varName = construct_<string>(arg1, arg2)] |
#                  "@{" >> (Identifier)[Variable.varName = construct_<string>(arg1, arg2)] >> "}";
Variable = pp.Combine((pp.Literal("@") + Identifier) | ("@{" + Identifier + "}"))


# String = (alnum_p - ch_p('!')) >> *(alnum_p | "_");
String = pp.Combine(pp.Word(pp.alphanums,excludeChars='!') + pp.ZeroOrMore(pp.Word(pp.alphanums) | UNDER))

# QuotedString << ch_p('"') >> lexeme_d[(*(lex_escape_ch_p - ch_p('"')))]
#                [QuotedString.noQuotes = construct_<string>(arg1, arg2)] >> ch_p('"') >> !QuotedString;
QuotedString = pp.Forward()

QuotedString << pp.Combine(pp.QuotedString(quoteChar='"', escChar='\\',multiline=True) + pp.Optional(QuotedString))

# Literal = Number | TestsuiteFlag | Variable | QuotedString | String;
Literal = Number | TestsuiteFlag | Variable | QuotedString | String

# Term = "(" >> Expression >> ")" | NumberFunction >>  "(" >> !((Expression) >> *( "," >> (Expression))) >> ")"
# | StringFunction >>  "(" >> !((Expression) >> *( "," >> (Expression))) >> ")" | Unary >> Term | Literal;
Term = pp.Forward()
Term = (LPAR + Expression + RPAR | NumberFunction + LPAR + pp.Optional(Expression + pp.ZeroOrMore(COMMA + Expression))
        + RPAR | StringFunction + LPAR + pp.Optional(Expression + pp.ZeroOrMore(COMMA + Expression))
        + RPAR | Unary + Term | Literal)

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
OptFileHeader = (pp.Optional(pp.Keyword("hp93000,testflow,0.1")))\
    .setResultsName("OptFileHeader")
class ParseOptFileHeader(object):
    def __init__(self,toks):
        self.section_name = "OptFileHeader"
        self.header = toks[0]
    def __str__(self):
        return self.header
OptFileHeader.setParseAction(ParseOptFileHeader)

# OptRevision = !(str_p("language_revision") >> ch_p('=') >> int_p >> ch_p(';'));
OptRevision = (pp.Optional(pp.Keyword("language_revision")).suppress() + EQ + pp.Word(pp.nums) + SEMI)\
    .setResultsName("OptRevision")
class ParseOptRevision(object):
    def __init__(self,toks):
        self.section_name = "OptRevision"
        self.language_revision = toks[0]
    def __str__(self):
        return "language_revision" + ' = ' + self.language_revision + ';\n'
OptRevision.setParseAction(ParseOptRevision)

# EmptySection = ch_p(';');
class ParseEmptySection(object):
    def __init__(self,toks):
        self.section_name = ""
EmptySection = pp.Group(SEMI)\
    .setResultsName("EmptySection")
EmptySection.setParseAction(ParseEmptySection)

# -------------------------------------------------------------------------------------------
# BEGIN InformationSection
# -------------------------------------------------------------------------------------------

# DeviceName = str_p("device_name") >> '=' >> (QuotedString)[bind(&SetDeviceName)(arg1)] >> ';';
DeviceName = pp.Keyword("device_name").suppress() + EQ + QuotedString.setResultsName("SetDeviceName") + SEMI

# DeviceRevision = str_p("device_revision") >> '=' >> QuotedString[bind(&SetDeviceRevision)(arg1)] >> ';';
DeviceRevision = pp.Keyword("device_revision").suppress() + EQ + QuotedString.setResultsName("SetDeviceRevision") + SEMI

# TestRevision = str_p("test_revision") >> '=' >> QuotedString[bind(&SetTestRevision)(arg1)] >> ';';
TestRevision = pp.Keyword("test_revision").suppress() + EQ + QuotedString.setResultsName("SetTestRevision") + SEMI

# Description = str_p("description") >> '=' >> QuotedString[bind(&SetDescription)(arg1)] >> ';';
Description = pp.Keyword("description").suppress() + EQ + QuotedString.setResultsName("SetDescription") + SEMI

# Application = str_p("application") >> '=' >> QuotedString[bind(&SetApplication)(arg1)] >> ';';
Application = pp.Keyword("application").suppress() + EQ + QuotedString.setResultsName("SetApplication") + SEMI

# Temperature = str_p("temperature") >> '=' >> real_p[bind(&SetTemperature)] >> ';';
Temperature = pp.Keyword("temperature").suppress() + EQ + Float.setResultsName("SetTemperature") + SEMI

# InformationElements = *(DeviceName | DeviceRevision | TestRevision | Description | Application | Temperature);
InformationElements = pp.Group(pp.ZeroOrMore(DeviceName | DeviceRevision | TestRevision | Description | Application | Temperature))

# InformationSection = str_p("information") >> InformationElements >> End;
InformationSection = (pp.Keyword("information").suppress() + InformationElements + End)\
    .setResultsName("InformationSection")
class ParseInformationSection(object):
    def __init__(self,toks):
        self.section_name = "information"
        for tok in toks:
            if "SetDeviceName" in tok:
                self.SetDeviceName = tok["SetDeviceName"]
            elif "SetDeviceRevision" in tok:
                self.SetDeviceRevision = tok["SetDeviceRevision"]
            elif "SetTestRevision" in tok:
                self.SetTestRevision = tok["SetTestRevision"]
            elif "SetDescription" in tok:
                self.SetDescription = tok["SetDescription"]
            elif "SetApplication" in tok:
                self.SetApplication = tok["SetApplication"]
            elif "SetTemperature" in tok:
                self.SetTemperature = tok["SetTemperature"]
            else:
                print tok
                sys.exit("ERROR!!! Unknown element in 'information' section!  Exiting ...")
    def __str__(self):
        rstr = self.section_name + "\n"
        for k,v in self.__dict__.items():
            if k == "section_name":
                rstr += v + "\n"
            elif k == "SetDeviceName":
                rstr += "device_name = \"" + v + "\";\n"
            elif k == "SetDeviceRevision":
                rstr += "device_revision = \"" + v + "\";\n"
            elif k == "SetTestRevision":
                rstr += "test_revision = \"" + v + "\";\n"
            elif k == "SetDescription":
                rstr += "description = \"" + v + "\";\n"
            elif k == "SetApplication":
                rstr += "application = \"" + v + "\";\n"
            elif k == "SetTemperature":
                rstr += "temperature = " + v + ";\n"
            else:
                print k,v
                sys.exit("ERROR!!! Unknown element in 'information' section!  Exiting ...")
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
ImplicitDeclarationSection = (pp.Keyword("implicit_declarations").suppress() + ImplicitDeclarations + End)\
    .setResultsName("ImplicitDeclarationSection")
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

# Definition = (Variable[Definition.varName = arg1] >> '=' >> Expression[Definition.value = arg1] >> ';')
#              [bind(&CreateVariable)(Definition.varName, Definition.value)];
# Definition = (Variable + EQ + Expression + SEMI)
Definition = pp.Group(Variable + EQ + Expression + SEMI)

# Declarations = (*Definition);
Declarations = pp.ZeroOrMore(Definition)

# DeclarationSection = str_p("declarations") >> Declarations >> End;
DeclarationSection = (pp.Keyword("declarations").suppress() + Declarations + End)\
    .setResultsName("DeclarationSection")
class ParseDeclarationSection(object):
    def __init__(self,toks):
        self.section_name = "declarations"
        self.Definition = {}
        for tok in toks:
            self.Definition[tok[0]] = tok[1]
    def __str__(self):
        rstr = self.section_name + "\n"
        for varName,value in self.Definition.iteritems():
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
FlagSection = (pp.Keyword("flags").suppress() + Flags + End)\
    .setResultsName("FlagSection")
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
TestfunctionDescription = pp.Keyword("testfunction_description") + EQ + QuotedString + SEMI

# TestfunctionParameter = str_p("testfunction_parameters")  >> '=' >> QuotedString[Testfunction.parameters = arg1] >> ';';
TestfunctionParameter = pp.Keyword("testfunction_parameters") + EQ + QuotedString + SEMI

# TestmethodParameter = ((Identifier)[bind(&StartTestmethod)(construct_<string>(arg1, arg2))] >> ch_p(':') >>
#                       *((QuotedString[TestmethodParameter.name = arg1] >> '=' >> QuotedString[TestmethodParameter.value = arg1])
#                       [bind(&AddTestmethodParameter)(TestmethodParameter.name, TestmethodParameter.value)] >> ';'))
#                       [bind(&SetTestmethodParameters)()];
TestmethodParameter = pp.Group(Identifier + COLON + pp.ZeroOrMore(pp.Group(QuotedString + EQ + QuotedString + SEMI)))

# TestfunctionDefinition = ((TestfunctionDescription >> TestfunctionParameter) | (TestfunctionParameter >> TestfunctionDescription));
TestfunctionDefinition = ((TestfunctionDescription + TestfunctionParameter) | (TestfunctionParameter + TestfunctionDescription))

# Testfunction = ((Identifier)[Testfunction.identifier = construct_<string>(arg1, arg2)] >> ':'>> TestfunctionDefinition)
#                [bind(&CreateTestfunction)(Testfunction.identifier, Testfunction.description, Testfunction.parameters)];
Testfunction = (Identifier + COLON + TestfunctionDefinition)

# Testfunctions = *(Testfunction) >> End;
Testfunctions = pp.ZeroOrMore(Testfunction) + End

# TestfunctionSection = str_p("testfunctions") >> Testfunctions;
TestfunctionSection = (pp.Keyword("testfunctions").suppress() + Testfunctions)\
    .setResultsName("TestfunctionSection")
class ParseTestfunctionSection(object):
    def __init__(self,toks):
        # TODO: need to work out syntax for this section
        for tok in toks:
            print tok
TestfunctionSection.setParseAction(ParseTestfunctionSection)

# -------------------------------------------------------------------------------------------
# BEGIN TestmethodParameterSection
# -------------------------------------------------------------------------------------------

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
TestmethodParameterSection = (pp.Keyword("testmethodparameters").suppress() + UTMTestmethodParameters + End)\
    .setResultsName("TestmethodParameterSection")
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
        rstr = self.section_name + "\n"
        for tm_id in self.UTMTestmethodParameters:
            rstr += tm_id + ":\n"
            for k,v in self.UTMTestmethodParameters[tm_id].iteritems():
                rstr += "  "+ k + " = \"" + v + "\";\n"
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
TestmethodLimit = pp.Group(Identifier.setResultsName("StartTestmethod")
                           + COLON + pp.ZeroOrMore((QuotedString.setResultsName("name") + EQ
                                                    + QuotedString.setResultsName("loVal") + COLON
                                                    + LowLimitSymbol.setResultsName("LowLimitSymbol") + COLON
                                                    + QuotedString.setResultsName("hiVal") + COLON
                                                    + HighLimitSymbol.setResultsName("HighLimitSymbol") + COLON
                                                    + QuotedString.setResultsName("unit") + COLON
                                                    + QuotedString.setResultsName("numOffset") + COLON
                                                    + QuotedString.setResultsName("numInc") + SEMI)))

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
TestmethodLimitSection = (pp.Keyword("testmethodlimits").suppress() + UTMTestmethodLimits + End)\
    .setResultsName("TestmethodLimitSection")
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
            rstr += "\"" + self.UTMTestmethodLimits[tm_id]["name"] + "\" = "
            rstr += "\"" + self.UTMTestmethodLimits[tm_id]["loVal"] + "\":"
            rstr += "\"" + self.UTMTestmethodLimits[tm_id]["LowLimitSymbol"] + "\":"
            rstr += "\"" + self.UTMTestmethodLimits[tm_id]["hiVal"] + "\":"
            rstr += "\"" + self.UTMTestmethodLimits[tm_id]["HighLimitSymbol"] + "\":"
            rstr += "\"" + self.UTMTestmethodLimits[tm_id]["unit"] + "\":"
            rstr += "\"" + self.UTMTestmethodLimits[tm_id]["numOffset"] + "\":"
            rstr += "\"" + self.UTMTestmethodLimits[tm_id]["numInc"] + "\";\n"
        rstr += EndStr
        return rstr
TestmethodLimitSection.setParseAction(ParseTestmethodLimitSection)

# -------------------------------------------------------------------------------------------
# BEGIN TestmethodSection
# -------------------------------------------------------------------------------------------

# UTMTestmethodClass = str_p("testmethod_class") >> '=' >> QuotedString[Testmethod.Class = arg1] >> ';';
UTMTestmethodClass = pp.Keyword("testmethod_class").suppress() + EQ + QuotedString.setResultsName("Class") + SEMI

# TestmethodClass = str_p("testmethod_class") >> '=' >> QuotedString[Testmethod.Class = arg1] >> ';';
TestmethodClass = pp.Keyword("testmethod_class").suppress() + EQ + QuotedString.setResultsName("Class") + SEMI

# TestmethodId = str_p("testmethod_id") >> '=' >> (String[Testmethod.methodId = construct_<string>(arg1, arg2)] |
#                QuotedString[Testmethod.methodId = arg1]) >> ';';
TestmethodId = pp.Keyword("testmethod_id").suppress() + EQ + (String | QuotedString).setResultsName("methodId") + SEMI

# TestmethodParameters = str_p("testmethod_parameters") >> '=' >> QuotedString[Testmethod.parameter = arg1] >> ';';
TestmethodParameters = pp.Keyword("testmethod_parameters").suppress() + EQ + QuotedString.setResultsName("parameter") + SEMI

# TestmethodLimits = str_p("testmethod_limits") >> '=' >> QuotedString[Testmethod.limits = arg1] >> ';';
TestmethodLimits = pp.Keyword("testmethod_limits").suppress() + EQ + QuotedString.setResultsName("limits") + SEMI

# TestmethodName = str_p("testmethod_name") >> '=' >> QuotedString[Testmethod.name = arg1] >> ';';
TestmethodName = pp.Keyword("testmethod_name").suppress() + EQ + QuotedString.setResultsName("name") + SEMI

# TestmethodDefinition = (TestmethodClass | TestmethodId | TestmethodParameters | TestmethodLimits | TestmethodName ) >> !TestmethodDefinition;
TestmethodDefinition = pp.Forward()
TestmethodDefinition << (TestmethodClass | TestmethodId | TestmethodParameters | TestmethodLimits | TestmethodName) + pp.Optional(TestmethodDefinition)


# TODO: figure out setting for isUTMBased
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
    Testmethod = pp.Group(Identifier.setResultsName("tm_id") + COLON + UTMTestmethodClass)
else:
    Testmethod = pp.Group(Identifier.setResultsName("tm_id") + COLON + TestmethodDefinition)

# Testmethods = *(Testmethod) >> End;
Testmethods = pp.ZeroOrMore(Testmethod) + End

# TestmethodSection = str_p("testmethods") >> Testmethods;
TestmethodSection = (pp.Keyword("testmethods").suppress() + Testmethods)\
    .setResultsName("TestmethodSection")
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
            rstr += tm_id + ":\n  "
            rstr += "testmethod_class = \"" + self.Testmethods[tm_id]["Class"] + "\";\n"
            if not self.isUTMBased:
                rstr += "testmethod_id = \"" + self.Testmethods[tm_id]["methodId"] + "\";\n"
                rstr += "testmethod_parameters = \"" + self.Testmethods[tm_id]["parameter"] + "\";\n"
                rstr += "testmethod_limits = \"" + self.Testmethods[tm_id]["limits"] + "\";\n"
                rstr += "testmethod_name = \"" + self.Testmethods[tm_id]["name"] + "\";\n"
        rstr += EndStr
        return rstr
TestmethodSection.setParseAction(ParseTestmethodSection)

# Userprocedure = ((Identifier)[Userprocedure.identifier = construct_<string>(arg1, arg2)] >> ':' >>
#                 str_p("user_procedure") >> '=' >> QuotedString[Userprocedure.commandline = arg1] >> ';')
#                 [bind(&CreateUserprocedure)(Userprocedure.identifier, Userprocedure.commandline)];
Userprocedure = (Identifier + COLON + pp.Keyword("user_procedure") + EQ + QuotedString + SEMI)

# Userprocedures = *(Userprocedure) >> End;
Userprocedures = pp.ZeroOrMore(Userprocedure) + End

# UserprocedureSection = str_p("tests") >> Userprocedures;
UserprocedureSection = pp.Group(pp.Keyword("tests") + Userprocedures)\
    .setResultsName("UserprocedureSection")

# -------------------------------------------------------------------------------------------
# BEGIN TestsuiteSection
# -------------------------------------------------------------------------------------------

# TestsuiteName = Identifier >> *ch_p(' ') >> ':';
TestsuiteName = Identifier + COLON

# TestsuiteTest = (str_p("override_testf") >> '=' >> Identifier[bind(&SetTestsuiteTest)(construct_<string>(arg1, arg2))] >>';') |
#                 (str_p("tests") >> '=' >> Identifier[bind(&SetTestsuiteTest)(construct_<string>(arg1, arg2))] >> ';');
TestsuiteTest = pp.Group((pp.Keyword("override_testf") + EQ + Identifier + SEMI) |  (pp.Keyword("tests") + EQ + Identifier + SEMI))\
    .setResultsName("TestsuiteTest")

# TestsuiteOverride = str_p("override") >> '=' >> int_p >> ';';
TestsuiteOverride = pp.Group(pp.Keyword("override").suppress() + EQ + integer + SEMI)\
    .setResultsName("TestsuiteOverride")

# TestsuiteTimEquSet = str_p("override_tim_equ_set") >> '=' >> Expression[bind(&SetTestsuiteTimEquSet)(arg1)] >> ';';
TestsuiteTimEquSet = pp.Group(pp.Keyword("override_tim_equ_set").suppress() + EQ + Expression + SEMI)\
    .setResultsName("TestsuiteTimEquSet")

# TestsuiteLevEquSet = str_p("override_lev_equ_set") >> '=' >> Expression[bind(&SetTestsuiteLevEquSet)(arg1)] >> ';';
TestsuiteLevEquSet = pp.Group(pp.Keyword("override_lev_equ_set").suppress() + EQ + Expression + SEMI)\
    .setResultsName("TestsuiteLevEquSet")

# TestsuiteTimSpecSet = str_p("override_tim_spec_set") >> '=' >> Expression[bind(&SetTestsuiteTimSpecSet)(arg1)] >> ';';
TestsuiteTimSpecSet = pp.Group(pp.Keyword("override_tim_spec_set").suppress() + EQ + Expression + SEMI)\
    .setResultsName("TestsuiteTimSpecSet")

# TestsuiteLevSpecSet = str_p("override_lev_spec_set") >> '=' >> Expression[bind(&SetTestsuiteLevSpecSet)(arg1)] >> ';';
TestsuiteLevSpecSet = pp.Group(pp.Keyword("override_lev_spec_set").suppress() + EQ + Expression + SEMI)\
    .setResultsName("TestsuiteLevSpecSet")

# TestsuiteTimSet = str_p("override_timset") >> '=' >> Expression[bind(&SetTestsuiteTimSet)(arg1)] >> ';';
TestsuiteTimSet = pp.Group(pp.Keyword("override_timset").suppress() + EQ + Expression + SEMI)\
    .setResultsName("TestsuiteTimSet")

# TestsuiteLevSet = str_p("override_levset") >> '=' >> Expression[bind(&SetTestsuiteLevSet)(arg1)] >> ';';
TestsuiteLevSet = pp.Group(pp.Keyword("override_levset").suppress() + EQ + Expression + SEMI)\
    .setResultsName("TestsuiteLevSet")

# TestsuiteSequencerLabel = str_p("override_seqlbl") >> '=' >> Expression[bind(&SetTestsuiteSequencerLabel)(arg1)] >> ';';
TestsuiteSequencerLabel = pp.Group(pp.Keyword("override_seqlbl").suppress() + EQ + Expression + SEMI)\
    .setResultsName("TestsuiteSequencerLabel")

# //Ignore this for now, because flag_ui handles the flags
# TestsuiteFlags = str_p("local_flags") >> '=' >> list_p(Identifier[bind(&SetTestsuiteFlag)(construct_<string>(arg1, arg2))], ch_p(',')) >> ';';
TestsuiteFlags = pp.Group(pp.Keyword("local_flags").suppress() + EQ + pp.ZeroOrMore(Identifier + COMMA) + Identifier + SEMI)\
    .setResultsName("TestsuiteFlags")

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
TestsuiteSiteControl = pp.Group(pp.Keyword("site_control").suppress() + EQ + SiteControlExpression + SEMI)\
    .setResultsName("TestsuiteSiteControl")

# TestsuiteFFCCount = str_p("ffc_on_fail") >> '=' >> int_p[bind(&SetTestsuiteFFCCount)(arg1)] >> ';';
TestsuiteFFCCount = pp.Group(pp.Keyword("ffc_on_fail").suppress() + EQ + integer + SEMI)\
    .setResultsName("TestsuiteFFCCount")

# TestsuiteTestLevel = str_p("test_level") >> '=' >> int_p[bind(&SetTestsuiteTestLevel)(arg1)] >> ';';
TestsuiteTestLevel = pp.Group(pp.Keyword("test_level").suppress() + EQ + integer + SEMI)\
    .setResultsName("TestsuiteTestLevel")

# TestsuiteDPSSet = str_p("override_dpsset") >> '=' >> Expression[bind(&SetTestsuiteDPSSet)(arg1)] >> ';';
TestsuiteDPSSet = pp.Group(pp.Keyword("override_dpsset").suppress() + EQ + Expression + SEMI)\
    .setResultsName("TestsuiteDPSSet")

# TestsuiteTestNumber = str_p("override_test_number") >> '=' >> Expression[bind(&SetTestsuiteTestNumber)(arg1)] >> ';';
TestsuiteTestNumber = pp.Group(pp.Keyword("override_test_number").suppress() + EQ + Expression + SEMI)\
    .setResultsName("TestsuiteTestNumber")

# TestsuiteAnalogSet = str_p("override_anaset") >> '=' >> Expression[bind(&SetTestsuiteAnalogSet)(arg1)] >> ';';
TestsuiteAnalogSet = pp.Group(pp.Keyword("override_anaset").suppress() + EQ + Expression + SEMI)\
    .setResultsName("TestsuiteAnalogSet")

# TestsuiteSiteMatch = str_p("site_match") >> '=' >> int_p[bind(&SetTestsuiteSiteMatch)(arg1)] >> ';';
TestsuiteSiteMatch = pp.Group(pp.Keyword("site_match").suppress() + EQ + integer + SEMI)\
    .setResultsName("TestsuiteSiteMatch")

# TestsuiteWaveformSet = str_p("override_wvfset") >> '=' >> Expression[bind(&SetTestsuiteWaveformSet)(arg1)] >> ';';
TestsuiteWaveformSet = pp.Group(pp.Keyword("override_wvfset").suppress() + EQ + Expression + SEMI)\
    .setResultsName("TestsuiteWaveformSet")

# TestsuiteComment = str_p("comment") >> '=' >> QuotedString[bind(&SetTestsuiteComment)(arg1)] >> ';';
TestsuiteComment = pp.Group(pp.Keyword("comment").suppress() + EQ + QuotedString + SEMI)\
    .setResultsName("TestsuiteComment")

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
Testsuite = pp.Group(TestsuiteName.setResultsName("TestsuiteName") + TestsuiteDefinition.setResultsName("TestsuiteDefinition"))

# Testsuites = *(Testsuite);
Testsuites = pp.ZeroOrMore(Testsuite)

# TestsuiteSection = str_p("test_suites") >> Testsuites  >> End;
TestsuiteSection = (pp.Keyword("test_suites").suppress() + Testsuites  + End)\
    .setResultsName("TestsuiteSection")
def ParseTestsuiteDefinition(toks):
    """
        Used by ParseTestsuiteSection and also ParseSpecialTestsuiteSection
    """
    # TODO: let's finish this so that we can re-use the code for SpecialTestsuites
    for tok in toks:
        print tok
class ParseTestsuiteSection(object):
    def __init__(self,toks):
        self.section_name = "test_suites"
        self.Testsuites = {}
        for tok in toks:
            ts_name = tok["TestsuiteName"][0]
            ts_def = tok["TestsuiteDefinition"]
            if ts_name not in self.Testsuites:
                self.Testsuites[ts_name] = {}
            if "TestsuiteTest" in ts_def:
                self.Testsuites[ts_name]["TestsuiteTest"] = {}
                self.Testsuites[ts_name]["TestsuiteTest"][ts_def["TestsuiteTest"][0]] = ts_def["TestsuiteTest"][1]
                self.Testsuites[ts_name]["TestsuiteOverride"] = ts_def["TestsuiteOverride"][0]
            if "TestsuiteTimEquSet" in ts_def:
                self.Testsuites[ts_name]["TestsuiteTimEquSet"] = ts_def["TestsuiteTimEquSet"][0]
            if "TestsuiteLevEquSet" in ts_def:
                self.Testsuites[ts_name]["TestsuiteLevEquSet"] = ts_def["TestsuiteLevEquSet"][0]
            if "TestsuiteTimSpecSet" in ts_def:
                self.Testsuites[ts_name]["TestsuiteTimSpecSet"] = ts_def["TestsuiteTimSpecSet"][0]
            if "TestsuiteLevSpecSet" in ts_def:
                self.Testsuites[ts_name]["TestsuiteLevSpecSet"] = ts_def["TestsuiteLevSpecSet"][0]
            if "TestsuiteTimSet" in ts_def:
                self.Testsuites[ts_name]["TestsuiteTimSet"] = ts_def["TestsuiteTimSet"][0]
            if "TestsuiteLevSet" in ts_def:
                self.Testsuites[ts_name]["TestsuiteLevSet"] = ts_def["TestsuiteLevSet"][0]
            if "TestsuiteSequencerLabel" in ts_def:
                self.Testsuites[ts_name]["TestsuiteSequencerLabel"] = ts_def["TestsuiteSequencerLabel"][0]
            if "TestsuiteFlags" in ts_def:
                self.Testsuites[ts_name]["TestsuiteFlags"] = []
                for flag in ts_def["TestsuiteFlags"]:
                    self.Testsuites[ts_name]["TestsuiteFlags"].append(flag)
            if "TestsuiteSiteControl" in ts_def:
                self.Testsuites[ts_name]["TestsuiteSiteControl"] = ts_def["TestsuiteSiteControl"][0]
            if "TestsuiteFFCCount" in ts_def:
                self.Testsuites[ts_name]["TestsuiteFFCCount"] = ts_def["TestsuiteFFCCount"][0]
            if "TestsuiteTestLevel" in ts_def:
                self.Testsuites[ts_name]["TestsuiteTestLevel"] = ts_def["TestsuiteTestLevel"][0]
            if "TestsuiteDPSSet" in ts_def:
                self.Testsuites[ts_name]["TestsuiteDPSSet"] = ts_def["TestsuiteDPSSet"][0]
            if "TestsuiteTestNumber" in ts_def:
                self.Testsuites[ts_name]["TestsuiteTestNumber"] = ts_def["TestsuiteTestNumber"][0]
            if "TestsuiteAnalogSet" in ts_def:
                self.Testsuites[ts_name]["TestsuiteAnalogSet"] = ts_def["TestsuiteAnalogSet"][0]
            if "TestsuiteSiteMatch" in ts_def:
                self.Testsuites[ts_name]["TestsuiteSiteMatch"] = ts_def["TestsuiteSiteMatch"][0]
            if "TestsuiteWaveformSet" in ts_def:
                self.Testsuites[ts_name]["TestsuiteWaveformSet"] = ts_def["TestsuiteWaveformSet"][0]
            if "TestsuiteComment" in ts_def:
                self.Testsuites[ts_name]["TestsuiteComment"] = ts_def["TestsuiteComment"][0]
    def __str__(self):
        rstr = self.section_name + "\n"
        for ts_name in self.Testsuites:
            rstr += ts_name + ":\n"
            if "TestsuiteTest" in self.Testsuites[ts_name]:
                for k,v in self.Testsuites[ts_name]["TestsuiteTest"].iteritems():
                    rstr += "  "+ k + " = " + v + ";\n"
            if "TestsuiteOverride" in self.Testsuites[ts_name]:
                rstr += "  override = " + self.Testsuites[ts_name]["TestsuiteOverride"] + ";\n"
            if "TestsuiteTimEquSet" in self.Testsuites[ts_name]:
                rstr += "  override_tim_equ_set = " + self.Testsuites[ts_name]["TestsuiteTimEquSet"] + ";\n"
            if "TestsuiteLevEquSet" in self.Testsuites[ts_name]:
                rstr += "  override_lev_equ_set = " + self.Testsuites[ts_name]["TestsuiteLevEquSet"] + ";\n"
            if "TestsuiteTimSpecSet" in self.Testsuites[ts_name]:
                rstr += "  override_tim_spec_set = " + self.Testsuites[ts_name]["TestsuiteTimSpecSet"] + ";\n"
            if "TestsuiteLevSpecSet" in self.Testsuites[ts_name]:
                rstr += "  override_lev_spec_set = " + self.Testsuites[ts_name]["TestsuiteLevSpecSet"] + ";\n"
            if "TestsuiteTimSet" in self.Testsuites[ts_name]:
                rstr += "  override_timset = " + self.Testsuites[ts_name]["TestsuiteTimSet"] + ";\n"
            if "TestsuiteLevSet" in self.Testsuites[ts_name]:
                rstr += "  override_levset = " + self.Testsuites[ts_name]["TestsuiteLevSet"] + ";\n"
            if "TestsuiteSequencerLabel" in self.Testsuites[ts_name]:
                rstr += "  override_seqlbl = " + self.Testsuites[ts_name]["TestsuiteSequencerLabel"] + ";\n"
            if "TestsuiteFlags" in self.Testsuites[ts_name]:
                rstr += "  local_flags = " + ','.join(self.Testsuites[ts_name]["TestsuiteFlags"]) + ";\n"
            if "TestsuiteSiteControl" in self.Testsuites[ts_name]:
                rstr += "  site_control = " + self.Testsuites[ts_name]["TestsuiteSiteControl"] + ";\n"
            if "TestsuiteFFCCount" in self.Testsuites[ts_name]:
                rstr += "  ffc_on_fail = " + self.Testsuites[ts_name]["TestsuiteFFCCount"] + ";\n"
            if "TestsuiteTestLevel" in self.Testsuites[ts_name]:
                rstr += "  test_level = " + self.Testsuites[ts_name]["TestsuiteTestLevel"] + ";\n"
            if "TestsuiteDPSSet" in self.Testsuites[ts_name]:
                rstr += "  override_dpsset = " + self.Testsuites[ts_name]["TestsuiteDPSSet"] + ";\n"
            if "TestsuiteTestNumber" in self.Testsuites[ts_name]:
                rstr += "  override_test_number = " + self.Testsuites[ts_name]["TestsuiteTestNumber"] + ";\n"
            if "TestsuiteAnalogSet" in self.Testsuites[ts_name]:
                rstr += "  override_anaset = " + self.Testsuites[ts_name]["TestsuiteAnalogSet"] + ";\n"
            if "TestsuiteSiteMatch" in self.Testsuites[ts_name]:
                rstr += "  site_match = " + self.Testsuites[ts_name]["TestsuiteSiteMatch"] + ";\n"
            if "TestsuiteWaveformSet" in self.Testsuites[ts_name]:
                rstr += "  override_wvfset = " + self.Testsuites[ts_name]["TestsuiteWaveformSet"] + ";\n"
            if "TestsuiteComment" in self.Testsuites[ts_name]:
                rstr += "  comment = " + self.Testsuites[ts_name]["TestsuiteComment"] + ";\n"
        rstr += EndStr
        # sys.exit()
        return rstr
TestsuiteSection.setParseAction(ParseTestsuiteSection)

# -------------------------------------------------------------------------------------------
# BEGIN TestflowSection
# -------------------------------------------------------------------------------------------

# RunStatement = (str_p("run") >> ch_p('(') >> Identifier[RunStatement.testsuite = construct_<string>(arg1, arg2)] >> ')' >> ';')
#                [bind(&CreateRunStatement)(RunStatement.testsuite)];
RunStatement = (pp.Keyword("run") + LPAR + Identifier + RPAR + SEMI)

FlowStatements = pp.Forward()

# RunAndBranchStatement = (str_p("run_and_branch") >> ch_p('(') >> Identifier[RunAndBranchStatement.testsuite = construct_<string>(arg1, arg2)] >> ')'
#                         >> str_p("then"))[bind(&CreateRunAndBranchStatement)(RunAndBranchStatement.testsuite)] >> str_p("{") [bind(&EnterSubBranch)(0)]
#                         >> FlowStatements >> str_p("}") [bind(&LeaveSubBranch)()] >> !(str_p("else")
#                         >> str_p("{") [bind(&EnterSubBranch)(1)] >> FlowStatements >> str_p("}") [bind(&LeaveSubBranch)()]);
RunAndBranchStatement = ((pp.Keyword("run_and_branch") + LPAR + Identifier + RPAR + pp.Keyword("then")) + LCURL +
                                 FlowStatements + RCURL + pp.Optional(pp.Keyword("else") + LCURL + FlowStatements + RCURL))

# IfStatement = (str_p("if") >> Expression[IfStatement.condition = arg1] >> str_p("then") )
#               [bind(&CreateIfStatement)(IfStatement.condition)]
#               >> (str_p("{")) [bind(&EnterSubBranch)(0)] >> FlowStatements >> (str_p("}")) [bind(&LeaveSubBranch)()]
#               >> !(str_p("else") >> (str_p("{")) [bind(&EnterSubBranch)(1)] >> FlowStatements >> (str_p("}")) [bind(&LeaveSubBranch)()]);
IfStatement = ((pp.Keyword("if") + Expression + pp.Keyword("then") ) + LCURL + FlowStatements + RCURL +
                       pp.Optional(pp.Keyword("else") + LCURL + FlowStatements + RCURL))

# GroupBypass = str_p("groupbypass") >> ',';
GroupBypass = pp.Keyword("groupbypass") + COMMA

# GroupStatement = str_p("{") [bind(&CreateGroupStatement)(), bind(&EnterSubBranch)(0)]
#                  >> FlowStatements >> str_p("}") [bind(&LeaveSubBranch)()] >> ','
#                  >> (GroupBypass[bind(&SetGroupBypass)()] |
#                 str_p("")[bind(&SetGroupNoBypass)()]) >> (str_p("open")[bind(&SetGroupOpen)()] |
#                 str_p("closed")[bind(&SetGroupClosed)()]) >> ',' >> (QuotedString) [bind(&SetGroupLabel)(arg1)]
#                 >> ',' >> (QuotedString) [bind(&SetGroupDescription)(arg1)];
GroupStatement = (LCURL + FlowStatements + RCURL + COMMA + pp.Optional(GroupBypass) + (pp.Keyword("open") |
                pp.Keyword("closed")) + COMMA + QuotedString + COMMA + QuotedString)

# AssignmentStatement = (( TestsuiteFlag[AssignmentStatement.varName = arg1] |  Variable[AssignmentStatement.varName = arg1])
#                       >> '=' >> (Expression[AssignmentStatement.value = arg1] | TestsuiteFlag[AssignmentStatement.value = arg1])
#                       >> ';') [bind(&CreateAssignmentStatement)(AssignmentStatement.varName, AssignmentStatement.value)];
AssignmentStatement = ((TestsuiteFlag | Variable) + EQ + (Expression | TestsuiteFlag) + SEMI)

# OOCRule = !(str_p("oocwarning") >> '=' >> int_p >> int_p >> int_p >> QuotedString) >> !(str_p("oocstop") >> '=' >> int_p >> int_p >> int_p >> QuotedString);
OOCRule = (pp.Optional(pp.Keyword("oocwarning") + EQ + integer + integer + integer + QuotedString) +
                   pp.Optional(pp.Keyword("oocstop") + EQ + integer + integer + integer + QuotedString))

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
BinDefinition = (QuotedString + COMMA + QuotedString + COMMA + pp.Optional(OOCRule) + COMMA + pp.Optional(Quality)
                  + COMMA + pp.Optional(Reprobe) + COMMA + Color + COMMA + pp.Optional(BinNumber) + COMMA + pp.Optional(Overon)
                  | (QuotedString + COMMA + QuotedString + COMMA + pp.Optional(Quality) + COMMA + pp.Optional(Reprobe) + COMMA + Color
                  + COMMA + pp.Optional(BinNumber) + COMMA + pp.Optional(Overon)))


# StopBinStatement = (str_p("stop_bin") >> (BinDefinition("", "", false, false, ::xoc::tapi::ZBinColor_BLACK, -1, false)) >> ';')
#                    [bind(&CreateStopBinStatement)()];
StopBinStatement = (pp.Keyword("stop_bin") + BinDefinition + SEMI)

# PrintStatement = (str_p("print") >> '(' >> Expression[PrintStatement.statement = arg1] >> ')' >> ';')
#                  [bind(&CreatePrintStatement)(PrintStatement.statement)];
PrintStatement = (pp.Keyword("print") + LPAR + Expression + RPAR + SEMI)

# PrintDatalogStatement = (str_p("print_dl") >> '(' >> Expression[PrintDatalogStatement.statement = arg1] >> ')' >> ';')
#                         [bind(&CreatePrintDatalogStatement)(PrintDatalogStatement.statement)];
PrintDatalogStatement = (pp.Keyword("print_dl") + LPAR + Expression + RPAR + SEMI)

# SVLRTimingStatement = (str_p("svlr_timing_command") >> '(' >> Expression[SVLRTimingStatement.equSet = arg1] >> ','
#                       >> Expression[SVLRTimingStatement.specSet = arg1] >> ',' >> QuotedString[SVLRTimingStatement.variable = arg1]
#                       >> ',' >> Expression[SVLRTimingStatement.value = arg1] >> ')' >> ';')
#                       [bind(&CreateSVLRTimingStatement)(SVLRTimingStatement.equSet, SVLRTimingStatement.specSet,
#                                                         SVLRTimingStatement.variable, SVLRTimingStatement.value)];
SVLRTimingStatement = (pp.Keyword("svlr_timing_command") + LPAR + Expression + COMMA + Expression + COMMA + QuotedString + COMMA + Expression + RPAR + SEMI)

# SVLRLevelStatement = (str_p("svlr_level_command") >> '(' >> Expression[SVLRLevelStatement.equSet = arg1] >> ',' >> Expression[SVLRLevelStatement.specSet = arg1]
#                       >> ',' >> QuotedString[SVLRLevelStatement.variable = arg1] >> ',' >> Expression[SVLRLevelStatement.value = arg1] >> ')' >> ';')
#                     [bind(&CreateSVLRLevelStatement)(SVLRLevelStatement.equSet, SVLRLevelStatement.specSet, SVLRLevelStatement.variable, SVLRLevelStatement.value)];
SVLRLevelStatement = (pp.Keyword("svlr_level_command") + LPAR + Expression + COMMA + Expression + COMMA + QuotedString + COMMA + Expression + RPAR + SEMI)

# TestNumLoopInc = str_p("test_number_loop_increment") >> '=' >> Expression[TestNumLoopInc.expression = arg1];
TestNumLoopInc = pp.Keyword("test_number_loop_increment") + EQ + Expression

# WhileStatement = (str_p("while") >> Expression [WhileStatement.condition = arg1, WhileStatement.testnum = construct_<string>("")] >> str_p("do")
#                  >> !(TestNumLoopInc [WhileStatement.testnum = arg1])) [bind(&CreateWhileStatement)(WhileStatement.condition, WhileStatement.testnum)]
#                  >> str_p("{") [bind(&EnterSubBranch)(0)] >> FlowStatements >> str_p("}") [bind(&LeaveSubBranch)()];
WhileStatement = ((pp.Keyword("while") + Expression + pp.Keyword("do") + pp.Optional(TestNumLoopInc)) + LCURL + FlowStatements + RCURL)

# RepeatStatement = str_p("repeat") [bind(&CreateRepeatStatement)(), bind(&EnterSubBranch)(0)] >> FlowStatements >> str_p("until") [bind(&LeaveSubBranch)()]
#                   >> Expression [bind(&SetRepeatCondition)(arg1)] >> !(TestNumLoopInc [bind(&SetRepeatTestnum)(arg1)]);
RepeatStatement = (pp.Keyword("repeat") + FlowStatements + pp.Keyword("until") + Expression + pp.Optional(TestNumLoopInc))

# ForStatement = (str_p("for")[ForStatement.testnum = construct_<string>("")] >> QualifiedIdentifier[ForStatement.assignVar = arg1]
#                >> '=' >> Expression[ForStatement.assignValue = arg1] >> ';' >> Expression[ForStatement.condition = arg1]
#                >> ';' >> QualifiedIdentifier[ForStatement.incrementVar = arg1] >> '=' >> Expression[ForStatement.incrementValue = arg1]
#                >> ';' >> str_p("do") >> !(TestNumLoopInc [ForStatement.testnum = arg1]))
#                [bind(&CreateForStatement)(ForStatement.assignVar, ForStatement.assignValue, ForStatement.condition, ForStatement.incrementVar,
#                                           ForStatement.incrementValue, ForStatement.testnum)]
#                >> str_p("{") [bind(&EnterSubBranch)(0)] >> FlowStatements >> str_p("}") [bind(&LeaveSubBranch)()];
ForStatement = ((pp.Keyword("for") + QualifiedIdentifier + EQ + Expression + SEMI + Expression + SEMI + QualifiedIdentifier +
                         EQ + Expression + SEMI + pp.Keyword("do") + pp.Optional(TestNumLoopInc)) + LCURL + FlowStatements + RCURL)

# MultiBinStatement = str_p("multi_bin")[bind(&CreateMultiBinStatement)()] >> ';';
MultiBinStatement = pp.Keyword("multi_bin") + SEMI

# EmptyStatement = ch_p(';');
EmptyStatement = ';'

# TestflowSection = str_p("test_flow")[bind(&FlowSectionStart)()] >> FlowStatements >> End;
TestflowSection = pp.Group(pp.Keyword("test_flow") + FlowStatements + End)\
    .setResultsName("TestflowSection")

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
FlowStatement = (RunStatement |
                 RunAndBranchStatement |
                 GroupStatement |
                 IfStatement |
                 AssignmentStatement |
                 StopBinStatement |
                 PrintStatement |
                 PrintDatalogStatement |
                 SVLRTimingStatement |
                 SVLRLevelStatement |
                 WhileStatement |
                 RepeatStatement |
                 ForStatement |
                 MultiBinStatement |
                 EmptyStatement)

# FlowStatements = *(FlowStatement);
FlowStatements << pp.ZeroOrMore(FlowStatement)

# -------------------------------------------------------------------------------------------
# BEGIN SpecialTestsuiteSection
# -------------------------------------------------------------------------------------------

# DownloadTestsuite = (str_p("download")[bind(&StartTestsuite)("download")] >> TestsuiteDefinition >> End) [bind(&SetDownloadSuite)()];
DownloadTestsuite = pp.Group(pp.Keyword("download").setResultsName("download")  + TestsuiteDefinition + End)

# InitTestsuite = (str_p("initialize")[bind(&StartTestsuite)("initialize")] >> TestsuiteDefinition >> End )[bind(&SetInitSuite)()];
InitTestsuite = pp.Group(pp.Keyword("initialize").setResultsName("initialize")  + TestsuiteDefinition + End)

# PauseTestsuite = (str_p("pause")[bind(&StartTestsuite)("pause")] >> TestsuiteDefinition >> End)[bind(&SetPauseSuite)()];
PauseTestsuite = pp.Group(pp.Keyword("pause").setResultsName("pause")  + TestsuiteDefinition + End)

# AbortTestsuite = (str_p("abort")[bind(&StartTestsuite)("abort")] >> TestsuiteDefinition >> End)[bind(&SetAbortSuite)()];
AbortTestsuite = pp.Group(pp.Keyword("abort").setResultsName("abort")  + TestsuiteDefinition + End)

# ResetTestsuite = (str_p("reset")[bind(&StartTestsuite)("reset")] >> TestsuiteDefinition >> End)[bind(&SetResetSuite)()];
ResetTestsuite = pp.Group(pp.Keyword("reset").setResultsName("reset")  + TestsuiteDefinition + End)

# ExitTestsuite = (str_p("exit")[bind(&StartTestsuite)("exit")] >> TestsuiteDefinition >> End)[bind(&SetExitSuite)()];
ExitTestsuite = pp.Group(pp.Keyword("exit").setResultsName("exit")  + TestsuiteDefinition + End)

# DisconnectTestsuite = (str_p("bin_disconnect")[bind(&StartTestsuite)("bin_disconnect")] >> TestsuiteDefinition >> End)[bind(&SetDisconnectSuite)()];
DisconnectTestsuite = pp.Group(pp.Keyword("bin_disconnect").setResultsName("bin_disconnect")  + TestsuiteDefinition + End)

# MultiBinDecisionTestsuite = (str_p("multi_bin_decision")[bind(&StartTestsuite)("multi_bin_decision")] >> TestsuiteDefinition >> End)[bind(&SetMultiBinDecisionSuite)()];
MultiBinDecisionTestsuite = pp.Group(pp.Keyword("multi_bin_decision").setResultsName("multi_bin_decision")  + TestsuiteDefinition + End)

# SpecialTestsuiteSection = DownloadTestsuite| InitTestsuite| PauseTestsuite| AbortTestsuite| ResetTestsuite| ExitTestsuite| DisconnectTestsuite| MultiBinDecisionTestsuite;
SpecialTestsuiteSection = pp.ZeroOrMore(DownloadTestsuite | InitTestsuite | PauseTestsuite | AbortTestsuite |
                                   ResetTestsuite | ExitTestsuite| DisconnectTestsuite| MultiBinDecisionTestsuite)\
    .setResultsName("SpecialTestsuiteSection")
class ParseSpecialTestsuiteSection(object):
    def __init__(self,toks):
        for tok in toks:
            print tok
        sys.exit()
        self.section_name = "test_suites"
SpecialTestsuiteSection.setParseAction(ParseSpecialTestsuiteSection)

# -------------------------------------------------------------------------------------------
# BEGIN BinningSection
# -------------------------------------------------------------------------------------------

# OtherwiseBin = (str_p("otherwise bin") >> '= ' >> BinDefinition >> ';')[bind(&CreateOtherwiseBin)()];
OtherwiseBin = (pp.Keyword("otherwise bin") + EQ + BinDefinition + SEMI)

# BinningSection = str_p("binning") >> *(OtherwiseBin| (BinDefinition >> ';')) >> End;
BinningSection = pp.Group(pp.Keyword("binning") + pp.ZeroOrMore(OtherwiseBin | (BinDefinition + SEMI)) + End)\
    .setResultsName("BinningSection")

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
SetupFiles = (ConfigFile | LevelsFile | TimingFile | VectorFile | AttribFile | ChannelAttribFile | MixedSignalFile |
                      AnalogControlFile| WaveformFile| RoutingFile| TestTableFile| Protocols)

# SetupSection = str_p("context") >> *(SetupFiles) >> End;
SetupSection = pp.Group(pp.Keyword("context") + pp.ZeroOrMore(SetupFiles) + End)\
    .setResultsName("SetupSection")

# -------------------------------------------------------------------------------------------
# BEGIN OOCSection
# -------------------------------------------------------------------------------------------

# OOCSection = str_p("oocrule") >> OOCRule >> End;
OOCSection = pp.Group(pp.Keyword("oocrule") + OOCRule + End)\
    .setResultsName("OOCSection")

# -------------------------------------------------------------------------------------------
# BEGIN HardwareBinSection
# -------------------------------------------------------------------------------------------

# HardBinDescription = (int_p[HardBinDescription.hwBin =  arg1] >> '= ' >> QuotedString[HardBinDescription.description =  arg1] >> ';')[bind(&SetHardBinDescription)(HardBinDescription.hwBin, HardBinDescription.description)];
HardBinDescription = (integer + EQ + QuotedString + SEMI)

# HardwareBinSection = str_p("hardware_bin_descriptions") >> *(HardBinDescription) >> End;
HardwareBinSection = pp.Group(pp.Keyword("hardware_bin_descriptions") + pp.ZeroOrMore(HardBinDescription) + End)\
    .setResultsName("HardwareBinSection")

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
                          UserprocedureSection | # TODO: UserprocedureSection is untested code and may need debugging
                          TestsuiteSection |
                          TestflowSection |
                          SpecialTestsuiteSection |
                          BinningSection |
                          SetupSection |
                          OOCSection |
                          HardwareBinSection + pp.Optional(Sections))

# Start = OptFileHeader[Start.isUTMBased=false] >> OptRevision >> Sections;
Start = OptFileHeader + OptRevision + Sections

# DebugSections = pp.Forward()
# DebugSections << TestsuiteSection
# Start = (OptFileHeader + OptRevision + InformationSection + DeclarationSection + pp.Optional(ImplicitDeclarationSection)
#          + FlagSection + pp.Optional(TestfunctionSection) + TestmethodParameterSection + TestmethodLimitSection
#          + TestmethodSection + pp.Optional(UserprocedureSection) + TestsuiteSection + pp.ZeroOrMore(SpecialTestsuiteSection)
#          + pp.ZeroOrMore(TestflowSection) + BinningSection + SetupSection + pp.Optional(OOCSection) + HardwareBinSection)


from print_debug import *
import sys

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 1:
        print "usage: (python) testflow.py <input file>"
        exit()
    print '\n\n'

    f = open(args[0])
    result = Start.parseFile(f)
    f.close()
    for section in result:
        print section
