#!/bin/bash
# --------------------------------------------------------------------------------------------------
# This script will submit the processing of all data using slurm. One job per sector.
#
# --------------------------------------------------------------------------------------------------

# software
export BASE=/home/submit/paus/Tools/Sky

# data
export DATA=/scratch/submit/tess/data
export SECTORS="1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44"

# how many light curve files to process per file
export NFILES=1000

cd $DATA

for s in `echo $SECTORS`
do

  echo "\
  process_directory.py -d tesscurl_sector_${s}_lc"

  echo "\
#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --time=40:00
#SBATCH --mem-per-cpu=1000
#SBATCH --partition=submit,submit-gpu
#SBATCH --job-name=tesscurl_sector_${s}_lc
#SBATCH --error=tesscurl_sector_${s}_lc.err
#SBATCH --output=tesscurl_sector_${s}_lc.out
#pip3 install --user packaging pyqt5 pandas matplotlib astropy h5py tables
source $BASE/setup.sh
process_directory.py -d ./tesscurl_sector_${s}_lc -n $NFILES -x
" > tesscurl_sector_${s}_lc.ssl

  sbatch tesscurl_sector_${s}_lc.ssl

done
