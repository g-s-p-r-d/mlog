import matplotlib.pyplot as plt
import mlog_test as mlog

from argparse import ArgumentParser


AGGREGATES = ['mean', 'median', 'min', 'max', 'std']


def pull(args):
    pass


def plot(args):
    project = mlog.connect('project')
    df = project.get('_run_id', args.x_axis, args.y_axis)

    if args.group and args.scatter:
        raise NotImplementedError("Grouping not implemented for scatter plots")

    fig, ax = plt.subplots()

    if not args.group:
        if args.scatter:
            ax.scatter(df[args.x_axis], df[args.y_axis])
        else:
            for run_id, run in df.groupby('_run_id'):
                ax.plot(run[args.x_axis], run[args.y_axis])

    else:
        df = df.groupby(args.x_axis).aggregate(AGGREGATES)

        if args.confidence == 'max':
            df['_lower'] = df[args.y_axis]['min']
            df['_upper'] = df[args.y_axis]['max']
        elif args.confidence == 'std':
            df['_lower'] = df[args.y_axis]['mean'] - df[args.y_axis]['std']
            df['_upper'] = df[args.y_axis]['mean'] + df[args.y_axis]['std']

        ax.plot(df.index, df[args.y_axis][args.aggregate])
        ax.fill_between(df.index, df['_lower'], df['_upper'], alpha=0.4)

    ax.set_xlabel(args.x_axis)
    ax.set_ylabel(args.y_axis)

    if args.output is not None:
        plt.savefig(args.output)

    plt.show()


def main():
    # TODO: improve confidence intervals by defining aggregation functions
    # TODO: implement stderr confidence intervals
    # TODO: implement quantiles confidence intervals

    parser = ArgumentParser()

    subparser = parser.add_subparsers(required=True, dest='command')
    parser_plot = subparser.add_parser('plot')
    parser_pull = subparser.add_parser('pull')

    parser_plot.add_argument('project')
    parser_plot.add_argument('x_axis')
    parser_plot.add_argument('y_axis')

    parser_plot.add_argument('-g', '--group', action='store_true')
    parser_plot.add_argument('-a', '--aggregate', choices=('mean', 'median'),
                             default='mean')
    parser_plot.add_argument('-c', '--confidence', choices=('std', 'max'),
                             default='std')

    parser_plot.add_argument('-s', '--scatter', action='store_true')

    parser_plot.add_argument('-o', '--output')

    args = parser.parse_args()

    if args.command == 'plot':
        plot(args)
    elif args.command == 'pull':
        pull(args)
