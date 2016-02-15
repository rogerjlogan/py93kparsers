import xlwt

titleStyle = xlwt.easyxf('pattern:pattern solid, fore_colour light_yellow;'
                         'align: vertical centre, horizontal centre;'
                         'border: right medium, bottom medium, left medium, top medium;')

bodyStyle = xlwt.easyxf('pattern:pattern solid, fore_colour light_green;'
                        'align: vertical centre, horizontal centre;'
                        'border: right thin, bottom thin, left thin,top thin;')
bodyLeft  = xlwt.easyxf('pattern:pattern solid, fore_colour light_green;'
                        'align: vertical centre, horizontal left;'
                        'border: right thin, bottom thin, left thin,top thin;')
titleLeft = xlwt.easyxf('pattern:pattern solid, fore_colour light_yellow;'
                         'align: vertical centre, horizontal left;'
                         'border: right medium, bottom medium, left medium, top medium;')

def _addTitle(sheet, names, style = titleStyle, startRow=0,
              startCol=0, defWidth=256*30):
    for ii, name in enumerate(names):
        sheet.row(startRow).write(startCol+ii, name, style=style)
        sheet.col(startCol+ii).width = defWidth

def createFlowSheet(flowDict, wkBook):
    assert(isinstance(wkBook, xlwt.Workbook))
    sheet = wkBook.add_sheet("TEST_FLOW")
    _addTitle(sheet, ["GROUP", "TEST_SUITE", "Test Method"])
    sheet.write_merge(1,1,4,6, "Timinig", titleStyle)
    sheet.write_merge(1,1,7,9, "Levels", titleStyle)
    _addTitle(sheet, ["SPEC", "EQU", "TINESET"], startRow=2, startCol=4)
    _addTitle(sheet, ["EQUSET","SPECSET", "LEVELSET"], startRow=2, startCol=7)
    groups = sorted((flowDict[x]['_ii'],x) for x in flowDict)
    groups = [x[1] for x in groups]
    currRow = 3
    for grpName in groups:
        sheet.write_merge(currRow, currRow+len(flowDict[grpName])-2, 1, 1, grpName, style=bodyStyle)
        suites = sorted((flowDict[grpName][x]['_ii'],x) for x in flowDict[grpName] if x != '_ii')
        suites = [x[1] for x in suites]
        for ii, name in enumerate(suites):
            sheet.row(currRow+ii).write(2,name, style=bodyStyle)
            sheet.row(currRow+ii).write(3, flowDict[grpName][name]['TM'],style=bodyStyle)
            sheet.row(currRow+ii).write(4, str(flowDict[grpName][name]['TIM']['timSpec']),style=bodyStyle)
            sheet.row(currRow+ii).write(5, str(flowDict[grpName][name]['TIM']['timEq']),style=bodyStyle)
            sheet.row(currRow+ii).write(6, str(flowDict[grpName][name]['TIM']['timSet']),style=bodyStyle)
            sheet.row(currRow+ii).write(7, str(flowDict[grpName][name]['LEVS']['levEq']),style=bodyStyle)
            sheet.row(currRow+ii).write(8, str(flowDict[grpName][name]['LEVS']['levSpec']),style=bodyStyle)
            sheet.row(currRow+ii).write(9, str(flowDict[grpName][name]['LEVS']['levSet']),style=bodyStyle)
        currRow += len(flowDict[grpName]) - 1


