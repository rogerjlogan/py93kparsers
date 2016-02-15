import pyparsing as pp
import operator
import math
expop = pp.Literal('**')
plus = pp.Literal('+')
minus = pp.Literal('-')
div = pp.Literal('/') 
mult = (pp.Literal('*') + pp.NotAny("*"))
dot = pp.Literal(".").setName('dot').suppress()
bitOr = pp.Literal('|')
bitAnd = pp.Literal('&')
bitXor = pp.Literal('^')
bitNot = pp.Literal('~')
lShift = pp.Literal("<<")
rShift = pp.Literal(">>")

multop = div ^ mult
addop = plus ^ minus
rPar = pp.Literal(')').suppress()
lPar = pp.Literal('(').suppress()
lBrac = pp.Literal('[').suppress()
rBrac = pp.Literal(']').suppress()
lCur = pp.Literal("{").suppress()
rCur = pp.Literal("}").suppress()
and_ = pp.Keyword('AND') ^ bitAnd    
orXor_ = pp.Keyword('OR') ^ bitOr ^bitXor
not_ =  pp.Keyword('NOT')
qStr = pp.QuotedString(quoteChar='"', unquoteResults=False)
eq = pp.Literal('=').suppress()
neq = pp.Literal('<>')
lessEq = pp.Literal('<=')
grEq = pp.Literal('>=')
less = pp.Literal('<') + pp.NotAny("<=")
gr = pp.Literal('>') + pp.NotAny(">=")
relop = eq ^ neq ^lessEq ^ grEq ^ less ^gr
colon =  (pp.Literal(':') + pp.NotAny(eq)).suppress()
semi = pp.Literal(";").suppress()
# numbers
# commma
comma = pp.Literal(",").suppress()
point = pp.Literal('.')
e = pp.CaselessLiteral('E')
plusorminus = plus ^ minus
number = pp.Word(pp.nums)
decNumber = pp.Combine( pp.Optional(plusorminus) + number
                            )
hexNumber = pp.Combine(pp.CaselessLiteral('0X').suppress()+\
                        pp.Word(pp.hexnums)).setName('hexInt')
    
integer = (decNumber) ^ hexNumber
integer.parseWithTabs()

# pascal has units with floats (TReal).
floatnum = pp.Combine( decNumber +
                    pp.Optional( point + pp.Optional(number) ) +
                    pp.Optional( e + integer ))
floatnum.setParseAction(lambda x : float(x[0]))
HEADER = "hp93000,timing,0.1"
header = pp.Literal(HEADER)
start = pp.Keyword("EQSP")+pp.Keyword("TIM") + comma +\
        pp.Word(pp.alphas+'_') + comma
expr = pp.Forward()
name = pp.Word(pp.alphas+"_", pp.alphanums+"_")
funcall = (name + lPar + pp.delimitedList(expr|qStr) +
                   rPar).setName('funcall')

def getVal(val, envi):
    try:
        if isinstance(val, str):
            return envi[val]
        if isinstance(val, float):
            return val
        return val.eval(envi)
    except KeyError, msg:
        raise
    

class funcEval(object):
    _funDict = dict((meth,getattr(math,meth)) for meth in dir(math) if
                     callable(getattr(math, meth)))
    _funDict['chr'] = chr
    _funDict['abs'] = abs
    _funDict['fract'] = lambda x, y,z : x/y*z
    def __init__(self,toks):
        print "Processing function..." + toks[0]
        self.name = toks[0]
        self.params = toks[1:]
        self.repr = self.name + '(' +\
                    ",".join(str(param) for param in self.params) + ')'
    def eval(self, env=None):
        pars = [getVal(x, env) for x in self.params]
        try:
            return funcEval._funDict[self.name](*pars)
        except KeyError:
            print "Warning!! ", str(self), " not defined"
            return 0

    def __str__(self):
        return self.name + '(' + ", ".join(str(x) for x in self.params)\
               + ')'
    
funcall.setParseAction(funcEval)


atom = floatnum^name^funcall
class singleOpEval(object):
    _opsDict = {'!NOT!' : operator.not_,
                '': lambda x: x,
                '-' : lambda x : -1 * x,
                '~' : operator.inv}
    def __init__(self, toks):
        self.val = toks[0][1]
        self.op = toks[0][0]
        if self.op=='+':
            self.op = ''
        self.elems = [self.val]        
    def eval(self, env=None):
        return self._opsDict[self.op](getVal(self.val, env))

    def __str__(self):
        return self.op + str(self.val)

