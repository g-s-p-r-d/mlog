import random
import mlog_test as mlog
import matplotlib.pyplot as plt

from argparse import ArgumentParser


# Run connection setup
PROJECT = 'project'     # None: default database
RUN = 'run'             # None: id as name


# Configuration
CONFIG = {'epochs': 100, 'lr': 1e-3, 'batch_size': 24}


def main(args):

    # Connection
    project = mlog.connect(project=PROJECT)
    run = project.start(run=RUN, config=CONFIG)


    # Training
    for epoch in range(CONFIG['epochs']):
        loss = random.random() * (1.05 ** (- epoch))
        run.log(epoch=epoch, loss=loss)


    # Plot run
    if args.plot:
        df = run.get('epoch', 'loss')

        df.plot('epoch', 'loss')
        plt.show()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--plot', action='store_true')

    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--learning_rate', type=float, default=1e-3)
    parser.add_argument('--batch_size', type=int, default=32)

    args = parser.parse_args()
    main(args)
