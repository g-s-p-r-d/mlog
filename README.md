# MLog

A minimal logging utility for machine learning experiments.

## Installation

```sh
> pip install pymlog
```

## Logging

```python3
import mlog
import random

CONFIG = {'num_epochs': 100}

# Create a new run with an associated configuration
run = mlog.start(run='run_name', config=CONFIG, save='*.py')

# Log seamlessly
for epoch in range(CONFIG['num_epochs']):
    loss = random.random() * (1.05 ** (- epoch))
    run.log(epoch=epoch, loss=loss)
    metric = random.random()
    run.log(epoch=epoch, metric=metric)
```

## Quick preview

```sh
> mlog plot epoch loss
> mlog plot epoch loss --aggregate median
> mlog plot epoch loss --aggregate median --intervals max
> mlog plot loss metric --scatter
```

## Manage runs

```sh
> mlog list
        _name  num_epochs  learning_rate  batch_size
_run_id
1         run         100          0.001          32
2         run         100          0.001          32
3         run         100          0.001          32
4         run         100          0.001          32
5         run         100          0.001          32
6         run         100          0.001          32
7         run         100          0.001          32
8         run         100          0.001          32
9         run         100          0.001          32
10        run         100          0.001          32
```

This command starts an interactive interface where you can use commands like:

 - `hjkl` to navigate left, down, up and right,
 - `gG` to go up and down,
 - `d` to delete run,
 - `space` to preview plot,
 - `q` to exit.

## Plotting

```python3
import mlog
import pandas as pd
import matplotlib.pyplot as plt

# Retrieve data
df = mlog.get('epoch', 'loss')
df = df.groupby('epoch').aggregate(['mean', 'min', 'max'])

# Plot data
fig, ax = plt.subplots()
ax.plot(df.index, df.loss['mean'])
ax.fill_between(df.index, df.loss['min'], df.loss['max'], alpha=0.4)
plt.show()
```
