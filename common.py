import sys
import os

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
    from pprint import *
    f = open(ofile,"wb")
    pprint(ostring,f, indent=4)
    f.close()