class opsEval(object):
    _opsDict  = {'**' : operator.pow,
                 '+' : operator.add,
                 '-' : operator.sub,
                 '*' : operator.mul,
                 '/' : operator.div,
                 'DIV' : operator.div,
                 'MOD' : operator.mod,
                 'AND': lambda a,b : a and b,
                 'OR' : lambda a,b : a or b,
                 'NOT': lambda a : not a,
                 '&' : operator.and_,
                 '^' : operator.xor,
                 '|' : operator.or_,
                 'IN': lambda a,b : a in b,
                 '>=': operator.ge,
                 '<=': operator.le,
                 '=' : operator.eq,
                 '<' : operator.lt,
                 '>' : operator.gt,
                 '<>': operator.ne,
                 '>>': operator.rshift,
                 '<<': operator.lshift
                 }

    _opsRepr  = {'**' : '**',
                 '+' : '+',
                 '-' : '-',
                 '*' : '*',
                 '/' : '/',
                 'DIV' : '/',
                 'MOD' : 'mod',
                 'AND': 'and',
                 'OR' : 'or',
                 'NOT': 'not',
                 '&' : '&',
                 '|' : '|',
                 '^' : '^',
                 'IN': 'in',
                 '>=': '>=',
                 '<=': '<=',
                 '=' : '==',
                 '<' : '<',
                 '>' : '>',
                 '<>': '!=',
                 '>>' : '>>',
                 '<<' : '>>'
                 }
    def __init__(self, toks):
        self.val =toks[0][:]


        
    def eval(self, env=None):
        value = getVal(self.val[0], env)

        for op,val in zip(self.val[1::2], self.val[2::2]):
            value2 = getVal(val, env)
            value = self._opsDict[op](value,value2)
        return value
    def addTerms(self, terms):
        return opsEval([self.val + terms])
    def __str__(self):
        strVal = str(self.val[0])
        for op,val in zip(self.val[1::2], self.val[2::2]):
            strVal = strVal + ' ' + self._opsRepr[op] + ' ' +\
                     str(val)

        return '(' + strVal.replace('!','') + ')'



opTup = [(not_|addop|bitNot, 1, pp.opAssoc.RIGHT,singleOpEval),
         (expop, 2, pp.opAssoc.RIGHT, opsEval),
         (multop^and_, 2, pp.opAssoc.LEFT, opsEval),
         (addop^orXor_^rShift^lShift, 2, pp.opAssoc.LEFT, opsEval),
         (relop, 2, pp.opAssoc.LEFT, opsEval)]
expr << pp.operatorPrecedence(atom, opTup)
expr.enablePackrat()
expr.addParseAction(expr.resetCache)
condExpr = expr + pp.Literal('?').suppress() + expr + colon + expr
class CondExpr(object):
    def __init__(self,toks):
        self.cond = toks[0]
        self.trueExp = toks[1]
        self.falseExp = toks[2]
    def eval(self, envi):
        value = getVal(self.cond, envi)
        if value:
            return getVal(self.trueExp, envi)
        return getVal(self.falseExp, envi)
    def __str__(self):
        return str(self.cond) + "? " + str(self.trueExp) + " : " + str(self.falseExp)
condExpr.setParseAction(CondExpr)

valueExpr = expr ^ condExpr + pp.StringEnd()



class Start(object):
    def __init__(self, toks):
        self.st =toks[0] + " " + toks[1]
        self.typ = toks[2]
        
    def __str__(self):
        return self.st + "," + self.typ + ','
start.setParseAction(Start)

end = pp.OneOrMore(pp.Literal('@')) + pp.Keyword("NOOP") + pp.QuotedString(
    quoteChar= '"', unquoteResults=False) + comma + comma + comma

class End(object):
    def __init__(self, toks):
        self.ats = [x for x in toks if x=='@']
        self.ver = toks[-1]
    def __str__(self):
        return "\n".join(self.ats) + "\n\nNOOP " + self.ver + ",,,"
        
end.setParseAction(End)
