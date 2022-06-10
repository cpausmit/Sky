#!/usr/bin/env python3
import sys,os,glob
from optparse import OptionParser
import pandas as pd
import h5py
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.timeseries import LombScargle

# Remove annoying warning
import warnings
from tables import NaturalNameWarning
warnings.filterwarnings('ignore', category=NaturalNameWarning)

DEBUG = 1

def decode_filename(input_file):
    f = input_file.split("/")
    sector = f[-2]
    file_id = f[-1]
    file_id = file_id.replace('.fits','')
    path = '/'.join(f[:-2])
    if DEBUG>0:
        print(" Processing:  Path:%s  Sector:%s  Id:%s"%(path,sector,file_id))
    return (path, sector, file_id)

def package_data(frequencies,powers):
    # Package the frequency and power data up to be stored in hdf5 format
    index = [ 'frequency', 'power' ]
    data_frame = pd.DataFrame(data=np.vstack((frequencies,powers)),index=index)
    return data_frame

def store_powerspectrum(store,path,sector,file_id,data_frame):
    # Open the hdf5 store and tuck it away
    #store = pd.HDFStore('%s/%s/%s.h5'%(path,sector,file_id))
    store.put('%s'%(file_id),data_frame)
    metadata = {'sector': sector, 'id': file_id}
    store.get_storer('%s'%(file_id)).attrs.metadata = metadata
    #store.close()
    return

def load_powerspectrum(path,sector,file_id):
    # Read it back and see it worked
    with pd.HDFStore('%s/%s/%s.h5'%(path,sector,file_id)) as store:
        data = store['%s'%(file_id)]
        metadata = store.get_storer('%s'%(file_id)).attrs.metadata
    return (metadata,data)

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

def analyze_data(input):

    path,sector,file_id = decode_filename(input)
    t, y, dy, ra, dec = load_lightcurve(input)

    plt.figure('Time Series')
    plt.plot(t,y,marker=".",ls='dashed')
    plt.show()

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

    return (frequencies, powers)

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
elif inputs != 'invalid':
    inputs = options.inputs.split(',')


#store = pd.HDFStore('%s/%s/%s.h5'%(path,sector,file_id))
store = pd.HDFStore('test.h5')

for input in inputs:

    frequencies, powers = analyze_data(input)

    # package the data in Panda frames
    data_frame = package_data(frequencies,powers)

    ## Store it to a file
    #store_powerspectrum(store,path,sector,file_id,data_frame)

    # Read it back and see it worked
    #metadata, data = load_powerspectrum(path,sector,file_id)
    #print(metadata)
    #print(data)
    #
    # Show a plot of the Fourier transform of the light curve
    plt.figure('Light Curve')
    plt.plot(frequencies,powers,marker=".",ls='dashed')
    plt.show()

store.close()
