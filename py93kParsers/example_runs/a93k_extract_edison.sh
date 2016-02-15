#!/bin/csh
unsetenv PYTHONPATH
unsetenv LD_LIBRARY_PATH
set path = ( /db/kepler_pe/93k/anaconda_ete/bin $path )
/db/kepler_pe/93k/anaconda_ete/bin/python /db/kepler_pe/93k/working/py93kParsers/a93k_extract.py\
    -tp /db/edison_pe/v93k/prod_pgms/EDISON93K02/EDISON93K02/testprog/EDISON93K02.tpg\
    -name edison\
    -bin BinningEdison.csv\
    -out /db/kepler_pe/93k/working/py93kParsers/py93kParsers/example_runs/edison\
    -tt2c FT_RPC_HT\
    -pic png\
    -c
