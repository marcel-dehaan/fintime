import numpy as np
from fintime.types import (
    FloatingArray1D,
    DatetimeArray1D,
    Array1D,
    RectVertices,
    LineSegments,
)


def get_vertical_line_segments(
    b_x: FloatingArray1D, b_ymin: FloatingArray1D, b_ymax: FloatingArray1D
) -> LineSegments:
    return np.stack(
        (
            np.stack((b_x, b_ymin), axis=1),
            np.stack((b_x, b_ymax), axis=1),
        ),
        axis=1,
    )


def get_rolled_line_segments(b_x: Array1D, b_y: Array1D) -> LineSegments:
    b_x_rolled = np.roll(np.array(b_x), -1)
    b_y_rolled = np.roll(b_y, -1)

    return np.stack(
        (
            np.stack((b_x, b_y), axis=1),
            np.stack((b_x_rolled, b_y_rolled), axis=1),
        ),
        axis=1,
    )[:-1]


def get_horizontal_line_segments(
    b_xmin: FloatingArray1D, b_xmax: FloatingArray1D, b_y: FloatingArray1D
) -> LineSegments:
    return np.stack(
        (
            np.stack((b_xmin, b_y), axis=1),
            np.stack((b_xmax, b_y), axis=1),
        ),
        axis=1,
    )


def get_rectangle_vertices(
    b_xmin: FloatingArray1D,
    b_xmax: FloatingArray1D,
    b_ymin: FloatingArray1D,
    b_ymax: FloatingArray1D,
) -> RectVertices:
    return np.stack(
        (
            np.stack((b_xmin, b_ymin), axis=1),
            np.stack((b_xmin, b_ymax), axis=1),
            np.stack((b_xmax, b_ymax), axis=1),
            np.stack((b_xmax, b_ymin), axis=1),
        ),
        axis=1,
    )


def to_num_td(dt: DatetimeArray1D) -> np.timedelta64:
    "infer bar duration in days"
    td = dt - np.roll(dt, 1)
    td[0] = np.median(td)
    return td / np.timedelta64(1, "D")
