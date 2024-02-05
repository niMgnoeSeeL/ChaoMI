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
├── HyLeak-data             # Subject programs and results of HyLeak
├── README.md               # This file
├── data1M/                 # Directory containing the 1M samples for the ground truth
├── figures/                # Directory containing the figures for the paper
├── result/                 # Directory containing the results of the proposed estimator
├── notebook                # Directory containing the Jupyter notebooks for the paper
│   ├── RQ1-RQ2(partial).ipynb
│   ├── RQ2.ipynb
│   └── RQ3.ipynb
├── chao.py
├── empirical.py
├── estimate.py
├── experiment.py
├── ground_truth.py
├── lychee.py
├── miller.py
├── run-para.py             # Script for running the experiments
└── util.py
```
