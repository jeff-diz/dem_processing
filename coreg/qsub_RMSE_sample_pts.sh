#!/bin/bash

#PBS -l walltime=40:00:00,nodes=1:ppn=2
#PBS -m n
#PBS -k oe
#PBS -j oe


## Expected environment variables (passed with -v argument)

source /mnt/pgc/data/scratch/jeff/build/miniconda3/bin/activate nk
echo `which python`

cd $PBS_O_WORKDIR

echo $PBS_JOBID
echo $PBS_O_HOST
echo $PBS_NODEFILE

echo $p1 $p2 $p3 $p4
python ~/scratch/code/coreg/RMSE_sample_pts.py $p1 $p2 $p3 $p4

echo Done