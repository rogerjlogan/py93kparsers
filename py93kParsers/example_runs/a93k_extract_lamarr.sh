#!/bin/csh
unsetenv PYTHONPATH
unsetenv LD_LIBRARY_PATH
set path = ( /db/kepler_pe/93k/anaconda_ete/bin $path )
/db/kepler_pe/93k/anaconda_ete/bin/python /db/kepler_pe/93k/working/py93kParsers/a93k_extract.py\
    -tp /db/lamarr_pe/93k/working/kimc/lamarr/testprog/F791857_Final_RPC.tpg\
    -name lamarr\
    -bin BinningLamarr.csv\
    -out /db/kepler_pe/93k/working/py93kParsers/py93kParsers/example_runs/lamarr\
    -tt2c FT_RPC_HT\
    -pic png\
    -c\
    -ignore lamarr.ignore
