#!/bin/csh
unsetenv PYTHONPATH
unsetenv LD_LIBRARY_PATH
/db/kepler_pe/93k/anaconda_ete/bin/python /db/kepler_pe/93k/py93kParsers/working/ti_binning.py\
    -tp /db/kepler_pe/93k/py93kParsers/working/example_progs/lamarr/testprog/F791857_Final_RPC.tpg\
    -name lamarr\
    -bin BinningLamarr.csv\
    -out /db/kepler_pe/93k/py93kParsers/working/example_runs/lamarr_chinhn\
    -tt2c FT_RPC_HT\
    -pic png\
    -c
#    -ignore lamarr.ignore
