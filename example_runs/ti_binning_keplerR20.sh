#!/bin/csh
unsetenv PYTHONPATH
unsetenv LD_LIBRARY_PATH
/db/kepler_pe/93k/anaconda_ete/bin/python /db/kepler_pe/93k/py93kParsers/working/ti_binning.py\
    -tp /db/kepler_pe/93k/py93kParsers/working/example_progs/KEPLERI8220/testprog/KEPLERI8220.tpg\
    -name kepler_r20\
    -bin BinningKepler_pg2.csv\
    -out /db/kepler_pe/93k/py93kParsers/working/example_runs/kepler_r20\
    -tt2c FT_RPC_HT\
    -pic png
    -c
#    -ignore kepler.ignore
