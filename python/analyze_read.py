#!/usr/bin/env python3

from functools import partial

from utils import (
    open_all_bmfiles, make_overview_table, per_event_comparison_plot
)

SETUP_STEPS = (
    ('constructor', 1e3),
    ('open_file', 1e6),
    ('close_file', 1e3),
    ('read_collection_ids', 1e3)
)

overview_table = partial(make_overview_table, setup_steps=SETUP_STEPS)

def main(args):
    """Main"""
    bmfiles = open_all_bmfiles(args.bmfiles)
    overview_table(bmfiles)

    if args.tablefile:
        with open(args.tablefile, 'w') as tablefile:
            overview_table(bmfiles, print_f=lambda l: tablefile.write(l + '\n'))

    if args.per_event_dist:
        fig = per_event_comparison_plot(bmfiles)
        fig.savefig(args.per_event_dist, bbox_inches='tight')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Analyze the benchmark output of podio::TimedReader')
    parser.add_argument('-t', '--tablefile', help='Save the overview table into a file in addition '
                        'to printing it to stdout', default=None, type=str)
    parser.add_argument('-f', '--per-event-dist', help='Make per event distribution plot and save it'
                        ' into the filename passed here', default=None, type=str)
    parser.add_argument('bmfiles', help='Labelled input files that should be analyzed. Format: '
                        '"label:benchmark_file.root"',
                        nargs='+', type=str)

    clargs = parser.parse_args()
    main(clargs)
