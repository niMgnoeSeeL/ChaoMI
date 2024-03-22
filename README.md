# Repository Description

This replication repository contains the data, result, and scripts for the paper "Accounting for Missing Events in Statistical Information Leakage Estimation" submitted to ISSTA 2025.

## Requirements

- python 3
- numpy
- scipy
- pandas
- matplotlib
- seaborn

## Structure

```bash
$ tree .
.
├── README.md                       # This file
├── HyLeak-data/                    # Subject programs (HyLeak IR) and results of HyLeak for RQ1-3
├── data1M/                         # Directory containing the 1M samples for the ground truth of the subject programs for RQ1-3
├── data-epassport/                 # Directory containing the data for the ePassport experiment
├── data-LocPrivacy/                # Directory containing the data for the location privacy experiment
├── result/                         # Directory containing the results of estimation for RQ1-3
├── figures/                        # Directory containing the figures for the paper
├── notebook                        # Directory containing the Jupyter notebooks for the paper
│   ├── combine-hyleak-result.ipynb
│   ├── RQ1-RQ2(partial).ipynb      # Notebook for RQ1 and RQ2
│   ├── RQ2.ipynb                   # Notebook for RQ2
│   ├── RQ3.ipynb                   # Notebook for RQ3
│   ├── LocPrivacyProbgen.ipynb     # Notebook for generating the joint distribution of LPPMs
│   ├── RQ4-ePassport.ipynb         # Notebook for RQ4 on ePassport experiment
│   └── RQ4-figgen.ipynb            # Notebook for generating the figures for RQ4
├── chao.py
├── empirical.py
├── estimate.py
├── experiment.py
├── ground_truth.py
├── lychee.py
├── miller.py
├── util.py
├── run-para.py                     # Script for running the experiments for RQ1-3
└── run-locprivacy.py               # Script for running the experiments for RQ4, location privacy
```

## Usage

### Estimation

#### 1. Run the experiments for RQ1-3

First, set the parameters:

- the number of repetitions for each configuration, i.e., (subject, sample ratio) pair in the script `run-para.py` (`NUM_RUNS_PER_NUM_SAMPLES`); 30 is the number we used in the paper.
- the number of repetitions for our proposed method with the same sample in the script `run-para.py` (`NUM_RUNS_PER_NUM_SAMPLES`); 30 is the number we used in the paper.
- the number of cores for parallel computation in the script `experiment.py` (`MAX_CORES`).

Then, run the script with the following command with the data in the `data1M/` directory:

```bash
$ python run-para.py
```

The script will generate the results in the `result/` directory.

#### 2. Run the experiments for RQ4

- **Location Privacy**

First, download the pre-generated joint probability distribution of LPPMs from [here-closed-for-double-blind], which contains `prob_df-Opt.csv` and `prob_df-PG2.csv`. Then, put them in the `data-LocPrivacy/` directory.

If you want to generate the joint distribution of LPPMs by yourself, run the notebook `LocPrivacyProbgen.ipynb` in the `notebook/` directory with the data `data-LocPrivacy/Gowalla_totalCheckins.txt`.

Then, set the number of cores for parallel computation in the script `run-locprivacy.py` (`MAX_CORES`).

Finally, run the script with the following command:

```bash
$ python run-locprivacy.py --subject {pg2,opt} --maxsample M --numruns N
```

where `M` is the maximum number of samples to use. the number of samples considered will be $400$ (the domain size of the secret location)$ \times 2^i$ for $i \in [0..]$ until the maximum number of samples is reached.

For example, to run the experiments for the optimal mechanisms proposed by Oya et al. (Blahut-Arimoto method) with 1M samples and 30 runs (the experiment we conducted in the paper)

```bash
$ python run-locprivacy.py --subject opt --maxsample 1000000 --numruns 30
```

The script will generate the results in the `data-LocPrivacy/` directory.

- **ePassport Privacy**

Run the notebook `RQ4-ePassport.ipynb` in the `notebook/` directory with the data `data-epassport/raw-time-data/*.csv`.

The notebook will generate the results in the `data-epassport/estimate` directory.

### Analysis and Visualization

Use the notebooks in the `notebook/` directory to analyze the results and generate the figures.
