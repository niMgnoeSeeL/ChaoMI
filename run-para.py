import os
import time
from typing import Tuple
from experiment import experiment
from ground_truth import ground_truth

import numpy as np

NUM_RUNS_PER_NUM_SAMPLES = 30
NUM_CHAO = 30

# (name, input domain size, output domain size)
hyleak_subjects = [
    ("smartgrid-1", 3, 12),
    ("prob-termination-5", 6, 10),
    ("prob-termination-7", 8, 10),
    ("smartgrid-2", 9, 12),
    ("prob-termination-9", 10, 10),
    ("prob-termination-12", 13, 20),
    ("reservoir-4", 16, 4),
    ("window-20", 20, 20),
    ("window-24", 24, 24),
    ("smartgrid-3", 27, 12),
    ("window-28", 28, 28),
    ("window-32", 32, 32),
    ("reservoir-6", 64, 8),
    ("smartgrid-4", 81, 12),
    ("smartgrid-5", 243, 12),
    ("reservoir-8", 256, 16),
    ("random-walk-3", 500, 24),
    ("random-walk-5", 500, 31),
    ("random-walk-7", 500, 33),
    ("random-walk-14", 500, 40),
    ("reservoir-10", 1024, 32),
    ("reservoir-12", 4096, 64),
]


def run_experiment(args: Tuple[str, int]) -> None:
    subject_filename, input_domain_size, output_domain_size = args

    print(
        f"Running experiment on '{subject_filename}', output domain size {output_domain_size}"
    )

    s_xy_path = os.path.join("/ChaoMI/data1M/", f"{subject_filename}-s-xy.csv")
    s_xy = np.loadtxt(s_xy_path, delimiter=",", dtype=int)
    assert s_xy.shape == (input_domain_size, output_domain_size)

    estimators = [
        "empirical",
        "miller",
        "ChaoFON",
        "ChaoFRN",
        "ChaoFOM",
        "ChaoFRM",
        "ChaoION",
        "ChaoIRN",
        "ChaoIOM",
        "ChaoIRM",
    ]

    i_xy_ground_truth = ground_truth(s_xy)
    df_estimates, df_time = experiment(
        s_xy,
        output_domain_size,
        NUM_RUNS_PER_NUM_SAMPLES,
        estimators,
        num_chao=NUM_CHAO,
    )
    df_estimates["GT"] = i_xy_ground_truth
    df_estimates["N"] = np.sum(s_xy)

    df_estimates.to_csv(
        os.path.join(
            "result", f"esti-{subject_filename}-i-xy.csv"
        )
    )
    df_time.to_csv(
        os.path.join(
            "result", f"time-{subject_filename}-i-xy.csv"
        )
    )


if __name__ == "__main__":
    for subject in hyleak_subjects:
        start_time = time.time()
        run_experiment(subject)
        print(f"{subject[0]}: {time.time() - start_time}", flush=True)
