import matplotlib.pyplot as plt
import mlog_test as mlog

from argparse import ArgumentParser


AGGREGATES = ['mean', 'median', 'min', 'max', 'std']


def plot(args):
    project = mlog.connect('project')
    df = project.get('_run_id', args.x_axis, args.y_axis)

    fig, ax = plt.subplots()

    if not args.group:
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

    plt.show()


def main():
    # TODO: implement scatter plot
    # TODO: improve confidence intervals by defining aggregation functions
    # TODO: implement stderr confidence intervals
    # TODO: implement quantiles confidence intervals

    parser = ArgumentParser()

    parser.add_argument('project')
    parser.add_argument('x_axis')
    parser.add_argument('y_axis')

    parser.add_argument('-g', '--group', action='store_true')
    parser.add_argument('-a', '--aggregate', choices=('mean', 'median'),
                        default='mean')
    parser.add_argument('-c', '--confidence', choices=('std', 'max'),
                        default='std')

    args = parser.parse_args()

    plot(args)
