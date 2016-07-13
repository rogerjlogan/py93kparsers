import sys
import os
from pprint import *
import logging
import gzip
from itertools import islice
from tempfile import mkstemp
from shutil import move
from os import remove, close
from sys import maxint
import re
import traceback
import argparse
import math
import platform


class color:
    PURPLE = '\033[95m'    # '\x1b[95m'
    CYAN = '\033[96m'      # '\x1b[96m'
    DARKCYAN = '\033[36m'  # '\x1b[36m'
    BLUE = '\033[94m'      # '\x1b[94m'
    GREEN = '\033[92m'     # '\x1b[92m'
    YELLOW = '\033[33m'    # '\x1b[33m'
    GREY = '\033[90m'      # '\x1b[90m'
    RED = '\033[91m'       # '\x1b[91m'
    BOLD = '\033[1m'       # '\x1b[1m'
    UNDERLINE = '\033[4m'  # '\x1b[4m'
    END = '\033[0m'        # '\x1b[0m'


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

def add_coloring_to_emit_windows(fn):
        # add methods we need to the class
    def _out_handle(self):
        import ctypes
        return ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
        out_handle = property(_out_handle)

    def _set_color(self, code):
        import ctypes
        # Constants from the Windows API
        self.STD_OUTPUT_HANDLE = -11
        hdl = ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
        ctypes.windll.kernel32.SetConsoleTextAttribute(hdl, code)

    setattr(logging.StreamHandler, '_set_color', _set_color)

    def new(*args):
        FOREGROUND_BLUE      = 0x0001 # text color contains blue.
        FOREGROUND_GREEN     = 0x0002 # text color contains green.
        FOREGROUND_RED       = 0x0004 # text color contains red.
        FOREGROUND_INTENSITY = 0x0008 # text color is intensified.
        FOREGROUND_WHITE     = FOREGROUND_BLUE|FOREGROUND_GREEN |FOREGROUND_RED
       # winbase.h
        STD_INPUT_HANDLE = -10
        STD_OUTPUT_HANDLE = -11
        STD_ERROR_HANDLE = -12

        # wincon.h
        FOREGROUND_BLACK     = 0x0000
        FOREGROUND_BLUE      = 0x0001
        FOREGROUND_GREEN     = 0x0002
        FOREGROUND_CYAN      = 0x0003
        FOREGROUND_RED       = 0x0004
        FOREGROUND_MAGENTA   = 0x0005
        FOREGROUND_YELLOW    = 0x0006
        FOREGROUND_GREY      = 0x0007
        FOREGROUND_INTENSITY = 0x0008 # foreground color is intensified.

        BACKGROUND_BLACK     = 0x0000
        BACKGROUND_BLUE      = 0x0010
        BACKGROUND_GREEN     = 0x0020
        BACKGROUND_CYAN      = 0x0030
        BACKGROUND_RED       = 0x0040
        BACKGROUND_MAGENTA   = 0x0050
        BACKGROUND_YELLOW    = 0x0060
        BACKGROUND_GREY      = 0x0070
        BACKGROUND_INTENSITY = 0x0080 # background color is intensified.

        levelno = args[1].levelno
        if(levelno>=50):
            color = BACKGROUND_YELLOW | FOREGROUND_RED | FOREGROUND_INTENSITY | BACKGROUND_INTENSITY
        elif(levelno>=40):
            color = FOREGROUND_RED | FOREGROUND_INTENSITY
        elif(levelno>=30):
            color = FOREGROUND_YELLOW | FOREGROUND_INTENSITY
        elif(levelno>=20):
            color = FOREGROUND_GREEN
        elif(levelno>=10):
            color = FOREGROUND_MAGENTA
        else:
            color =  FOREGROUND_WHITE
        args[0]._set_color(color)

        ret = fn(*args)
        args[0]._set_color( FOREGROUND_WHITE )
        return ret
    return new


def add_coloring_to_emit_ansi(fn):
    # add methods we need to the class
    def new(*args):
        levelno = args[1].levelno
        if levelno >= 50:
            this_color = color.RED
        elif levelno >= 40:
            this_color = color.RED
        elif levelno >= 30:
            this_color = color.YELLOW
        elif levelno >= 20:
            this_color = color.BLUE
        elif levelno >= 10:
            this_color = color.GREY
        else:
            this_color = color.END
        if not isinstance(args[1].msg, basestring):
            args[1].msg = pformat(args[1].msg)
        args[1].msg = this_color + args[1].msg + color.END
        return fn(*args)
    return new


