from pathlib import Path

import matplotlib.pyplot as plt
import mlog_test as mlog

from argparse import ArgumentParser


AGGS = ['mean', 'median']
INTS = ['std', 'max']

REDUCTIONS = ['mean', 'median', 'min', 'max', 'std']


def add(args):
    pass


def sync(args):
    pass


def plot(args):

    df = mlog.get('_run_id', args.x_axis, args.y_axis)

    fig, ax = plt.subplots()

    if args.scatter:
        ax.scatter(df[args.x_axis], df[args.y_axis])

    elif args.ungroup:
        for run_id, run in df.groupby('_run_id'):
            ax.plot(run[args.x_axis], run[args.y_axis])

    else:
        df = df.groupby(args.x_axis).agg(REDUCTIONS)

        if args.intervals == 'max':
            df['_lower'] = df[args.y_axis]['min']
            df['_upper'] = df[args.y_axis]['max']
        elif args.intervals == 'std':
            df['_lower'] = df[args.y_axis]['mean'] - df[args.y_axis]['std']
            df['_upper'] = df[args.y_axis]['mean'] + df[args.y_axis]['std']

        ax.plot(df.index, df[args.y_axis][args.aggregate])
        ax.fill_between(df.index, df['_lower'], df['_upper'], alpha=0.4)

    ax.set_xlabel(args.x_axis)
    ax.set_ylabel(args.y_axis)

    plt.tight_layout()

    if args.output is not None:
        plt.savefig(args.output)

    plt.show()


def main():

    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Add
    parser_add = subparsers.add_parser('add')
    parser_add.set_defaults(func=add)
    parser_add.add_argument('remote', nargs='+')

    # Sync
    parser_sync = subparsers.add_parser('sync')
    parser_sync.set_defaults(func=sync)
    parser_sync.add_argument('remote', nargs='*')

    # Plot
    parser_plot = subparsers.add_parser('plot')
    parser_plot.set_defaults(func=plot)
    parser_plot.add_argument('x_axis')
    parser_plot.add_argument('y_axis')

    parser_plot.add_argument('-s', '--scatter', action='store_true')
    parser_plot.add_argument('-u', '--ungroup', action='store_true')
    parser_plot.add_argument('-a', '--aggregate', choices=AGGS, default='mean')
    parser_plot.add_argument('-i', '--intervals', choices=INTS, default='std')

    parser_plot.add_argument('-o', '--output')

    # Parse arguments and execute command
    args = parser.parse_args()
    args.func(args)
