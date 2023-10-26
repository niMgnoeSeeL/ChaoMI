from empirical import empirical


def miller(sample_xy_empirical, num_samples):
    s_x = sample_xy_empirical.sum(axis=1)
    s_y = sample_xy_empirical.sum(axis=0)

    num_non_zero_x = (s_x > 0).sum()
    num_non_zero_y = (s_y > 0).sum()

    i_xy_empirical = empirical(sample_xy_empirical)

    return i_xy_empirical - (num_non_zero_x - 1) * (num_non_zero_y - 1) / (
        2 * num_samples
    )
