from matplotlib.pylab import rand
import numpy as np
import random


def generate_random_trade_ticks(
    dt_start: np.datetime64 = np.datetime64("now"),
    td_session: np.timedelta64 = np.timedelta64(6, "h"),
    initial_price=100,
    volatility: float = 0.5,
    liquidity: float = 2.5,
    seed=None,
):

    assert td_session < np.timedelta64(4, "D")
    assert volatility > 0 and volatility <= 10
    assert liquidity > 0 and liquidity <= 5

    dt_stop = dt_start + td_session
    dt_range = np.arange(dt_start, dt_stop, 10, dtype="datetime64[ms]")
    n_secs_session = td_session / np.timedelta64(1, "s")
    np.random.seed(seed)
    n_ticks = int(n_secs_session * liquidity**2)

    dt_ticks = np.random.choice(dt_range, size=n_ticks, replace=False)
    dt_ticks = np.sort(dt_ticks)
    scale = 0.001 * volatility**2
    drift_values = np.random.normal(loc=0, scale=scale, size=n_ticks)

    cumulative_drift = np.cumsum(drift_values)
    prices = initial_price * np.exp(cumulative_drift)
    sizes = np.random.randint(0, 100, size=n_ticks)
    ticks = {"dt": dt_ticks, "price": prices, "size": sizes}
    return ticks


def to_timebar(ticks, span: int, n_bars: int = 200):
    t_dt = ticks["dt"]
    t_price = ticks["price"]
    t_size = ticks["size"]

    td_step = np.timedelta64(span, "s")
    dt_start = t_dt[0].astype(f"datetime64[{span}s]")
    dt_stop = t_dt[-1].astype(f"datetime64[{span}s]") + td_step

    b_dt = np.arange(dt_start, dt_stop, td_step)
    b_open = []
    b_high = []
    b_low = []
    b_close = []
    b_vol = []

    i_tick = 0
    p_close = t_price[0]
    for dt_open in b_dt:
        prices = []
        volume = 0
        while t_dt[i_tick] < dt_open:
            prices.append(t_price[i_tick])
            volume += t_size[i_tick]
            i_tick += 1
        i_tick += 1

        if prices:
            b_open.append(prices[0])
            b_high.append(max(prices))
            b_low.append(min(prices))
            b_close.append(prices[-1])
            b_vol.append(volume)
            p_close = prices[-1]
        else:
            b_open.append(p_close)
            b_high.append(p_close)
            b_low.append(p_close)
            b_close.append(p_close)
            b_vol.append(0)

    return {
        "dt": np.array(b_dt[-n_bars:]).astype("datetime64[ms]"),
        "open": np.array(b_open[-n_bars:]).round(2),
        "high": np.array(b_high[-n_bars:]).round(2),
        "low": np.array(b_low[-n_bars:]).round(2),
        "close": np.array(b_close[-n_bars:]).round(2),
        "vol": np.array(b_vol[-n_bars:]),
    }


def add_random_trades(data, n_trades, seed=1):
    random.seed(seed)
    n = data["dt"].size
    indx = random.sample(range(n), n_trades)

    data["price"] = np.zeros_like(data["close"])
    data["side"] = np.empty(n, object)
    data["size"] = np.zeros_like(data["close"])

    for i in indx:
        data["price"][i] = round(
            np.random.uniform(data["low"][i], data["high"][i]), 2
        )
        data["side"][i] = np.random.choice(["buy", "sell"])
        data["size"][i] = np.random.randint(1, 10) * 10


def add_random_imb(data):
    data["imb"] = np.random.uniform(-1, 1, data["dt"].size)


def add_moving_average(data, n):
    moving_avg = np.convolve(data["close"], np.ones(n), "valid") / n
    moving_avg = np.concatenate(([np.nan] * (n - 1), moving_avg))
    data[f"ma{n}"] = moving_avg
