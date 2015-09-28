
#ifndef BOOST_SPIRIT_FILEITERATOR_STD
#define BOOST_SPIRIT_FILEITERATOR_STD
#endif


#include "TestflowParser.hpp"
#include "Actions.hpp"

#include "xoc/tapi/ZTestflowVariableType.hpp"
#include "xoc/tapi/ZSiteSequenceType.hpp"
#include "xoc/tapi/ZBinColor.hpp"
#include "xoc/exc/ZCorrectnessException.hpp"

#include <string>
#include "xoc/zutils.hpp"

#include <streambuf>


//Enable this define to get lots of debugging output from the parser
//#define BOOST_SPIRIT_DEBUG

#ifdef BOOST_SPIRIT_DEBUG
#define BOOST_SPIRIT_DEBUG_OUT std::cerr
#endif

#define PHOENIX_LIMIT 9
#define BOOST_SPIRIT_CLOSURE_LIMIT 9


#define NOUTM 0

#include <boost/spirit/actor.hpp>
#include <boost/spirit.hpp>
#include <boost/spirit/phoenix.hpp>
#include <boost/spirit/dynamic/if.hpp>
#include <boost/spirit/iterator.hpp>
#include <boost/spirit/core.hpp>
#include <boost/spirit/iterator/position_iterator.hpp>
#include <boost/spirit/utility/functor_parser.hpp>


using namespace boost::spirit;
using namespace phoenix;
using namespace std;
using namespace xoc::threads;
using namespace xoc::exc;
using namespace xoc;

std::ostream& operator<<(std::ostream& out, file_position const& lc)
{
    return out <<
            "\nFile:\t" << lc.file <<
            "\nLine:\t" << lc.line <<
            "\nCol:\t" << lc.column << 
      endl;
}


struct overall_closure : boost::spirit::closure<overall_closure, bool>
{
  member1 isUTMBased;
};

struct string_closure : boost::spirit::closure<string_closure, string>
{
  member1 noQuotes;
};

struct variable_closure : boost::spirit::closure<variable_closure, string>
{
  member1 varName;
};

struct expression_closure : boost::spirit::closure<expression_closure, string>
{
  member1 expression;
};

struct type_closure : boost::spirit::closure<type_closure, ::xoc::tapi::ZTestflowVariableType>
{
  member1 type;
};

struct definition_closure : boost::spirit::closure<definition_closure, string, string>
{
  member1 varName;
  member2 value;
};

struct declaration_closure : boost::spirit::closure<declaration_closure, string, ::xoc::tapi::ZTestflowVariableType>
{
  member1 varName;
  member2 varType;
};

struct testfunction_closure : boost::spirit::closure<testfunction_closure, string, string, string>
{
  member1 identifier;
  member2 description;
  member3 parameters;
};

struct testmethod_closure : boost::spirit::closure<testmethod_closure, string, string, string, string, string, string>
{
  member1 identifier;
  member2 Class;
  member3 methodId;
  member4 parameter;
  member5 limits;
  member6 name;
};

struct testmethodparameter_closure : boost::spirit::closure<testmethodparameter_closure, string, string>
{
  member1 name;
  member2 value;
};

struct testmethodlimit_closure : boost::spirit::closure<testmethodlimit_closure, string, string, ::xoc::tapi::ZLimitSymbol, string, ::xoc::tapi::ZLimitSymbol, string, string, string>
{
  member1 name;
  member2 loVal;
  member3 loSym;
  member4 hiVal;
  member5 hiSym;
  member6 unit;
  member7 numOffset;
  member8 numInc;
};

struct userprocedure_closure : boost::spirit::closure<userprocedure_closure, string, string>
{
  member1 identifier;
  member2 commandline;
};

//struct sitecontrol_closure : boost::spirit::closure<sitecontrol_closure, ::xoc::tapi::ZSiteSequenceType, int, int>
struct sitecontrol_closure : boost::spirit::closure<sitecontrol_closure, ::xoc::tapi::ZSiteSequenceType>
{
  member1 type;
};

struct runstatement_closure : boost::spirit::closure<runstatement_closure, string>
{
  member1 testsuite;
};

struct ifstatement_closure : boost::spirit::closure<ifstatement_closure, string>
{
  member1 condition;
};

struct bin_closure : boost::spirit::closure<bin_closure, string, string, bool, bool, ::xoc::tapi::ZBinColor, int, bool>
{
  member1 swBin;
  member2 swBinDescription;  
  member3 quality;
  member4 reprobe;
  member5 color;
  member6 binNumber;
  member7 overon;
};

struct print_closure : boost::spirit::closure<print_closure, string>
{
  member1 statement;
};

struct svlr_closure : boost::spirit::closure<svlr_closure, string, string, string, string>
{
  member1 equSet;
  member2 specSet;
  member3 variable;
  member4 value;
};

struct while_closure : boost::spirit::closure<while_closure, string, string>
{
  member1 condition;
  member2 testnum;
};

struct for_closure : boost::spirit::closure<for_closure, string, string, string, string, string, string>
{
  member1 assignVar;
  member2 assignValue;
  member3 condition;
  member4 incrementVar;
  member5 incrementValue;
  member6 testnum;
};

struct hardbin_closure : boost::spirit::closure<hardbin_closure, int, string>
{
  member1 hwBin;
  member2 description;
};

struct error_report_parser {
    error_report_parser()
    {}

    typedef boost::spirit::nil_t result_t;

    template <typename ScannerT>
    int
    operator()(ScannerT const& scan, result_t& /*result*/) const
    {
      file_position fpos = scan.first.get_position();
      cerr << fpos << endl;

      return -1; // Fail.
    }

};

typedef functor_parser<error_report_parser> error_report_p;

error_report_p Error = 
	error_report_parser();

