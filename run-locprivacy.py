import os
import sys
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import chao
from miller import miller
from empirical import empirical
from typing import Tuple
from multiprocessing import Pool, cpu_count


MAX_CORE = 100


def parse_args(args):
    arg_parser = argparse.ArgumentParser(
        description="Run the local privacy algorithm"
    )
    arg_parser.add_argument(
        "--subject",
        type=str,
        required=True,
        help="The name of the subject",
        choices=["pg2", "opt"],
    )
    arg_parser.add_argument(
        "--maxsample",
        help="the maximum number of samples to use; the number of samples considered will be 400 * 2^i for i in [0..] until the maximum number of samples is reached",
        type=int,
        default=400,
    )
    arg_parser.add_argument(
        "--numruns",
        help="the number of runs to average over",
        type=int,
        default=1,
    )
    arg_parser.add_argument(
        "--outputdir",
        help="the directory to store the output",
        type=str,
        default="data-LocPrivacy",
    )
    return arg_parser.parse_args(args)


def load_prob(subject: str) -> pd.DataFrame:
    if subject == "pg2":
        prob_path = os.path.join("data-LocPrivacy", "prob_df-PG2.csv")
    elif subject == "opt":
        prob_path = os.path.join("data-LocPrivacy", "prob_df-OPT.csv")
    else:
        raise ValueError(f"Unknown subject: {subject}")
    prob_df = pd.read_csv(prob_path)
    return prob_df


def entropy(p: np.ndarray) -> float:
    p_nonzero = p[p > 0]
    return -np.sum(p_nonzero * np.log2(p_nonzero))


def estimate(
    samples: pd.DataFrame, num_samples: int, run: int, random_seed: int
) -> Tuple[float, float, float]:
    prob_emp_sec = samples.groupby("idx_sec").size() / num_samples
    prob_emp_obs = samples.groupby("idx_obs").size() / num_samples
    prob_emp_joint = (
        samples.groupby(["idx_sec", "idx_obs"]).size() / num_samples
    )
    ent_emp_sec = entropy(prob_emp_sec)
    ent_emp_obs = entropy(prob_emp_obs)
    ent_emp_joint = entropy(prob_emp_joint)
    mi_emp = ent_emp_sec + ent_emp_obs - ent_emp_joint
    unique_sec = len(prob_emp_sec)
    unique_obs = len(prob_emp_obs)
    mi_miller = mi_emp - (unique_sec - 1) * (unique_obs - 1) / (2 * num_samples)

    sample_xy_empirical = (
        samples.groupby(["idx_sec", "idx_obs"])
        .size()
        .unstack()
        .fillna(0)
        .values
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        p_xy_chao = chao.get_p_xy_chao(sample_xy_empirical, is_adjust=True)
    p_xy_chao = p_xy_chao * prob_emp_sec.values[:, np.newaxis]
    p_xy_chao = p_xy_chao / np.sum(p_xy_chao)
    assert all(np.sum(p_xy_chao, axis=1) - prob_emp_sec.values < 1e-8)
    orign = np.sum(sample_xy_empirical)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        try:
            newn = max(orign, np.ceil(1 / np.min(p_xy_chao[p_xy_chao > 0])))
            mi_chao = miller(p_xy_chao, newn)
        except:
            mi_chao = empirical(p_xy_chao)
    return (mi_emp, mi_miller, mi_chao)


def draw_plot(
    df: pd.DataFrame, subject: str, mi: float, outputdir: str
) -> None:
    fig, ax = plt.subplots()
    sns.lineplot(data=df, x="num_samples", y="mi_emp", ax=ax, label="Empirical")
    sns.lineplot(data=df, x="num_samples", y="mi_miller", ax=ax, label="Miller")
    sns.lineplot(data=df, x="num_samples", y="mi_chao", ax=ax, label="Chao")
    ax.axhline(mi, color="r", linestyle="--", label="Ground Truth")
    ax.set_xscale("log")
    ax.set_xlabel("Number of Samples")
    ax.set_ylabel("Mutual Information")
    ax.set_title(f"Mutual Information Estimation for {subject}")
    ax.legend()
    # save as pdf
    fig.savefig(
        os.path.join(outputdir, f"mi-{subject}.pdf"),
        bbox_inches="tight",
    )


def sampling(params):
    prob_df, num_samples, run = params
    random_seed = int.from_bytes(os.urandom(4), "big")
    np.random.seed(random_seed) # use os.urandom(4) to generate a random seed
    samples = np.random.choice(
        prob_df.index, num_samples, p=prob_df.prob
    )
    samples = pd.DataFrame(
        np.array(list(samples)),
        columns=["lati_sec", "long_sec", "lati_obs", "long_obs"],
    )
    samples["idx_sec"] = list(zip(samples.lati_sec, samples.long_sec))
    samples["idx_obs"] = list(zip(samples.lati_obs, samples.long_obs))
    samples = samples[["idx_sec", "idx_obs"]]
    return (samples, num_samples, run, random_seed)


def run_experiment(args: argparse.Namespace) -> None:
    subject = args.subject
    prob_df = load_prob(subject)
    prob_df.set_index(
        ["lati_sec", "long_sec", "lati_obs", "long_obs"], inplace=True
    )
    # ground truth mutual information
    probs_sec = prob_df.groupby(["lati_sec", "long_sec"]).prob.sum()
    ent_sec = entropy(probs_sec)
    probs_obs = prob_df.groupby(["lati_obs", "long_obs"]).prob.sum()
    ent_obs = entropy(probs_obs)
    ent_joint = entropy(prob_df.prob)
    mi = ent_sec + ent_obs - ent_joint

    maxsample = args.maxsample
    sample_sizes = [400]
    while sample_sizes[-1] < maxsample:
        sample_sizes.append(sample_sizes[-1] * 2)
    if sample_sizes[-1] > maxsample:
        sample_sizes = sample_sizes[:-1]
    print(f"Sample sizes: {sample_sizes}")
    numruns = args.numruns

    params1 = []
    for num_samples in sample_sizes:
        for run in range(numruns):
            params1.append((prob_df, num_samples, run))
    with Pool(min(MAX_CORE, cpu_count())) as pool:
        params2 = pool.map(sampling, params1)
    # sort params2 by num_samples and run
    params2 = sorted(params2, key=lambda x: (x[1], x[2]))

    with Pool(min(MAX_CORE, cpu_count())) as pool:
        results = pool.starmap(estimate, params2)

    rows = []
    for (samples, num_samples, run, seed), (mi_emp, mi_miller, mi_chao) in zip(
        params2, results
    ):
        rows.append([num_samples, run, mi_emp, mi_miller, mi_chao, seed])
    df = pd.DataFrame(
        rows,
        columns=["num_samples", "run", "mi_emp", "mi_miller", "mi_chao", "seed"],
    )
    df.to_csv(
        os.path.join(args.outputdir, f"mi-{subject}.csv"),
        index=False,
    )

    draw_plot(df, subject, mi, args.outputdir)


if __name__ == "__main__":
    print("Starting...")
    args = parse_args(sys.argv[1:])
    print(f"Subject: {args.subject}")
    print(f"Max samples: {args.maxsample}")
    print(f"Number of runs: {args.numruns}")
    print(f"Output directory: {args.outputdir}")
    run_experiment(args)
    print("Done!")
