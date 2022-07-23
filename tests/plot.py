import random
import mlog_test as mlog
import matplotlib.pyplot as plt

from argparse import ArgumentParser
from train import PROJECT


def main(args):

    # Connection
    project = mlog.connect(project=PROJECT)

    # Retrieve data
    df = project.get('epoch', 'loss')
    mean = df.groupby('epoch').mean().reset_index()
    std = df.groupby('epoch').std().reset_index()
    minimum = df.groupby('epoch').min().reset_index()
    maximum = df.groupby('epoch').max().reset_index()

    # Plot
    fig, ax = plt.subplots()
    ax.plot(mean['epoch'], mean['loss'])
    ax.fill_between(mean['epoch'], mean['loss'] - std['loss'],
                    mean['loss'] + std['loss'], alpha=0.3)
    plt.show()


if __name__ == '__main__':
    parser = ArgumentParser()
    agrs = parser.parse_args()
    main(args)
