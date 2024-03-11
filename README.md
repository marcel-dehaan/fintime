# FinTime
FinTime is a financial time series plotting library built on Matplotlib.  

**Features:** 
- Visual elements as standalone objects (Artists).
- Dynamically sized composite structures (Grid, Subplots, Panels) organise multiple plots within a figure.
- Branched propagation of data and configurations to sub-components, enabling overrides at any level.




## Table of Contents

- [Installation](#installation)
- [The plot function](#the-plot-function)
  - [Terminology](#terminology)
  - [Flow](#flow)
- [Usage](#sage)
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

3. **Data Validation:** Following the consolidation of final data and configurations across components, a data validation step ensures that all components are prepared for successful rendering later on.

4. **Component Sizing:** The sizing of components is intricately tied to the hierarchical structure. While artists can employ dynamic sizing with best-effort defaults, each component provides a `size` argument, granting it precedence over any dynamic settings. Sizing information is propagated upward in the hierarchical structure, and whenever fixed sizing is specified, it takes precedence. In such cases, the dimensions of components are determined based on their size ratios.

5. **Finalize Sizing:** Conclusive sizing information is computed and cascaded down through the components, communicating their ultimate dimensions. This information is used to enhance the final appearance of the plot, influencing aspects like tick densities, line widths, and more.

6. **Drawing:** In the final stage, cascading down the hierarchical structure once more, each container invokes the `draw` method of its components, instantiating actual Matplotlib objects along the way. Artists then draw onto Axes, completing the visualization process.


<a id="usage"></a>
## Usage

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
    specs=[
        Panel(artists=[CandleStick()]),
        Panel(artists=[Volume()]),
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
from fieldconfig import Config
from fintime.plot import Subplot
from fintime.artists import Line

datas["1s"]["sin"] = np.sin(np.linspace(0, 2 * np.pi, datas["1s"]["dt"].size))

subplots = [
    Subplot(
        [
            Panel(
                artists=[
                    CandleStick(data=datas["1s"]),
                    Line(
                        data=datas["1s"],
                        yfeat="sin",
                        ylabel="sine wave",
                        twinx=True,
                    ),
                ]
            ),
            Panel(artists=[Volume(data=datas["1s"])]),
        ]
    ),
    Subplot(
        [
            Panel(
                artists=[
                    CandleStick(
                        config={"candlestick.body.up_color": "black"}
                    ),
                ]
            ),
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

fig = plot(
    subplots,
    title="OHLCV of Different Temporal Intervals in Their Own Subplots",
)
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
- More artists: 
  - trade annotations with collision control
  - diverging bars
  - trading session shading
  - and more 

