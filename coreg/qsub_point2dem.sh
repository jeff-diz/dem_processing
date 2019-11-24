#!/bin/bash

#PBS -l walltime=40:00:00,nodes=1:ppn=2
#PBS -m n
#PBS -k oe
#PBS -j oe


## Does this change working dir?
cd $PBS_O_WORKDIR

echo $PBS_JOBID
echo $PBS_O_HOST
echo $PBS_NODEFILE

module load gdal/2.1.3
module load asp

echo $p1
echo $p2
point2dem $p1 -o $p2