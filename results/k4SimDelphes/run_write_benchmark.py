#!/usr/bin/env python3

import subprocess
import os
import logging
import shlex

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)8s] - %(asctime)s | %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S'
)

logger = logging.getLogger()

def run_k4simdelphes(reader, args, logfile):
    """Run the k4simdelphes reader"""
    cmd = os.path.expandvars('${K4SIMDELPHES}/bin/') + reader

    logger.debug('Running: ' + shlex.join([cmd] + args))
    with open(logfile, 'w') as logf:
        proc = subprocess.run([cmd] + args, stdout=logf, stderr=subprocess.STDOUT, text=True)
        logger.debug(f'Process returned with exit code {proc.returncode}')
        if proc.returncode != 0:
            logger.error(f'Got non-zero exit code from running {shlex.join([cmd] + args)}')


def create_dir(path):
    """Create the directory if it does not already exist"""
    try:
        if path:
            logger.debug(f'Creating directory: \'{path}\'')
            os.makedirs(path)
    except FileExistsError:
        if not os.path.isdir(path):
            logger.error(f'Cannot create output directory \'{path}\' because a file already exists')
            raise


def create_case_output_dirs(base_outdir, cases):
    """Create a separate output directory for each case"""
    for case in cases:
        create_dir(os.path.join(base_outdir, case))


def pythia(args):
    """Run the pythia reader"""
    logger.debug('Running pythia reader')
    reader = 'DelphesPythia8_EDM4HEP'

    output_file_base = 'k4simdelphes_pythia_output'
    # prepare output directories for both cases
    create_case_output_dirs(args.outdir, ['root', 'sio'])

    base_args = [args.card, args.output_config, args.pythia_cmd]

    for i in range(args.nruns):
        # root
        converter_args = base_args + [f'{args.outdir}/root/{output_file_base}.{i}.root']
        logfile = f'{args.outdir}/root/{output_file_base}.{i}.out'
        logger.info(f'Starting run {i} for root I/O')
        run_k4simdelphes(reader, converter_args, logfile)

        # sio
        converter_args = base_args + [f'{args.outdir}/sio/{output_file_base}.{i}.sio']
        logfile = f'{args.outdir}/sio/{output_file_base}.{i}.out'
        logger.info(f'Starting run {i} for sio I/O')
        run_k4simdelphes(reader, converter_args, logfile)


def stdhep(args):
    """Run the stdhep reader"""
    logger.debug('Running pythia reader')
    reader = 'DelphesSTDHEP_EDM4HEP'

    output_file_base = 'k4simdelphes_stdhep_output'
    create_case_output_dirs(args.outdir, ['root', 'sio'])


    base_args = [args.card, args.output_config]

    for i in range(args.nruns):
        # root
        converter_args = base_args + [f'{args.outdir}/root/{output_file_base}.{i}.root', args.input]
        logfile = f'{args.outdir}/root/{output_file_base}.{i}.out'
        logger.info(f'Starting run {i} for root I/O')
        run_k4simdelphes(reader, converter_args, logfile)

        # sio
        converter_args = base_args + [f'{args.outdir}/sio/{output_file_base}.{i}.sio', args.input]
        logfile = f'{args.outdir}/sio/{output_file_base}.{i}.out'
        logger.info(f'Starting run {i} for sio I/O')
        run_k4simdelphes(reader, converter_args, logfile)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run the benchmarks using k4SimDelphes '
                                     'and different I/O backends for podio')

    readers = parser.add_subparsers(title='readers', help='The reader to use for k4SimDelphes',
                                    dest='readers')
    readers.required = True # fail if no subcommand is given

    global_parser = argparse.ArgumentParser(add_help=False)

    global_parser.add_argument('card', help='The delphes card to use')
    global_parser.add_argument('output_config', help='The output configuration for the converter')
    global_parser.add_argument('-o', '--outdir', help='The directory into which the outputs a',
                               default='.')
    global_parser.add_argument('--no-outputs', help='Discard the outputs of the benchmark runs and only '
                               'keep the benchmark outputs', default=False, action='store_true')
    global_parser.add_argument('-n', '--nruns', help='Number of runs per benchmark case',
                        type=int, default=10)
    global_parser.add_argument('--verbose', help='Enable verbose logger', action='store_true',
                               default=False)


    pythia_parser = readers.add_parser('pythia', description='Use the Pythia8 reader',
                                       parents=[global_parser])
    pythia_parser.add_argument('pythia_cmd', help='The pythia cmd to use')
    pythia_parser.set_defaults(func=pythia)


    stdhep_parser = readers.add_parser('stdhep', description='Use the STDHEP reader',
                                       parents=[global_parser])
    stdhep_parser.add_argument('inputfile', help='The STDHEP input file to use')
    stdhep_parser.set_defaults(func=stdhep)


    clargs = parser.parse_args()
    if 'verbose' in clargs and clargs.verbose:
        logger.setLevel(logging.DEBUG)

    clargs.func(clargs)
