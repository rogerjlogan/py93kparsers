#!/bin/csh
unsetenv PYTHONPATH
unsetenv LD_LIBRARY_PATH
set path = ( /db/kepler_pe/93k/anaconda_ete/bin $path )
/db/kepler_pe/93k/anaconda_ete/bin/python /db/kepler_pe/93k/working/py93kParsers/ti_binning.py\
    -tp /db/kepler_pe/93k/working/py93kParsers/example_progs/KEPLERI8220/testprog/KEPLERI8220.tpg\
    -name kepler_r20\
    -bin BinningKepler_pg2.csv\
    -out /db/kepler_pe/93k/working/py93kParsers/example_runs/kepler_r20\
    -tt2c FT_RPC_HT\
    -pic png\
    -c\
    -ignore kepler.ignore
