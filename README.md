# FinTime
FinTime is a financial time series plotting library built on Matplotlib.  

**Features:** 
- Visual elements as standalone objects (Artists).
- Dynamically sized composite structures (Grid, Subplots, Panels) organise multiple plots within a figure.
- Branched propagation of data and configurations to sub-components, enabling overrides at any level.


## Table of Contents

- [Installation](#installation)
- [The Plot Function](#the-plot-function)
  - [Terminology](#terminology)
  - [Flow](#flow)
- [Usage](#sage)
  - [Data](#data)
  - [Panels Plot](#panels-plot)
  - [Subplots Plot](#subplots-plot)
  - [Standalone Use of Artists](#standalone-use-of-artists)
- [Configuration](#configuration)
- [Upcoming Features](#upcoming-features)
- [Note of Warning](#note-of-warning)


<a id="installation"></a>
## Installation
```python
pip install fintime
```

<a id="the-plot-function"></a>
## The Plot Function
Before delving into the inner workings of the plot function, let's briefly introduce the key concepts that help organize your figure.

<a id="terminology"></a>
### Terminology
  - **Artist**: An object capable of drawing a visual on an Axes.
  - **Panel**: Panels serve as the canvas for either one Axes or two twinx Axes. 
  - **Subplot**: A collection of panels is referred to as a Subplot. Panels within a Subplot are visually stacked vertically and share the x-axis.
  - **Grid**: A collection of Subplots. This object is not exposed directly but manages its Subplots.
  
<a id="flow"></a>
### Flow
The flow of the plot function unfolds in the following sequential steps:

1. **Initialization:** When subplots are provided, a `Grid` object is populated. Alternatively, if panels are passed, a `Subplot` object functions as the top-level container, resulting in a hierarchical structure: 
    - `grid -> subplots -> panels -> artists`.
    - `subplot -> panels -> artists`

2. **Config and Data Propagation:** Configurations and data flow down the hierarchical structure, enabling components to incorporate local changes received during instantiation. Fintime's configuration object (`fieldconfig.Config`) ensures the correctness of configuration settings, triggering exceptions for any invalid values.

3. **Data Validation:** Following the merging of data and configurations across components, a data validation step ensures that all components are prepared for successful rendering later on.

4. **Component Sizing:** The sizing of components is intricately tied to the hierarchical structure. While artists can employ dynamic sizing with best-effort defaults, each component provides a `size` argument, granting it precedence over any dynamic settings. Sizing information is propagated upward in the hierarchical structure, and whenever fixed sizing is specified, it takes precedence. In such cases, the dimensions of components are determined based on their size ratios.

5. **Finalize Sizing:** Conclusive sizing information is computed and cascaded down through the components, communicating their final dimensions. This information is used to enhance the final appearance of the plot, influencing aspects like tick densities, line widths, and more.

6. **Drawing:** In the final stage, cascading down the hierarchical structure once more, each container invokes the `draw` method of its components, instantiating actual Matplotlib objects along the way. Artists then draw onto Axes, completing the visualization process.


<a id="usage"></a>
## Usage

<a id="data"></a>
### Data
FinTime expects data to be structured as a flat mapping, such as a dictionary, containing NumPy arrays. The example below demonstrates the generation of mock OHLCV data with intervals of 1, 10, 30, and 300 seconds. This data will be used in the following examples.

```python
from fintime.mock.data import (
    generate_random_trade_ticks,
    add_random_trades,
    add_random_imb,
    add_moving_average,
)
from fintime.mock.data import to_timebar

spans = [1, 10, 30, 300]
ticks = generate_random_trade_ticks(seed=1)
datas = {f"{span}s": to_timebar(ticks, span=span) for span in spans}

for span in spans:
    data = datas[f"{span}s"]
    add_random_imb(data)
    add_random_trades(data, 10)
    add_moving_average(data, 20)

for feat, array in datas["10s"].items():
    print(feat.ljust(6), repr(array[:2]))

# --> dt     array(['2024-03-18T16:43:10.000', '2024-03-18T16:43:20.000'], dtype='datetime64[ms]')
# --> open   array([101.61, 101.61])
# --> high   array([101.76, 101.92])
# --> low    array([101.54, 101.57])
# --> close  array([101.61, 101.57])
# --> vol    array([2824, 2749])
# --> imb    array([ 0.41030182, -0.44632449])
# --> price  array([0., 0.])
# --> side   array([None, None], dtype=object)
# --> size   array([0., 0.])
# --> ma20   array([nan, nan])
```

<a id="panels-plot"></a>
### Panels Plot
Let's proceed and plot candlesticks and volume bars with a 10-second span.
```python
from matplotlib.pylab import plt
from fintime.plot import plot, Panel
from fintime.artists import (
    CandleStick,
    Volume,
    DivergingBar,
    FillBetween,
    TradeAnnotation,
    Line,
)


fig = plot(
    specs=[
        Panel(
            artists=[
                CandleStick(),
                FillBetween(y1_feat="low", y2_feat="high"),
                TradeAnnotation(),
                Line(yfeat="ma20"),
            ]
        ),
        Panel(artists=[Volume()]),
        Panel(artists=[DivergingBar(feat="imb")]),
    ],
    data=datas["10s"],
    title="Candlestick & Volume Plotted in Separate Panels",
)
plt.show()

```
![panels plot](https://raw.githubusercontent.com/marcel-dehaan/fintime/main/images/panels_plot.png)


Alternatively, it is also possible to draw Candlesticks and Volumebars in the same panel.
```python 
fig = plot(
    specs=[
        Panel(
            artists=[
                CandleStick(config={"candlestick.padding.ymin": 0.2}),
                Volume(
                    twinx=True,
                    config={
                        "volume.edge.linewidth": 1,
                        "volume.face.alpha": 0.3,
                        "volume.edge.alpha": 0.5,
                        "volume.padding.ymax": 2,
                        "volume.relwidth": 1,
                    },
                ),
            ]
        ),
    ],
    data=datas["10s"],
    figsize=(20, 15),
    title="Candlestick & Volume Plotted in the Same Panel",
)
plt.show()
```
![panel plot](https://raw.githubusercontent.com/marcel-dehaan/fintime/main/images/panel_plot.png)

<a id="subplots-plot"></a>
### Subplots Plot
Displaying multiple groups of panels within a single figure is achieved by passing a list of Subplots (rather than Panels) to the plot function. In the following example, we will draw candlestick and volume bars with spans of 1, 30 and 300 seconds while overriding some configurations.  

```python
from fintime.plot import Subplot
from fintime.config import get_config

config = get_config()
config.figure.facecolor = "#131722"
config.figure.title.color = "lightgray"
config.panel.facecolor = "#042530"
config.panel.spine.color = config.panel.facecolor
config.grid.color = "lightgray"
config.xlabel.color = "lightgray"
config.ylabel.color = "lightgray"
config.candlestick.body.face.color.up = "#53b987"
config.candlestick.body.face.color.down = "#eb4d5c"
config.candlestick.wick.color = "lightgray"
config.candlestick.doji.color = "lightgray"
config.volume.face.color.up = "#53b987"
config.volume.face.color.down = "#eb4d5c"
config.fill_between.alpha = 0.2
config.trade_annotation.text.bbox.edge.linewidth = 0.5
for side in ["buy", "sell"]:
    config.trade_annotation.arrow.edge.color[side] = "lightgray"
    config.trade_annotation.arrow.face.color[side] = "lightgray"
    config.trade_annotation.text.bbox.edge.color[side] = "lightgray"


subplots = [
    Subplot(
        [
            Panel(
                artists=[
                    CandleStick(data=datas["1s"]),
                    TradeAnnotation(data=datas["1s"]),
                    Line(data=datas["1s"], yfeat="ma20"),
                ]
            ),
            Panel(artists=[Volume(data=datas["1s"])]),
            Panel(artists=[DivergingBar(data=datas["1s"], feat="imb")]),
        ]
    ),
    Subplot(
        [
            Panel(
                artists=[
                    TradeAnnotation(),
                    CandleStick(),
                    Line(yfeat="ma20"),
                    FillBetween(y1_feat="low", y2_feat="high"),
                ]
            ),
            Panel(artists=[Volume()]),
        ],
        data=datas["30s"],
    ),
    Subplot(
        [
            Panel(
                artists=[
                    CandleStick(
                        config={"candlestick.body.face.color.up": "#2c7a99"}
                    ),
                    TradeAnnotation(),
                    Line(yfeat="ma20"),
                ]
            ),
            Panel(artists=[Volume()]),
        ],
        data=datas["300s"],
    ),
]

fig = plot(
    subplots,
    title="OHLCV of Different Temporal Intervals in Their Own Subplots",
    config=config,
)
plt.show()
```
![subplots plot](https://raw.githubusercontent.com/marcel-dehaan/fintime/main/images/subplots_plot.png)


<a id="standalone-use-of-artists"></a>
### Standalone Use of Artists

You also have the option to have Artists draw on your own Axes.
```python
import matplotlib.pyplot as plt
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

FinTime uses [FieldConfig](https://pypi.org/project/fieldconfig/) for configurations, and, as demonstrated in the examples it supports updates by passing a new Config object or a dictionary, whether flat or nested. If you're interested in creating your own configurations, please refer to the documentation.

The available configuration options can be displayed using:
```python
from fintime.config import get_config

cfg = get_config()
for k, v in cfg.to_flat_dict().items():
    print(k.ljust(30), v)

# Expected output:
# --> font.family                    sans-serif
# --> font.color                     black
# --> font.weight                    300
# --> ylabel.font.family             sans-serif
# --> ylabel.font.color              black
# --> ylabel.font.weight             300
# --> ylabel.font.size               18
# --> ylabel.pad                     30
# --> ...
```

<a id="upcoming-features"></a>
## Upcoming Features
- Legends
- Custom y-tick formatting
- Improved default spacing logic
- Support for non-linear datetime xaxis to display OHCV data of irregular intervals
- More artists: 
  - Trading session shading
  - Table
  - and more 
  
<a id="note-of-warning"></a>
## Note of Warning
FinTime is currently in its early alpha development stage, and interfaces are subject to change without prior notice, including potential modifications that may not be backward compatible. Please be aware of this ongoing development state.
