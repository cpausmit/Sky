#!/bin/bash
#SBATCH --job-name=test
#SBATCH --ntasks=1
#SBATCH --mail-type=begin
#SBATCH --mail-type=end
#SBATCH --mail-user=roche@mit.edu
#SBATCH --array=0,1
#SBATCH --output=res_%j_%a.txt
#SBATCH --error=err_%j_%a.txt
#SBATCH --time=30:00
#SBATCH --mem-per-cpu=2GB

SLURM_ARRAY_TASK_ID=1

# -------- Load Environment --------
cd /home/submit/roche/miniconda3/envs/py3/bin
source activate py3


# -------- Go to directory with scripts --------
cd /work/submit/paus/DR3_hackathon


# -------- run download --------
srun python3 /work/submit/paus/DR3_hackathon/download_patch.py $SLURM_ARRAY_TASK_ID
