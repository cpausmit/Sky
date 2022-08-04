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

#import matplotlib.pyplot as plt
#plt.figure('Phase curve')
#plt.plot(phases,y,marker=".",ls='dashed')
#plt.show()

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

def package_data(file_id,frequencies,powers,t,phases):
    # Package the frequency and power data up to be stored in hdf5 format
    index = [ 'frequency', file_id ]
    df_powers = pd.DataFrame(data=np.vstack((frequencies,powers)),index=index)
    index = [ 'times', file_id ]
    df_phases = pd.DataFrame(data=np.vstack((t,phases)),index=index)
    return df_powers,df_phases

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

def fft(t,y,dy):
    if False:
        frequencies, powers = LombScargle(t, y, dy).autopower(maximum_frequency=360)
    else:
        # fixed frequency grid
        baseline = 27.6
        pmin = 20
        freq_oversample_factor = 3

        df = 1.0/(baseline*freq_oversample_factor)
        fmin = 2.0/baseline
        fmax = 1440/pmin

        nf = int(np.ceil((fmax - fmin) / df))
        frequencies = np.linspace(fmin,fmax,nf)

        powers = LombScargle(t, y, dy).power(frequencies)

    return (frequencies, powers)

def phase_fold(t,best_frequency,powers):
    best_period = 1/best_frequency
    phases = (t%best_period)/best_period
    return (phases)

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
parser.add_option("-n", "--n_lcs",dest="n_lcs",default=-1,help="number of light curves to process")
parser.add_option("-s", "--n_skip",dest="n_skip",default=0,help="number of light curves to skip")
(options, args) = parser.parse_args()

# Convert input options
n_skip = int(options.n_skip)
n_lcs = int(options.n_lcs)

# Generate inputs and outputs
inputs = []
if options.input_dir != '/invalid':
    origin = os.getcwd()
    os.chdir(options.input_dir)
    for file in glob.glob("*.fits"):
        inputs.append("%s/%s"%(options.input_dir,file))
    os.chdir(origin)
    if n_lcs > -1:
        output_file_powers = "%s_powers_%06d_%06d.pkl"%(options.input_dir.split('/')[-1],n_skip+1,n_skip+n_lcs)
        output_file_phases = "%s_phases_%06d_%06d.pkl"%(options.input_dir.split('/')[-1],n_skip+1,n_skip+n_lcs)
    else:
        output_file_powers = "%s_powers_%06d_%06d.pkl"%(options.input_dir.split('/')[-1],n_skip+1,len(inputs))
        output_file_phases = "%s_phases_%06d_%06d.pkl"%(options.input_dir.split('/')[-1],n_skip+1,len(inputs))
elif inputs != 'invalid':
    inputs = options.inputs.split(',')
    output_file_powers = "%s_%s_powers_%d.pkl"%(inputs[0].split('/')[-1],inputs[0].split('/')[-1],len(inputs))
    output_file_phases = "%s_%s_phases_%d.pkl"%(inputs[0].split('/')[-1],inputs[0].split('/')[-1],len(inputs))
    # overwrite n_lcs ans n_skip
    print(" WARNING - Options n_cls and n_skip are ignored.")
    n_cls = -1
    n_skip = 0

if DEBUG>0:
    print(" Outputfiles:\n %s\n %s"%(output_file_powers,output_file_phases))
    print(" Inputs")
    print(inputs)

# Protect overwriting existing files
if os.path.exists(output_file_powers):
    print(" Output file for powers - %s - exists already. STOP!"%(output_file_powers))
    sys.exit(0)
if os.path.exists(output_file_phases):
    print(" Output file for phases - %s - exists already. STOP!"%(output_file_phases))
    sys.exit(0)

# Set up relevant counters
n = 0
n_proc = 0

# Now go over our input files
for input in inputs:

    n += 1

    if n<n_skip:
        pass
    elif n_proc>=n_lcs and n_lcs>0:
        print(" EXIT -- Files read:      %d  skipped first  %d"%(n,n_skip))
        print(" EXIT -- Files processed: %d  of  %d"%(n_proc,n_lcs))
        sys.exit(0)
    else:
        # processing this input file
        print("\n Processing file (%d /%d): %s"%(n_proc,n,input))
        n_proc += 1
   
        path,sector,file_id = decode_filename(input,n)
        t, y, dy, ra, dec = load_lightcurve(input)
    
        # power spectrum
        frequencies, powers = fft(t,y,dy)
    
        # phase folding
        phases = phase_fold(t,frequencies[np.argmax(powers)],powers)
        
        # package the data into panda frame
        df_powers, df_phases = package_data(file_id,frequencies,powers,t,phases)
    
        # append it to the pickly file
        add_to_pickle(output_file_powers,df_powers)
        add_to_pickle(output_file_phases,df_phases)
