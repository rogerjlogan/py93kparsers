__author__ = 'Roger'

import pyparsing as pp

SEMI = pp.Literal(';').suppress()

E = pp.CaselessLiteral("E")
UNDERSCORE = pp.Literal('_')

number = pp.Word(pp.nums)
plusorminus = pp.Literal('+') | '-'
integer = pp.Combine(pp.Optional(plusorminus) + number)
Float = pp.Combine(integer +
        pp.Optional('.' + pp.Optional(number)) +
        pp.Optional(E + integer))
Bool = pp.Literal('0') | '1'

# BinaryAdd = str_p("+") | "-"  ;
BinaryAdd  = pp.Literal('+') | '-'

# BinaryMult = str_p("*") | "/"  ;
BinaryMult = pp.Literal('*') | '/'

# BinaryRel = str_p("==") |  "!="  | "<="  | ">="  | "<"   | ">";
BinaryRel = pp.Literal('==') | '!=' | '<=' | '>=' | '<' | '>'

# BinaryLogic = str_p("or") | "and" ;
BinaryLogic = pp.Keyword("or") | pp.Keyword("and")

# Unary = str_p("!") | "-"  | "not";
Unary = pp.Literal('!') | '-' | "not"

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
NumberFunction  = pp.Keyword("pass") |  pp.Keyword("fail") |  pp.Keyword("has_run") |  pp.Keyword("has_not_run") |\
                  pp.Keyword("tf_result") |  pp.Keyword("tf_pin_result") |  pp.Keyword("spst_timing") |\
                  pp.Keyword("spst_level") |  pp.Keyword("svlr_timing") |  pp.Keyword("svlr_level") |\
                   pp.Keyword("wsus") |  pp.Keyword("bsus") |  pp.Keyword("lsus") |  pp.Keyword("tsus")

# StringFunction = str_p("burstfirst") | "burstnext";
StringFunction = pp.Keyword("burstfirst") | pp.Keyword("burstnext")

# Number = real_p | int_p;
Number = Float | integer

# End = str_p("end");
End = pp.Keyword("end")

# Identifier = lexeme_d[(*((alnum_p | ch_p('_')))) - (str_p("end"))];
Identifier = pp.Word(pp.alphanums + "_")

# TestsuiteFlag = ch_p('@') >> (Identifier >> "." >> Identifier)[TestsuiteFlag.varName = construct_<string>(arg1, arg2)];
TestsuiteFlag = '@' + pp.Group(Identifier + "." + Identifier)


# Variable = str_p("@") >> (Identifier)[Variable.varName = construct_<string>(arg1, arg2)] |
#                  "@{" >> (Identifier)[Variable.varName = construct_<string>(arg1, arg2)] >> "}";
Variable = "@" + Identifier | "@{" + Identifier + "}"


# String = (alnum_p - ch_p('!')) >> *(alnum_p | "_");
String = pp.Combine(pp.Word(pp.alphanums,excludeChars='!') + pp.ZeroOrMore(pp.Word(pp.alphanums) | "_"))

# QuotedString << ch_p('"') >> lexeme_d[(*(lex_escape_ch_p - ch_p('"')))]
#                [QuotedString.noQuotes = construct_<string>(arg1, arg2)] >> ch_p('"') >> !QuotedString;
QuotedString = pp.Forward()

QuotedString << pp.Combine(pp.QuotedString(quoteChar = '"', escChar = '\\') + pp.Optional(QuotedString))

# Literal = Number | TestsuiteFlag | Variable | QuotedString | String;
Literal = Number | TestsuiteFlag | Variable | QuotedString | String

# Term = "(" >> Expression >> ")" | NumberFunction >>  "(" >> !((Expression) >> *( "," >> (Expression))) >> ")"
# | StringFunction >>  "(" >> !((Expression) >> *( "," >> (Expression))) >> ")" | Unary >> Term | Literal;
Term = pp.Forward()
Term << "(" + Expression + ")" | NumberFunction +  "(" + pp.Optional( (Expression) + pp.ZeroOrMore("," + (Expression))) +\
        ")" | StringFunction +  "(" + pp.Optional( (Expression) + pp.ZeroOrMore("," + (Expression))) + ")" | Unary + Term | Literal

BinaryRelTerm << Term + pp.ZeroOrMore(BinaryRel + BinaryRelTerm)

# QualifiedIdentifier = Variable[QualifiedIdentifier.varName = arg1] |
#     Identifier[QualifiedIdentifier.varName = construct_<string>(arg1, arg2)];
QualifiedIdentifier = Variable | Identifier

# TestsuiteFlag = ch_p('@') >> (Identifier >> "." >> Identifier)[TestsuiteFlag.varName = construct_<string>(arg1, arg2)];
TestsuiteFlag = '@' + pp.Group(Identifier + "." + Identifier)


# Type = str_p("double")[Type.type = ::xoc::tapi::ZTestflowVariableType_DOUBLE] |
#      str_p("string")[Type.type = ::xoc::tapi::ZTestflowVariableType_STRING];
Type = pp.Keyword("double") | pp.Keyword("string")

# OptFileHeader = !str_p("hp93000,testflow,0.1");
OptFileHeader = pp.Optional(pp.Keyword("hp93000,testflow,0.1"))

# OptRevision = !(str_p("language_revision") >> ch_p('=') >> int_p >> ch_p(';'));
OptRevision = pp.Group(pp.Optional(pp.Keyword("language_revision")) + pp.Literal('=').suppress() + pp.Word(pp.nums) + SEMI)

