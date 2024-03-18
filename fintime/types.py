from typing import Any, Optional, TypeVar, TypedDict, Literal
from datetime import timezone
from dateutil import tz
from nptyping import NDArray, Shape
from nptyping import Floating, Datetime64, Integer, Number, String, Object

LineSegments = NDArray[Shape["*, 2, 2"], Floating]
RectVertices = NDArray[Shape["*, 4, 2"], Floating]

Array1D = NDArray[Shape["*"], Any]
FloatingArray1D = NDArray[Shape["*"], Floating]
IntegerArray1D = NDArray[Shape["*"], Integer]
NumberArray1D = NDArray[Shape["*"], Number]
StringArray1D = NDArray[Shape["*"], Object]

DatetimeArray1D = NDArray[Shape["*"], Datetime64]
SizeSpec = tuple[Optional[float], Optional[float]]
Timezone = TypeVar("Timezone", timezone, tz.tz.tzfile)
Side = Literal["buy", "sell"]


class Ohlc(TypedDict):
    dt: DatetimeArray1D
    open: FloatingArray1D
    high: FloatingArray1D
    low: FloatingArray1D
    close: FloatingArray1D


class Volume(TypedDict):
    dt: DatetimeArray1D
    vol: NumberArray1D


class Fill(TypedDict):
    dt: DatetimeArray1D
    price: NumberArray1D
    size: NumberArray1D
    side: StringArray1D
