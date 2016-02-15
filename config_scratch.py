import util
import re
import os

dirPath = "/HDD1TB/qcom/jacob/q55xx/trunk/Q55xx"
configFile = os.path.join(dirPath,"configuration", "Q55XX.cfg")
f = util.FileUtils(configFile, True)

# read in config file.  populate dict structure of pin groups, pins, and ports
g = util.m_re(f.contents)
g.grep("^DFPN\s+\w+,\s*\"\w+\",\(\w+\)")
pinListDict = [re.search("^DFPN\s+(?P<chan>\w+),\s*\"(?P<id>\w+)\",\s*\((?P<pin>\w+)\)", a_row) for a_row in g.lines]
pinList = [m.groupdict()["pin"] for m in pinListDict if m]

g.clear_cache()
g.grep("^DFGP")
chkList = [re.search("DFGP\s+\w+,\((?P<pins>[\w\,]+)\),\((?P<pin_group>\w+)\)", a_row) for a_row in g.lines]
pinGroupDict = {}
for m in chkList:
    if m:
        pinGroup, pins = m.groupdict()["pin_group"], m.groupdict()["pins"].split(",")
        if not pinGroupDict.has_key(pinGroup):
            pinGroupDict[pinGroup] = []
        pinGroupDict[pinGroup] = list(set(pinGroupDict[pinGroup] + pins))

g.clear_cache()
g.grep("^DFPT")
chkList = [re.search("DFPT\s+\((?P<pins>[\w\,]+)\),\((?P<port>\w+)\)", a_row) for a_row in g.lines]
portDict = {}
for m in chkList:
    if m:
        port, pins = m.groupdict()["port"], m.groupdict()["pins"].split(",")
        if not portDict.has_key(port):
            portDict[port] = []
        portDict[port] += pins

# pull in D10 bin map and definitions
d10DirPathTester = "/HDD1TB/qcom/jacob/csr_q55xx_d10/trunk/Q55XX_B0_FT_D10/FT_DF/FT_D10_r2_TP/tester"
d10BinDefFn = "55XX.bindef"
d10BinMapFn = "55XX.binmap"
f = util.FileUtils(os.path.join(d10DirPathTester, d10BinDefFn), True)
g = util.m_re([a_row.strip() for a_row in f.contents])
g.grep("^Bin (?:FAIL|PASS) \"\w+\" \d+")
chkList = [
    re.search("^Bin (?P<pf>FAIL|PASS) \"(?P<name>\w+)\" (?P<bin>\d+)(?:\s?\"(?P<comment>[\w\s]+)\")?;", a_row)
    for a_row in g.lines
]
binDefDict = {}
for m in chkList:
    if m:
        aDict = m.groupdict()
        if not binDefDict.has_key(aDict["name"]):
            binDefDict[aDict["name"]] = dict([(k,v) for k,v in aDict.iteritems() if not k == "name"])

f = util.FileUtils(os.path.join(d10DirPathTester, d10BinMapFn), True)
g = util.m_re([a_row.strip() for a_row in f.contents])
g.grep("^\"\w+\"\s+.>\s+\d+;")
chkList = [re.search("^\"(?P<name>\w+)\"\s+->\s+(?P<bin>\d+);", a_row) for a_row in g.lines]
binMapDict = {}
for m in chkList:
    if m:
        aDict = m.groupdict()
        if not binMapDict.has_key(aDict["name"]):
            binMapDict[aDict["name"]] = {"bin": int(aDict["bin"])}

# get lookup table for v93k test table and bin names
f = util.FileUtils("/home/jacob/Projects/q55xx/v93kLookUpTable.csv", True)
chkList = [a_row.strip().split(",") for a_row in f.contents]
v93kTestSuite2BinNameDict = dict([tuple(a_row) for a_row in chkList])

# line up D10 and V93K test names
v93kDlogFn = "/home/jacob/Projects/q55xx/dlogV93K_20151209.txt"
f = util.FileUtils(v93kDlogFn, True)
g = util.m_re(f.contents)
g.grep("(?:Started Testsuite|Test Name:)")
iList = [(i,int(float(a_coord)-1)) for (i,a_line), a_coord in zip(enumerate(g.lines), g.coordinates) if util.in_string(a_line, "Testsuite")]
testSuites = []
testSuiteDict = {}
for cStart, cStop in zip(iList[:-1], iList[1:]):
    iStart, m = cStart[0], re.search("^=+\s+Started Testsuite (?P<id>\w+) =+", g.lines[cStart[0]])
    iStop = cStop[0]
    if m:
        testSuite = m.groupdict()["id"]
        if not testSuiteDict.has_key(testSuite):
            testSuiteDict[testSuite] = []
    else:
        testSuite = "UhOh:{0}:{1}".format(cStart[0],cStart[1])
    testSuites.append(testSuite)
    for aLine in g.lines[iStart+1:iStop]:
        m = re.search("^-+\s+Test Name:\s+(?P<id>\w+)(?:@\w+)?:", aLine)
        if m:
            testSuiteDict[testSuite].append(m.groupdict()["id"])