struct TestflowSyntax : public grammar<TestflowSyntax>
{
  template <typename ScannerT>
  struct definition
  {
    definition(TestflowSyntax const& self)
    {

      Expression =
	BinaryAddTerm[Expression.expression = construct_<string>(arg1, arg2)]
	;
      
      Term =
	"(" >> Expression >> ")"
	| NumberFunction >>  "(" >> !((Expression) >> *( "," >> (Expression))) >> ")"
	| StringFunction >>  "(" >> !((Expression) >> *( "," >> (Expression))) >> ")"
	| Unary >> Term
	| Literal
	;

      BinaryAddTerm =
	BinaryMultTerm >> *(BinaryAdd >> BinaryMultTerm)
	;

      BinaryMultTerm =
	BinaryLogicTerm >> *(BinaryMult >> BinaryLogicTerm)
	;

      BinaryLogicTerm =
	BinaryRelTerm >> *(BinaryLogic >> BinaryRelTerm)
	;

      BinaryRelTerm =
	Term >> *(BinaryRel >> BinaryRelTerm)
	;


      BinaryAdd =
	str_p("+")
	| "-"
	;

      BinaryMult =
	str_p("*")
	| "/"
	;

      BinaryRel =
	str_p("==")
	| "!="
	| "<="
	| ">="
	| "<"
	| ">"

	;

      BinaryLogic =
	str_p("or")
	| "and"
	;

      Unary =
	str_p("!")
	| "-"
	| "not"
	;

      NumberFunction = 
	str_p("pass")
	| "fail"
	| "has_run"
	| "has_not_run"
	| "tf_result"
	| "tf_pin_result"
	| "spst_timing"
	| "spst_level"
	| "svlr_timing"
	| "svlr_level"
	| "wsus"
	| "bsus"
	| "lsus"
  | "tsus" 
	;
      
      StringFunction =
	str_p("burstfirst")
	| "burstnext"
	;

      Literal =
	Number
        | TestsuiteFlag       
        | Variable
                
	| QuotedString
	| String
	;

      Number =
	real_p
	| int_p
	;

      TestsuiteFlag =
        ch_p('@') >> (Identifier >> "." >> Identifier)[TestsuiteFlag.varName = construct_<string>(arg1, arg2)] 
	;

      Variable =
	str_p("@") >> (Identifier)[Variable.varName = construct_<string>(arg1, arg2)]
	| "@{" >> (Identifier)[Variable.varName = construct_<string>(arg1, arg2)] >> "}"
	;

      String =
      (alnum_p - ch_p('!')) >> *(alnum_p | "_")
	;
      End =
	str_p("end") 
	//	!(*(ch_p('-')))
	;

      QuotedString = 
	ch_p('"') >> lexeme_d[(*(lex_escape_ch_p - ch_p('"')))][QuotedString.noQuotes = construct_<string>(arg1, arg2)] >> ch_p('"')
		  >> !QuotedString
	//	confix_p('"', *c_escape_ch_p, '"')
	;

      Identifier =
	lexeme_d[(*((alnum_p | ch_p('_')))) - (str_p("end"))]
	;

      QualifiedIdentifier =
	Variable[QualifiedIdentifier.varName = arg1]
	| Identifier[QualifiedIdentifier.varName = construct_<string>(arg1, arg2)]
	;

      Type = 
	str_p("double")[Type.type = ::xoc::tapi::ZTestflowVariableType_DOUBLE]
	| str_p("string")[Type.type = ::xoc::tapi::ZTestflowVariableType_STRING]
	;

      Start =
	OptFileHeader[Start.isUTMBased=false] >>
	OptRevision >>
	Sections
	;

      OptFileHeader = !str_p("hp93000,testflow,0.1")
	;

      OptRevision = !(str_p("language_revision") >> ch_p('=') >> int_p >> ch_p(';'))
	;

      Sections = 
	(
	 EmptySection
	 | InformationSection
	 | ImplicitDeclarationSection
	 | DeclarationSection
	 | FlagSection
	 | TestfunctionSection
	 | TestmethodParameterSection
	 | TestmethodLimitSection
	 | TestmethodSection
	 | UserprocedureSection
	 | TestsuiteSection
	 | TestflowSection
	 | SpecialTestsuiteSection
	 | BinningSection
	 | SetupSection
	 | OOCSection
	 | HardwareBinSection
	 )
	   >> !Sections
	;

      EmptySection =
	ch_p(';')
	;

      InformationSection = 
	str_p("information")
	  >> InformationElements
	  >> End
	;

      InformationElements =
	*(
	  DeviceName
	  | DeviceRevision
	  | TestRevision
	  | Description
	  | Application
	  | Temperature
	 )
	;

      DeviceName = 
	str_p("device_name") >> '=' >> (QuotedString)[bind(&SetDeviceName)(arg1)] >> ';'
	;

      DeviceRevision =
	str_p("device_revision") >> '=' >> QuotedString[bind(&SetDeviceRevision)(arg1)] >> ';'
	;

      TestRevision =
	str_p("test_revision") >> '=' >> QuotedString[bind(&SetTestRevision)(arg1)] >> ';'
	;

      Description = 
	str_p("description") >> '=' >> QuotedString[bind(&SetDescription)(arg1)] >> ';'
	;

      Application = 
	str_p("application") >> '=' >> QuotedString[bind(&SetApplication)(arg1)] >> ';'
	;

      Temperature =
	str_p("temperature") >> '=' >> real_p[bind(&SetTemperature)] >> ';'
	;

      ImplicitDeclarationSection =
	str_p("implicit_declarations") 
	  >> ImplicitDeclarations
	  >> End
	;

      ImplicitDeclarations =
	(*Declaration)
	;

      Declaration = 
	(
	 Variable[Declaration.varName = arg1]
	 >> ':'
	 >> Type[Declaration.varType = arg1]
	 >> ';'
	 )[bind(&CreateImplicitVariable)(Declaration.varName, Declaration.varType)]
	;

      DeclarationSection =
	str_p("declarations") 
	  >> Declarations
	  >> End
	
	;

      Declarations =
	(*Definition)
	;

      Definition =
	(
	 Variable[Definition.varName = arg1]
	 >> '='
	 >> Expression[Definition.value = arg1]
	 >> ';'
	 )[bind(&CreateVariable)(Definition.varName, Definition.value)]
	;

      FlagSection =
	str_p("flags") 
	  >> Flags
	  >> End
	;

      Flags = 
	*(
	  UserFlag
	  | SystemFlag //Systemflags are ignored for now, as they are still handled by the flag_ui
	  )
	;

      SystemFlag = 
	*(alnum_p | ch_p('_')) >> '=' >> *(alnum_p | '-') >> ';'
	;

      UserFlag = 
	(str_p("user") >> (alpha_p >> *(alnum_p | '_'))[UserFlag.varName = construct_<string>(arg1, arg2)]
		      >> '='
		      >> Expression[UserFlag.value = arg1]
		      >> ';'
	 )
	[bind(&CreateUserVariable)(UserFlag.varName, UserFlag.value)]
	;

      TestfunctionSection =
	str_p("testfunctions")
	  >> Testfunctions
	;

      Testfunctions = 
	*(Testfunction)
	  >> End
	;

      Testfunction =
	(
	 (Identifier)[Testfunction.identifier = construct_<string>(arg1, arg2)] >> ':'
	 >> TestfunctionDefinition
	 )
	[bind(&CreateTestfunction)(Testfunction.identifier, Testfunction.description, Testfunction.parameters)]
	 ;

      TestfunctionDefinition =
	 (
	  (TestfunctionDescription >> TestfunctionParameter)
	  | (TestfunctionParameter >> TestfunctionDescription)
	  )
	;

       TestfunctionDescription =
	str_p("testfunction_description") >> '=' >> QuotedString[Testfunction.description = arg1] >> ';'
	;

      TestfunctionParameter = 
	str_p("testfunction_parameters")  >> '=' >> QuotedString[Testfunction.parameters = arg1] >> ';'
	;

      TestmethodParameterSection =
	str_p("testmethodparameters")[Start.isUTMBased = true]
#if NOUTM
	  >> Error
#else
	  >> UTMTestmethodParameters
	  >> End
#endif
	;

      UTMTestmethodParameters =
	*(TestmethodParameter)
	;

      TestmethodParameter =
	(
	 (Identifier)[bind(&StartTestmethod)(construct_<string>(arg1, arg2))] >> ch_p(':')
	 >>
	 *( 
	   (
	    QuotedString[TestmethodParameter.name = arg1]
	    >> '=' 
	    >> QuotedString[TestmethodParameter.value = arg1]
	    )[bind(&AddTestmethodParameter)(TestmethodParameter.name, TestmethodParameter.value)]
	   >> ';'
	   )
	 )[bind(&SetTestmethodParameters)()]
	;

      
      TestmethodLimitSection =
	str_p("testmethodlimits")[Start.isUTMBased = true, bind(&SetUTMBased)()]
#if NOUTM
	  >> Error
#else
	  >> UTMTestmethodLimits
	  >> End
#endif
	;

      UTMTestmethodLimits =
	*(TestmethodLimit)
	;

      TestmethodLimit =
	(
	 (Identifier)[bind(&StartTestmethod)(construct_<string>(arg1, arg2))] >> ch_p(':')
	 >>
	 *(
	   (
	    QuotedString[TestmethodLimit.name = arg1]
	    >> '='
	    >> QuotedString[TestmethodLimit.loVal = arg1] >> ':'
	    >> LowLimitSymbol >> ':'
	    >> QuotedString[TestmethodLimit.hiVal = arg1] >> ':'
	    >> HighLimitSymbol >> ':'
	    >> QuotedString[TestmethodLimit.unit = arg1] >> ':'
	    >> QuotedString[TestmethodLimit.numOffset = arg1] >> ':'
	    >> QuotedString[TestmethodLimit.numInc = arg1] >> ';')
	   [bind(&AddTestmethodLimit)(TestmethodLimit.name,
				      TestmethodLimit.loVal,
				      TestmethodLimit.loSym,
				      TestmethodLimit.hiVal,
				      TestmethodLimit.hiSym,
				      TestmethodLimit.unit,
				      TestmethodLimit.numOffset,
				      TestmethodLimit.numInc)]
	   )
	 )[bind(&SetTestmethodLimits)()]
	   | Error
	;

      LowLimitSymbol =
	ch_p('"')
	  >> (
	      str_p("NA")[TestmethodLimit.loSym = ::xoc::tapi::ZLimitSymbol_DONT_CARE]
	      | str_p("GT")[TestmethodLimit.loSym = ::xoc::tapi::ZLimitSymbol_GREATER]
	      | str_p("GE")[TestmethodLimit.loSym = ::xoc::tapi::ZLimitSymbol_GREATER_EQUAL]
	      )
	  >> ch_p('"')
	;

      HighLimitSymbol =
	ch_p('"')
	  >> (
	      str_p("NA")[TestmethodLimit.hiSym = ::xoc::tapi::ZLimitSymbol_DONT_CARE]
	      | str_p("LT")[TestmethodLimit.hiSym = ::xoc::tapi::ZLimitSymbol_LESSER]
	      | str_p("LE")[TestmethodLimit.hiSym = ::xoc::tapi::ZLimitSymbol_LESSER_EQUAL]
	      )
	  >> ch_p('"')
	;


      TestmethodSection =
	str_p("testmethods")
	  >> Testmethods
	;

      Testmethods = 
	*(Testmethod)
	  >> End
	;

      Testmethod = 
	(
	 (Identifier)[
				 Testmethod.identifier = construct_<string>(arg1, arg2),
				 Testmethod.Class = "",
				 Testmethod.methodId = "",
				 Testmethod.parameter = "",
				 Testmethod.limits = "",
				 Testmethod.name = ""
	  ]
	 >> ':' >>
	 if_p(Start.isUTMBased)
	 [
	  UTMTestmethodClass[bind(&CreateUTMTestmethod)(Testmethod.identifier, Testmethod.Class)]
	  ]
	 .else_p[
		 TestmethodDefinition[bind(&CreateTestmethod)(Testmethod.identifier, Testmethod.Class, Testmethod.methodId, Testmethod.parameter, Testmethod.limits, Testmethod.name)]
	 ]
	 )
	;
	
      UTMTestmethodClass =
	str_p("testmethod_class") 
	  >> '=' 
	  >> QuotedString[Testmethod.Class = arg1]
	  >> ';'
	;

      TestmethodDefinition = 
	(
	 TestmethodClass
	 | TestmethodId
	 | TestmethodParameters
	 | TestmethodLimits
	 | TestmethodName
	 )
	   >> !TestmethodDefinition
	;

      TestmethodClass = 
	str_p("testmethod_class") >> '=' >> QuotedString[Testmethod.Class = arg1] >> ';'
	;

      TestmethodId = 
	str_p("testmethod_id") >> '=' >> 
	(
	 String[Testmethod.methodId = construct_<string>(arg1, arg2)] 
	 | QuotedString[Testmethod.methodId = arg1]
	 ) >> ';'
	;

      TestmethodParameters =
	str_p("testmethod_parameters") >> '=' >> QuotedString[Testmethod.parameter = arg1] >> ';'
	;

      TestmethodLimits = 
	str_p("testmethod_limits") >> '=' >> QuotedString[Testmethod.limits = arg1] >> ';'
	;

      TestmethodName =
	str_p("testmethod_name") >> '=' >> QuotedString[Testmethod.name = arg1] >> ';'
	;

      UserprocedureSection = 
	str_p("tests")
	  >> Userprocedures
	;

      Userprocedures = 
	*(Userprocedure)
	  >> End
	;

      Userprocedure = 
	(
	 (Identifier)[Userprocedure.identifier = construct_<string>(arg1, arg2)] >> ':'
	 >> str_p("user_procedure") >> '=' >> QuotedString[Userprocedure.commandline = arg1]
	 >> ';'
	 )
	[bind(&CreateUserprocedure)(Userprocedure.identifier, Userprocedure.commandline)]
	;

      TestsuiteSection = 
	str_p("test_suites")
	  >> Testsuites
	  >> End
	;

      Testsuites =
	*(Testsuite)
	;

      Testsuite = 
	(
	 TestsuiteName
	 [bind(&StartTestsuite)(construct_<string>(arg1, arg2-1))]
	 )
	 >> TestsuiteDefinition
	;

      TestsuiteName =
	Identifier >> *ch_p(' ') >> ':'
	;

      TestsuiteDefinition =
	(
	 TestsuiteTest
	 | TestsuiteOverride
	 | TestsuiteTimEquSet
	 | TestsuiteLevEquSet
	 | TestsuiteTimSpecSet
	 | TestsuiteLevSpecSet
	 | TestsuiteTimSet
	 | TestsuiteLevSet
	 | TestsuiteSequencerLabel
	 | TestsuiteFlags
	 | TestsuiteSiteControl
	 | TestsuiteFFCCount
	 | TestsuiteTestLevel
	 | TestsuiteDPSSet
	 | TestsuiteTestNumber
	 | TestsuiteAnalogSet
	 | TestsuiteSiteMatch
	 | TestsuiteWaveformSet
   | TestsuiteComment
	 | Error
	 )
	   >> !TestsuiteDefinition
	;

      TestsuiteTest =
	(str_p("override_testf") >> '=' >> Identifier[bind(&SetTestsuiteTest)(construct_<string>(arg1, arg2))] >>';')
	| (str_p("tests") >> '=' >> Identifier[bind(&SetTestsuiteTest)(construct_<string>(arg1, arg2))] >> ';')
	;

      TestsuiteOverride = 
	str_p("override") >> '=' >> int_p >> ';'
	;

      TestsuiteTimEquSet = 
	str_p("override_tim_equ_set") >> '=' >> Expression[bind(&SetTestsuiteTimEquSet)(arg1)] >> ';'
	;

      TestsuiteLevEquSet = 
	str_p("override_lev_equ_set") >> '=' >> Expression[bind(&SetTestsuiteLevEquSet)(arg1)] >> ';'
	;

      TestsuiteTimSpecSet = 
	str_p("override_tim_spec_set") >> '=' >> Expression[bind(&SetTestsuiteTimSpecSet)(arg1)] >> ';'
	;

      TestsuiteLevSpecSet = 
	str_p("override_lev_spec_set") >> '=' >> Expression[bind(&SetTestsuiteLevSpecSet)(arg1)] >> ';'
	;

      TestsuiteTimSet =
	str_p("override_timset") >> '=' >> Expression[bind(&SetTestsuiteTimSet)(arg1)] >> ';'
	;

      TestsuiteLevSet =
	str_p("override_levset") >> '=' >> Expression[bind(&SetTestsuiteLevSet)(arg1)] >> ';'
	;

      TestsuiteSequencerLabel =
	str_p("override_seqlbl") >> '=' >> Expression[bind(&SetTestsuiteSequencerLabel)(arg1)] >> ';'
	;
      
      TestsuiteFlags =
	str_p("local_flags") >> '=' >> list_p(Identifier[bind(&SetTestsuiteFlag)(construct_<string>(arg1, arg2))], ch_p(',')) >> ';' //Ignore this for now, because flag_ui handles the flags
	;

      TestsuiteSiteControl = 
	str_p("site_control")[bind(&ClearSiteControlArguments)()]
	  >> '=' >> SiteControlExpression
	  >> ';'
	;

      SiteControlExpression =
	(
	 str_p("\"serial:\"")[SiteControlExpression.type = ::xoc::tapi::ZSiteSequenceType_SERIAL]
	 | str_p("\"parallel:\"")[SiteControlExpression.type = ::xoc::tapi::ZSiteSequenceType_PARALLEL]
	 | (
	    str_p("\"semiparallel:")[SiteControlExpression.type = ::xoc::tapi::ZSiteSequenceType_SEMIPARALLEL]
	    >> int_p[bind(&NewSiteControlArgument)(arg1)]
	    >> ':'
	    >> int_p[bind(&NewSiteControlArgument)(arg1)]
	    >> !ch_p(':')
 	    >> '"'
	    )
	 | (
	    str_p("\"other:")[SiteControlExpression.type = ::xoc::tapi::ZSiteSequenceType_OTHER]
	    >> list_p.direct(int_p[bind(&NewSiteControlArgument)(arg1)], ch_p(':'))
	    >> !ch_p(':')
	    >> ch_p('"')
	    )
	 )
	[bind(&SetTestsuiteSiteControl)(SiteControlExpression.type)]
	;

      TestsuiteFFCCount = 
	str_p("ffc_on_fail") >> '=' >> int_p[bind(&SetTestsuiteFFCCount)(arg1)] >> ';'
	;

      TestsuiteTestLevel =
	str_p("test_level") >> '=' >> int_p[bind(&SetTestsuiteTestLevel)(arg1)] >> ';'
	;

      TestsuiteDPSSet =
	str_p("override_dpsset") >> '=' >> Expression[bind(&SetTestsuiteDPSSet)(arg1)] >> ';'
	;

      TestsuiteWaveformSet = 
	str_p("override_wvfset") >> '=' >> Expression[bind(&SetTestsuiteWaveformSet)(arg1)] >> ';'
	;
      
      TestsuiteAnalogSet = 
	str_p("override_anaset") >> '=' >> Expression[bind(&SetTestsuiteAnalogSet)(arg1)] >> ';'
	;

      TestsuiteTestNumber =
	str_p("override_test_number") >> '=' >> Expression[bind(&SetTestsuiteTestNumber)(arg1)] >> ';'
	;

      TestsuiteSiteMatch =
	str_p("site_match") >> '=' >> int_p[bind(&SetTestsuiteSiteMatch)(arg1)] >> ';'
	;

      TestsuiteComment = 
  str_p("comment") >> '=' >> QuotedString[bind(&SetTestsuiteComment)(arg1)] >> ';'
  ;

      TestflowSection =
	str_p("test_flow")[bind(&FlowSectionStart)()]
	  >> FlowStatements
	  >> End
	;

      FlowStatements =
	*(FlowStatement)
	;

      FlowStatement = 
	RunStatement
	| RunAndBranchStatement
	| GroupStatement
	| IfStatement
	| AssignmentStatement
	| StopBinStatement
	| PrintStatement
	| PrintDatalogStatement
	| SVLRTimingStatement
	| SVLRLevelStatement
	| WhileStatement
	| RepeatStatement
	| ForStatement
	| MultiBinStatement
	| EmptyStatement
	| Error
	;

      RunStatement =
	(
	 str_p("run") >> ch_p('(')
	   >> Identifier[RunStatement.testsuite = construct_<string>(arg1, arg2)]
	   >> ')'
	   >> ';'
	 )
	[bind(&CreateRunStatement)(RunStatement.testsuite)]
	;

      RunAndBranchStatement =
	(
	 str_p("run_and_branch") >> ch_p('(')
	 >> Identifier[RunAndBranchStatement.testsuite = construct_<string>(arg1, arg2)]
	 >> ')'
	 >> str_p("then")
	 )
	[bind(&CreateRunAndBranchStatement)(RunAndBranchStatement.testsuite)]
	 >> str_p("{") [bind(&EnterSubBranch)(0)]
	 >> FlowStatements
	 >> str_p("}") [bind(&LeaveSubBranch)()]
	 >> 
	!(
	  str_p("else")
	  >> str_p("{") [bind(&EnterSubBranch)(1)]
	  >> FlowStatements
	  >> str_p("}") [bind(&LeaveSubBranch)()]
	  )
	;

      IfStatement =
	(
	 str_p("if")
	 >> Expression[IfStatement.condition = arg1]
	 >> str_p("then")
	 )
	[bind(&CreateIfStatement)(IfStatement.condition)]
 	 >> (str_p("{")) [bind(&EnterSubBranch)(0)]
 	 >> FlowStatements
 	 >> (str_p("}")) [bind(&LeaveSubBranch)()]
	 >>
	!(
	  str_p("else")
	  >> (str_p("{")) [bind(&EnterSubBranch)(1)]
	  >> FlowStatements
	  >> (str_p("}")) [bind(&LeaveSubBranch)()]
	  )
	;

      GroupStatement =
	str_p("{") [bind(&CreateGroupStatement)(), bind(&EnterSubBranch)(0)]
	  >> FlowStatements
	  >> str_p("}") [bind(&LeaveSubBranch)()]
          >> ','
	  >> (
	      GroupBypass[bind(&SetGroupBypass)()]
	      | str_p("")[bind(&SetGroupNoBypass)()]
	      )
	  >> (
	      str_p("open")[bind(&SetGroupOpen)()]
	      | str_p("closed")[bind(&SetGroupClosed)()]
	      )
	  >> ','
	  >> (QuotedString) [bind(&SetGroupLabel)(arg1)]
	  >> ','
	  >> (QuotedString) [bind(&SetGroupDescription)(arg1)]
	;

      GroupBypass =
        str_p("groupbypass")
        >> ','
        ;

      AssignmentStatement =
	(
	 ( TestsuiteFlag[AssignmentStatement.varName = arg1]
	   |  Variable[AssignmentStatement.varName = arg1]
	 )
	 >> '=' 
	 >> (Expression[AssignmentStatement.value = arg1]         
	     | TestsuiteFlag[AssignmentStatement.value = arg1])
	 >> ';'
	 )
	[bind(&CreateAssignmentStatement)(AssignmentStatement.varName, AssignmentStatement.value)]
	;

      StopBinStatement =
	(
	 str_p("stop_bin")
	 >> (BinDefinition("", "", false, false, ::xoc::tapi::ZBinColor_BLACK, -1, false))
	 >> ';'
	 )
	[bind(&CreateStopBinStatement)()]
	;

      BinDefinition =
  // the first alternate rule is an old definition format which accepts an OOCcrule 
  // as third parameter without using it;
  // that way, syntax compability with older testflows is achieved 
	(   
	 QuotedString [BinDefinition.swBin = arg1, BinDefinition.binNumber = -1]
	  >> ','
	  >> QuotedString [BinDefinition.swBinDescription = arg1]
	  >> ','
	  >> !OOCRule
	  >> ','
	  >> !Quality
	  >> ','
	  >> !Reprobe
	  >> ','
	  >> Color
	  >> ','
	  >> !BinNumber
	  >> ','
	  >> !Overon
	)
	[bind(&CreateBin)(BinDefinition.swBin,
			  BinDefinition.swBinDescription,
			  BinDefinition.quality,
			  BinDefinition.reprobe,
			  BinDefinition.color,
			  BinDefinition.binNumber,
			  BinDefinition.overon)]
  |
  (
   QuotedString [BinDefinition.swBin = arg1, BinDefinition.binNumber = -1]
    >> ','
    >> QuotedString [BinDefinition.swBinDescription = arg1]
    >> ','
    >> !Quality
    >> ','
    >> !Reprobe
    >> ','
    >> Color
    >> ','
    >> !BinNumber
    >> ','
    >> !Overon
  )
  [bind(&CreateBin)(BinDefinition.swBin,
        BinDefinition.swBinDescription,
        BinDefinition.quality,
        BinDefinition.reprobe,
        BinDefinition.color,
        BinDefinition.binNumber,
        BinDefinition.overon)]
	;

      OOCRule =
	!(str_p("oocwarning") >> '='
	  >> int_p >> int_p >> int_p >> QuotedString
	  )
			      >> !(str_p("oocstop") >> '='
				   >> int_p >> int_p >> int_p >> QuotedString)
	;
      
      Quality =
	str_p("good") [BinDefinition.quality = true]
	| str_p("bad")[BinDefinition.quality = false]
	;

      Reprobe =
	str_p("reprobe") [BinDefinition.reprobe = true]
	| str_p("noreprobe") [BinDefinition.reprobe = false]
	;

      Color = 
	int_p [BinDefinition.color = static_cast_< ::xoc::tapi::ZBinColor >(arg1)]
	| str_p("black") [BinDefinition.color = ::xoc::tapi::ZBinColor_BLACK]
	| str_p("white") [BinDefinition.color = ::xoc::tapi::ZBinColor_WHITE]
	| str_p("red") [BinDefinition.color = ::xoc::tapi::ZBinColor_RED]
	| str_p("yellow") [BinDefinition.color = ::xoc::tapi::ZBinColor_YELLOW]
	| str_p("green") [BinDefinition.color = ::xoc::tapi::ZBinColor_GREEN]
	| str_p("cyan") [BinDefinition.color = ::xoc::tapi::ZBinColor_CYAN]
	| str_p("blue") [BinDefinition.color = ::xoc::tapi::ZBinColor_BLUE]
	| str_p("magenta") [BinDefinition.color = ::xoc::tapi::ZBinColor_MAGENTA]
	;
      
      BinNumber =
	int_p [BinDefinition.binNumber = arg1]
	;

      Overon =
	str_p("over_on") [BinDefinition.overon = true]
	| str_p("not_over_on") [BinDefinition.overon = false]
	;

      PrintStatement =
	(
	 str_p("print")
	 >> '('
	 >> Expression[PrintStatement.statement = arg1]
	 >> ')'
	 >> ';'
	 )
	[bind(&CreatePrintStatement)(PrintStatement.statement)]
	;

      PrintDatalogStatement =
	(
	 str_p("print_dl")
	 >> '('
	 >> Expression[PrintDatalogStatement.statement = arg1]
	 >> ')'
	 >> ';'
	 )
	[bind(&CreatePrintDatalogStatement)(PrintDatalogStatement.statement)]
	;

      SVLRTimingStatement =
	(
	 str_p("svlr_timing_command")
	 >> '('
	 >> Expression[SVLRTimingStatement.equSet = arg1]
	 >> ','
	 >> Expression[SVLRTimingStatement.specSet = arg1]
	 >> ','
	 >> QuotedString[SVLRTimingStatement.variable = arg1] 
	 >> ','
	 >> Expression[SVLRTimingStatement.value = arg1]
	 >> ')'
	 >> ';'
	 )
	[bind(&CreateSVLRTimingStatement)(SVLRTimingStatement.equSet,
					  SVLRTimingStatement.specSet,
					  SVLRTimingStatement.variable,
					  SVLRTimingStatement.value)]
	;

      SVLRLevelStatement =
	(
	 str_p("svlr_level_command")
	 >> '('
	 >> Expression[SVLRLevelStatement.equSet = arg1]
	 >> ','
	 >> Expression[SVLRLevelStatement.specSet = arg1]
	 >> ','
	 >> QuotedString[SVLRLevelStatement.variable = arg1] 
	 >> ','
	 >> Expression[SVLRLevelStatement.value = arg1]
	 >> ')'
	 >> ';'
	 )
	[bind(&CreateSVLRLevelStatement)(SVLRLevelStatement.equSet,
					 SVLRLevelStatement.specSet,
					 SVLRLevelStatement.variable,
					 SVLRLevelStatement.value)]
	;

      TestNumLoopInc =
	str_p("test_number_loop_increment")
	  >> '='
	  >> Expression[TestNumLoopInc.expression = arg1]
	;

      WhileStatement =
	(
	 str_p("while")
	 >> Expression [WhileStatement.condition = arg1, WhileStatement.testnum = construct_<string>("")]
	 >> str_p("do") 
	 >> !(TestNumLoopInc [WhileStatement.testnum = arg1])
	 )
	[bind(&CreateWhileStatement)(WhileStatement.condition, WhileStatement.testnum)]
	 >> str_p("{") [bind(&EnterSubBranch)(0)]
	 >> FlowStatements
	 >> str_p("}") [bind(&LeaveSubBranch)()]
      ;

      RepeatStatement =
	str_p("repeat") [bind(&CreateRepeatStatement)(), bind(&EnterSubBranch)(0)]
	  >> FlowStatements
	  >> str_p("until") [bind(&LeaveSubBranch)()]
	  >> Expression [bind(&SetRepeatCondition)(arg1)]
	  >> !(TestNumLoopInc [bind(&SetRepeatTestnum)(arg1)])
	;

      ForStatement =
	(
	 str_p("for")[ForStatement.testnum = construct_<string>("")]
	  >> QualifiedIdentifier[ForStatement.assignVar = arg1] >> '=' >> Expression[ForStatement.assignValue = arg1]
	  >> ';'
	  >> Expression[ForStatement.condition = arg1]
	  >> ';'
	  >> QualifiedIdentifier[ForStatement.incrementVar = arg1] >> '=' >> Expression[ForStatement.incrementValue = arg1]
	  >> ';'
	  >> str_p("do")
	  >> !(TestNumLoopInc [ForStatement.testnum = arg1])
	)
	[bind(&CreateForStatement)(ForStatement.assignVar,
				   ForStatement.assignValue,
				   ForStatement.condition,
				   ForStatement.incrementVar,
				   ForStatement.incrementValue,
				   ForStatement.testnum)]
	  >> str_p("{") [bind(&EnterSubBranch)(0)]
	  >> FlowStatements
	  >> str_p("}") [bind(&LeaveSubBranch)()]
	;

      MultiBinStatement =
	str_p("multi_bin")[bind(&CreateMultiBinStatement)()]
	  >> ';'
	;

      EmptyStatement = 
	ch_p(';')
	;

      SpecialTestsuiteSection =
	DownloadTestsuite
	| InitTestsuite
	| PauseTestsuite
	| AbortTestsuite
	| ResetTestsuite
	| ExitTestsuite
	| DisconnectTestsuite
	| MultiBinDecisionTestsuite
	;

      DownloadTestsuite =
	(
	 str_p("download")[bind(&StartTestsuite)("download")]
	  >> TestsuiteDefinition
	 >> End
	 )
	[bind(&SetDownloadSuite)()]
	;

      InitTestsuite =
	(
	 str_p("initialize")[bind(&StartTestsuite)("initialize")]
	 >> TestsuiteDefinition
	 >> End
	 )
	[bind(&SetInitSuite)()]
	;

      PauseTestsuite =
	(
	 str_p("pause")[bind(&StartTestsuite)("pause")]
	 >> TestsuiteDefinition
	 >> End
	 )
	[bind(&SetPauseSuite)()]
	;

      AbortTestsuite =
	(
	 str_p("abort")[bind(&StartTestsuite)("abort")]
	 >> TestsuiteDefinition
	 >> End
	 )
	[bind(&SetAbortSuite)()]
	;

      ResetTestsuite =
	(
	 str_p("reset")[bind(&StartTestsuite)("reset")]
	 >> TestsuiteDefinition
	 >> End
	 )
	[bind(&SetResetSuite)()]
	;

      ExitTestsuite =
	(
	 str_p("exit")[bind(&StartTestsuite)("exit")]
	 >> TestsuiteDefinition
	 >> End
	 )
	[bind(&SetExitSuite)()]
	;
      DisconnectTestsuite =
	(
	 str_p("bin_disconnect")[bind(&StartTestsuite)("bin_disconnect")]
	 >> TestsuiteDefinition
	 >> End
	 )
	[bind(&SetDisconnectSuite)()]
	;
      
      MultiBinDecisionTestsuite =
        (
            str_p("multi_bin_decision")[bind(&StartTestsuite)("multi_bin_decision")]
                                        >> TestsuiteDefinition
                                        >> End
            )
            [bind(&SetMultiBinDecisionSuite)()]
             ;

      BinningSection = 
	str_p("binning")
	  >> *(
	      OtherwiseBin
	      | (BinDefinition >> ';')
	      )
	  >> End
	;

      OtherwiseBin =
	(
	str_p("otherwise bin") 
	  >> '='
	  >> BinDefinition
	  >> ';'
	)
	[bind(&CreateOtherwiseBin)()]
	;

      SetupSection =
	str_p("context")
	  >> *(SetupFiles)
	  >> End
	;

      SetupFiles = 
	 ConfigFile
	 | LevelsFile
	 | TimingFile
	 | VectorFile
	 | AttribFile
	 | ChannelAttribFile
	 | MixedSignalFile
	 | AnalogControlFile
	 | WaveformFile
	 | RoutingFile
	 | TestTableFile
	 | Protocols
	;

      ConfigFile = 
	str_p("context_config_file")
	  >> '='
	  >> QuotedString [bind(&SetConfigFile)(arg1)]
	  >> ';'
	;

      LevelsFile =
	str_p("context_levels_file")
	  >> '='
	  >> QuotedString [bind(&SetLevelsFile)(arg1)]
	  >> ';'
	;

      TimingFile =
	str_p("context_timing_file")
	  >> '='
	  >> QuotedString [bind(&SetTimingFile)(arg1)]
	  >> ';'
	;

      VectorFile =
	str_p("context_vector_file")
	  >> '='
	  >> QuotedString [bind(&SetVectorFile)(arg1)]
	  >> ';'
	;

      AttribFile = 
	str_p("context_attrib_file")
	  >> '='
	  >> QuotedString [bind(&SetAttribFile)(arg1)]
	  >> ';'
	;

      ChannelAttribFile =
	str_p("context_channel_attrib_file")
	  >> '='
	  >> QuotedString [bind(&SetChannelAttribFile)(arg1)]
	  >> ';'
	;

      MixedSignalFile =
	str_p("context_mixsgl_file")
	  >> '='
	  >> QuotedString [bind(&SetMixedSignalFile)(arg1)]
	  >> ';'
	;

      AnalogControlFile =
	str_p("context_analog_control_file")
	  >> '='
	  >> QuotedString [bind(&SetAnalogControlFile)(arg1)]
	  >> ';'
	;

      WaveformFile =
	str_p("context_waveform_file")
	  >> '='
	  >> QuotedString [bind(&SetWaveformFile)(arg1)]
	  >> ';'
	;

      RoutingFile =
	str_p("context_routing_file")
	  >> '='
	  >> QuotedString [bind(&SetRoutingFile)(arg1)]
	  >> ';'
	;
      
      TestTableFile =
        str_p("context_testtable_file")
        >> '='
        >> QuotedString[bind(&SetTestTableFile)(arg1)]
        >> ';'
       ;

      Protocols =
        str_p("context_protocols")
        >> '='
        >> QuotedString[bind(&SetProtocols)(arg1)]
        >> ';'
       ;


      OOCSection =
	str_p("oocrule") 
	  >> OOCRule
	  >> End;

      HardwareBinSection =
	str_p("hardware_bin_descriptions")
	  >> *(HardBinDescription)
	  >> End
	;

      HardBinDescription =
	(
	int_p[HardBinDescription.hwBin = arg1]
	  >> '=' 
	  >> QuotedString[HardBinDescription.description = arg1]
	  >> ';'
	)
	[bind(&SetHardBinDescription)(HardBinDescription.hwBin, HardBinDescription.description)]
	;


#ifdef BOOST_SPIRIT_DEBUG
      BOOST_SPIRIT_DEBUG_RULE(Expression);
      BOOST_SPIRIT_DEBUG_RULE(BinaryAddTerm);
      BOOST_SPIRIT_DEBUG_RULE(Term);
      BOOST_SPIRIT_DEBUG_RULE(Unary);
      BOOST_SPIRIT_DEBUG_RULE(NumberFunction);
      BOOST_SPIRIT_DEBUG_RULE(Literal);
      BOOST_SPIRIT_DEBUG_RULE(Number);
      BOOST_SPIRIT_DEBUG_RULE(TestsuiteFlag);
      BOOST_SPIRIT_DEBUG_RULE(Variable);
      BOOST_SPIRIT_DEBUG_RULE(QuotedString);
      BOOST_SPIRIT_DEBUG_RULE(String);
      BOOST_SPIRIT_DEBUG_RULE(BinaryRelTerm);
      BOOST_SPIRIT_DEBUG_RULE(BinaryMultTerm);
      BOOST_SPIRIT_DEBUG_RULE(BinaryLogicTerm);
      BOOST_SPIRIT_DEBUG_RULE(QuotedString);
      BOOST_SPIRIT_DEBUG_RULE(Identifier);
      BOOST_SPIRIT_DEBUG_RULE(QualifiedIdentifier);
      BOOST_SPIRIT_DEBUG_RULE(String);
      BOOST_SPIRIT_DEBUG_RULE(Start);
      BOOST_SPIRIT_DEBUG_RULE(OptFileHeader);
      BOOST_SPIRIT_DEBUG_RULE(OptRevision);
      BOOST_SPIRIT_DEBUG_RULE(Sections);
      BOOST_SPIRIT_DEBUG_RULE(EmptySection);
      BOOST_SPIRIT_DEBUG_RULE(InformationSection);
      BOOST_SPIRIT_DEBUG_RULE(InformationElements);
      BOOST_SPIRIT_DEBUG_RULE(DeviceName);
      BOOST_SPIRIT_DEBUG_RULE(DeviceRevision);
      BOOST_SPIRIT_DEBUG_RULE(TestRevision);
      BOOST_SPIRIT_DEBUG_RULE(Description);
      BOOST_SPIRIT_DEBUG_RULE(Application);
      BOOST_SPIRIT_DEBUG_RULE(Temperature);
      BOOST_SPIRIT_DEBUG_RULE(ImplicitDeclarationSection);
      BOOST_SPIRIT_DEBUG_RULE(DeclarationSection);
      BOOST_SPIRIT_DEBUG_RULE(End);
      BOOST_SPIRIT_DEBUG_RULE(Declarations);
      BOOST_SPIRIT_DEBUG_RULE(Definition);
      BOOST_SPIRIT_DEBUG_RULE(Variable);
      BOOST_SPIRIT_DEBUG_RULE(Expression);
      BOOST_SPIRIT_DEBUG_RULE(Declaration);
      BOOST_SPIRIT_DEBUG_RULE(ImplicitDeclarations);
      BOOST_SPIRIT_DEBUG_RULE(Type);
      BOOST_SPIRIT_DEBUG_RULE(FlagSection);
      BOOST_SPIRIT_DEBUG_RULE(Flags);
      BOOST_SPIRIT_DEBUG_RULE(SystemFlag);
      BOOST_SPIRIT_DEBUG_RULE(UserFlag);
      BOOST_SPIRIT_DEBUG_RULE(TestfunctionSection);
      BOOST_SPIRIT_DEBUG_RULE(Testfunctions);
      BOOST_SPIRIT_DEBUG_RULE(Testfunction);
      BOOST_SPIRIT_DEBUG_RULE(TestfunctionDescription);
      BOOST_SPIRIT_DEBUG_RULE(TestfunctionParameter);
      BOOST_SPIRIT_DEBUG_RULE(TestfunctionDefinition);
      BOOST_SPIRIT_DEBUG_RULE(TestmethodSection);
      BOOST_SPIRIT_DEBUG_RULE(Testmethods);
      BOOST_SPIRIT_DEBUG_RULE(Testmethod);
      BOOST_SPIRIT_DEBUG_RULE(TestmethodClass);
      BOOST_SPIRIT_DEBUG_RULE(TestmethodDefinition);
      BOOST_SPIRIT_DEBUG_RULE(TestmethodId);
      BOOST_SPIRIT_DEBUG_RULE(TestmethodParameters);
      BOOST_SPIRIT_DEBUG_RULE(TestmethodLimits);
      BOOST_SPIRIT_DEBUG_RULE(TestmethodName);
      BOOST_SPIRIT_DEBUG_RULE(UserprocedureSection);
      BOOST_SPIRIT_DEBUG_RULE(Userprocedures);
      BOOST_SPIRIT_DEBUG_RULE(Userprocedure);
      BOOST_SPIRIT_DEBUG_RULE(TestsuiteSection);
      BOOST_SPIRIT_DEBUG_RULE(Testsuites);
      BOOST_SPIRIT_DEBUG_RULE(Testsuite);
      BOOST_SPIRIT_DEBUG_RULE(TestsuiteName);
      BOOST_SPIRIT_DEBUG_RULE(TestsuiteDefinition);
      BOOST_SPIRIT_DEBUG_RULE(TestsuiteTest);
      BOOST_SPIRIT_DEBUG_RULE(TestsuiteOverride);
      BOOST_SPIRIT_DEBUG_RULE(TestsuiteTimEquSet);
      BOOST_SPIRIT_DEBUG_RULE(TestsuiteLevEquSet);
      BOOST_SPIRIT_DEBUG_RULE(TestsuiteTimSpecSet);
      BOOST_SPIRIT_DEBUG_RULE(TestsuiteLevSpecSet);
      BOOST_SPIRIT_DEBUG_RULE(TestsuiteTimSet);
      BOOST_SPIRIT_DEBUG_RULE(TestsuiteLevSet);
      BOOST_SPIRIT_DEBUG_RULE(TestsuiteSequencerLabel);
      BOOST_SPIRIT_DEBUG_RULE(TestsuiteFlags);
      BOOST_SPIRIT_DEBUG_RULE(TestsuiteSiteControl);
      BOOST_SPIRIT_DEBUG_RULE(TestsuiteFFCCount);
      BOOST_SPIRIT_DEBUG_RULE(TestsuiteTestLevel);
      BOOST_SPIRIT_DEBUG_RULE(TestsuiteDPSSet);
      BOOST_SPIRIT_DEBUG_RULE(TestsuiteWaveformSet);
      BOOST_SPIRIT_DEBUG_RULE(TestsuiteComment);
      BOOST_SPIRIT_DEBUG_RULE(SiteControlExpression);
      BOOST_SPIRIT_DEBUG_RULE(TestsuiteAnalogSet);
      BOOST_SPIRIT_DEBUG_RULE(TestsuiteTestNumber);
      BOOST_SPIRIT_DEBUG_RULE(TestsuiteSiteMatch);
      BOOST_SPIRIT_DEBUG_RULE(TestflowSection);
      BOOST_SPIRIT_DEBUG_RULE(FlowStatement);
      BOOST_SPIRIT_DEBUG_RULE(FlowStatements);
      BOOST_SPIRIT_DEBUG_RULE(RunStatement);
      BOOST_SPIRIT_DEBUG_RULE(RunAndBranchStatement);
      BOOST_SPIRIT_DEBUG_RULE(IfStatement);
      BOOST_SPIRIT_DEBUG_RULE(GroupStatement);
      BOOST_SPIRIT_DEBUG_RULE(GroupBypass);
      BOOST_SPIRIT_DEBUG_RULE(AssignmentStatement);
      BOOST_SPIRIT_DEBUG_RULE(StopBinStatement);
      BOOST_SPIRIT_DEBUG_RULE(OOCRule);
      BOOST_SPIRIT_DEBUG_RULE(Quality);
      BOOST_SPIRIT_DEBUG_RULE(Reprobe);
      BOOST_SPIRIT_DEBUG_RULE(Color);
      BOOST_SPIRIT_DEBUG_RULE(BinNumber);
      BOOST_SPIRIT_DEBUG_RULE(Overon);
      BOOST_SPIRIT_DEBUG_RULE(PrintStatement);
      BOOST_SPIRIT_DEBUG_RULE(PrintDatalogStatement);
      BOOST_SPIRIT_DEBUG_RULE(SVLRTimingStatement);
      BOOST_SPIRIT_DEBUG_RULE(SVLRLevelStatement);
      BOOST_SPIRIT_DEBUG_RULE(WhileStatement);
      BOOST_SPIRIT_DEBUG_RULE(RepeatStatement);
      BOOST_SPIRIT_DEBUG_RULE(ForStatement);
      BOOST_SPIRIT_DEBUG_RULE(TestNumLoopInc);
      BOOST_SPIRIT_DEBUG_RULE(MultiBinStatement);
      BOOST_SPIRIT_DEBUG_RULE(EmptyStatement);
      BOOST_SPIRIT_DEBUG_RULE(SpecialTestsuiteSection);
      BOOST_SPIRIT_DEBUG_RULE(DownloadTestsuite);
      BOOST_SPIRIT_DEBUG_RULE(InitTestsuite);
      BOOST_SPIRIT_DEBUG_RULE(PauseTestsuite);
      BOOST_SPIRIT_DEBUG_RULE(AbortTestsuite);
      BOOST_SPIRIT_DEBUG_RULE(ResetTestsuite);
      BOOST_SPIRIT_DEBUG_RULE(ExitTestsuite);
      BOOST_SPIRIT_DEBUG_RULE(DisconnectTestsuite);
      BOOST_SPIRIT_DEBUG_RULE(BinningSection);
      BOOST_SPIRIT_DEBUG_RULE(OtherwiseBin);
      BOOST_SPIRIT_DEBUG_RULE(BinDefinition);
      BOOST_SPIRIT_DEBUG_RULE(SetupSection);
      BOOST_SPIRIT_DEBUG_RULE(SetupFiles);
      BOOST_SPIRIT_DEBUG_RULE(ConfigFile);
      BOOST_SPIRIT_DEBUG_RULE(LevelsFile);
      BOOST_SPIRIT_DEBUG_RULE(TimingFile);
      BOOST_SPIRIT_DEBUG_RULE(VectorFile);
      BOOST_SPIRIT_DEBUG_RULE(AttribFile);
      BOOST_SPIRIT_DEBUG_RULE(ChannelAttribFile);
      BOOST_SPIRIT_DEBUG_RULE(MixedSignalFile);
      BOOST_SPIRIT_DEBUG_RULE(AnalogControlFile);
      BOOST_SPIRIT_DEBUG_RULE(WaveformFile);
      BOOST_SPIRIT_DEBUG_RULE(RoutingFile);
      BOOST_SPIRIT_DEBUG_RULE(TestTableFile);
      BOOST_SPIRIT_DEBUG_RULE(Protocols);
      BOOST_SPIRIT_DEBUG_RULE(OOCSection);
      BOOST_SPIRIT_DEBUG_RULE(HardwareBinSection);
      BOOST_SPIRIT_DEBUG_RULE(HardBinDescription);
      BOOST_SPIRIT_DEBUG_RULE(TestmethodParameterSection);
      BOOST_SPIRIT_DEBUG_RULE(UTMTestmethodParameters);
      BOOST_SPIRIT_DEBUG_RULE(TestmethodParameter);
      BOOST_SPIRIT_DEBUG_RULE(TestmethodLimitSection);
      BOOST_SPIRIT_DEBUG_RULE(UTMTestmethodLimits);
      BOOST_SPIRIT_DEBUG_RULE(TestmethodLimit);
      BOOST_SPIRIT_DEBUG_RULE(LowLimitSymbol);
      BOOST_SPIRIT_DEBUG_RULE(HighLimitSymbol);
      BOOST_SPIRIT_DEBUG_RULE(UTMTestmethodClass);
#endif


    }

