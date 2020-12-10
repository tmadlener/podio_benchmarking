#!/usr/bin/env python3

import os
import glob
import re

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


class MultiBenchmarkData:
    """Helper class for holding multiple benchmark results, e.g. from running the
    same benchmark multiple times. Allows to obtain summary statistics using all
    runs
    """
    def __init__(self, bmfiles):
        """
        Args:
            bmfile (list or str): List of filepaths or str representing a
                wildcard pattern that will be used in glob.glob to get a list of
                files
        """
        if not isinstance(bmfiles, (list, tuple)):
            bmfiles = glob.glob(bmfiles)

        self.bm_data = [BenchmarkData(f) for f in bmfiles]

    def total_time(self, trees_steps=None, summary_funcs=('min', 'mean', 'max')):
        """Get the total time spent in different trees and possibly sub steps per tree.
        All stored benchmarks are considered and summarized according to the
        summary statistics that are passed.

        Args:
            trees_steps (list or dict, optional): If a list all the steps in
                each tree are summed up. If dict, the tree names are the keys
                and only the steps passed as values are summed up. Use None for
                all steps of a given tree. If None, sum up all the trees and
                steps therein
            summary_funcs (list of functions): Functions calculating the desired
                summary statistics from all stored benchmarks. Default, min,
                mean, max

        Returns:
            summary_stats (tuple of float or float): The results of the
                summary_funcs

        See also:
            BenchmarkData.total_time

        """
        times = np.array([b.total_time(trees_steps) for b in self.bm_data])
        # Call the numpy version of the function on the times
        return tuple(getattr(np, f)(times) for f in summary_funcs)

    def per_event_time(self, steps=None, stat_f=np.median, summary_funcs=('min', 'mean', 'max')):
        """Get a summary statistic for the per event times, possibly limited to only a
        subset of all available steps. Additionally, run another summary
        statistic over the per event summary statistics of all stored benchmarks.

        Args:
            steps (list, optional): List of step names that should be
                considered. If None, all steps will be considered (default)
            stat_f (function, optional): Function taking a numpy.array as single
                argument and returning one float value. Default is np.median
            summary_funcs (list of functions): Functions calculating the desired
                summary statistics from all stored benchmarks. Default, min, mean, max

        Returns:
            summary_stats (tuple of float or float): The results of the
                summary_funcs

        See also:
            BenchmarkData.per_event_time
        """
        times = np.array([b.per_event_time(steps, stat_f) for b in self.bm_data])
        # Call the numpy version of the function on the times
        return tuple(getattr(np, f)(times) for f in summary_funcs)

    def per_event_dist(self, steps=None, hist_f=np.histogram):
        """Get a histogram of the distribution of the per event times, possibly limited
        to only a subset of all available steps, the final distribution will be
        the averaged distribution of all stored benchmarks.

        Args:
            steps (list, optional): List of step names that should be
                considered. If None, all steps will be considered (default)
            hist_f (function, optional): Function taking a numpy.array as single
                argument and returning arrays of bin contents and bin-edges

        Returns:
            hist (np.array): Values of the histogram (i.e. bin contents)
            bin_edges (np.array): Bin edges of the histogram

        See also:
            BenchmarkData.per_event_dist
        """
        hist0, bin_edges = self.bm_data[0].per_event_dist(steps, hist_f)
        all_dists = [b.per_event_dist(steps, hist_f)[0] for b in self.bm_data[1:]]

        all_dists = np.array([hist0] + all_dists)

        return np.mean(all_dists, axis=0), bin_edges

    def num_entries(self, irun=None):
        """Get the number of all entries that were used int he benchmarking. NOTE:
        simply assuming here that all stored benchmarks have the same number of
        events. If a dedicated run is passed, get the number of entries for that
        run.
        """
        if irun is not None:
            return self.bm_data[irun].num_entries()
        return self.bm_data[0].num_entries() * len(self.bm_data)

    def n_runs(self):
        """Number of runs that are stored in the MultiBenchmark"""
        return len(self.bm_data)

    def __repr__(self):
        return f'MultiBenchmarkData [{len(self.bm_data)} benchmarks]'

    def __str__(self):
        return self.__repr__()


def open_bmfile(input_bmfile):
    """Open a benchmark file and return the data therein as well as the label for
    associated to the file"""
    label_filename = input_bmfile.split(':')
    if len(label_filename) == 2:
        label, bmfile = label_filename
    else:
        label = ''
        bmfile = label_filename[0]
    return label, BenchmarkData(bmfile)


def open_all_bmfiles(labelled_files):
    """Open all bmfiles passed as arguments and return a dict using the lables as
    keys and the file data as values"""
    bmfiles = {}
    for icase, label_file in enumerate(labelled_files):
        label, bmfile = open_bmfile(label_file)
        # Give it a generic label if none is named in the input
        if not label:
            label = f'case {icase}'
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


def flatten(iterable):
    """
    Flatten any list or iterable into a 1D-list. Keep dictionaries and strings
    intact.
    Taken from here: http://stackoverflow.com/a/2158532/3604607
    Args:
        iterable (iterable): Possibly nested list or iterable that should be
            converted into a flat (1D) list
    Returns:
        generator: The generator that yields all the elements of the passed in
            list as a flat iterable
    """
    for elem in iterable:
        # only checking for the __iter__ attribute here should allow to enter
        # sub lists but not tear apart strings since they don't have it
        if hasattr(elem, "__iter__") and not isinstance(elem, dict):
            for sub in flatten(elem):
                yield sub
        else:
            yield elem

