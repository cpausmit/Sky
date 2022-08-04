#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------------------
# process files in one sector
#
# - n_files - number of light curve files processed per sector
# - 
#---------------------------------------------------------------------------------------------------------------
import sys,os,glob
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-n", "--n_files",dest="n_files",default=1000,help="number of files per processing")
parser.add_option("-d", "--input_dir",dest="input_dir",default='/invalid',help="input directory name")
parser.add_option("-x", "--execute",action="store_true",dest="execute",default=False,help="execute this?")
(options, args) = parser.parse_args()

# go to the input directory and find the files
origin = os.getcwd()
os.chdir(options.input_dir)

inputs = []
for file in glob.glob("*.fits"):
    inputs.append("%s/%s"%(options.input_dir,file))

# back to where we started
os.chdir(origin)

n_files_dir = len(inputs)
print("Number of files in directory: %d"%(len(inputs)))


n_files = int(options.n_files)
first = 1
last = int(options.n_files)
while last <= n_files_dir:
    cmd = " write_file.py -d %s -s %6d -n %6d >& %s_%06d_%06d.log"%(options.input_dir,first-1,n_files,options.input_dir,first,last)
    #cmd = " write_file.py -d %s -s %6d -n %6d"%(options.input_dir,first-1,n_files)
    print(cmd)
    if options.execute:
        os.system(cmd)
    first += n_files
    last += n_files

if last > n_files_dir:
    cmd = " write_file.py -d %s -s %6d -n %6d >& %s_%06d_%06d.log"%(options.input_dir,first-1,n_files,options.input_dir,first,n_files_dir)
    #cmd = " write_file.py -d %s -s %6d -n %6d"%(options.input_dir,first-1,n_files)
    print(cmd)
    if options.execute:
        os.system(cmd)
