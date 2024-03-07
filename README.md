# FinTime
FinTime is a financial time series plotting library built on Matplotlib. 

**Features include:** 
- Visual elements as standalone objects (Artists).
- Composite structures (Grid, Subplots, Panels) organise multiple plots within a figure.
- Branched propagation of data and configurations to sub-components, enabling overrides at any level.
- Dynamic sizing and spacing of components.

## Table of Contents

- [Installation](#installation)
- [Usage](#examples)
  - [Data](#data)
  - [Panels Plot](#panels-plot)
  - [Subplots Plot](#subplots-plot)
  - [Standalone Use of Artists](#standalone-use-of-artists)
- [Configuration](#configuration)
- [Upcoming Features](#upcoming-features)


<a id="installation"></a>
## Installation
```python
pip install fintime
```

<a id="examples"></a>
## Examples

<a id="data"></a>
### Data
FinTime expects data to be structured as a flat mapping, such as a dictionary, containing NumPy arrays. The example below demonstrates the generation of mock OHLCV data with intervals of 1, 10, 30, and 300 seconds. This data will be used in the following examples.

```python
from fintime.mock.data import generate_random_trade_ticks
from fintime.mock.data import to_timebar

ticks = generate_random_trade_ticks(seed=1)
datas = {f"{span}s": to_timebar(ticks, span=span) for span in [1, 10, 30, 300]}

# inspect the data
for feat, array in datas["10s"].items():
    print(feat.ljust(6), repr(array[:2]))

# Expected output:
# --> dt     array(['2024-03-03T21:00:00.000'], dtype='datetime64[ms]')
# --> open   array([101.62])
# --> high   array([101.92])
# --> low    array([101.59])
# --> close  array([101.6])
# --> vol    array([2941])
```

<a id="panels-plot"></a>
### Panels Plot
Let's proceed and plot candlesticks and volume bars with a 10-second span.
```python
from matplotlib.pylab import plt
from fintime.plot import plot, Panel
from fintime.artists import CandleStick, Volume

fig = plot(
    specs=[Panel(artists=[CandleStick()]), Panel(artists=[Volume()])],
    data=datas["10s"],
    title="Panels Plot",
)
plt.show()
```
![panels plot](https://raw.githubusercontent.com/marcel-dehaan/fintime/main/images/panels_plot.png)

> **Note**: Panels act as the canvas for either one Axes or two twinx Axes. Visually stacked vertically, a list of panels shares the x-axis. An artist is an element that can be drawn within a panel.

<a id="subplots-plot"></a>
### Subplots Plot
Displaying multiple groups of panels within a single figure is achieved by passing a list of Subplots (rather than Panels) to the plot function. In the following example, we will draw candlestick and volume bars with spans of 1, 30 and 300 seconds while overriding some configurations.  

```python
from fieldconfig import Config
from fintime.plot import Subplot

cfg_dark = Config(create_intermediate_attributes=True)
cfg_dark.panel.facecolor = "#36454F"
cfg_dark.candlestick.body.relwidth = 0.9
cfg_dark.candlestick.wick.color = "lightgray"
cfg_dark.candlestick.wick.linewidth = 2.0

subplots = [
    Subplot(
        [
            Panel(artists=[CandleStick(data=datas["1s"])]),
            Panel(artists=[Volume(data=datas["1s"])]),
        ]
    ),
    Subplot(
        [
            Panel(artists=[CandleStick(config={"candlestick.body.up_color": "black"})]),
            Panel(artists=[Volume()]),
        ],
        data=datas["30s"],
    ),
    Subplot(
        [
            Panel(artists=[CandleStick()]),
            Panel(artists=[Volume()]),
        ],
        data=datas["300s"],
        config=cfg_dark,
    ),
]

fig = plot(subplots, title="Subplots Plot")
plt.show()
```

![subplots plot](https://raw.githubusercontent.com/marcel-dehaan/fintime/main/images/subplots_plot.png)

<a id="standalone-use-of-artists"></a>
### Standalone Use of Artists

You also have the option to have Artists draw on your own Axes.
```python
import matplotlib.pyplot as plt
from fintime.artists import CandleStick
from fintime.config import get_config

data = datas["30s"]
fig = plt.Figure(figsize=(10, 5))
axes = fig.subplots()
axes.set_xlim(min(data["dt"]), max(data["dt"]))
axes.set_ylim(min(data["low"]), max(data["high"]))

cs_artist = CandleStick(data=data, config=get_config())
cs_artist.draw(axes)
plt.show()
```
![standalone plot](https://raw.githubusercontent.com/marcel-dehaan/fintime/main/images/standalone_plot.png)

<a id="configuration"></a>
## Configuration
FinTime provides granular control over configurations through its `config` argument, available in the plot function, subplot, panel, and artists classes. These configurations are propagated downward to sub-components, including updates along each branch. 

FinTime uses [FieldConfig](https://pypi.org/project/fieldconfig/) for configurations, and, as demonstrated in the [Multi-plot](#multi-plot) example it supports updates by passing a new Config object or a dictionary, whether flat or nested. If you're interested in creating your own configurations, please refer to the documentation.

The available configuration options can be displayed using:
```python
from fintime.config import get_config

cfg = get_config()
for k, v in cfg.to_flat_dict().items():
    print(k.ljust(30), v)

# Expected output:
# --> figure.layout                  tight
# --> figure.facecolor               #f9f9f9
# --> figure.title.fontsize          22
# --> figure.title.fontweight        bold
# --> figure.title.y                 0.98
# --> panel.facecolor                white
# --> xaxis.tick.nudge               0
# --> candlestick.panel.height       9.0
# --> candlestick.panel.width        None
# --> ...
```

<a id="upcoming-features"></a>
## Upcoming Features
- Axes labels and legend
- Custom y-tick formatting
- More artists: 
  - lines
  - diverging bars
  - trade annotations with collision control
  - trading session shading
  - and more 