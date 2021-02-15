#!/usr/bin/env python3

import subprocess
import os
import logging
import shlex
from contextlib import contextmanager
from timeit import default_timer
from datetime import timedelta


logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)8s] - %(asctime)s | %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S'
)

logger = logging.getLogger()

THIS_PATH = os.path.dirname(os.path.realpath(__file__))

class WallTimeRecorder():
    def __init__(self):
        self.write_times = []
        self.read_times = []

    def add_read(self, time):
        self.read_times.append(time)

    def add_write(self, time):
        self.write_times.append(time)

def store_wall_times(wtime_recorder, filename):
    with open(filename, 'w') as logfile:
        logfile.write('write,read\n')
        for twrite, tread in zip(wtime_recorder.write_times, wtime_recorder.read_times):
            logfile.write(f'{twrite}, {tread}\n')


@contextmanager
def elapsed_timer():
    start_time = default_timer()

    class _Timer():
        start = start_time
        end = default_timer()

        def __str__(self):
            duration = timedelta(seconds=self.duration())
            return f'{duration.seconds}.{duration.microseconds}'

        def duration(self):
            return self.end - self.start

    yield _Timer

    _Timer.end = default_timer()


def run_read_benchmark(input_file, bm_file, wtime_recorder):
    """Run the read benchmarks"""
    # TODO: install the read_benchmark and use install dir
    cmd = os.path.realpath(os.path.join(THIS_PATH, '../../build/reading_benchmark/read_benchmark', ))
    cmd_args = [cmd, bm_file, input_file]

    logger.debug('Running: ' + shlex.join(cmd_args))
    with elapsed_timer() as timer:
        proc = subprocess.run(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    logger.debug(f'Process ran {timer()} s'
                 f' and returned with exit code {proc.returncode}')
    wtime_recorder.add_read(timer().duration())

    if proc.returncode != 0:
        logger.error(f'Got non-zero exit code from running {shlex.join(cmd_args)}')
        return False

    return True


def run_k4simdelphes(reader, args, logfile, wtime_recorder):
    """Run the k4simdelphes reader"""
    cmd = os.path.expandvars('${K4SIMDELPHES}/bin/') + reader

    logger.debug('Running: ' + shlex.join([cmd] + args))
    with open(logfile, 'w') as logf:
        with elapsed_timer() as timer:
            proc = subprocess.run([cmd] + args, stdout=logf, stderr=subprocess.STDOUT, text=True)
        logger.debug(f'Process ran {timer()} s'
                     f' and returned with exit code {proc.returncode}')
        wtime_recorder.add_write(timer().duration())

        if proc.returncode != 0:
            logger.error(f'Got non-zero exit code from running {shlex.join([cmd] + args)}')
            return False

    return True


def run_write_read_benchmark(reader, reader_args, outputfile, label, index, wtime_rec,
                             keep_output=False):
    """Run k4SimDelphes to produce an outptu file which will then immediately be
    used to run read_benchmark.
    """
    logfile = outputfile.rsplit('.', 1)[0] + '.out'
    logger.info(f'Starting write benchmark run {index} for case {label}')
    # We don't have to go any further if we didn't succeed here
    if not run_k4simdelphes(reader, reader_args, logfile, wtime_rec):
        return

    read_bm_base = outputfile.rsplit('.', 3)[0] # split of index and file-ending
    read_bm_file = f'{read_bm_base}.{index}.bench.read.root'
    logging.info(f'Starting read benchmark run {index} for case {label}')
    logging.debug(f'Benchmark results for \'{outputfile}\' will be stored in {read_bm_file}')
    run_read_benchmark(outputfile, read_bm_file, wtime_rec)

    if not keep_output:
        logging.debug(f'Removing outputfile: \'{outputfile}\'')
        os.remove(outputfile)


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

    cases = ['root', 'sio']
    output_file_base = 'k4simdelphes_pythia_output'
    # prepare output directories for both cases
    create_case_output_dirs(args.outdir, cases)

    base_args = [args.card, args.output_config, args.pythia_cmd]

    wall_time_rec = {case: WallTimeRecorder() for case in cases}

    for i in range(args.nruns):
        for case in cases:
            output_file = f'{args.outdir}/{case}/{output_file_base}.{i}.{case}'
            converter_args = base_args + [output_file]
            run_write_read_benchmark(reader, converter_args, output_file, case, i,
                                     wall_time_rec[case],
                                     args.keep_outputs)


def stdhep(args):
    """Run the stdhep reader"""
    logger.debug('Running pythia reader')
    reader = 'DelphesSTDHEP_EDM4HEP'

    cases = ['root', 'sio']
    output_file_base = 'k4simdelphes_stdhep_output'
    create_case_output_dirs(args.outdir, cases)


    base_args = [args.card, args.output_config]

    wall_time_rec = {case: WallTimeRecorder() for case in cases}

    for i in range(args.nruns):
        for case in cases:
            output_file = f'{args.outdir}/{case}/{output_file_base}.{i}.{case}'
            converter_args = base_args + [output_file, args.inputfile]
            run_write_read_benchmark(reader, converter_args, output_file, case, i,
                                     wall_time_rec[case],
                                     args.keep_outputs)

    for case in cases:
        store_wall_times(wall_time_rec[case], f'{args.outdir}/wall_times_{case}.csv')


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
    global_parser.add_argument('-o', '--outdir', help='The directory into which the outputs are stored',
                               default='.')
    global_parser.add_argument('--keep-outputs', help='Keep the output files of the benchmark runs. '
                               'Default behaviour is to only keep the benchmark results.'
                               , default=False, action='store_true')
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