# EmptySection = ch_p(';');
EmptySection = ';'

# DeviceName = str_p("device_name") >> '=' >> (QuotedString)[bind(&SetDeviceName)(arg1)] >> ';';
DeviceName = pp.Keyword("device_name") + '=' + (QuotedString) + ';'

# DeviceRevision = str_p("device_revision") >> '=' >> QuotedString[bind(&SetDeviceRevision)(arg1)] >> ';';
DeviceRevision = pp.Keyword("device_revision") + '=' + QuotedString + ';'

# TestRevision = str_p("test_revision") >> '=' >> QuotedString[bind(&SetTestRevision)(arg1)] >> ';';
TestRevision = pp.Keyword("test_revision") + '=' + QuotedString + ';'

# Description = str_p("description") >> '=' >> QuotedString[bind(&SetDescription)(arg1)] >> ';';
Description = pp.Keyword("description") + '=' + QuotedString + ';'

# Application = str_p("application") >> '=' >> QuotedString[bind(&SetApplication)(arg1)] >> ';';
Application = pp.Keyword("application") + '=' + QuotedString + ';'

# Temperature = str_p("temperature") >> '=' >> real_p[bind(&SetTemperature)] >> ';';
Temperature = pp.Keyword("temperature") + '=' + Float + ';'


# InformationElements = *(DeviceName | DeviceRevision | TestRevision | Description | Application | Temperature);
InformationElements = pp.ZeroOrMore(DeviceName | DeviceRevision | TestRevision | Description | Application | Temperature)


# InformationSection = str_p("information") >> InformationElements >> End;
InformationSection = pp.Keyword("information") + InformationElements + End

# Declaration = (Variable[Declaration.varName = arg1] >> ':' >> Type[Declaration.varType = arg1] >> ';' )
#                [bind(&CreateImplicitVariable)(Declaration.varName, Declaration.varType)];
Declaration = pp.Group(Variable + ':' + Type + ';')

# ImplicitDeclarations = (*Declaration);
ImplicitDeclarations = pp.ZeroOrMore(Declaration)

# ImplicitDeclarationSection = str_p("implicit_declarations") >> ImplicitDeclarations >> End;
ImplicitDeclarationSection = pp.Keyword("implicit_declarations") + ImplicitDeclarations + End

# Definition = (Variable[Definition.varName = arg1] >> '=' >> Expression[Definition.value = arg1] >> ';')
#              [bind(&CreateVariable)(Definition.varName, Definition.value)];
# Definition = pp.Group(Variable + '=' + Expression + ';')
Definition = pp.Group(Variable + '=' + Expression + ';')

# Declarations = (*Definition);
Declarations = pp.ZeroOrMore(Definition)

# DeclarationSection = str_p("declarations") >> Declarations >> End;
DeclarationSection = pp.Keyword("declarations") + Declarations + End


# SystemFlag = *(alnum_p | ch_p('_')) >> '=' >> *(alnum_p | '-') >> ';';
SystemFlag = pp.Word(pp.alphanums + '_') + '=' + pp.Word(pp.alphanums + '-') + ';'

# UserFlag = (str_p("user") >> (alpha_p >> *(alnum_p | '_'))[UserFlag.varName = construct_<string>(arg1, arg2)]
#            >> '=' >> Expression[UserFlag.value = arg1] >> ';')
#            [bind(&CreateUserVariable)(UserFlag.varName, UserFlag.value)];
UserFlag = pp.Group(pp.Keyword("user") + (pp.alphas + pp.Word(pp.alphanums + '_')) + '=' + Expression + ';')

# //Systemflags are ignored for now, as they are still handled by the flag_ui
# Flags = *(UserFlag | SystemFlag);
Flags = pp.ZeroOrMore(UserFlag | SystemFlag)


# FlagSection = str_p("flags") >> Flags >> End;
FlagSection = pp.Keyword("flags") + Flags + End

# TestfunctionDescription = str_p("testfunction_description") >> '=' >> QuotedString[Testfunction.description = arg1] >> ';';
TestfunctionDescription = pp.Keyword("testfunction_description") + '=' + QuotedString + ';'

# TestfunctionParameter = str_p("testfunction_parameters")  >> '=' >> QuotedString[Testfunction.parameters = arg1] >> ';';
TestfunctionParameter = pp.Keyword("testfunction_parameters")  + '=' + QuotedString + ';'

# TestmethodParameter = ((Identifier)[bind(&StartTestmethod)(construct_<string>(arg1, arg2))] >> ch_p(':') >>
#                       *((QuotedString[TestmethodParameter.name = arg1] >> '=' >> QuotedString[TestmethodParameter.value = arg1])
#                       [bind(&AddTestmethodParameter)(TestmethodParameter.name, TestmethodParameter.value)] >> ';'))
#                       [bind(&SetTestmethodParameters)()];
TestmethodParameter = pp.Group(Identifier + ':' + pp.ZeroOrMore((QuotedString + '=' + QuotedString) + ';'))

# TestfunctionDefinition = ((TestfunctionDescription >> TestfunctionParameter) | (TestfunctionParameter >> TestfunctionDescription));
TestfunctionDefinition = pp.Group((TestfunctionDescription + TestfunctionParameter) | (TestfunctionParameter + TestfunctionDescription))

