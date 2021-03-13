#!/usr/bin/env python3

import subprocess
import os
import logging
import shlex
from contextlib import contextmanager
from timeit import default_timer
from datetime import timedelta


logger = logging.getLogger()
formatter = logging.Formatter('[%(levelname)8s] - %(asctime)s | %(message)s',
                              datefmt='%d.%m.%Y %H:%M:%S')
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

def setup_file_logging(out_basedir):
    """Setup a logger that prints to file"""
    create_dir(out_basedir)
    file_handler = logging.FileHandler(f'{out_basedir}/run.log')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG) # always verbose for files
    logger.addHandler(file_handler)



THIS_PATH = os.path.dirname(os.path.realpath(__file__))

TASKSET = ''


def store_root_info(out_basedir):
    version = subprocess.check_output('root-config --version', shell=True,
                                          stderr=subprocess.DEVNULL).decode()
    features = subprocess.check_output('root-config --features', shell=True).decode()
    with open(f'{out_basedir}/root_info.txt', 'w') as infof:
        infof.write('\n'.join([version.strip(), features.strip()]))


def set_taskset(arg):
    """Set the taskset global string variable to be used for all invocations of a
    reader or writer command"""
    if arg:
        global TASKSET
        TASKSET = ['taskset', '-c', arg]


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


def run_read_benchmark(input_file, bm_file, wtime_recorder, read_colls):
    """Run the read benchmarks"""
    # Either use a dedicated version from environment or look for one on PATH
    cmd = os.environ.get('PODIO_READBENCHMARK_EXE', None) or 'read_benchmark'
    if input_file.endswith('.slcio'):
        cmd = os.environ.get('LCIO_READBENCHMARK_EXE', None) or 'read_benchmark_lcio'

    cmd_args = [cmd, bm_file, input_file]
    if TASKSET:
        cmd_args = TASKSET + cmd_args

    if read_colls:
        for coll in read_colls.split(','):
            cmd_args.append(coll)

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


def run_k4simdelphes(cmd, args, logfile, wtime_recorder):
    """Run the k4simdelphes reader"""
    # cmd = os.path.expandvars('${K4SIMDELPHES}/bin/') + reader

    cmd_args = [cmd] + args
    if TASKSET:
        cmd_args = TASKSET + cmd_args

    logger.debug('Running: ' + shlex.join(cmd_args))
    with open(logfile, 'w') as logf:
        with elapsed_timer() as timer:
            proc = subprocess.run(cmd_args, stdout=logf, stderr=subprocess.STDOUT, text=True)
        logger.debug(f'Process ran {timer()} s'
                     f' and returned with exit code {proc.returncode}')
        wtime_recorder.add_write(timer().duration())

        if proc.returncode != 0:
            logger.error(f'Got non-zero exit code from running {shlex.join([cmd] + args)}')
            return False

    return True


def get_reader_command(reader, outputfile):
    """Get the correct reader depending on the filename of the output file"""
    if outputfile.endswith('.slcio'):
        # dirty, dirty, dirty here, but works for now
        reader = reader.replace('EDM4HEP', 'LCIO')
        return os.path.expandvars('${LCIO_DIR}/bin/') + reader

    return os.path.expandvars('${K4SIMDELPHES}/bin/') + reader


def run_write_read_benchmark(reader, reader_args, outputfile, label, index, wtime_rec,
                             read_colls=None, keep_output=False):
    """Run k4SimDelphes to produce an outptu file which will then immediately be
    used to run read_benchmark.
    """
    logfile = outputfile.rsplit('.', 1)[0] + '.out'
    logger.info(f'Starting write benchmark run {index} for case {label}')
    reader_cmd = get_reader_command(reader, outputfile)
    # We don't have to go any further if we didn't succeed here
    if not run_k4simdelphes(reader_cmd, reader_args, logfile, wtime_rec):
        return

    read_bm_base = os.path.join(
        os.path.dirname(outputfile),
        os.path.basename(outputfile).split('.')[0]
    )

    read_bm_file = f'{read_bm_base}.{index}.bench.read.root'
    logger.info(f'Starting read benchmark run {index} for case {label}')
    logger.debug(f'Benchmark results for \'{outputfile}\' will be stored in {read_bm_file}')
    if not run_read_benchmark(outputfile, read_bm_file, wtime_rec, read_colls):
        return

    if not keep_output:
        logger.debug(f'Removing outputfile: \'{outputfile}\'')
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

    args_f = lambda o: [args.card, args.output_config, args.pythia_cmd, o]
    run(args, reader, args_f, cases, output_file_base)


def stdhep(args):
    """Run the stdhep reader"""
    logger.debug('Running pythia reader')
    reader = 'DelphesSTDHEP_EDM4HEP'

    cases = ['root', 'sio', 'slcio']
    output_file_base = 'k4simdelphes_stdhep_output'

    args_f = lambda o : [args.card, args.output_config, o, args.inputfile]
    run(args, reader, args_f, cases, output_file_base)


def run(args, reader, reader_arg_f, cases, output_base):
    """Run the given reader using the base_args for all the cases. reader_arg_f is a
    function taking as single argument the output file name and returning the
    arguments to the k4SimDelphes reader as a list of strings.
    """
    create_case_output_dirs(args.outdir, cases)
    wall_time_rec = {case: WallTimeRecorder() for case in cases}

    for i in range(args.nruns):
        for case in cases:
            output_file = f'{args.outdir}/{case}/{output_base}.{i}.{case}'
            converter_args = reader_arg_f(output_file)
            run_write_read_benchmark(reader, converter_args, output_file, case, i,
                                     wall_time_rec[case],
                                     args.collections,
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
    global_parser.add_argument('-c', '--collections', help='Only touch the specified collections '
                               '(comma separated)',
                               default=None)
    global_parser.add_argument('--pin', help='Pin the reading/writing benchmark processes to a '
                               'given cpu or range of cpus with the use of \'taskset -c\'',
                               default=None, type=set_taskset)

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
        stream_handler.setLevel(logging.DEBUG)

    setup_file_logging(clargs.outdir)
    store_root_info(clargs.outdir)

    clargs.func(clargs)
