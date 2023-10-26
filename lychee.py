import numpy as np
from chao import get_p_xy_chao
from empirical import empirical
from miller import miller


def lychee(
    sample_xy_empirical,
    is_flat=False,
    is_adjust=True,
    is_muller=False,
    debug=False,
):
    if is_flat:
        sample_corrdim = sample_xy_empirical.reshape((1, -1))
    else:
        sample_corrdim = sample_xy_empirical
    orign = np.sum(sample_xy_empirical)

    p_xy_chao = get_p_xy_chao(sample_corrdim, is_adjust=is_adjust, debug=debug)
    if is_flat:
        p_xy_chao = p_xy_chao.reshape(sample_xy_empirical.shape)
    if is_muller:
        orign = np.sum(sample_xy_empirical)
        newn = max(orign, np.ceil(1 / np.min(p_xy_chao[p_xy_chao > 0])))
        return miller(p_xy_chao, newn)
    else:
        return empirical(p_xy_chao)