# Testfunction = ((Identifier)[Testfunction.identifier = construct_<string>(arg1, arg2)] >> ':'>> TestfunctionDefinition)
#                [bind(&CreateTestfunction)(Testfunction.identifier, Testfunction.description, Testfunction.parameters)];
Testfunction = (Identifier + ':' + TestfunctionDefinition)

# Testfunctions = *(Testfunction) >> End;
Testfunctions = pp.ZeroOrMore(Testfunction) + End

# TestfunctionSection = str_p("testfunctions") >> Testfunctions;
TestfunctionSection = pp.Keyword("testfunctions") + Testfunctions

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
TestmethodParameterSection = pp.Keyword("testmethodparameters") + UTMTestmethodParameters + End

# LowLimitSymbol = ch_p('"') >> (str_p("NA")[TestmethodLimit.loSym = ::xoc::tapi::ZLimitSymbol_DONT_CARE] |
#                                str_p("GT")[TestmethodLimit.loSym = ::xoc::tapi::ZLimitSymbol_GREATER] |
#                                str_p("GE")[TestmethodLimit.loSym = ::xoc::tapi::ZLimitSymbol_GREATER_EQUAL])
#                            >> ch_p('"');
LowLimitSymbol = pp.Literal('"').suppress() + pp.Group(pp.Keyword("NA") | pp.Keyword("GT") | pp.Keyword("GE")) + pp.Literal('"').suppress()

# HighLimitSymbol = ch_p('"') >> (str_p("NA")[TestmethodLimit.loSym = ::xoc::tapi::ZLimitSymbol_DONT_CARE] |
#                                 str_p("LT")[TestmethodLimit.loSym = ::xoc::tapi::ZLimitSymbol_LESSER] |
#                                 str_p("LE")[TestmethodLimit.loSym = ::xoc::tapi::ZLimitSymbol_LESSER_EQUAL])
#                             >> ch_p('"');
HighLimitSymbol = pp.Literal('"').suppress() + pp.Group(pp.Keyword("NA") | pp.Keyword("LT") | pp.Keyword("LE")) + pp.Literal('"').suppress()

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
TestmethodLimit = pp.Group(Identifier + ':'
                           + pp.ZeroOrMore((QuotedString + '='
                           + QuotedString + ':'
                           + LowLimitSymbol + ':'
                           + QuotedString + ':'
                           + HighLimitSymbol + ':'
                           + QuotedString + ':'
                           + QuotedString + ':'
                           + QuotedString + ';')))

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
TestmethodLimitSection = pp.Keyword("testmethodlimits") + UTMTestmethodLimits + End

# UTMTestmethodClass = str_p("testmethod_class") >> '=' >> QuotedString[Testmethod.Class = arg1] >> ';';
UTMTestmethodClass = pp.Keyword("testmethod_class") + '=' + QuotedString + ';'

# TestmethodClass = str_p("testmethod_class") >> '=' >> QuotedString[Testmethod.Class = arg1] >> ';';
TestmethodClass = pp.Keyword("testmethod_class") + '=' + QuotedString + ';'

# TestmethodId = str_p("testmethod_id") >> '=' >> (String[Testmethod.methodId = construct_<string>(arg1, arg2)] |
#                QuotedString[Testmethod.methodId = arg1]) >> ';';
TestmethodId = pp.Keyword("testmethod_id") + '=' + (String | QuotedString) + ';'

# TestmethodParameters = str_p("testmethod_parameters") >> '=' >> QuotedString[Testmethod.parameter = arg1] >> ';';
TestmethodParameters = pp.Keyword("testmethod_parameters") + '=' + QuotedString + ';'

# TestmethodLimits = str_p("testmethod_limits") >> '=' >> QuotedString[Testmethod.limits = arg1] >> ';';
TestmethodLimits = pp.Keyword("testmethod_limits") + '=' + QuotedString + ';'

# TestmethodName = str_p("testmethod_name") >> '=' >> QuotedString[Testmethod.name = arg1] >> ';';
TestmethodName = pp.Keyword("testmethod_name") + '=' + QuotedString + ';'

# TestmethodDefinition = (TestmethodClass | TestmethodId | TestmethodParameters | TestmethodLimits | TestmethodName ) >> !TestmethodDefinition;
TestmethodDefinition = pp.Forward()
TestmethodDefinition << pp.Group((TestmethodClass |
                                 TestmethodId |
                                 TestmethodParameters |
                                 TestmethodLimits |
                                 TestmethodName) + pp.Optional(TestmethodDefinition))


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
Testmethod = pp.Group(Identifier + ':' + UTMTestmethodClass | TestmethodDefinition)

# Testmethods = *(Testmethod) >> End;
Testmethods = pp.ZeroOrMore(Testmethod) + End

# TestmethodSection = str_p("testmethods") >> Testmethods;
TestmethodSection = pp.Keyword("testmethods") + Testmethods

# Userprocedure = ((Identifier)[Userprocedure.identifier = construct_<string>(arg1, arg2)] >> ':' >>
#                 str_p("user_procedure") >> '=' >> QuotedString[Userprocedure.commandline = arg1] >> ';')
#                 [bind(&CreateUserprocedure)(Userprocedure.identifier, Userprocedure.commandline)];
Userprocedure = pp.Group(Identifier + ':' + pp.Keyword("user_procedure") + '=' + QuotedString + ';')

# Userprocedures = *(Userprocedure) >> End;
Userprocedures = pp.ZeroOrMore(Userprocedure) + End

