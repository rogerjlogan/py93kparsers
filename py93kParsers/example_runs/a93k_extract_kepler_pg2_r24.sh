#!/bin/csh
unsetenv PYTHONPATH
unsetenv LD_LIBRARY_PATH
set path = ( /db/kepler_pe/93k/anaconda_ete/bin $path )
set python = /db/kepler_pe/93k/anaconda_ete/bin/python
set script = /db/kepler_pe/93k/working/py93kParsers/a93k_extract.py

$python $script\
    -tp /db/kepler_pe_sl/93k/prod_pgms/KEPLERI8224/KEPLERI8224/testprog/KEPLERI8224.tpg\
    -name kepler_pg2_r24\
    -bin BinningKepler_pg2.csv\
    -out /db/kepler_pe/93k/working/py93kParsers/py93kParsers/example_runs/kepler_pg2_r24\
    -tt2c PB_RPC_LT\
    -pic png\
    -c\
    -ignore kepler.ignore