    rule<ScannerT> Term;
    rule<ScannerT> BinaryAddTerm;
    rule<ScannerT> BinaryMultTerm;
    rule<ScannerT> BinaryRelTerm;
    rule<ScannerT> BinaryLogicTerm;
    rule<ScannerT> BinaryAdd;
    rule<ScannerT> BinaryMult;
    rule<ScannerT> BinaryRel;
    rule<ScannerT> BinaryLogic;
    rule<ScannerT> Unary;
    rule<ScannerT> NumberFunction;
    rule<ScannerT> StringFunction;
    rule<ScannerT> Literal;
    rule<ScannerT> Number;
    rule<ScannerT, variable_closure::context_t> TestsuiteFlag;
    rule<ScannerT, string_closure::context_t> QuotedString;
    rule<ScannerT, variable_closure::context_t> Variable;
    rule<ScannerT, expression_closure::context_t> Expression;
    rule<ScannerT, type_closure::context_t> Type;
    rule<ScannerT> String, Identifier;
    rule<ScannerT, variable_closure::context_t> QualifiedIdentifier;
    rule<ScannerT, overall_closure::context_t> Start;
    rule<ScannerT> End;
    rule<ScannerT> OptFileHeader, OptRevision, Sections;
    rule<ScannerT> EmptySection, InformationSection, ImplicitDeclarationSection, DeclarationSection, TestfunctionSection, TestmethodSection;
    rule<ScannerT> InformationElements, DeviceName, DeviceRevision, TestRevision, Description, Application, Temperature;
    rule<ScannerT> ImplicitDeclarations;
    rule<ScannerT, declaration_closure::context_t> Declaration;
    rule<ScannerT> Declarations;
    rule<ScannerT, definition_closure::context_t> Definition;
    rule<ScannerT> FlagSection, Flags, SystemFlag;
    rule<ScannerT, definition_closure::context_t> UserFlag;
    rule<ScannerT> Testfunctions;
    rule<ScannerT, testfunction_closure::context_t> Testfunction;
    rule<ScannerT> TestfunctionDescription, TestfunctionParameter, TestfunctionDefinition;
    rule<ScannerT> Testmethods;
    rule<ScannerT, testmethod_closure::context_t> Testmethod;
    rule<ScannerT> TestmethodDefinition, TestmethodClass, TestmethodId, TestmethodParameters, TestmethodLimits, TestmethodName;
    rule<ScannerT> UserprocedureSection, Userprocedures;
    rule<ScannerT, userprocedure_closure::context_t> Userprocedure;
    rule<ScannerT> TestsuiteSection, Testsuites;
    rule<ScannerT> Testsuite, TestsuiteName;
    rule<ScannerT> TestsuiteDefinition;
    rule<ScannerT> TestsuiteTest, TestsuiteOverride, TestsuiteTimEquSet, TestsuiteLevEquSet;
    rule<ScannerT> TestsuiteTimSpecSet, TestsuiteLevSpecSet, TestsuiteTimSet, TestsuiteLevSet;
    rule<ScannerT> TestsuiteSequencerLabel, TestsuiteFlags, TestsuiteSiteControl, TestsuiteFFCCount;
    rule<ScannerT> TestsuiteTestLevel, TestsuiteDPSSet, TestsuiteWaveformSet, TestsuiteAnalogSet;
    rule<ScannerT> TestsuiteComment;
    rule<ScannerT, sitecontrol_closure::context_t> SiteControlExpression;
    rule<ScannerT> TestsuiteTestNumber, TestsuiteSiteMatch;
    rule<ScannerT> TestflowSection;
    rule<ScannerT> FlowStatements, FlowStatement;
    rule<ScannerT, runstatement_closure::context_t> RunStatement, RunAndBranchStatement;
    rule<ScannerT, ifstatement_closure::context_t> IfStatement;
    rule<ScannerT> GroupStatement;
    rule<ScannerT> GroupBypass;
    rule<ScannerT, definition_closure::context_t> AssignmentStatement;
    rule<ScannerT> StopBinStatement;
    rule<ScannerT, bin_closure::context_t> BinDefinition;
    rule<ScannerT> OOCRule, Quality, Reprobe, Color, BinNumber, Overon;
    rule<ScannerT, print_closure::context_t> PrintStatement, PrintDatalogStatement;
    rule<ScannerT, svlr_closure::context_t> SVLRTimingStatement, SVLRLevelStatement;
    rule<ScannerT, expression_closure::context_t> TestNumLoopInc;
    rule<ScannerT, while_closure::context_t> WhileStatement;
    rule<ScannerT> RepeatStatement;
    rule<ScannerT, for_closure::context_t> ForStatement;
    rule<ScannerT> MultiBinStatement, EmptyStatement;
    rule<ScannerT> SpecialTestsuiteSection;
    rule<ScannerT> DownloadTestsuite, InitTestsuite, PauseTestsuite, AbortTestsuite, ResetTestsuite, ExitTestsuite, DisconnectTestsuite, MultiBinDecisionTestsuite;
    rule<ScannerT> BinningSection;
    rule<ScannerT> OtherwiseBin;
    rule<ScannerT> SetupSection, SetupFiles;
    rule<ScannerT> ConfigFile, LevelsFile, TimingFile, VectorFile, AttribFile, ChannelAttribFile, MixedSignalFile, AnalogControlFile, WaveformFile, RoutingFile, TestTableFile, Protocols;
    rule<ScannerT> OOCSection;
    rule<ScannerT> HardwareBinSection;
    rule<ScannerT, hardbin_closure::context_t> HardBinDescription;
    rule<ScannerT> TestmethodParameterSection, UTMTestmethodParameters;
    rule<ScannerT, testmethodparameter_closure::context_t> TestmethodParameter;
    rule<ScannerT> TestmethodLimitSection, UTMTestmethodLimits;
    rule<ScannerT, testmethodlimit_closure::context_t> TestmethodLimit;
    rule<ScannerT> LowLimitSymbol, HighLimitSymbol;
    rule<ScannerT> UTMTestmethodClass;
    rule<ScannerT> Error;


