#!/usr/bin/env python3

import subprocess
import logging
import shlex
import glob
import os

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)8s] - %(asctime)s | %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S'
)

logger = logging.getLogger()

THIS_PATH = os.path.dirname(os.path.realpath(__file__))


def run_read_benchmark(input_file, bm_file):
    """Run the read benchmarks"""
    # TODO: install the read_benchmark and use install dir
    cmd = os.path.realpath(os.path.join(THIS_PATH, '../../build/reading_benchmark/read_benchmark', ))
    cmd_args = [cmd, bm_file, input_file]

    logger.debug('Running: ' + shlex.join(cmd_args))
    proc = subprocess.run(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    logger.debug(f'Process returned with exit code {proc.returncode}')
    if proc.returncode != 0:
        logger.error(f'Got non-zero exit code from running {shlex.join(cmd_args)}')


def run_on_all_outputs(directory, glob_pattern):
    """Run on all output files matching the glob_pattern"""
    output_files = glob.glob(os.path.join(directory, glob_pattern))
    # filter out the write benchmark files that might slip through the globbing
    output_files = [f for f in output_files if not f.endswith('.bench.root')]

    logger.info(f'Found {len(output_files)} files to run the read benchmarks on in {directory}')
    for infile in output_files:
        logging.info(f'Running read benchmark on {infile}')
        file_base, index = os.path.basename(infile).split('.')[:2]
        bm_file = f'{directory}/{file_base}.{index}.bench.read.root'
        logging.debug(f'Benchmark results for \'{infile}\' will be stored in \'{bm_file}\'')
        run_read_benchmark(infile, bm_file)


def main(args):
    """Main"""
    run_on_all_outputs(os.path.join(args.inputbase, 'root'), 'k4simdelphes_*_output.*.root')
    run_on_all_outputs(os.path.join(args.inputbase, 'sio'), 'k4simdelphes_*_output.*.sio')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run the read benchmarks on output files produced '
                                     'by k4SimDelphes using run_write_benchmark.py')
    parser.add_argument('inputbase', help='The base directory where the output directories for the '
                        'different cases are located')
    parser.add_argument('--verbose', help='Enable verbose logger', action='store_true', default=False)

    clargs = parser.parse_args()
    if clargs.verbose:
        logger.setLevel(logging.DEBUG)

    main(clargs)
