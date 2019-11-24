"""
Wrapper for clip2min_bb.py to submit jobs to PBS.

bash: qsub_clip2minbb.sh
"""
import argparse
import os
import subprocess
from subprocess import PIPE, STDOUT


def batch_clip2min_bb(src_dir, dst_dir, suffix, compress, dryrun):
    """
    batch/qsub function for submitting clip2min_bb.py to PBS.

    src
    """
    # Paths
    if not os.path.exists(dst_dir):
        os.mkdir(dst_dir)

    pairs = os.listdir(src_dir)

    for pair in pairs:
        src_path = os.path.join(src_dir, pair)
        dst_path = os.path.join(dst_dir, pair)
        if not os.path.exists(dst_path):
            os.mkdir(dst_path)

        cmd = 'qsub -v p1="{}",p2="{}",p3="{}",p4="{}" ~/scratch/code/coreg/qsub_clip2min_bb.sh'.format(src_path,
                                                                                                        dst_path,
                                                                                                        suffix,
                                                                                                        compress)
        if dryrun:
            print(cmd)
        else:
            p = subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
            output = p.stdout.read()
            print(output)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('src_dir', type=os.path.abspath,
                        help='Path to directory holding pair directories.')
    parser.add_argument('dst_dir', type=os.path.abspath,
                        help='Path to directory to write new clipped directories.')
    parser.add_argument('--out_suffix', type=str, default='',
                        help='Suffix to add to output rasters.')
    parser.add_argument('-s', '--suffix', nargs='?', default='.tif', type=str,
                        help="Suffix that all rasters share.")
    parser.add_argument('-c', '--compress', type=str, default='LZW',
                        help='''Compress to apply. Default is LZW. Options:
                        JPEG/LZW/PACKBITS/DEFLATE/CCITTRLE/CCITTFAX3/CCITTFAX4
                        /LZMA/ZSTD/LERC/LERC_DEFLATE/LERC_ZSTD/WEBP/NONE''')
    parser.add_argument('--dryrun', action='store_true',
                        help='Print qsub commands without submitting.')
    args = parser.parse_args()

    src_dir = args.src_dir
    dst_dir = args.dst_dir
    out_suffix = args.out_suffix
    suffix = args.suffix
    compress = args.compress
    dryrun = args.dryrun

    batch_clip2min_bb(src_dir,
                      dst_dir,
                      # out_suffix=out_suffix,
                      suffix=suffix,
                      compress=compress,
                      dryrun=dryrun)
