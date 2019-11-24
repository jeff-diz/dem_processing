#!/bin/bash

#PBS -l walltime=40:00:00,nodes=1:ppn=2
#PBS -m n
#PBS -k oe
#PBS -j oe


## Expected environment variables (passed with -v argument)
# p1 :: Reference DEM
# p2 :: Comparison DEM (to be translated)
# p3 :: Output path for diff DEM (dir with be used for other outputs)

cd $PBS_O_WORKDIR

echo $PBS_JOBID
echo $PBS_O_HOST
echo $PBS_NODEFILE

module load gdal/2.1.3

echo $p1 
echo $p2
echo $p3
echo $p4

python ~/scratch/code/coreg/clip2min_bb.py $p1 -o $p2 -s $p3 -c $p4