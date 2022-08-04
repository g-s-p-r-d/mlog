import mlog
import curses
import argparse
import matplotlib.pyplot as plt

from argparse import ArgumentParser


AGGS = ['mean', 'median']
INTS = ['std', 'max']

REDUCTIONS = ['mean', 'median', 'min', 'max', 'std']


def display(df, index, key):
    run_id = df.index[index]
    run_df = mlog.get(key, _run_id=run_id)

    fig, ax = plt.subplots()
    series = run_df[key].dropna()
    ax.plot(range(len(series)), series)
    ax.set_ylabel(key)
    plt.tight_layout()
    plt.show(block=False)
    plt.pause(0.001)


def get_lines(df):

    # Get number of lines
    num_runs = len(df)

    # Check there are runs
    if num_runs == 0:
        return None, None, 0, 0

    # Extract content and number of columns
    lines = df.to_string().splitlines()
    num_columns = max(map(len, lines)) + 1
    header, lines = lines[0:2], lines[2:]

    return header, lines, num_runs, num_columns


def explore(window, args):

    # TODO: create a class for this display mechanism (num_* are properties)

    # Initialize curse
    screen = curses.initscr()

    # No echo input, no enter for input, hide cursor and use arrow keys
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    screen.keypad(True)

    # Get inputs
    df = mlog.lst()
    header, lines, num_runs, num_columns = get_lines(df)

    if lines is None:
        raise IndexError("No runs")

    # Create pad (TODO: if new lines added, pad should grow)
    pad = curses.newpad(num_runs + 2, num_columns)

    # Write header and lines
    screen.addstr(0, 0, header[0])
    screen.addstr(1, 0, header[1])
    for i, line in enumerate(lines):
        pad.addstr(i, 0, line)

    top, left, index, next_index = 0, 0, 0, 0

    # Open plot if requested
    if args.explore:
        display(df, index, args.explore)

    while True:

        if lines is None:
            raise IndexError("No runs")

        # TODO: min-max check outside of the cases

        # Refresh list and update cursor position
        pad.addstr(index, 0, lines[index])
        index = next_index
        if index - top < 0:
            top = index
        elif index - top > curses.LINES - 1 - 2:
            top = index - curses.LINES + 1 + 2
        screen.move(index - top + 2, 0)
        pad.addstr(index, 0, lines[index], curses.A_REVERSE)
        pad.refresh(top, 0, 2, 0, curses.LINES - 1, curses.COLS - 1)

        # Update plot if necessary
        if args.explore:
            plt.close()
            display(df, index, args.explore)

        # Wait for input
        c = screen.getch()

        # Take action
        if c == ord('q'):
            break

        elif c == ord('j') or c == curses.KEY_DOWN:
            next_index = min(index + 1, num_runs - 1)

        elif c == ord('k') or c == curses.KEY_UP:
            next_index = max(index - 1, 0)

        elif c == ord('h') or c == curses.KEY_LEFT:
            raise NotImplementedError

        elif c == ord('l') or c == curses.KEY_RIGHT:
            raise NotImplementedError

        elif c == 4:  # CTRL-D
            next_index = min(index + int((curses.LINES - 2) / 2), num_runs - 1)

        elif c == 21:  # CTRL-U
            next_index = max(index - int((curses.LINES - 2) / 2), 0)

        elif c == ord('g'):
            next_index = 0

        elif c == ord('G'):
            next_index = num_runs - 1

        elif c == ord(' '):
            raise NotImplementedError

        elif c == ord('r'):
            raise NotImplementedError

        elif c == ord('d'):
            run_id = df.index[index]
            mlog.delete(run_id)

            df = mlog.lst()
            header, lines, num_runs, num_columns = get_lines(df)

            next_index = index = max(0, min(index, num_runs - 1))
            if lines is None:
                raise IndexError("No runs")

            pad.clear()
            for i, line in enumerate(lines):
                pad.addstr(i, 0, line)

    # Reset terminal behavior
    curses.curs_set(1)
    curses.nocbreak()
    curses.echo()


def lst(args):
    try:
        curses.wrapper(explore, args)
    except IndexError:
        print('No runs')


def plot(args):

    df = mlog.get('_run_id', args.x_axis, args.y_axis, **args.filters)

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


class ParseKwargs(argparse.Action):
    """
    https://sumit-ghosh.com
    """
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())
        for value in values:
            key, value = value.split('=')
            getattr(namespace, self.dest)[key] = value


def main():

    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', required=True)

    # List
    parser_list = subparsers.add_parser('list')
    parser_list.set_defaults(func=lst)
    # TODO: no explicit column choice, directly selected from the interface
    parser_list.add_argument('-e', '--explore', help='Column to preview')

    # Plot
    parser_plot = subparsers.add_parser('plot')
    parser_plot.set_defaults(func=plot)
    parser_plot.add_argument('x_axis')
    parser_plot.add_argument('y_axis')

    parser_plot.add_argument('-f', '--filters', nargs='*', action=ParseKwargs,
                             default={})
    parser_plot.add_argument('-s', '--scatter', action='store_true')
    parser_plot.add_argument('-u', '--ungroup', action='store_true')
    parser_plot.add_argument('-a', '--aggregate', choices=AGGS, default='mean')
    parser_plot.add_argument('-i', '--intervals', choices=INTS, default='std')

    parser_plot.add_argument('-o', '--output')

    # Parse arguments and execute command
    args = parser.parse_args()
    args.func(args)