# Conversion factors and corresponding units
UNIT = {1: ' [ns]', 1e3: ' [us]', 1e6: ' [ms]', 1e9: ' [s]'}

def _make_overview_table(bmdata, setup_steps, print_f,
                         fmt_strings, total_time_f, setup_t_f, per_event_t_f,
                         sub_header=None, no_header=False, no_hlines=False):
    """Internal helper function gluing together the different functions and
    formatting options
    """
    header = fmt_strings['header'].format(*bmdata.keys())
    def hline():
        if no_hlines:
            return
        print_f('-' * len(header))
    vline = fmt_strings['value_line']


    if not no_header:
        print_f(fmt_strings['header'].format(*bmdata.keys()))
        hline()

    if sub_header:
        print_f(sub_header)
        print_f(re.sub(r'[^|]', '-', sub_header))

    print_f(vline.format('total [s]', *[fmt_time(t, 1e9) for t in total_time_f(bmdata)]))
    hline

    def setup_line(label, steps=None, scale=1e3):
        print_f(vline.format(
            label + UNIT[scale], *[fmt_time(t, scale) for t in setup_t_f(bmdata, steps)]
        ))

    def per_event_line(label, stat_f, scale=1e3):
        print_f(vline.format(
            label + UNIT[scale], *[fmt_time(t, scale) for t in per_event_t_f(bmdata, stat_f)]
        ))

    # setup times
    setup_line('total setup', scale=1e6)
    for step, fact in setup_steps:
        setup_line(step.replace('_', ' '), step, fact)

    # per event overview
    hline()
    per_event_line('median', np.median)
    per_event_line('min', np.min)
    per_event_line('max', np.max)
    per_event_line('90 percentile', lambda v: np.quantile(v, 0.9))
    per_event_line('99 percentile', lambda v: np.quantile(v, 0.99))


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

    See also:
        _make_overview_table
    """
    # Define some format strings for easier line formatting
    fmt_strings = {
        'header': ' ' * 25 + '| {:^8.8} ' * len(bmfiles),
        'value_line': '{:<24.24} ' + '| {:>8.8} ' * len(bmfiles)
    }

    def setup_times(data, steps=None):
        """Helper function for printing a setup step line"""
        if steps:
            if not isinstance(steps, (list, tuple)):
                steps = [steps]

        return [b.total_time({'setup_times': steps}) for b in data.values()]

    def per_event_times(data, stat_f):
        """Helper function to print a per event summary statistic line"""
        return [b.per_event_time(stat_f=stat_f) for b in data.values()]

    total_times = lambda d: [b.total_time() for b in d.values()]

    _make_overview_table(bmfiles, setup_steps, print_f, fmt_strings,
                         total_times, setup_times, per_event_times)


def make_multi_overview_table(bmdata, setup_steps, print_f=print, summary_funcs=('min', 'mean', 'max'), no_header=False, no_hlines=False):
    """Print an overview table summarizing multiple benchmarks per column, detailing
    some of the setup steps and also giving an overview over the per-event times.

    Args:

        bmdata (dict): Labelled MultiBenchmarkData. The labels are used as
            column headers, each column gets sub-columns according to the used
            summary_funcs
        setup_steps (list): List of pairs of (str, float), where the str is the
            name of a step occuring during setup and the float is the
            (multiplicative) conversion factor to convert the raw nanosecond
            times into a more digestible unit. 
        print_f (function, optional): Function applied to all the formated lines
            of the table that can be used to divert the output from the default
            stdout to a e.g. a file
        summary_funcs (list of functions): Functions calculating the desired
            summary statistics from all stored benchmarks. Default, min, mean,
            max

    See also:
        _make_overview_table
    """
    # Define some format strings for easier line formatting
    column_width = 10 * len(summary_funcs)
    column_header = '| {:^' + '.'.join([str(column_width)] * 2)  + '} '
    sub_header = '| ' + ' ' * 25 + ('| {:^8.8} ' * len(summary_funcs)).format(*summary_funcs) * len(bmdata) + '|'

    fmt_strings  = {
        'header': '| ' + ' ' * 25 + column_header * len(bmdata) + '|',
        'value_line': '| {:<24.24} ' + '| {:>8.8} ' * len(summary_funcs) * len(bmdata) + '|'
    }

    def setup_times(data, steps=None):
        """Helper function for formatting a setup line"""
        if steps:
            if not isinstance(steps, (list, tuple)):
                steps = [steps]

        times = [b.total_time({'setup_times': steps}) for b in data.values()]
        return [t for t in flatten(times)]

    def per_event_times(data, stat_f):
        """Helper function for formatting per event times"""
        times = [b.per_event_time(stat_f=stat_f) for b in data.values()]
        return [t for t in flatten(times)]

    total_line = lambda d: [t for t in flatten([b.total_time() for b in d.values()])]

    _make_overview_table(bmdata, setup_steps, print_f,
                         fmt_strings, total_line, setup_times, per_event_times,
                         sub_header, no_header, no_hlines)


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
