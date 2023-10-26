import numpy as np
import numpy.typing as npt
from util import shannon_entropy


def mi_from_p_xy(p_xy: npt.NDArray[np.float64]) -> float:
    if len(p_xy.shape) == 1:
        p_xy = p_xy.reshape((1, -1))

    assert len(p_xy.shape) == 2

    p_x = np.sum(p_xy, axis=1)

    h_x = shannon_entropy(p_x)
    h_xy = shannon_entropy(p_xy)

    return h_x - h_xy


def empirical(sample_xy_empirical: npt.NDArray[np.float64]) -> float:
    if np.sum(sample_xy_empirical) == 0:
        raise ValueError("Sample is all zeros")

    p_xy = sample_xy_empirical / np.sum(sample_xy_empirical)
    return mi_from_p_xy(p_xy)
