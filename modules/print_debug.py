__author__ = 'Roger'

from pprint import pprint

def print2file(ostring, ofile="debug.out"):
    f = open(ofile,"wb")
    pprint(ostring,f, indent=4)
    f.close()