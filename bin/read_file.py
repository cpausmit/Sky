#!/usr/bin/env python3
import glob,os,pickle,sys
from optparse import OptionParser

DEBUG = 1

def read_from_pickle(path):
    # sequentially ready pickly objects that were stored

    with open(path,'rb') as file:
        try:
            while True:
                yield pickle.load(file)
        except EOFError:
            pass

#---------------------------------------------------------------------------------------------------
#                                             M A I N
#---------------------------------------------------------------------------------------------------
parser = OptionParser()
parser.add_option("-i", "--inputs",dest="inputs",default='invalid',help="input file names (comma separated)")
parser.add_option("-d", "--input_dir",dest="input_dir",default='/invalid',help="input dir name")
parser.add_option("-n", "--n_lcs",dest="n_lcs",default=1,help="number of light curves to process")
parser.add_option("-s", "--n_skip",dest="n_skip",default=0,help="number of light curves to skip")
(options, args) = parser.parse_args()

inputs = []
if options.input_dir != '/invalid':
    origin = os.getcwd()
    os.chdir(options.input_dir)
    for file in glob.glob("*.pkl"):
        inputs.append("%s/%s"%(options.input_dir,file))
    os.chdir(origin)
elif inputs != 'invalid':
    inputs = options.inputs.split(',')

n = 0
n_proc = 0
n_skip = int(options.n_skip)
n_lcs = int(options.n_lcs)

for input in inputs:

    # Show what was packed up
    for item in read_from_pickle(input):

        if n<n_skip:
            pass
        elif n_proc>=int(options.n_lcs):
            print(" EXIT -- Events read:      %d  skipped first  %d"%(n,n_skip))
            print(" EXIT -- Events processed: %d  of  %d"%(n_proc,n_lcs))
            sys.exit(0)
        else:
            # processing this event
            print("\n Processing event: %d (total read: %d)"%(n_proc,n))
            n_proc += 1
            print(repr(item))

        n += 1

print(" EXIT -- Events read:      %d  skipped first  %d"%(n,n_skip))
print(" EXIT -- Events processed: %d  of  %d requested"%(n_proc,n_lcs))
if n_lcs>n_proc:
    print(" WARNING -- less events processed than requested.")
print(" EXIT -- REACHED END OF DATA")
sys.exit(0)
