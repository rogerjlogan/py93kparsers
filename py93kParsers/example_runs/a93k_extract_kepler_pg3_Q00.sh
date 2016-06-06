#!/bin/csh
unsetenv PYTHONPATH
unsetenv LD_LIBRARY_PATH
set path = ( /db/kepler_pe/93k/anaconda_ete/bin $path )
set python = /db/kepler_pe/93k/anaconda_ete/bin/python
set script = /db/kepler_pe/93k/working/py93kParsers/a93k_extract.py

$python $script\
    -tp /db/kepler_pe_sl/93k/prod_pgms/KEPLERI83Q00/KEPLERI83Q00/testprog/KEPLERI83Q00.tpg\
    -name kepler_pg3_Q00\
    -bin BinningKepler_pg3.csv\
    -out /db/kepler_pe/93k/working/py93kParsers/py93kParsers/example_runs/kepler_pg3_Q00\
    -tt2c QUAL_T0\
    -pic png\
    -c\
    -ignore kepler.ignore
