import itertools
from collections import Counter
from typing import List
import numpy as np
import numpy.typing as npt


def log2(x: float) -> float:
    if x < 0:
        raise ValueError(f"Cannot take log of negative number {x}")
    return 0 if x == 0 else float(np.log2(x))


def gen_samples_per_x(
    p_xy: npt.NDArray[np.float64], num_samples_per_x: int, seed: int = 0
) -> List[npt.NDArray[np.int64]]:
    num_x, num_y = p_xy.shape
    y_indices = list(range(num_y))

    rng = np.random.default_rng(seed)

    return [
        rng.choice(
            y_indices, size=num_samples_per_x, p=p_xy[i] / np.sum(p_xy[i])
        )
        for i in range(num_x)
    ]


def gen_truncated_sample_xy(
    num_x: int,
    num_y: int,
    samples_per_x: List[npt.NDArray[np.int64]],
    num_samples_per_x: int,
) -> npt.NDArray[np.float64]:

    sample_xy_empirical = np.zeros((num_x, num_y))
    for i in range(num_x):
        assert num_samples_per_x <= len(samples_per_x[i])
        sample_y = samples_per_x[i][:num_samples_per_x]

        freq_y = Counter(sample_y)
        for idx in freq_y:
            sample_xy_empirical[i, idx] = freq_y[idx]

    return sample_xy_empirical


def shannon_entropy(p_xy: npt.NDArray[np.float64]) -> float:
    if len(p_xy.shape) == 1:
        p_xy = p_xy.reshape((-1, 1))

    num_x, num_y = p_xy.shape

    p_y = np.sum(p_xy, axis=0)

    return 0 - sum(
        p_xy[i, j] * log2(p_xy[i, j] / p_y[j])
        for i, j in itertools.product(range(num_x), range(num_y))
        if p_xy[i, j] != 0
    )
