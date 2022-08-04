import mlog
import random
import matplotlib.pyplot as plt

from argparse import ArgumentParser


CONFIG = {'num_epochs': 100, 'learning_rate': 1e-3, 'batch_size': 32}


def main(args):
    run = mlog.start(run='run', config=CONFIG, save='*.py')

    for epoch in range(CONFIG['num_epochs']):
        loss = random.random() * (1.05 ** (- epoch))
        metric = random.random()
        run.log(epoch=epoch, loss=loss, metric=metric)

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
