# -*- coding: utf-8 -*-
"""
Created on Sat Sep 28 19:10:52 2019

@author: disbr007
"""


import argparse
import glob
import logging
import os
import subprocess
from subprocess import PIPE, STDOUT

from lib.utils import constrict_pairs


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_dems(src_dir):
    """
    Iterate over a subdirectory containing pairs.
    Returns two dems in date order.
    src_dir: directoring containing subdirectories
    pair_dir: subdirectory containing pairs
    """
    
    method_dir, pair_dir = os.path.split(src_dir)
    _, method = os.path.split(method_dir)
    
    method_patterns = {'pairs': ('*_dem.tif',),
                       'pc_align_reg': ('*_dem.tif', '*DEM.tif'),
                       'icesat_reg': ('*dem_reg.tif',),
                       'nuth_reg': ('*dem.tif', '*dem_trans.tif')}
    
    # Get all DEMs in srcdir (should be two)
    dems = []
    for pattern in method_patterns[method]:
        dems_pattern = os.path.join(src_dir, pattern)
        dems.extend(glob.glob(dems_pattern))
    
    return dems


def batch_RMSE_sample_pts(src_dir, overwrite, run_pairs_f, dryrun):
    """
    Run point2dem in batch on cluster using qsub
    src_dir: dir holding subdirs of paired 
    dryrun: flag to just print commands with no job submission
    """
    
    def submit_job(src_dir, pair_dir):
        # Get DEMs in date order
        dem_files = get_dems(os.path.join(src_dir, pair_dir))  
        if len(dem_files) == 2:
            dem1, dem2 = dem_files[0], dem_files[1]
        
            # Build cmd
            cmd = 'qsub -v p1="{}",p2="{}",p3="{}" ~/scratch/code/coreg/qsub_RMSE_sample_pts.sh'.format(dem1, dem2, method)
    
            if dryrun:
                print(cmd)
            else:
                p = subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
                output = p.stdout.read()
                print(output)
        else:
            logging.info(pair_dir)
            logging.info('Incorrect number of DEM files found: {}'.format(len(dem_files)))
            pass
        
        
    data_dir, method = os.path.split(src_dir)
    
    # List subdirectory names
    pairs = os.listdir(src_dir)
    pairs = [x for x in pairs if os.path.isdir(os.path.join(src_dir, x))]
    if run_pairs_f:
        pairs = constrict_pairs(run_pairs_f, pairs)

    for pair_dir in pairs:
        print(pair_dir)
        
        files = os.listdir(os.path.join(src_dir, pair_dir))
        rmse_match = [x for x in files if 'rmse.txt' in x]
#        print('RMSE match files found: {}'.format(len(rmse_match)))
        
        if len(rmse_match) == 0:
            submit_job(src_dir, pair_dir)
        elif overwrite:
            submit_job(src_dir, pair_dir)
        else:
            pass
            

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument('src_dir', type=os.path.abspath,
                        help='''Directory holding pair subdirectories
                        with .tifs to calculate RMSE on.''')
    parser.add_argument('--overwrite', action='store_true',
                        help='Recalc and overwrite existing rmse.txt files.')
    parser.add_argument('--run_pairs', type=os.path.abspath,
                        help='Text file with one pair per line to run.')
    parser.add_argument('--dryrun', action='store_true',
                        help='Print qsub commands without submitting them.')
    
    args = parser.parse_args()
    
    batch_RMSE_sample_pts(args.src_dir,
                          overwrite=args.overwrite,
                          run_pairs_f=args.run_pairs,
                          dryrun=args.dryrun)