# UserprocedureSection = str_p("tests") >> Userprocedures;
UserprocedureSection = pp.Keyword("tests") + Userprocedures

# TestsuiteName = Identifier >> *ch_p(' ') >> ':';
TestsuiteName = Identifier + pp.ZeroOrMore(' ') + ':'


# TestsuiteTest = (str_p("override_testf") >> '=' >> Identifier[bind(&SetTestsuiteTest)(construct_<string>(arg1, arg2))] >>';') |
#                 (str_p("tests") >> '=' >> Identifier[bind(&SetTestsuiteTest)(construct_<string>(arg1, arg2))] >> ';');
TestsuiteTest = (pp.Keyword("override_testf") + '=' + Identifier +';') |  (pp.Keyword("tests") + '=' + Identifier + ';')

# TestsuiteOverride = str_p("override") >> '=' >> int_p >> ';';
TestsuiteOverride = pp.Keyword("override") + '=' + integer + ';'

# TestsuiteTimEquSet = str_p("override_tim_equ_set") >> '=' >> Expression[bind(&SetTestsuiteTimEquSet)(arg1)] >> ';';
TestsuiteTimEquSet = pp.Keyword("override_tim_equ_set") + '=' + Expression + ';'

# TestsuiteLevEquSet = str_p("override_lev_equ_set") >> '=' >> Expression[bind(&SetTestsuiteLevEquSet)(arg1)] >> ';';
TestsuiteLevEquSet = pp.Keyword("override_lev_equ_set") + '=' + Expression + ';'

# TestsuiteTimSpecSet = str_p("override_tim_spec_set") >> '=' >> Expression[bind(&SetTestsuiteTimSpecSet)(arg1)] >> ';';
TestsuiteTimSpecSet = pp.Keyword("override_tim_spec_set") + '=' + Expression + ';'

# TestsuiteLevSpecSet = str_p("override_lev_spec_set") >> '=' >> Expression[bind(&SetTestsuiteLevSpecSet)(arg1)] >> ';';
TestsuiteLevSpecSet = pp.Keyword("override_lev_spec_set") + '=' + Expression + ';'

# TestsuiteTimSet = str_p("override_timset") >> '=' >> Expression[bind(&SetTestsuiteTimSet)(arg1)] >> ';';
TestsuiteTimSet = pp.Keyword("override_timset") + '=' + Expression + ';'

# TestsuiteLevSet = str_p("override_levset") >> '=' >> Expression[bind(&SetTestsuiteLevSet)(arg1)] >> ';';
TestsuiteLevSet = pp.Keyword("override_levset") + '=' + Expression + ';'

# TestsuiteSequencerLabel = str_p("override_seqlbl") >> '=' >> Expression[bind(&SetTestsuiteSequencerLabel)(arg1)] >> ';';
TestsuiteSequencerLabel = pp.Keyword("override_seqlbl") + '=' + Expression + ';'

# //Ignore this for now, because flag_ui handles the flags
# TestsuiteFlags = str_p("local_flags") >> '=' >> list_p(Identifier[bind(&SetTestsuiteFlag)(construct_<string>(arg1, arg2))], ch_p(',')) >> ';';
TestsuiteFlags = pp.Keyword("local_flags") + '=' + pp.OneOrMore(Identifier + ',') + ';'

# SiteControlExpression = (str_p("\"serial:\"")[SiteControlExpression.type = ::xoc::tapi::ZSiteSequenceType_SERIAL] |
#                          str_p("\"parallel:\"")[SiteControlExpression.type = ::xoc::tapi::ZSiteSequenceType_PARALLEL] |
#                         (str_p("\"semiparallel:")[SiteControlExpression.type = ::xoc::tapi::ZSiteSequenceType_SEMIPARALLEL] >>
#                          int_p[bind(&NewSiteControlArgument)(arg1)] >> ':' >> int_p[bind(&NewSiteControlArgument)(arg1)] >> !ch_p(':') >> '"')|
#                         (str_p("\"other:")[SiteControlExpression.type = ::xoc::tapi::ZSiteSequenceType_OTHER] >>
#                          list_p.direct(int_p[bind(&NewSiteControlArgument)(arg1)], ch_p(':')) >> !ch_p(':') >> ch_p('"')))
#                         [bind(&SetTestsuiteSiteControl)(SiteControlExpression.type)];
SiteControlExpression = (pp.Keyword("serial:") | pp.Keyword("parallel:") |
                        (pp.Keyword("semiparallel:") + integer + ':' + integer + pp.Optional(':') + '"') |
                        (pp.Keyword("other:") + pp.Optional(integer + ':') + pp.Optional(':') + '"'))

# TestsuiteSiteControl = str_p("site_control")[bind(&ClearSiteControlArguments)()] >> '=' >> SiteControlExpression >> ';';
TestsuiteSiteControl = pp.Keyword("site_control") + '=' + SiteControlExpression + ';'

# TestsuiteFFCCount = str_p("ffc_on_fail") >> '=' >> int_p[bind(&SetTestsuiteFFCCount)(arg1)] >> ';';
TestsuiteFFCCount = pp.Keyword("ffc_on_fail") + '=' + integer + ';'

# TestsuiteTestLevel = str_p("test_level") >> '=' >> int_p[bind(&SetTestsuiteTestLevel)(arg1)] >> ';';
TestsuiteTestLevel = pp.Keyword("test_level") + '=' + integer + ';'

