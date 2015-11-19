import sys
import os
from pprint import *
import logging as log
import gzip

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

def myOpen(fn, mode="r"):
    if fn.endswith('.gz'):
        return gzip.open(fn,mode)
    return open(fn,mode)

def progress_tracker(lineno):
    if lineno%1000 == 0:
        if lineno==1000:
            sys.stdout.write("\n\nProgress (each dot = 1k lines)\n")
        sys.stdout.write('.')
        if lineno%50000 == 0:
            sys.stdout.write('\n\t')
        elif lineno%10000 == 0:
            sys.stdout.write(' ')
        sys.stdout.flush()

def get_linecount(pathfn):
    # TODO: need windows equivalent
    return os.popen("wc -l "+pathfn).readline().split()[0]

def humanize_time(secs):
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02dh:%02dm:%02ds' % (hours, mins, secs)

def get_recursive_files(item,extension=".csv",zipped_ok=False):
    for dir_,_,files in os.walk(item):
        for fn in files:
            if fn.endswith(extension) or (zipped_ok and fn.endswith(extension+"gz")):
                yield os.path.join(dir_,fn)

def get_files(items,recursive=True,extension=".csv",zipped_ok=False):
    myfiles = []
    for item in items:
        if recursive and os.path.isdir(item):
            myfiles += get_recursive_files(item)
        elif item.endswith(extension) or (zipped_ok and item.endswith(extension+"gz")):
            myfiles.append(item)
    numfiles = len(myfiles)
    if numfiles == 0:
        sys.exit("ERROR! No files passed")
    return myfiles,numfiles

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def splitfile_delim(filename,delim=''):
    import itertools as it
    with open(filename,'r') as f:
        for key,group in it.groupby(f,lambda line: line.startswith(delim)):
            if not key:
                return list(group)

class LineSplitter(object):
        def __init__(self, token):
            self.token = token
            self.count = 0
            self.prev = ''
        def __call__(self, token):
            self.count += (self.prev == self.token)
            self.prev = token
            return self.count

def print2file(ostring, ofile="debug.out"):
    f = open(ofile,"wb")
    pprint(ostring,f, indent=4)
    f.close()

def init_logging(scriptname='default.log', args=None):
    """
    :param args: argparse object with (at least) the following objects:
        args.output_dir
        args.verbose
        args.maxlogs
    """
    if not isinstance(vars(args),dict):
        sys.exit('ERROR!!! "args" passed is not a argparse object.  Exiting ...')

    outdir = ''
    if args.maxlogs > 0:
        warn_msg = []
        info_msg = []
        if len(args.output_dir):
            if os.path.isfile(args.output_dir):
                # let's not clobber the file
                outdir = os.path.split(args.output_dir)[0]
                msg = 'output_dir: ' + args.output_dir + ' is a file! Creating directory in ' + outdir
                warn_msg.append(msg)
                print 'WARNING! : ' + msg
            else:
                outdir = args.output_dir
                if not os.path.isdir(outdir):
                    try:
                        msg = "Creating new directory: "+outdir
                        info_msg.append(msg)
                        os.makedirs(outdir)
                    except:
                        err = 'Unable to create directory: '+outdir+'\n'
                        err += 'Check file read/write permissions\n'
                        err += 'You might also try closing all editors and explorer windows with a view in this directory.\n'
                        print err
                        raise IOError

        if len(args.name):
            progname = '_'+args.name
        else:
            progname = ''
        basename = scriptname.split('.')[0]+progname
        logname = basename + '.log'
        log_pathfn = os.path.join(outdir, logname)

        counter = 0
        while os.path.isfile(log_pathfn):
            counter += 1
            if counter >= args.maxlogs:
                warn_msg.append('maxlogs reached! Consider moving/deleting previous logs. Clobbering ' + logname)
                break
            else:
                logname = basename + '.' + str(counter) + '.log'
                log_pathfn = os.path.join(outdir, logname)

        print '\nCreating log file:',log_pathfn
        log.basicConfig(filename=log_pathfn, format='%(asctime)s %(levelname)s: %(message)s', level=log.INFO, datefmt='%m/%d/%Y %I:%M:%S %p', filemode='w')
        for msg in warn_msg:
            log.warning(msg)
        for msg in info_msg:
            log.info(msg)
    else:
        log.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=log.INFO, datefmt='%m/%d/%Y %I:%M:%S %p')
    if args.verbose:
        log.getLogger().setLevel('DEBUG')
        log.debug('Setting log level to DEBUG (-v option was passed)')
    else:
        log.getLogger().setLevel('INFO')
        log.info('Setting log level to INFO (add -v option to see more stuff logged)')
        log.debug('Test string. You should NOT see this in the log file.')

    if isinstance(vars(args),dict):
        for k,v in vars(args).iteritems():
            if len(str(v).strip()):
                log.debug('ARGUMENT PASSED: name(%s) = %s',k,v)

    log.info('BEGIN ' + scriptname)
    return outdir

from tempfile import mkstemp
from shutil import move
from os import remove, close

def replace(file_path, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    with gzip.open(abs_path,'wb') as new_file:
        with myOpen(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    close(fh)
    #Remove original file
    remove(file_path)
    #Move new file
    move(abs_path, file_path)