    rule<ScannerT, overall_closure::context_t> const& start() const { return Start; }

  };
};


void removeComments(ifstream& input, stringbuf& output)
{
  char curr, prev = '\0';
  bool charLiteral   = false;
  bool stringLiteral = false;

  while(input.get(curr)) {

    if(charLiteral) {
      output.sputc(curr);
      if(curr == '\'' && prev != '\\') {
	charLiteral = false;
      }
      prev = (prev == '\\' && curr == '\\') ? '\0' : curr;
    }
    else if(stringLiteral) {
      output.sputc(curr);
      if(curr == '\"' && prev != '\\') {
	stringLiteral = false;
      }
      prev = (prev == '\\' && curr == '\\') ? '\0' : curr;
    }
    else if(prev == '-') {
      if(curr == '-') {
	output.sputc('\n');
	prev = '\0';
	while(input.get() != '\n');
      }
      else {
	output.sputc(prev);
	output.sputc(curr);
	prev = curr;
      }
    }
    else {
      if(curr != '-') {
	output.sputc(curr);
      }
      charLiteral   = (prev != '\\' && curr =='\'');
      stringLiteral = (prev != '\\' && curr =='\"');
      prev = (prev == '\\' && curr == '\\') ? '\0' : curr;
    }
  }
}

class FileLockGuard
{
public:
  FileLockGuard(int fd):mFd(fd) { flock(fd, LOCK_EX); }
  ~FileLockGuard() { flock(mFd, LOCK_UN); close(mFd); }

private:
  int mFd;
};


