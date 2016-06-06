#!/bin/csh
unsetenv PYTHONPATH
unsetenv LD_LIBRARY_PATH
unsetenv LD_LIBRARY_PATH
set path = ( /db/kepler_pe/93k/anaconda_ete/bin $path )
set python = /db/kepler_pe/93k/anaconda_ete/bin/python
set script = /db/kepler_pe/93k/working/py93kParsers/a93k_extract.py

$python $script\
    -tp /db/kepler_pe_sl/93k/prod_pgms/KEPLERI8324/KEPLERI8324/testprog/KEPLERI8324.tpg\
    -name kepler_pg3\
    -bin BinningKepler_pg3.csv\
    -out /db/kepler_pe/93k/working/py93kParsers/py93kParsers/example_runs/kepler_pg3\
    -tt2c FT_RPC_HT\
    -pic png\
    -c\
    -ignore kepler.ignore
