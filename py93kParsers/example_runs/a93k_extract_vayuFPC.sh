#!/bin/csh
unsetenv PYTHONPATH
unsetenv LD_LIBRARY_PATH
set path = ( /db/kepler_pe/93k/anaconda_ete/bin $path )

# number of arguments is $#argv
# if argument supplied, it will be used to specify the working directory and should be the toplevel 
# of the local git repository, i.e. /db/kepler_pe/93k/working/py93kParsers, which will in
# turn be used to specify the a93k_extract.py file location and output directory
if ( $#argv == 1 ) then
    set workDir = ($1 )
else
    set workDir = ( /db/kepler_pe/93k/working/py93kParsers )
endif
set outDir = ( $workDir/py93kParsers/example_runs/vayuFPC )

/db/kepler_pe/93k/anaconda_ete/bin/python $workDir/a93k_extract.py\
    -tp /data/mkoe3/VAYU/USERS/cgreen/VAYU_FPC/VAYU/testprog/VAYUFPC.tpg\
    -name vayuFPC\
    -out $outDir\
    -pic png