# TestsuiteDPSSet = str_p("override_dpsset") >> '=' >> Expression[bind(&SetTestsuiteDPSSet)(arg1)] >> ';';
TestsuiteDPSSet = pp.Keyword("override_dpsset") + '=' + Expression + ';'

# TestsuiteTestNumber = str_p("override_test_number") >> '=' >> Expression[bind(&SetTestsuiteTestNumber)(arg1)] >> ';';
TestsuiteTestNumber = pp.Keyword("override_test_number") + '=' + Expression + ';'

# TestsuiteAnalogSet = str_p("override_anaset") >> '=' >> Expression[bind(&SetTestsuiteAnalogSet)(arg1)] >> ';';
TestsuiteAnalogSet = pp.Keyword("override_anaset") + '=' + Expression + ';'

# TestsuiteSiteMatch = str_p("site_match") >> '=' >> int_p[bind(&SetTestsuiteSiteMatch)(arg1)] >> ';';
TestsuiteSiteMatch = pp.Keyword("site_match") + '=' + integer + ';'

# TestsuiteWaveformSet = str_p("override_wvfset") >> '=' >> Expression[bind(&SetTestsuiteWaveformSet)(arg1)] >> ';';
TestsuiteWaveformSet = pp.Keyword("override_wvfset") + '=' + Expression + ';'

# TestsuiteComment = str_p("comment") >> '=' >> QuotedString[bind(&SetTestsuiteComment)(arg1)] >> ';';
TestsuiteComment = pp.Keyword("comment") + '=' + QuotedString + ';'

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
TestsuiteDefinition << pp.Group((TestsuiteTest |
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
                       TestsuiteComment) + pp.Optional(TestsuiteDefinition))

# Testsuite = (TestsuiteName [bind(&StartTestsuite)(construct_<string>(arg1, arg2-1))]) >> TestsuiteDefinition;
Testsuite = TestsuiteName + TestsuiteDefinition

# Testsuites = *(Testsuite);
Testsuites = pp.ZeroOrMore(Testsuite)

# TestsuiteSection = str_p("test_suites") >> Testsuites  >> End;
TestsuiteSection = pp.Keyword("test_suites") + Testsuites  + End

# RunStatement = (str_p("run") >> ch_p('(') >> Identifier[RunStatement.testsuite = construct_<string>(arg1, arg2)] >> ')' >> ';')
#                [bind(&CreateRunStatement)(RunStatement.testsuite)];
RunStatement = pp.Group(pp.Keyword("run") + '(' + Identifier + ')' + ';')

FlowStatements = pp.Forward()

# RunAndBranchStatement = (str_p("run_and_branch") >> ch_p('(') >> Identifier[RunAndBranchStatement.testsuite = construct_<string>(arg1, arg2)] >> ')'
#                         >> str_p("then"))[bind(&CreateRunAndBranchStatement)(RunAndBranchStatement.testsuite)] >> str_p("{") [bind(&EnterSubBranch)(0)]
#                         >> FlowStatements >> str_p("}") [bind(&LeaveSubBranch)()] >> !(str_p("else")
#                         >> str_p("{") [bind(&EnterSubBranch)(1)] >> FlowStatements >> str_p("}") [bind(&LeaveSubBranch)()]);
RunAndBranchStatement = pp.Group((pp.Keyword("run_and_branch") + '(' + Identifier + ')' + pp.Keyword("then")) + "{" +
                                 FlowStatements + "}" + pp.Optional(pp.Keyword("else")  + "{"  + FlowStatements + "}"))

# IfStatement = (str_p("if") >> Expression[IfStatement.condition = arg1] >> str_p("then") )
#               [bind(&CreateIfStatement)(IfStatement.condition)]
#               >> (str_p("{")) [bind(&EnterSubBranch)(0)] >> FlowStatements >> (str_p("}")) [bind(&LeaveSubBranch)()]
#               >> !(str_p("else") >> (str_p("{")) [bind(&EnterSubBranch)(1)] >> FlowStatements >> (str_p("}")) [bind(&LeaveSubBranch)()]);
IfStatement = pp.Group((pp.Keyword("if") + Expression + pp.Keyword("then") ) + "{" + FlowStatements + "}" +
                       pp.Optional(pp.Keyword("else") + "{" + FlowStatements + "}"))

# GroupBypass = str_p("groupbypass") >> ',';
GroupBypass = pp.Keyword("groupbypass") + ','

# GroupStatement = str_p("{") [bind(&CreateGroupStatement)(), bind(&EnterSubBranch)(0)]
#                  >> FlowStatements >> str_p("}") [bind(&LeaveSubBranch)()] >> ','
#                  >> (GroupBypass[bind(&SetGroupBypass)()] |
#                 str_p("")[bind(&SetGroupNoBypass)()]) >> (str_p("open")[bind(&SetGroupOpen)()] |
#                 str_p("closed")[bind(&SetGroupClosed)()]) >> ',' >> (QuotedString) [bind(&SetGroupLabel)(arg1)]
#                 >> ',' >> (QuotedString) [bind(&SetGroupDescription)(arg1)];
GroupStatement = pp.Group("{" + FlowStatements + "}" + ',' + pp.Optional(GroupBypass) + (pp.Keyword("open") |
                pp.Keyword("closed")) + ',' + QuotedString + ',' + QuotedString)

