#!/bin/bash
#Description: Dynamically modifies the RPTV counts to find the first passing
#condition of an MATCHLOOP flattened pattern. Considers the fact that these
#patterns have multiple ports and the modulo behavior needs to be preserved for LMAP.
#
#optional arguments:
#  -h, --help            show this help message and exit
#  -name NAME, --name NAME
#                        Optional name used for output files/logs.
#  -d, --debug           print a lot of debug stuff to dlog
#  -out OUTPUT_DIR, --output_dir OUTPUT_DIR
#                        Directory to place log file(s).
#  -max MAXLOGS, --maxlogs MAXLOGS
#                        (0=OFF:log data to stdout).Set to 1 to keep only one
#                        log (subsequent runs will overwrite).
#  -comm_port COMMENT_PORT, --comment_port COMMENT_PORT
#                        Port that has the search comments (just give one port,
#                        even if others have the string.
#  -cmt_offst COMMENT_OFFSET, --comment_offset COMMENT_OFFSET
#                        Vector comment address offset from matchloop.
#                        (0=comm_srch_str is on matchloop repeat vector;
#                        -1=comm_srch_str is one vector BEFORE matchloop START;
#                        1=comm_srch_str is one vector AFTER matchloop END)
#  -comm_srch_str COMMENT_SEARCH_STRING, --comment_search_string COMMENT_SEARCH_STRING
#                        String to search for in comments
#  -keep_temp_burst KEEP_TEMP_BURST, --keep_temp_burst KEEP_TEMP_BURST
#                        Do not delete the temporary burst at the end of the
#                        script exeuction (not the default)
#  -skip_func, --skip_func
#                        Do not run an initial functional test... not the
#                        default !
#  -bin, --bin           Dse a binary search algorithm instead of linear... not
#                        the default !

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

