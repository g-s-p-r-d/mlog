# MLog

A minimal logging utility for machine learning experiments.

## Installation

```
pip install -i https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ -U mlog-test
```

## Logging

```python3
import mlog_test as mlog
import random

CONFIG = {'num_epochs': 100}

# Connect to project database
project = mlog.connect(project='project')

# Create a new run with an associated configuration
run = project.start(run='run', config=CONFIG)

# Log seamlessly
for epoch in range(CONFIG['num_epochs']):
    loss = random.random() * (1.05 ** (- epoch))
    run.log(epoch=epoch, loss=loss)
    metric = random.random()
    run.log(epoch=epoch, metric=metric)
```

## Consulting

```sh
mlog project epoch loss --group
mlog project epoch loss --group --aggregate median
mlog project epoch loss --group --aggregate median --confidence max
```

## Plotting

```python3
import matplotlib.pyplot as plt
import pandas as pd

# Connect to project database
project = mlog.connect(project='project')

# Retrieve data
df = project.get('epoch', 'loss')
df = df.groupby('epoch').aggregate(['mean', 'min', 'max'])

# Plot data
fig, ax = plt.subplots()
ax.plot(df.index, df.loss['mean'])
ax.fill_between(df.index, df.loss['min'], df.loss['max'], alpha=0.4)
plt.show()
```