# AssignmentStatement = (( TestsuiteFlag[AssignmentStatement.varName = arg1] |  Variable[AssignmentStatement.varName = arg1])
#                       >> '=' >> (Expression[AssignmentStatement.value = arg1] | TestsuiteFlag[AssignmentStatement.value = arg1])
#                       >> ';') [bind(&CreateAssignmentStatement)(AssignmentStatement.varName, AssignmentStatement.value)];
AssignmentStatement = pp.Group(( TestsuiteFlag |  Variable) + '=' + (Expression | TestsuiteFlag) + ';')

# OOCRule = !(str_p("oocwarning") >> '=' >> int_p >> int_p >> int_p >> QuotedString) >> !(str_p("oocstop") >> '=' >> int_p >> int_p >> int_p >> QuotedString);
OOCRule = pp.Group(pp.Optional(pp.Keyword("oocwarning") + '=' + integer + integer + integer + QuotedString) +
                   pp.Optional(pp.Keyword("oocstop") + '=' + integer + integer + integer + QuotedString))

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
Color = pp.Group(integer | pp.Keyword("black") | pp.Keyword("white") | pp.Keyword("red") | pp.Keyword("yellow") |
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
BinDefinition = pp.Group(QuotedString + ',' + QuotedString + ',' + pp.Optional(OOCRule) + ',' + pp.Optional(Quality)
                  + ','  + pp.Optional(Reprobe) + ',' + Color + ',' + pp.Optional(BinNumber) + ',' + pp.Optional(Overon)
                  | (QuotedString + ',' + QuotedString + ',' + pp.Optional(Quality) + ',' + pp.Optional(Reprobe) + ',' + Color
                  + ',' + pp.Optional(BinNumber) + ',' + pp.Optional(Overon)))


# StopBinStatement = (str_p("stop_bin") >> (BinDefinition("", "", false, false, ::xoc::tapi::ZBinColor_BLACK, -1, false)) >> ';')
#                    [bind(&CreateStopBinStatement)()];
StopBinStatement = pp.Group(pp.Keyword("stop_bin") + BinDefinition + ';')



# PrintStatement = (str_p("print") >> '(' >> Expression[PrintStatement.statement = arg1] >> ')' >> ';')
#                  [bind(&CreatePrintStatement)(PrintStatement.statement)];
PrintStatement = pp.Group(pp.Keyword("print") + '(' + Expression + ')' + ';')

# PrintDatalogStatement = (str_p("print_dl") >> '(' >> Expression[PrintDatalogStatement.statement = arg1] >> ')' >> ';')
#                         [bind(&CreatePrintDatalogStatement)(PrintDatalogStatement.statement)];
PrintDatalogStatement = pp.Group(pp.Keyword("print_dl") + '(' + Expression + ')' + ';')

# SVLRTimingStatement = (str_p("svlr_timing_command") >> '(' >> Expression[SVLRTimingStatement.equSet = arg1] >> ','
#                       >> Expression[SVLRTimingStatement.specSet = arg1] >> ',' >> QuotedString[SVLRTimingStatement.variable = arg1]
#                       >> ',' >> Expression[SVLRTimingStatement.value = arg1] >> ')' >> ';')
#                       [bind(&CreateSVLRTimingStatement)(SVLRTimingStatement.equSet, SVLRTimingStatement.specSet,
#                                                         SVLRTimingStatement.variable, SVLRTimingStatement.value)];
SVLRTimingStatement = pp.Group(pp.Keyword("svlr_timing_command") + '(' + Expression + ',' + Expression + ',' + QuotedString + ',' + Expression + ')' + ';')

# SVLRLevelStatement = (str_p("svlr_level_command") >> '(' >> Expression[SVLRLevelStatement.equSet = arg1] >> ',' >> Expression[SVLRLevelStatement.specSet = arg1]
#                       >> ',' >> QuotedString[SVLRLevelStatement.variable = arg1] >> ',' >> Expression[SVLRLevelStatement.value = arg1] >> ')' >> ';')
#                     [bind(&CreateSVLRLevelStatement)(SVLRLevelStatement.equSet, SVLRLevelStatement.specSet, SVLRLevelStatement.variable, SVLRLevelStatement.value)];
SVLRLevelStatement = pp.Group(pp.Keyword("svlr_level_command") + '(' + Expression + ',' + Expression + ',' + QuotedString + ',' + Expression + ')' + ';')

# TestNumLoopInc = str_p("test_number_loop_increment") >> '=' >> Expression[TestNumLoopInc.expression = arg1];
TestNumLoopInc = pp.Keyword("test_number_loop_increment") + '=' + Expression

# WhileStatement = (str_p("while") >> Expression [WhileStatement.condition = arg1, WhileStatement.testnum = construct_<string>("")] >> str_p("do")
#                  >> !(TestNumLoopInc [WhileStatement.testnum = arg1])) [bind(&CreateWhileStatement)(WhileStatement.condition, WhileStatement.testnum)]
#                  >> str_p("{") [bind(&EnterSubBranch)(0)] >> FlowStatements >> str_p("}") [bind(&LeaveSubBranch)()];
WhileStatement = pp.Group((pp.Keyword("while") + Expression + pp.Keyword("do") + pp.Optional(TestNumLoopInc)) + "{" + FlowStatements + "}")

# RepeatStatement = str_p("repeat") [bind(&CreateRepeatStatement)(), bind(&EnterSubBranch)(0)] >> FlowStatements >> str_p("until") [bind(&LeaveSubBranch)()]
#                   >> Expression [bind(&SetRepeatCondition)(arg1)] >> !(TestNumLoopInc [bind(&SetRepeatTestnum)(arg1)]);
RepeatStatement = pp.Group(pp.Keyword("repeat") + FlowStatements + pp.Keyword("until") + Expression + pp.Optional(TestNumLoopInc))

# ForStatement = (str_p("for")[ForStatement.testnum = construct_<string>("")] >> QualifiedIdentifier[ForStatement.assignVar = arg1]
#                >> '=' >> Expression[ForStatement.assignValue = arg1] >> ';' >> Expression[ForStatement.condition = arg1]
#                >> ';' >> QualifiedIdentifier[ForStatement.incrementVar = arg1] >> '=' >> Expression[ForStatement.incrementValue = arg1]
#                >> ';' >> str_p("do") >> !(TestNumLoopInc [ForStatement.testnum = arg1]))
#                [bind(&CreateForStatement)(ForStatement.assignVar, ForStatement.assignValue, ForStatement.condition, ForStatement.incrementVar,
#                                           ForStatement.incrementValue, ForStatement.testnum)]
#                >> str_p("{") [bind(&EnterSubBranch)(0)] >> FlowStatements >> str_p("}") [bind(&LeaveSubBranch)()];
ForStatement = pp.Group((pp.Keyword("for") + QualifiedIdentifier + '=' + Expression + ';' + Expression + ';' + QualifiedIdentifier +
                         '=' + Expression + ';' + pp.Keyword("do") + pp.Optional(TestNumLoopInc)) + "{" + FlowStatements + "}")

# MultiBinStatement = str_p("multi_bin")[bind(&CreateMultiBinStatement)()] >> ';';
MultiBinStatement = pp.Keyword("multi_bin") + ';'

# EmptyStatement = ch_p(';');
EmptyStatement = ';'


# TestflowSection = str_p("test_flow")[bind(&FlowSectionStart)()] >> FlowStatements >> End;
TestflowSection = pp.Keyword("test_flow") + FlowStatements + End

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
FlowStatement = pp.Group(RunStatement |
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

# DownloadTestsuite = (str_p("download")[bind(&StartTestsuite)("download")] >> TestsuiteDefinition >> End) [bind(&SetDownloadSuite)()];
DownloadTestsuite = pp.Group(pp.Keyword("download") + TestsuiteDefinition + End)

# InitTestsuite = (str_p("initialize")[bind(&StartTestsuite)("initialize")] >> TestsuiteDefinition >> End )[bind(&SetInitSuite)()];
InitTestsuite = pp.Group(pp.Keyword("initialize") + TestsuiteDefinition + End)

# PauseTestsuite = (str_p("pause")[bind(&StartTestsuite)("pause")] >> TestsuiteDefinition >> End)[bind(&SetPauseSuite)()];
PauseTestsuite = pp.Group(pp.Keyword("pause") + TestsuiteDefinition + End)

# AbortTestsuite = (str_p("abort")[bind(&StartTestsuite)("abort")] >> TestsuiteDefinition >> End)[bind(&SetAbortSuite)()];
AbortTestsuite = pp.Group(pp.Keyword("abort") + TestsuiteDefinition + End)

# ResetTestsuite = (str_p("reset")[bind(&StartTestsuite)("reset")] >> TestsuiteDefinition >> End)[bind(&SetResetSuite)()];
ResetTestsuite = pp.Group(pp.Keyword("reset") + TestsuiteDefinition + End)

# ExitTestsuite = (str_p("exit")[bind(&StartTestsuite)("exit")] >> TestsuiteDefinition >> End)[bind(&SetExitSuite)()];
ExitTestsuite = pp.Group(pp.Keyword("exit") + TestsuiteDefinition + End)

# DisconnectTestsuite = (str_p("bin_disconnect")[bind(&StartTestsuite)("bin_disconnect")] >> TestsuiteDefinition >> End)[bind(&SetDisconnectSuite)()];
DisconnectTestsuite = pp.Group(pp.Keyword("bin_disconnect") + TestsuiteDefinition + End)

# MultiBinDecisionTestsuite = (str_p("multi_bin_decision")[bind(&StartTestsuite)("multi_bin_decision")] >> TestsuiteDefinition >> End)[bind(&SetMultiBinDecisionSuite)()];
MultiBinDecisionTestsuite = pp.Group(pp.Keyword("multi_bin_decision") + TestsuiteDefinition + End)

# SpecialTestsuiteSection = DownloadTestsuite| InitTestsuite| PauseTestsuite| AbortTestsuite| ResetTestsuite| ExitTestsuite| DisconnectTestsuite| MultiBinDecisionTestsuite;
SpecialTestsuiteSection = pp.Group(DownloadTestsuite | InitTestsuite | PauseTestsuite | AbortTestsuite | ResetTestsuite |\
                                   ExitTestsuite| DisconnectTestsuite| MultiBinDecisionTestsuite)

# OtherwiseBin = (str_p("otherwise bin") >> '= ' >> BinDefinition >> ';')[bind(&CreateOtherwiseBin)()];
OtherwiseBin = pp.Group(pp.Keyword("otherwise bin") + '= ' + BinDefinition + ';')

# BinningSection = str_p("binning") >> *(OtherwiseBin| (BinDefinition >> ';')) >> End;
BinningSection = pp.Group(pp.Keyword("binning") + pp.ZeroOrMore(OtherwiseBin | (BinDefinition + ';')) + End)

# ConfigFile = str_p("context_config_file") >> '= ' >> QuotedString [bind(&SetConfigFile)(arg1)] >> ';';
ConfigFile = pp.Group(pp.Keyword("context_config_file") + '= ' + QuotedString + ';')

# LevelsFile = str_p("context_levels_file") >> '= ' >> QuotedString [bind(&SetLevelsFile)(arg1)] >> ';';
LevelsFile = pp.Group(pp.Keyword("context_levels_file") + '= ' + QuotedString + ';')

# TimingFile = str_p("context_timing_file") >> '= ' >> QuotedString [bind(&SetTimingFile)(arg1)] >> ';';
TimingFile = pp.Group(pp.Keyword("context_timing_file") + '= ' + QuotedString + ';')

# VectorFile = str_p("context_vector_file") >> '= ' >> QuotedString [bind(&SetVectorFile)(arg1)] >> ';';
VectorFile = pp.Group(pp.Keyword("context_vector_file") + '= ' + QuotedString + ';')

# AttribFile = str_p("context_attrib_file") >> '= ' >> QuotedString [bind(&SetAttribFile)(arg1)] >> ';';
AttribFile = pp.Group(pp.Keyword("context_attrib_file") + '= ' + QuotedString + ';')

# ChannelAttribFile = str_p("context_channel_attrib_file") >> '= ' >> QuotedString [bind(&SetChannelAttribFile)(arg1)] >> ';';
ChannelAttribFile = pp.Group(pp.Keyword("context_channel_attrib_file") + '= ' + QuotedString + ';')

# MixedSignalFile = str_p("context_mixsgl_file") >> '= ' >> QuotedString [bind(&SetMixedSignalFile)(arg1)] >> ';';
MixedSignalFile = pp.Group(pp.Keyword("context_mixsgl_file") + '= ' + QuotedString + ';')

# AnalogControlFile = str_p("context_analog_control_file") >> '= ' >> QuotedString [bind(&SetAnalogControlFile)(arg1)] >> ';';
AnalogControlFile = pp.Group(pp.Keyword("context_analog_control_file") + '= ' + QuotedString + ';')

# WaveformFile = str_p("context_waveform_file") >> '= ' >> QuotedString [bind(&SetWaveformFile)(arg1)] >> ';';
WaveformFile = pp.Group(pp.Keyword("context_waveform_file") + '= ' + QuotedString + ';')

# RoutingFile = str_p("context_routing_file") >> '= ' >> QuotedString [bind(&SetRoutingFile)(arg1)] >> ';';
RoutingFile = pp.Group(pp.Keyword("context_routing_file") + '= ' + QuotedString + ';')

# TestTableFile = str_p("context_testtable_file") >> '= ' >> QuotedString[bind(&SetTestTableFile)(arg1)] >> ';';
TestTableFile = pp.Group(pp.Keyword("context_testtable_file") + '= ' + QuotedString + ';')

# Protocols = str_p("context_protocols") >> '= ' >> QuotedString[bind(&SetProtocols)(arg1)] >> ';';
Protocols = pp.Group(pp.Keyword("context_protocols") + '= ' + QuotedString + ';')

# SetupFiles = ConfigFile| LevelsFile| TimingFile| VectorFile| AttribFile| ChannelAttribFile| MixedSignalFile| AnalogControlFile| WaveformFile| RoutingFile| TestTableFile| Protocols;
SetupFiles = pp.Group(ConfigFile | LevelsFile | TimingFile | VectorFile | AttribFile | ChannelAttribFile | MixedSignalFile |
                      AnalogControlFile| WaveformFile| RoutingFile| TestTableFile| Protocols)

# SetupSection = str_p("context") >> *(SetupFiles) >> End;
SetupSection = pp.Group(pp.Keyword("context") + pp.ZeroOrMore(SetupFiles) + End)

# OOCSection = str_p("oocrule") >> OOCRule >> End;
OOCSection = pp.Group(pp.Keyword("oocrule") + OOCRule + End)

# HardBinDescription = (int_p[HardBinDescription.hwBin =  arg1] >> '= ' >> QuotedString[HardBinDescription.description =  arg1] >> ';')[bind(&SetHardBinDescription)(HardBinDescription.hwBin, HardBinDescription.description)];
HardBinDescription = pp.Group(integer + '= ' + QuotedString + ';')

# HardwareBinSection = str_p("hardware_bin_descriptions") >> *(HardBinDescription) >> End;
HardwareBinSection = pp.Group(pp.Keyword("hardware_bin_descriptions") + pp.ZeroOrMore(HardBinDescription) + End)

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
Sections << pp.Group(EmptySection |
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

DebugSections = pp.Forward()
DebugSections << DeclarationSection

# Start = OptFileHeader[Start.isUTMBased=false] >> OptRevision >> Sections;
# Start = OptFileHeader + OptRevision + Sections
Start = OptFileHeader + OptRevision + DebugSections


from print_debug import *
import sys

class parse_TestFlow(object):
    def __init__(self, toks):
        for tok in toks:
            pprint(tok)

Start.setParseAction(parse_TestFlow)

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 1:
        print "usage: (python) testflow.py <input file>"
        exit()
    print '\n\n'

    f = open(args[0])
    result = Start.parseFile(f)
    f.close()
