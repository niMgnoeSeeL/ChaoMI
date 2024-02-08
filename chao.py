import numpy as np
from estimate import estimate_multinomial


def calculate_detected_and_undetected(
    sample_xy_empirical, num_sample_per_x_list, num_non_zero_y, debug=False
):
    shp = sample_xy_empirical.shape
    num_x, num_y = (1, shp[0]) if len(shp) == 1 else shp
    p_xy_detected = []
    p_xy_undetected = []

    assert len(num_sample_per_x_list) == num_x

    for i in range(num_x):
        if debug:
            print(f"Estimating x={i}, {num_sample_per_x_list[i]} samples")
        if not num_sample_per_x_list[i]:
            p_xy_detected.append(np.zeros(num_y))
            p_xy_undetected.append(np.zeros(num_y))
            continue
        detected_i, undetected_i = estimate_multinomial(
            sample_xy_empirical[i],
            num_y,
            num_sample_per_x_list[i],
            num_non_zero_y,
            debug=debug,
        )
        detected_i, undetected_i = (
            np.array(detected_i),
            np.array(undetected_i),
        )

        for x in detected_i:
            assert x >= 0

        p_xy_detected.append(detected_i)
        p_xy_undetected.append(undetected_i)

    return p_xy_detected, p_xy_undetected


def get_p_xy_chao(sample_xy_empirical, is_adjust=True, debug=False):
    num_x, num_y = sample_xy_empirical.shape

    p_xy = sample_xy_empirical / np.sum(sample_xy_empirical)
    p_y = np.sum(p_xy, axis=0)
    num_non_zero_y = np.sum(p_y > 0) if num_x > 1 else num_y

    num_sample_per_x_list = sample_xy_empirical.sum(axis=1)
    p_xy_detected, p_xy_undetected = calculate_detected_and_undetected(
        sample_xy_empirical, num_sample_per_x_list, num_non_zero_y, debug=debug
    )

    p_xy_chao = np.zeros((num_x, num_y))

    for i in range(num_x):
        if debug:
            print(f"Recovering x={i}")
        p_xiy_detected = p_xy_detected[i]
        p_xiy_undetected = p_xy_undetected[i]
        if sum(p_xiy_detected) == 0:
            p_xy_chao[i] = p_xiy_detected
            continue
        if debug:
            print(
                f"p_xiy_detectd.shape={p_xiy_detected.shape}, p_y.shape={p_y.shape}"
            )
        condition = lambda i: (
            p_xiy_detected[i] <= 0 and p_y[i] > 0
            if num_x > 1
            else p_xiy_detected[i] <= 0
        )
        undetected_indices = list(filter(condition, range(len(p_xiy_detected))))

        if debug:
            print(
                f"len(p_xiy_undetected)={len(p_xiy_undetected)}, len(undetected_indices)={len(undetected_indices)}"
            )
        if len(p_xiy_undetected) == 0 or len(undetected_indices) == 0:
            p_xy_chao[i] = p_xiy_detected
            continue
        if is_adjust:
            if debug:
                print(
                    f"Adjusting x={i}, min_detected={min(p_xiy_detected[p_xiy_detected > 0]):.4f}, max_undetected={max(p_xiy_undetected):.4f}"
                )
            while min(p_xiy_detected[p_xiy_detected > 0]) < max(
                p_xiy_undetected
            ):
                if debug:
                    print(
                        f"max(p_xiy_undetected) = {max(p_xiy_undetected)} is greater than min(p_xiy_detected[p_xiy_detected > 0]) = {min(p_xiy_detected[p_xiy_detected > 0])}; swapping"
                    )
                max_undetected = max(p_xiy_undetected)
                max_undetected_idx = np.where(
                    p_xiy_undetected == max_undetected
                )[0][0]
                max_detected_less_than_undetected = np.max(
                    p_xiy_detected[p_xiy_detected < max_undetected]
                )
                max_detected_less_than_undetected_idx = np.where(
                    p_xiy_detected == max_detected_less_than_undetected
                )[0][0]
                if debug:
                    print(
                        f"Exchanging {max_undetected} in max_undetected[{max_undetected_idx}] with {max_detected_less_than_undetected} in p_xiy_detected[{max_detected_less_than_undetected_idx}]"
                    )
                p_xiy_detected[max_detected_less_than_undetected_idx] = (
                    max_undetected
                )
                p_xiy_undetected[max_undetected_idx] = (
                    max_detected_less_than_undetected
                )

        p_xy_chao[i] = p_xiy_detected
        p_xiy_undetected = p_xiy_undetected.tolist()

        if num_x > 1:
            condition = lambda i: p_xiy_detected[i] <= 0 and p_y[i] > 0
            undetected_indices = list(
                filter(condition, range(len(p_xiy_detected)))
            )
            undetected_indices_prob = p_y[undetected_indices]
            try:
                ordered_undetected_indices = np.random.choice(
                    undetected_indices,
                    size=len(undetected_indices),
                    replace=False,
                    p=undetected_indices_prob / np.sum(undetected_indices_prob),
                )
            except ValueError as e:
                print(e)
                print(p_xiy_undetected)
                print(f"undetected_indices_prob = {undetected_indices_prob}")
                raise e
        else:
            undetected_indices = list(
                filter(
                    lambda i: p_xiy_detected[i] <= 0, range(len(p_xiy_detected))
                )
            )
            ordered_undetected_indices = np.random.choice(
                undetected_indices,
                size=len(undetected_indices),
                replace=False,
            )
        ordered_p_xiy_undetected = sorted(p_xiy_undetected, reverse=True)
        for y_idx in ordered_undetected_indices:
            assert p_xy_chao[i, y_idx] <= 0
            if len(ordered_p_xiy_undetected) == 0:
                break
            p_xy_chao[i, y_idx] = ordered_p_xiy_undetected.pop()

    p_xy_chao = p_xy_chao / np.sum(p_xy_chao)

    return p_xy_chao