::xoc_tapi::Testflow* ParseTestflow(const string& filename, 
                                    FastMutex& mutex) throw (xoc::exc::ZCorrectnessException)
{
  Guard< FastMutex > guard(mutex);

  int fd = open(filename.c_str(), O_RDONLY);
  if(fd < 0) {
    return 0;
  }

  FileLockGuard fileGuard(fd);

  ifstream fin;
  fin.open(filename.c_str(), ios_base::in);
  if(!fin.is_open()) {
    fin.close();
    return 0;
  }

  CreateNewTestflow();

  stringbuf cleanFile;

  removeComments(fin, cleanFile);

  fin.close();

  string fileWithoutComments = cleanFile.str();

  if(fileWithoutComments.length() == 0) {
    return GetTestflow();
  }

  
  static TestflowSyntax syntax;

  typedef position_iterator< string::const_iterator > iterator_t;

  iterator_t begin(fileWithoutComments.begin(), fileWithoutComments.end());
  iterator_t end;

  
  parse_info<iterator_t> info;
  XOC_TRY {
    info = parse(begin, end, syntax , space_p);
  }
  XOC_CATCH(ZCorrectnessException& e) {
    DEH_ERROR("Testflow could not be parsed.");
    cerr << e.what << endl;
    XOC_THROW(e, "Invalid testflow");
  }
  XOC_CATCH(...) {
    ZCorrectnessException e;
    e.what = toOu("Invalid testflow");
    XOC_THROW(e, "Invalid testflow");
  }

  if(!info.full) {
    XOC_ERROR("Parser consumed " << info.length << " characters.");
    XOC_ERROR("Hit?: " << info.hit);
    XOC_ERROR("Syntax error at " << info.stop.get_position());
    return NULL;
  }

  return GetTestflow();
}

