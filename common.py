import sys
import os
from pprint import *
import logging
import gzip
from itertools import islice

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

def get_valid_dir(name,outdir=''):

    warn_msg = []
    info_msg = []

    if len(outdir) and not os.path.isdir(outdir):
        warn = '%s is NOT a valid directory'.format(outdir)
        print 'WARNING!!! '+warn
        warn_msg.append(warn)
        outdir = ''

    if not len(outdir):
        outdir = os.path.join(os.path.dirname(os.path.realpath(__file__)),name)

    if os.path.isfile(outdir):
        # let's not clobber the file
        outdir = os.path.split(outdir)[0]
        msg = 'output_dir: ' + outdir + ' is a file! Creating directory in ' + outdir
        warn_msg.append(msg)
        print 'WARNING! : ' + msg
    else:
        outdir = outdir
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
    return outdir,info_msg,warn_msg

def get_valid_file(scriptname=os.path.basename(sys.modules[__name__].__file__),name='',outdir='',maxlogs=1,ext='.log'):
    outdir,info_msg,warn_msg = get_valid_dir(name=name,outdir=outdir)
    if len(name):
        progname = name+'_'
    else:
        progname = ''
    basename = progname + scriptname.split('.')[0]
    fn = basename + ext
    pathfn = os.path.join(outdir, fn)

    counter = 0
    while os.path.isfile(pathfn):
        counter += 1
        if counter >= maxlogs:
            info_msg.append('maxlogs={} (default=1) Consider moving/deleting previous files (logs,png\'s,csv\'s,etc) between runs. Overwriting {}'.format(maxlogs,fn))
            break
        else:
            fn = basename + '.' + str(counter) + ext
            pathfn = os.path.join(outdir, fn)

    msg = 'Creating file: '+pathfn
    print msg
    info_msg.append(msg)
    return pathfn,outdir,info_msg,warn_msg

def init_logging(scriptname=os.path.basename(sys.modules[__name__].__file__), outdir='', name='', maxlogs=1 ,level=logging.INFO):

    logger_name = 'log'
    if maxlogs > 0:

        pathfn,outdir,info_msg,warn_msg = get_valid_file(scriptname=scriptname,name=name,outdir=outdir,maxlogs=maxlogs,ext='.log')

        basename = os.path.basename(pathfn).split('.')[0]
        logger_name = 'log_'+basename
        l = logging.getLogger(logger_name)
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')
        fileHandler = logging.FileHandler(pathfn, mode='w')
        fileHandler.setFormatter(formatter)

        l.setLevel(level)
        l.addHandler(fileHandler)

        log = logging.getLogger(logger_name)

        for msg in warn_msg:
            print 'WARNING!!! ',msg
            log.warning(msg)
        for msg in info_msg:
            log.info(msg)
    else:
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=level, datefmt='%m/%d/%Y %I:%M:%S %p')

    return logger_name,outdir

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


def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))


class TextException(Exception): pass


def prompt_user(query,errmsg,choices):
    my_exit = False
    while 1:
        try:
            ans = raw_input(query)
            if ans.lower() == 'q':
                my_exit = True
                break
            elif ans.lower() not in choices:
                raise TextException()
            else:
                break
        except Exception:
            print errmsg
    if my_exit:
        sys.exit()
    else:
        return ans

class callcounted(object):
    """Decorator to determine number of calls for a method"""

    def __init__(self,method):
        self.method=method
        self.counter=0

    def __call__(self,*args,**kwargs):
        self.counter+=1
        return self.method(*args,**kwargs)
