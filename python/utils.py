#!/usr/bin/env python3

import os

import uproot4 as uproot
import matplotlib.pyplot as plt
import numpy as np

class BenchmarkData:
    """Small helper class to hold the benchmark data"""
    def __init__(self, bmfile):
        """Read benchmark data from a file

        Args:
            bmfile (path): Path to the .root file containing the benchmark data
        """
        data = uproot.open(bmfile)
        self.bmfile = os.path.realpath(bmfile)
        self.trees = [b.split(';')[0] for b in data]
        for tree in self.trees:
            self.__dict__[tree] = data[tree]

    def total_time(self, trees_steps=None):
        """Get the total time spent in different trees and possibly sub steps per
        tree.

        Args:
            trees_steps (list or dict, optional): If a list all the steps in
                each tree are summed up. If dict, the tree names are the keys
                and only the steps passed as values are summed up. Use None for
                all steps of a given tree. If None, sum up all the trees and
                steps therein

        Returns:
            total_time (float): The sum of all the desired times

        """
        # If no trees passed, simply use all available ones
        trees_steps = trees_steps or self.trees
       
        if isinstance(trees_steps, (list, tuple)):
            return np.sum(self._total_time(t) for t in trees_steps)

        if isinstance(trees_steps, dict):
            return np.sum(self._total_time(t, s) for t, s in trees_steps.items())

        raise ValueError('trees_steps needs to be a list or a dictionary')

    def per_event_time(self, steps=None, stat_f=np.median):
        """Get a summary statistic for the per event times, possibly limited to only a
        subset of all available steps.

        Args:
            steps (list, optional): List of step names that should be
                considered. If None, all steps will be considered (default)
            stat_f (function, optional): Function taking a numpy.array as single
                argument and returning one float value. Default is np.median

        Returns:
            per_event_time (float): Result of evaluating stat_f on the per-event
                sums of all considered steps
        """
        return stat_f(self._per_event_time(steps))

    def per_event_dist(self, steps=None, hist_f=np.histogram):
        """Get a histogram of the distribution of the per event times, possibly limited
        to only a subset of all available steps

        Args:
            steps (list, optional): List of step names that should be
                considered. If None, all steps will be considered (default)
            hist_f (function, optional): Function taking a numpy.array as single
                argument and returning arrays of bin contents and bin-edges

        Returns:
            hist (np.array): Values of the histogram (i.e. bin contents)
            bin_edges (np.array): Bin edges of the histogram
        """
        return hist_f(self._per_event_time(steps))

    def num_entries(self):
        """Get the number of events that were used in the benchmarking"""
        return self.event_times.num_entries

    def _total_time(self, tree, steps=None):
        """Get the total time (summing all events) of a tree, possibly limited to
        selected steps in that tree"""
        return np.sum(self.__dict__[tree].arrays(steps))

    def _per_event_time(self, steps=None):
        """Get the per event time, possibly limited to only a subset of all available
        steps"""
        # Convert this into a pandas.DataFrame first, because then we can sum
        # the entries along the rows before computing the summary statistic on
        # this sum
        return np.sum(self.event_times.arrays(steps, library='pd'), axis=1)

    def __repr__(self):
        if 'event_times' in self.__dict__ and 'setup_times' in self.__dict__:
            return (
                f'BenchmarkData : {self.event_times.num_entries} events, '
                f'trees: {self.trees}, file: \'{self.bmfile}\''
            )

        return f'BenchmarkData, file: \'{self.bmfile}\' (not produced by TimedReader or TimedWriter)'

    def __str__(self):
        return self.__repr__()


def open_bmfile(input_bmfile):
    """Open a benchmark file and return the data therein as well as the label for
    associated to the file"""
    label, bmfile = input_bmfile.split(':')
    return label, BenchmarkData(bmfile)


def open_all_bmfiles(labelled_files):
    """Open all bmfiles passed as arguments and return a dict using the lables as
    keys and the file data as values"""
    bmfiles = {}
    for label_file in labelled_files:
        label, bmfile = open_bmfile(label_file)
        bmfiles[label] = bmfile

    return bmfiles


