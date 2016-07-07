#!/bin/csh

unsetenv PYTHONPATH
unsetenv LD_LIBRARY_PATH
set path = ( /db/kepler_pe/93k/anaconda_ete/bin $path )
set python = /db/kepler_pe/93k/anaconda_ete/bin/python
set script = /db/kepler_pe/93k/working/py93kParsers/py93kParsers/MatchLoopFixer.py

# setting this env variable will drastically improve FW commands in script
set session = `/opt/hp93000/soc/system/bin/sessionfinder.ksh`
setenv XOC_SESSION $session

$python $script\
    -name test\
    -out /tmp/matchloop_fixer # modify this to point wherever you want log file(s) to go\
    -comm_port pOTHER\
    -cmt_offst 1\
    -d
