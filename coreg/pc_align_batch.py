#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 22 13:36:22 2019

@author: disbr007
"""

import argparse
import glob
import os
import subprocess
from subprocess import PIPE, STDOUT

from lib.utils import constrict_pairs


def get_dems(src_dir, pair_dir):
    """
    Iterate over a subdirectory containing pairs.
    Returns two dems in date order.
    src_dir: directoring containing subdirectories
    pair_dir: subdirectory containing pairs
    """
    # Abs path to subdirectory
    dems_dir = os.path.join(src_dir, pair_dir)
    # Get all DEMs in subdir (should be two)
    dems = glob.glob(dems_dir, '*_dem.tif')

    # Identify old and new dems
    # Included index (i) in date to account for the same date  to
    # prevent overwriting the key
    # {date_[i]: dem_path}
    dems_dict = {'{}_{}'.format(os.path.split(x)[1].split('_')[1], i): x for i, x in enumerate(dems)}
    dem1, dem2 = dems_dict[sorted(dems_dict)[0]], dems_dict[sorted(dems_dict)[1]]

    return dem1, dem2


def batch_pc_align(src_dir, dryrun, run_pairs):
    """
    Run ASP pc_align on cluster using qsub.
    src_dir: directory containing subdirectories of paired DEMs to align.
    dryrun:  flag to specify only printing commands, no job submission
    """
    # List subdirectory names
    pairs = os.listdir(src_dir)
    # If a restricted list is supplied, reduce pairs to that list
    if run_pairs:
        pairs = constrict_pairs(run_pairs, pairs)

    for pair_dir in pairs:
        # Abs path to subdirectory
        dems_dir = os.path.join(src_dir, pair_dir)
        # Get all DEMs in subdir (should be two)
        dem_pattern = os.path.join(dems_dir, '*_dem.tif')
        dems = glob.glob(dem_pattern)

        # Identify old and new dems
        # Included index (i) in date to account for the same date to
        # prevent overwriting the key
        # {date_[i]: dem_path}
        dems_dict = {'{}_{}'.format(os.path.split(x)[1].split('_')[1], i):x for i, x in enumerate(dems)}
        dem1, dem2 = dems_dict[sorted(dems_dict)[0]], dems_dict[sorted(dems_dict)[1]]
        # Use this for the prefix as the transformation is being applied to it
        dem1_name = os.path.basename(dem1).split('.')[0][:13]
        prefix = os.path.join(dems_dir, dem1_name)
        # Build command
        cmd = 'qsub -v p1="{}",p2="{}",p3="{}" ~/scratch/code/coreg/qsub_pc_align.sh'.format(dem2, dem1, prefix)

        if dryrun:
            print(cmd)
        else:
            p = subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
            output = p.stdout.read()
            print(output)

        # break


def batch_point2dem(src_dir, dryrun):
    """
    Run point2dem in batch on cluster using qsub
    src_dir: dir holding subdirs of paired
    dryrun: flag to just print commands with no job submission
    """
    # List subdirectory names
    pairs = os.listdir(src_dir)

    for pair_dir in pairs:
        # Get DEMs in date order
        # dem1, dem2 = get_dems(src_dir, pair_dir)

        dems_dir = os.path.join(src_dir, pair_dir)
        trans_pattern = os.path.join(dems_dir, '*trans_source.tif')
        trans_source_files = glob.glob(trans_pattern)
        # Ensure trans_source file found
        if len(trans_source_files) > 0:

            # Should be the only trans_source
            # Can add checking the basename for matching a dem name
            trans_source = trans_source_files[0]
            trans_source_name = os.path.basename(trans_source).split('.')[0].split('-trans')[0]
            prefix = os.path.join(dems_dir, trans_source_name)
            # Build cmd
            cmd = 'qsub -v p1="{}",p2="{}" ~/scratch/code/coreg/qsub_point2dem.sh'.format(trans_source, prefix)

            if dryrun:
                print(cmd)
            else:
                p = subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
                output = p.stdout.read()
                print(output)
        else:
            print('No trans_source file found. Skipping: {}'.format(pair_dir))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('src_dir', type=os.path.abspath,
                        help='Path to directory holding pair directories')
    parser.add_argument('tool', type=str,
                        help='ASP tool to run, either "pc_align" or "point2dem"')
    parser.add_argument('--dryrun', action='store_true',
                        help='Print qsub commands without submitting')
    
    args = parser.parse_args()

    src_dir = args.src_dir
    tool = args.tool
    dryrun = args.dryrun

    if tool == 'pc_align':
        batch_pc_align(src_dir, dryrun)
    elif tool == 'point2dem':
        batch_point2dem(src_dir, dryrun)
    else:
        print('Unknown tool argument. Must be either: "pc_align" or "point2dem"')