def init_logging(scriptname=os.path.basename(sys.modules[__name__].__file__), outdir='', name='', maxlogs=1 ,level=logging.INFO):

    logger_name = 'log'
    if maxlogs > 0:

        pathfn, outdir, info_msg, warn_msg = get_valid_file(scriptname=scriptname,name=name,outdir=outdir,maxlogs=maxlogs,ext='.log')

        basename = os.path.basename(pathfn).split('.')[0]
        logger_name = 'log_'+basename

        # FIXME: damn, really wish i could get this to print with color encoding to file
        if platform.system() == 'Windows':
            # Windows does not support ANSI escapes and we are using API calls to set the console color
            logging.StreamHandler.emit = add_coloring_to_emit_windows(logging.StreamHandler.emit)
        else:
            # all non-Windows platforms are supporting ANSI escapes so we use them
            logging.StreamHandler.emit = add_coloring_to_emit_ansi(logging.StreamHandler.emit)

        log = logging.getLogger(logger_name)
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')
        file_handler = logging.FileHandler(pathfn, mode='w')
        file_handler.setFormatter(formatter)

        log.setLevel(level)
        log.addHandler(file_handler)

        stream_handler = logging.StreamHandler(stream=sys.stdout)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        stream_handler.setFormatter(formatter)
        log.addHandler(stream_handler)

    else:
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=level, datefmt='%m/%d/%Y %I:%M:%S %p')

    return logger_name, outdir, pathfn


def replace(file_path, pattern, subst):
    # Create temp file
    fh, abs_path = mkstemp()
    with gzip.open(abs_path,'wb') as new_file:
        with myOpen(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    close(fh)
    # Remove original file
    remove(file_path)
    # Move new file
    move(abs_path, file_path)


def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))


class TextException(Exception): pass


def prompt_user(query, errmsg, choices):
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


# optional '-' to support negative numbers
_num_re = re.compile(r'-?\d+')
# number of chars in the largest possible int
_maxint_digits = len(str(maxint))
# format for zero padding positive integers
_zero_pad_int_fmt = '{{0:0{0}d}}'.format(_maxint_digits)
# / is 0 - 1, so that negative numbers will come before positive
_zero_pad_neg_int_fmt = '/{{0:0{0}d}}'.format(_maxint_digits)


def _zero_pad(match):
    n = int(match.group(0))
    # if n is negative, we'll use the negative format and flip the number using
    # maxint so that -2 comes before -1, ...
    return _zero_pad_int_fmt.format(n) \
        if n > -1 else _zero_pad_neg_int_fmt.format(n + maxint)


def zero_pad_numbers(s):
    return _num_re.sub(_zero_pad, s)


def getFiles(directory,*args):
    matches = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith(tuple(args)):
                matches.append(os.path.join(root, filename))
    return matches


def byte2hex(byteStr):
    """
    Convert a byte string to it's hex string representation e.g. for output.
    """

    # Uses list comprehension which is a fractionally faster implementation than
    # the alternative, more readable, implementation below
    #
    #    hex = []
    #    for aChar in byteStr:
    #        hex.append( "%02X " % ord( aChar ) )
    #
    #    return ''.join( hex ).strip()

    return ''.join(["%02X" % ord(x) for x in byteStr]).strip()


# -------------------------------------------------------------------------------

def hex2byte(hexStr):
    """
    Convert a string hex byte values into a byte string. The Hex Byte values may
    or may not be space separated.
    """
    # The list comprehension implementation is fractionally slower in this case
    #
    #    hexStr = ''.join( hexStr.split(" ") )
    #    return ''.join( ["%c" % chr( int ( hexStr[i:i+2],16 ) ) \
    #                                   for i in range(0, len( hexStr ), 2) ] )

    bytes = []

    hexStr = ''.join(hexStr.split(" "))

    for i in range(0, len(hexStr), 2):
        bytes.append(chr(int(hexStr[i:i + 2], 16)))

    return ''.join(bytes)


# A.KA. gcf and hcf
def gcd(a, b):
    """Return greatest common divisor using Euclid's Algorithm."""
    while b:
        a, b = b, a % b
    return a


def lcm(a, b):
    """Return lowest common multiple."""
    return a * b // gcd(a, b)


def lcmm(*args):
    """Return lcm of args."""
    return reduce(lcm, args)


class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)

def restricted_float(x):
    x = float(x)
    if x < 0.0 or x > 1.0:
        raise argparse.ArgumentTypeError("%r not in range [0.0, 1.0]"%(x,))
    return x

def roundup2mod(val, mod):
    """
    Round up to nearest modulus integer
    :param val: int RPTV value
    :param mod: int modulus for that port
    :return: int updated RPTV value
    """
    return int(math.ceil(val / mod) * mod)
