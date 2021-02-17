#!/usr/bin/env python3

import sys
import os
import glob

import matplotlib.pyplot as plt
# Adapt defaults a bit for better readable plots
plt.rcParams.update({
    'font.size': 15.0,
    'savefig.bbox': 'tight'
})

import pandas as pd
import numpy as np

# make utils available
THIS_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.realpath(THIS_PATH + '/../../../python'))

from utils import (
    MultiBenchmarkData, BenchmarkData
)


def collect_total_times(base_path):
    """Collect summary data for one physics case given a base path"""
    times = {'read': {}, 'write': {}}
    pattern = {
        'read': 'k4simdelphes_*_output.*.bench.read.root',
        'write': 'k4simdelphes_*_output.*.*.bench.root'
    }

    for io_sys in ['sio', 'root']:
        for case in times.keys():
            bmdata = MultiBenchmarkData(f'{base_path}/{io_sys}/{pattern[case]}')
            times[case][io_sys] = bmdata.total_time(['setup_times', 'event_times'], ['mean'])[0] / 1e9

    return times


def collect_file_sizes(base_path):
    """Collect the output file sizes of the write operation"""
    sizes = {'sio': 1, 'root': -1}
    for io_sys in sizes.keys():
        datafile = glob.glob(f'{base_path}/{io_sys}/k4simdelphes_*_output.0.{io_sys}')[0]
        sizes[io_sys] = os.stat(datafile).st_size / 1024**2

    return sizes


def collect_overview_data(physics_cases):
    """Collect all the data into a DataFrame"""
    data = {}
    for label, base_path in physics_cases.items():
        data[label] = {}
        data[label].update(collect_total_times(base_path))
        data[label]['file size'] = collect_file_sizes(base_path)

    return pd.concat({
        k: pd.DataFrame.from_dict(v, 'index') for k, v in data.items()
    }).transpose(copy=True)

def event_contents_plots(physics_cases):
    """Print an overview plot over the event contents for the different physics
    cases"""
    histo_f = lambda v: np.histogram(v, bins=100, range=(0, 400))
    fig = plt.figure()

    colors = ['tab:blue', 'tab:orange', 'tab:red', 'tab:green']
    # lstyles = [(0, (1, 1)), (0, (2, 2)), (0, (2, 3, 1, 3))]

    def _plot_hist(data, **kwargs):
        n_ev, binning = histo_f(data)
        bin_centers = 0.5 * (binning[:-1] + binning[1:])
        n_ev = n_ev / data.shape[0]
        plt.step(bin_centers, n_ev, where='mid', **kwargs)
       

    for icol, (label, base_path) in enumerate(physics_cases.items()):
        bmfile = glob.glob(f'{base_path}/root/k4simdelphes_*_output.0.bench.read.root')[0]
        data = BenchmarkData(bmfile).collection_sizes.arrays(library='pd')

        # _plot_hist(data.loc[:, 'Particle_size'], label='MC', linestyle='dotted', color=colors[icol])
        # _plot_hist(data.loc[:, 'ReconstructedParticles_size'], label='Reco', linestyle='dashed', color=colors[icol])
        _plot_hist(np.sum(data.loc[:, ['Particle_size', 'ReconstructedParticles_size', 'MCRecoAssociations_size']], axis=1),
                   label=label, color=colors[icol])

        plt.xlabel(r'number of total objects per event')
        plt.ylabel('fraction of events')
        plt.yscale('log')
        plt.legend()
        plt.xlim(0, 400)

    return fig


def per_event_io_times(physics_cases):
    """Make plots for per event i/o times for the different physics cases. each
    time comparing root and sio"""
    # start with write
    histo_f = lambda v: np.histogram(v / 1e3, bins=100, range=(0, 2000))
    colors = ['tab:blue', 'tab:orange', 'tab:red', 'tab:green']
    # lstyles = [(0, (1, 1)), (0, (2, 2)), (0, (2, 3, 1, 3))]

    write_fig = plt.figure()

    def _plot_hist(bmdata, **kwargs):
        n_ev, binning = bmdata.per_event_dist(hist_f=histo_f)
        bin_centers = 0.5 * (binning[:-1] + binning[1:])
        n_ev = n_ev / bmdata.num_entries()
        return plt.step(bin_centers, n_ev, where='mid', **kwargs)

    io_lines = [0, 0]

    for icol, (label, base_path) in enumerate(physics_cases.items()):
        sio_data = MultiBenchmarkData(f'{base_path}/sio/k4simdelphes_*_output.*.sio.bench.root')
        root_data = MultiBenchmarkData(f'{base_path}/root/k4simdelphes_*_output.*.root.bench.root')

        io_lines[0], = _plot_hist(sio_data, linestyle=(0, (2, 1)), color=colors[icol])
        io_lines[1], = _plot_hist(root_data, label=label, linestyle='solid', color=colors[icol])

    io_leg = plt.legend(io_lines, ['sio', 'root'], loc=7)
    plt.gca().add_artist(io_leg)


    plt.yscale('log')
    plt.xlabel(r'per event write times / $\mu$s')
    plt.ylabel('fraction of events')
    plt.legend()
    plt.xlim(0, 2000)


    read_fig = plt.figure()
    for icol, (label, base_path) in enumerate(physics_cases.items()):
        sio_data = MultiBenchmarkData(f'{base_path}/sio/k4simdelphes_*_output.*.bench.read.root')
        root_data = MultiBenchmarkData(f'{base_path}/root/k4simdelphes_*_output.*.bench.read.root')

        io_lines[0], = _plot_hist(sio_data, linestyle=(0, (2, 1)), color=colors[icol])
        io_lines[1], = _plot_hist(root_data, label=label, linestyle='solid', color=colors[icol])

    io_leg = plt.legend(io_lines, ['sio', 'root'], loc=7)
    plt.gca().add_artist(io_leg)

    plt.yscale('log')
    plt.xlabel(r'per event read times / $\mu$s')
    plt.ylabel('fraction of events')
    plt.legend()
    plt.xlim(0, 2000)

    return write_fig, read_fig


def main():
    """Main"""
    # Using the 6.20/04 versions for now, until we find out what is wrong with
    # the 6.22/06
    physics_cases = {
        r'$ee\to Z\to b\bar{b}$': 'ee_Z_bbbar_root-6.20.04/',
        # r'$ee\to Z\to \tau\tau$': 'ee_Z_tautau_root-6.20.04/',
        r'$ee\to ZH\to \mu\mu X$': 'Higgs_recoil_at_ILD_root-6.20.04/'
    }

    fig = event_contents_plots(physics_cases)
    fig.savefig('vchep_2021/event_contents_overview.pdf')

    write_fig, read_fig = per_event_io_times(physics_cases)
    write_fig.savefig('vchep_2021/per_event_write_times.pdf')
    read_fig.savefig('vchep_2021/per_event_read_times.pdf')

    # print overview data frame
    dfr = collect_overview_data(physics_cases)
    # normalize to root and print
    print(dfr.loc[:, :] / dfr.loc['root', :])


if __name__ == '__main__':
    main()
