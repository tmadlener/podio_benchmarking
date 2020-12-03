#!/usr/bin/env python3

import yaml
import platform
import os
import subprocess

from utils import (
    MultiBenchmarkData, make_multi_overview_table, per_event_comparison_plot
)

SETUP_STEPS = {
    'write': (
        ('constructor', 1e6),
        ('finish', 1e6)
    ), 'read': {
        ('constructor', 1e3),
        ('open_file', 1e6),
        ('close_file', 1e3),
        ('read_collection_ids', 1e3)
    }
}

def get_cpu_info():
    """Get CPU info using lscpu"""
    cpu = subprocess.check_output('lscpu | grep "Model name"', shell=True).decode()
    return cpu.split(':')[-1].strip()


def get_mem_info():
    mem = subprocess.check_output('cat /proc/meminfo | grep MemTotal', shell=True).decode()
    return mem.split(':')[-1].strip()


def collect_sys_info(print_f):
    """Collect and write some system information"""
    cpu = platform.processor()
    if cpu == 'x86_64':
        cpu = get_cpu_info()
    print_f(f'- CPU: `{cpu}`')
    print_f(f'- Total available memory: `{get_mem_info()}`')


def collect_benchmarks(bm_dict, data_basedir):
    """Collect all the benchmarks as MultiBenchmarkData"""
    benchmarks = {}
    for case, files in bm_dict.items():
        benchmarks[case] = MultiBenchmarkData(os.path.join(data_basedir, files))
    return benchmarks
    

def main(args):
    """Main"""
    with open(args.report_config, 'r') as conf:
        report_conf = yaml.safe_load(conf)

    with open(os.path.join(args.basedir, 'README.md'), 'w') as report:
        print_rep = lambda s: report.write(s + '\n')
        print_rep('# Benchmark results')
        print_rep('## System info')
        collect_sys_info(print_rep)

        for label, cases in report_conf.items():
            print_rep(f'\n## {label}')
            bm_data = collect_benchmarks(cases, args.basedir)

            for case, data in bm_data.items():
                print_rep(f'\n### {case}')
                print_rep(f'Results from {data.n_runs()} benchmark runs')
                make_multi_overview_table({'dummy': data}, SETUP_STEPS.get(label, ()), print_rep,
                                          no_header=True, no_hlines=True)

            fig = per_event_comparison_plot(bm_data)
            fig.savefig(os.path.join(args.basedir, f'per_event_{label}.png'))
            print_rep('\n### per-event comparison plot')
            print_rep(f'\n![per event distribution for {label}](per_event_{label}.png)')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser('Script to generate a report compiled from several benchmarks')
    parser.add_argument('report_config', help='Report configuration in yaml format')
    parser.add_argument('basedir', help='Benchmark basedir from where the globs in the report '
                        'configuration will be evaluated to get the inputs and into which the '
                        'report file will be stored')


    clargs = parser.parse_args()
    main(clargs)
