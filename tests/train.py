import random
import mlog
import matplotlib.pyplot as plt

from argparse import ArgumentParser


CONFIG = {'epochs': 100, 'lr': 1e-3, 'batch_size': 32}


def main(args):
    run = mlog.start(run='run', config=CONFIG, save='*.py')

    for epoch in range(CONFIG['epochs']):
        loss = random.random() * (1.05 ** (- epoch))
        run.log(epoch=epoch, loss=loss)

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
