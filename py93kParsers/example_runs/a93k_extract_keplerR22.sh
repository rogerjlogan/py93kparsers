#!/bin/csh
unsetenv PYTHONPATH
unsetenv LD_LIBRARY_PATH
set path = ( /db/kepler_pe/93k/anaconda_ete/bin $path )
/db/kepler_pe/93k/anaconda_ete/bin/python /db/kepler_pe/93k/working/py93kParsers/a93k_extract.py\
    -tp /db/kepler_pe_sl/93k/prod_pgms/KEPLERI8222/KEPLERI8222/testprog/KEPLERI8222.tpg\
    -name kepler_r22\
    -bin BinningKepler_pg2.csv\
    -out /db/kepler_pe/93k/working/py93kParsers/py93kParsers/example_runs/kepler_r22\
    -tt2c FT_RPC_HT\
    -pic png\
    -c\
    -ignore kepler.ignore
