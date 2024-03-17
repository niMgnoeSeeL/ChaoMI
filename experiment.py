from multiprocessing import Pool, cpu_count
import numpy as np
from typing import Any, List, Tuple
import pandas as pd
from lychee import lychee
from empirical import empirical
from miller import miller
from util import (
    gen_truncated_sample_xy,
    gen_samples_per_x,
)
import time


MAX_CORE = 100


def determine_num_samples_per_x_values(output_domain_size: int) -> List[int]:

    num_samples_per_x_props = [50, 100, 200, 500]

    num_samples_per_x_values = sorted(
        {int(output_domain_size * (n / 100)) for n in num_samples_per_x_props}
        - {0}
    )
    assert 0 not in num_samples_per_x_values

    return num_samples_per_x_values


def esti_mp(params):
    (
        iter_idx,
        num_samples_per_x,
        estimator,
        chao_idx,
        samples,
        num_x,
        num_y,
    ) = params
    print(
        f"Iter: {iter_idx}, Num Samples per X: {num_samples_per_x}",
        end="\r",
        flush=True,
    )
    sample = gen_truncated_sample_xy(num_x, num_y, samples, num_samples_per_x)

    ret = None
    start_time = time.time()
    if estimator == "empirical":
        ret = empirical(sample)
    elif estimator == "miller":
        ret = miller(sample, num_x * num_samples_per_x)
    elif estimator.startswith("Chao"):
        is_flat = estimator[4] == "F"
        is_adjust = estimator[5] == "R"
        is_muller = estimator[6] == "M"
        ret = lychee(
            sample,
            is_flat=is_flat,
            is_adjust=is_adjust,
            is_muller=is_muller,
        )
    else:
        raise ValueError(f"Unknown estimator: {estimator}")
    return ret, time.time() - start_time


def experiment(
    data: List[Tuple[int, int]],
    output_domain_size: int,
    num_iterations: int = 1,
    estimators=None,
    **kwargs: Any,
) -> pd.DataFrame:
    num_chao = kwargs.get("num_chao", 30)
    if estimators is None:
        estimators = []

    s_xy = data
    p_xy = s_xy / np.sum(s_xy)
    num_x, num_y = s_xy.shape

    x_values = determine_num_samples_per_x_values(output_domain_size)

    i_xy_estimates = pd.DataFrame(
        columns=["Nx", "trial", *estimators],
        dtype=float,
    )
    i_xy_estimates.set_index(["Nx", "trial"], inplace=True)

    max_x_value = max(x_values)

    params_list = []
    for i in range(num_iterations):
        samples = gen_samples_per_x(p_xy, max_x_value, seed=i)
        for num_samples_per_x in x_values:
            for estimator in estimators:
                if not estimator.startswith("Chao"):
                    params_list.append(
                        (
                            i,
                            num_samples_per_x,
                            estimator,
                            0,
                            samples,
                            num_x,
                            num_y,
                        )
                    )
                else:
                    params_list.extend(
                        (
                            i,
                            num_samples_per_x,
                            estimator,
                            chao_idx,
                            samples,
                            num_x,
                            num_y,
                        )
                        for chao_idx in range(num_chao)
                    )
    with Pool(min(MAX_CORE, cpu_count())) as p:
        estimatess = p.map(esti_mp, params_list)

    rows = []
    for params, (estimate, time) in zip(params_list, estimatess):
        i, num_samples_per_x, estimator, chao_idx, *_ = params
        rows.append([num_samples_per_x, i, estimator, chao_idx, estimate, time])
    df = pd.DataFrame(
        rows,
        columns=["Nx", "trial", "estimator", "chao_idx", "estimate", "time"],
    )
    df_timesum = df.groupby(["Nx", "trial", "estimator"]).sum()
    df = df.groupby(["Nx", "trial", "estimator"]).mean()
    df = df.pivot_table(
        index=["Nx", "trial"],
        columns="estimator",
        values="estimate",
    )
    df_timesum = df_timesum.pivot_table(
        index=["Nx", "trial"],
        columns="estimator",
        values="time",
    )
    df = df.sort_index(level="trial")
    df_timesum = df_timesum.sort_index(level="trial")

    return df, df_timesum
