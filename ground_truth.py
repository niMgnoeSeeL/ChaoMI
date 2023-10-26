import numpy as np
from empirical import mi_from_p_xy

def ground_truth(s_xy: np.ndarray) -> float:
    p_xy = s_xy / np.sum(s_xy)
    return mi_from_p_xy(p_xy)
