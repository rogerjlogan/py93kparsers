#!/bin/bash

unset PYTHONPATH
unset LD_LIBRARY_PATH
path=/db/kepler_pe/93k/anaconda_ete/bin:$path
python=/db/kepler_pe/93k/anaconda_ete/bin/python
script=/db/kepler_pe/93k/working/py93kParsers/py93kParsers/MatchLoopFixer.py

# setting XOC_SESSION env variable will drastically improve speed of FW commands in script
# without XOC_SESSION, every FW command sent to hpt causes hpt to run sessionfinder.ksh
sessionfinder=/opt/hp93000/soc/system/bin/sessionfinder.ksh
if [ -f $sessionfinder ]; then
    session=`$sessionfinder 2>/dev/null`
    export XOC_SESSION=$session
    echo "Setting XOC_SESSION=$session"
else
    echo "WARNING: Unable to find sessionfinder.ksh!"
    echo "Cannot set XOC_SESSION which will make this script very slow!"
fi

$python $script\
    -name omap5\
    -out /var/opt/hp93000/soc/MatchLoopFixer\
    -comm_port pOTHER\
    -cmt_offst 1\
    -bin

