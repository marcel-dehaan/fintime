from typing import TypedDict
from typing import Mapping
from typing import Optional
from typing import Any
from typing import Literal
from fieldconfig import Config

from nptyping import NDArray, Shape
from nptyping import Floating, Datetime64, Integer

Array1D = NDArray[Shape["*"], Any]
FloatArray1D = NDArray[Shape["*"], Floating]
IntArray1D = NDArray[Shape["*"], Integer]
DatetimeArray1D = NDArray[Shape["*"], Datetime64]

SizeSpec = tuple[Optional[float], Optional[float]]

from typing import TypeVar
from datetime import timezone
from dateutil import tz

Timezone = TypeVar("Timezone", timezone, tz.tz.tzfile)

Side = Literal["buy", "sell"]


class Ohlc(TypedDict):
    dt: DatetimeArray1D  # represents the time of the open
    open: FloatArray1D
    high: FloatArray1D
    low: FloatArray1D
    close: FloatArray1D


class Volume(TypedDict):
    dt: DatetimeArray1D  # represents the time of the open
    vol: IntArray1D


class Fill(TypedDict):
    dt: Datetime64
    side: Side
    price: float
    size: int
