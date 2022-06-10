#!/usr/bin/env python3
import sys,os,glob
from optparse import OptionParser
import pandas as pd

import pickle
import numpy as np
from astropy.io import fits
from astropy.timeseries import LombScargle

# Remove annoying warning
import warnings
from tables import NaturalNameWarning
warnings.filterwarnings('ignore', category=NaturalNameWarning)

DEBUG = 1

def decode_filename(input_file,i):
    f = input_file.split("/")
    sector = f[-2]
    file_id = f[-1]
    file_id = file_id.replace('-s_lc.fits','')
    path = '/'.join(f[:-2])
    if DEBUG>0:
        print(" Processing:  Path:%s  Sector:%s  Id:%s [%d]"%(path,sector,file_id,i))
    return (path, sector, file_id)

def package_data(file_id,frequencies,powers):
    # Package the frequency and power data up to be stored in hdf5 format
    index = [ 'frequency', file_id ]
    data_frame = pd.DataFrame(data=np.vstack((frequencies,powers)),index=index)
    return data_frame

def load_lightcurve(f):
    # Load a standard light curve

    hdul = fits.open(f)
    ra = hdul[0].header['RA_OBJ']
    dec = hdul[0].header['DEC_OBJ']
    all_time = hdul[1].data['TIME']
    all_mag = hdul[1].data['PDCSAP_FLUX']
    all_err = hdul[1].data['PDCSAP_FLUX_ERR']
    
    # Only keep good data (filter))
    idx = (~np.isnan(all_time)) & (~np.isnan(all_mag)) & (~np.isnan(all_err))
    t = all_time[idx]
    y = all_mag[idx]
    dy = all_err[idx]

    return t, y, dy, ra, dec

def add_to_pickle(path,item):
    with open(path,'ab') as file:
        pickle.dump(item,file, pickle.HIGHEST_PROTOCOL)

#---------------------------------------------------------------------------------------------------
#                                             M A I N
#---------------------------------------------------------------------------------------------------
#input = "/scratch/submit/tess/data/tesscurl_sector_1_lc/tess2018206045859-s0001-0000000471016524-0120-s_lc.fits"

parser = OptionParser()
parser.add_option("-i", "--inputs",dest="inputs",default='invalid',help="input file name")
parser.add_option("-d", "--input_dir",dest="input_dir",default='/invalid',help="input dir name")
(options, args) = parser.parse_args()

inputs = []
if options.input_dir != '/invalid':
    origin = os.getcwd()
    os.chdir(options.input_dir)
    for file in glob.glob("*.fits"):
        inputs.append("%s/%s"%(options.input_dir,file))
    os.chdir(origin)
    output_file = "%s_%d.pkl"%(options.input_dir.split('/')[-1],len(inputs))
elif inputs != 'invalid':
    inputs = options.inputs.split(',')
    output_file = "%s_%s_%d.pkl"%(inputs[0].split('/')[-1],inputs[0].split('/')[-1],len(inputs))

if DEBUG>0:
    output_file = output_file.replace("-s_lc.fits","")
    print(" Outputfile: %s"%(output_file))

if os.path.exists(output_file):
    print(" Output file exists already. STOP!")
    sys.exit(0)

# Now go over our input files
i=0
for input in inputs:
    
    i += 1
    path,sector,file_id = decode_filename(input,i)
    t, y, dy, ra, dec = load_lightcurve(input)

    if False:
        frequencies, powers = LombScargle(t, y, dy).autopower(maximum_frequency=360)
    else:
        # fixed frequency grid
        baseline = 27.6
        pmin = 20
        freq_oversample_factor = 3

        df = 1.0 / (baseline*freq_oversample_factor)
        fmin = 2.0/baseline
        fmax = 1440/pmin

        nf = int(np.ceil((fmax - fmin) / df))
        frequencies = np.linspace(fmin,fmax,nf)

        powers = LombScargle(t, y, dy).power(frequencies)
    
    # package the data into panda frame
    data_frame = package_data(file_id,frequencies,powers)

    # append it to the pickly file
    add_to_pickle(output_file,data_frame)    