# setup binning for v93k test table
q55xxDirPath = "/HDD1TB/qcom/jacob/q55xx/trunk/Q55xx"
testTableFields = [
    "Suite name","Test name","Test number","FT_Lsl","FT_Lsl_typ","FT_Usl_typ",
    "FT_Usl","FT_Units","WS_Lsl","WS_Lsl_typ","WS_Usl_typ","WS_Usl","WS_Units",
    "QA_Lsl","QA_Lsl_typ","QA_Usl_typ","QA_Usl","QA_Units","Bin_s_num",
    "Bin_s_name","Bin_h_num","Bin_h_name","Bin_type","Bin_reprobe",
    "Bin_overon","Test_remarks"
]
testKeys = ("Suite name", "Test name", "Test number")
testFields = [aField for aField in testTableFields]
util._list_reduce(testKeys, testFields)
q55xxTestTableFn = os.path.join(q55xxDirPath, "testtable", "55xx_Screen")
f = util.FileUtils(q55xxTestTableFn, True)
header = f.contents[:2]
chkList = [re.sub('"', "", a_row).strip() for a_row in f.contents]
aList = [a_row.split(",") for a_row in chkList[2:]]
aListDict = [dict([(k, v) for k,v in zip(testTableFields, a_row)]) for a_row in aList]
testTableDict = {}
for aDict in aListDict:
    aKey = ":".join([aDict[k] for k in testKeys])
    if not testTableDict.has_key(aKey):
        testTableDict[aKey] = dict([(k, aDict[k]) for k in testTableFields])

# merge in bins for test table
binKeys = "Bin_h_name Bin_h_num Bin_s_name Bin_s_num".split()
for tKey, tDict in testTableDict.iteritems():
    testSuite, testName, testNumber = tKey.split(":")
    binName = v93kTestSuite2BinNameDict[testSuite]
    hBin = binMapDict[binName]["bin"]
    sBin = int(binDefDict[binName]["bin"])
    for binKey, binValue in zip(binKeys,  [binName, hBin, binName, sBin]):
        tDict[binKey] = binValue

f = util.FileUtils("/tmp/newTable.csv")
m = util.m_sort(testTableDict.keys())
m.sort_by([2,0,1], delim=":", joint=":", do_reverse=[False,False,False])
testSeq = m.sortList
chkList = []
for testKey in testSeq:
    chkList.append(",".join(["\"{0}\"".format(testTableDict[testKey][aField]) for aField in testTableFields]))

f.write_to_file(header + chkList)

# add test category WS
testCatWSFields = ["WS_Lsl","WS_Lsl_typ","WS_Usl_typ","WS_Usl","WS_Units"]
testCatFTFields = ["FT_Lsl","FT_Lsl_typ","FT_Usl_typ","FT_Usl","FT_Units"]
for k,v in testTableDict.iteritems():
    for ws, ft in zip(testCatWSFields, testCatFTFields):
        v[ws] = v[ft]

testTableFields = [
    "Suite name","Test name","Test number","FT_Lsl","FT_Lsl_typ","FT_Usl_typ",
    "FT_Usl","FT_Units","WS_Lsl","WS_Lsl_typ","WS_Usl_typ","WS_Usl","WS_Units",
    "QA_Lsl","QA_Lsl_typ","QA_Usl_typ","QA_Usl","QA_Units","Bin_s_num",
    "Bin_s_name","Bin_h_num","Bin_h_name","Bin_type","Bin_reprobe",
    "Bin_overon","Test_remarks"
]

#BIG TIME scratch.... adding new tests into table
sList = ["SLT_VERFAIL", "SLT_PLLFAIL", "SLT_RTCFAIL", "SLT_LVDSFAIL", "SLT_VX1FAIL", "SLT_OTPFAIL", "SLT_CIPFAIL", "SLT_A15FAIL", "SLT_DACADCFAIL", "SLT_USB3FAIL", "SLT_PCIEFAIL", "SLT_SATAFAIL", "SLT_DDRFAIL"]
tList = ["VERFAIL", "PLLFAIL", "RTCFAIL", "LVDSFAIL", "VX1FAIL", "OTPFAIL", "CIPFAIL", "A15FAIL", "DACADCFAIL", "USB3FAIL", "PCIEFAIL", "SATAFAIL", "DDRFAIL", "RWMFAIL"]
aString = "\"SLT\",\"{testName}\",\"{testNum}\",\"1\",\"GE\",\"LE\",\"1\",\"\",\"1\",\"GE\",\"LE\",\"1\",\"\",\"1\",\"GE\",\"LE\",\"1\",\"\",\"{sBinNum}\",\"{sBinName}\",\"{hBinNum}\",\"{hBinName}\",\"\",\"\",\"\",\"\""
chkList = [aString.format(testName=t, testNum=i, sBinNum=binDefDict[s]["bin"], sBinName=s, hBinNum=3, hBinName="FAIL_SLT") for t,s,i in zip(tList, sList, xrange(140001,140015,1))]

#redefining some HBINS:
hBinKeys = ["Bin_h_num", "Bin_h_name"]
chkList = [aKey for aKey in testTableDict.iterkeys() if not util.in_string(aKey, "(?:CONT|SLT|IDD)")] #FAIL_FUNC, 2
binNum, binName = 2, "FAIL_FUNC"
for aKey in chkList:
    testTableDict[aKey]["Bin_h_num"] = binNum
    testTableDict[aKey]["Bin_h_name"] = binName

chkList = list(set(testTableDict.keys()) - set(chkList))
chkList = [aKey for aKey in chkList if not util.in_string(aKey, "SLT")]
binNum, binName = 5, "FAIL_CONT"

# do dir listing comparison between 93k programs, see where they line up
dirPathA = "/HDD1TB/qcom/jacob/q55xx/trunk"
dirPathB = ""