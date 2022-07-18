import mlog_test as mlog

import random
import matplotlib.pyplot as plt


# Run connection setup

PROJECT = 'project'     # None: default database
RUN = 'run'             # None: id as name


# Configuration

CONFIG = {'epochs': 100, 'lr': 1e-3, 'batch_size': 24}


# Connection

project = mlog.connect(project=PROJECT)
run = project.start(run=RUN, config=CONFIG)


# Training

for epoch in range(CONFIG['epochs']):
    loss = random.random() * (1.05 ** (- epoch))
    run.log(epoch=epoch, loss=loss)


# Plot run

df = run.get('epoch', 'loss')
print(df)

df.plot('epoch', 'loss')
plt.show()


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