def fmt_time(time, scale_factor=None):
    """Format the time into easily readable values when possible and scientific
    notation with fixed width otherwise"""
    basic_fmt = '{:>6.2e}' # the fall-back format that always works
    if scale_factor:
        time = time / scale_factor

    fmt_brackets = {
        (1e-1, 1e0): '{:>.3f}',
        (1e0, 1e1): '{:>.3f}',
        (1e1, 1e2): '{:>.2f}',
        (1e2, 1e3): '{:>.1f}',
        (1e3, 1e4): '{:>.0f}',
    }

    for (low, high), fmt in fmt_brackets.items():
        if time > low and time < high:
            return fmt.format(time)

    return basic_fmt.format(time)


def make_overview_table(bmfiles, setup_steps, print_f=print):
    """Print an overview table with a column for each benchmark file detailing some
    of the setup steps and also giving an overview over the per-event times.

    Args:
        bmfiles (dict): Labelled BenchmarkData. The labels are used as column
            headers, the values are computed from the BenchmarkData
        setup_steps (list): List of pairs of (str, float), where the str is the
            name of a step occuring during setup and the float is the
            (multiplicative) conversion factor to convert the raw nanosecond
            times into a more digestible unit.
        print_f (function, optional): Function applied to all the formated lines
            of the table that can be used to divert the output from the default
            stdout to a e.g. a file
    """
    # Define some format strings for easier line formatting
    header = ' ' * 25 + '| {:^8.8} ' * len(bmfiles)
    hline = '-' * (25 + 11 * len(bmfiles))
    vline = '{:<24.24} ' + '| {:>8.8} ' * len(bmfiles)
    unit = {1: ' [ns]', 1e3: ' [us]', 1e6: ' [ms]', 1e9: ' [s]'}

    def setup_line(label, steps=None, scale=1e3):
        """Helper function for printing a setup step line"""
        if steps:
            if not isinstance(steps, (list, tuple)):
                steps = [steps]

        times = [b.total_time({'setup_times': steps}) for b in bmfiles.values()]

        print_f(vline.format(label + unit[scale], *[fmt_time(t, scale) for t in times]))

    def per_event_line(label, stat_f, scale=1e3):
        """Helper function to print a per event summary statistic line"""
        times = [b.per_event_time(stat_f=stat_f) for b in bmfiles.values()]
        print_f(vline.format(label + unit[scale], *[fmt_time(t, scale) for t in times]))


    # Now print the table
    print_f(header.format(*bmfiles.keys()))
    print_f(hline)
    print_f(vline.format('total [s]', *[fmt_time(b.total_time(), 1e9) for b in bmfiles.values()]))

    # Setup times
    print_f(hline)
    setup_line('total setup', scale=1e6)
    for step, fact in setup_steps:
        setup_line(step.replace('_', ' '), step, fact)

    # per event overview
    print_f(hline)
    per_event_line('median', np.median)
    per_event_line('min', np.min)
    per_event_line('max', np.max)
    per_event_line('90 percentile', lambda v: np.quantile(v, 0.9))
    per_event_line('99 percentile', lambda v: np.quantile(v, 0.99))


def per_event_comparison_plot(bmfiles, steps=None, bins=100, x_range=(0, 2000)):
    """Make a comparison plot of the per event times distributions for all passed
    benchmark files"""
    # Plot results in us
    histo_f = lambda v: np.histogram(v / 1e3, bins=bins, range=x_range)

    fig = plt.figure()
    for label, bmfile in bmfiles.items():
        n_events, binning = bmfile.per_event_dist(hist_f=histo_f)
        bin_centers = 0.5 * (binning[:-1] + binning[1:])
        # normalize to the total number of events (including under-/overflow)
        n_events = n_events / bmfile.num_entries()
        plt.step(bin_centers, n_events, label=label, where='mid')

    plt.yscale('log')
    plt.xlabel(r'per event times / $\mu$s')
    plt.ylabel('fraction of events')
    plt.legend()
    plt.xlim(*x_range)

    return fig
