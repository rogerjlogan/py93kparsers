#!/bin/csh
unsetenv PYTHONPATH
unsetenv LD_LIBRARY_PATH
set path = ( /db/kepler_pe/93k/anaconda_ete/bin $path )
set python = /db/kepler_pe/93k/anaconda_ete/bin/python
set script = /db/kepler_pe/93k/working/py93kParsers/a93k_extract.py

$python $script\
    -tp /db/kepler_pe_sl/93k/prod_pgms/KEPLERI8326/KEPLERI8326/testprog/KEPLERI8326.tpg\
    -name kepler_pg3_r26\
    -bin BinningKepler_pg3.csv\
    -out /db/kepler_pe/93k/working/py93kParsers/py93kParsers/example_runs/kepler_pg3_r26\
    -tt2c PB_RPC_LT\
    -pic png\
    -c\
    -ignore kepler.ignore
