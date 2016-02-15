#!/bin/csh
unsetenv PYTHONPATH
unsetenv LD_LIBRARY_PATH
set path = ( /db/kepler_pe/93k/anaconda_ete/bin $path )
/db/kepler_pe/93k/anaconda_ete/bin/python /db/kepler_pe/93k/working/py93kParsers/a93k_extract.py\
    -tp /data/mkoe3/VAYU/USERS/cgreen/VAYU_FPC/VAYU/testprog/VAYUFPC.tpg\
    -name vayu\
    -out /db/kepler_pe/93k/working/py93kParsers/py93kParsers/example_runs/vayuFPC\
    -pic png

