from typing import Callable, List, Tuple
from math import exp, ceil
import warnings
from collections import Counter
from scipy.optimize import fsolve

warnings.filterwarnings("ignore", "The iteration is not making good progress")


def cov_first_order(n: int, num_singletons: int, num_doubletons: int) -> float:
    if (n - 1) * num_singletons + 2 * num_doubletons == 0:
        return 1 - (num_singletons / n)

    return 1 - (num_singletons / n) * ((n - 1) * num_singletons) / (
        (n - 1) * num_singletons + 2 * num_doubletons
    )


def cov_deficit_first_order(
    n: int, num_singletons: int, num_doubletons: int
) -> float:
    return 1 - cov_first_order(n, num_singletons, num_doubletons)


def summation_xi_xi_minus_1(sample_abundance: List[int]) -> int:
    return sum(map(lambda xi: xi * (xi - 1), sample_abundance))


def cov_second_order(
    n: int,
    sample_abundance: List[int],
    num_doubletons: int,
    num_tripletons: int,
) -> float:

    return 1 - (
        2
        * num_doubletons
        / summation_xi_xi_minus_1(sample_abundance)
        * (
            ((n - 2) * num_doubletons)
            / ((n - 2) * num_doubletons + 3 * num_tripletons)
        )
        ** 2
    )


def cov_deficit_second_order(
    n: int,
    sample_abundance: List[int],
    num_doubletons: int,
    num_tripletons: int,
) -> float:

    return 1 - cov_second_order(
        n, sample_abundance, num_doubletons, num_tripletons
    )


def num_undetected_lower_bound(
    n: int, num_singletons: int, num_doubletons: int
) -> float:
    if num_doubletons > 0:
        return ((n - 1) / n) * ((num_singletons**2) / (2 * num_doubletons))
    else:
        return ((n - 1) / n) * (num_singletons * (num_singletons - 1) / 2)


def est_detected_rel_abundance(
    sample_abundance: int, n: int, theta: float, lambda_: float = 1.0
) -> float:
    if not (0 <= theta <= 1):
        theta = 1.0

    return (sample_abundance / n) * (
        1 - (lambda_ * exp(-(theta * sample_abundance)))
    )


def gen_detected_adj_model(
    sample_abundance: List[int],
    n: int,
    cov_1: float,
    cov_2: float,
    xixi_1: float,
) -> Callable[[Tuple[float, float]], Tuple[float, float]]:
    def model(params: Tuple[float, float]) -> Tuple[float, float]:
        lambda_, theta = params
        one_bias = (
            sum(
                map(
                    lambda xi: est_detected_rel_abundance(
                        xi, n, theta, lambda_
                    ),
                    sample_abundance,
                )
            )
            - cov_1
        )
        something = sum(
            map(
                lambda xi: est_detected_rel_abundance(xi, n, theta, lambda_)
                ** 2,
                sample_abundance,
            )
        )
        other = cov_2 * ((xixi_1) / (n * (n - 1))) if n > 1 else 0
        two_bias = something - other

        return one_bias, two_bias

    return model


def gen_detected_adj_model_no_doubletons(
    sample_abundance: List[int], n: int, cov_1: float
) -> Callable[[float], float]:
    def model(theta: float) -> float:
        return (
            sum(
                map(
                    lambda xi: est_detected_rel_abundance(xi, n, theta),
                    sample_abundance,
                )
            )
            - cov_1
        )

    return model


def gen_undetected_adj_model(
    n: int,
    cov_deficit_1: float,
    cov_deficit_2: float,
    xixi_1: float,
    num_undetected: int,
) -> Callable[[Tuple[float, float]], Tuple[float, float]]:
    def model(params: Tuple[float, float]) -> Tuple[float, float]:
        alpha, beta = params
        one_bias = (
            sum(alpha * (beta**i) for i in range(1, num_undetected + 1))
            - cov_deficit_1
        )
        something = sum(
            (alpha * (beta**i)) ** 2 for i in range(1, num_undetected + 1)
        )
        other = cov_deficit_2 * ((xixi_1) / (n * (n - 1))) if n > 1 else 0
        two_bias = something - other

        if beta < 0:
            two_bias += 1000

        return one_bias, two_bias

    return model


def gen_undetected_adj_model_no_doubletons(
    n: int, cov_deficit_1: float, num_undetected: int
) -> Callable[[float], float]:
    def model(beta: float) -> float:
        one_bias = (
            sum(beta**i for i in range(1, num_undetected + 1)) - cov_deficit_1
        )

        if beta < 0:
            one_bias += 1000

        return one_bias

    return model


def estimate_multinomial_no_doubletons(
    sample_abundance: List[int],
    s: int,
    n: int,
    num_non_zero_y: int,
    debug: bool = False,
) -> Tuple[List[float], List[float]]:
    assert all(x >= 0 for x in sample_abundance)

    empirical_result: Tuple[List[float], List[float]] = [
        f / n for f in sample_abundance
    ], []
    fvec = Counter(sample_abundance)

    detected_sample_abundance = list(filter(lambda x: x > 0, sample_abundance))
    max_f0 = num_non_zero_y - len(detected_sample_abundance)

    cov_1 = cov_first_order(n, fvec[1], 0)
    if debug:
        print(f"cov_1: {cov_1}")
    if cov_1 == 0:
        if debug:
            print("cov_1 == 0; return empirical_result")
        return empirical_result

    fn_detected = gen_detected_adj_model_no_doubletons(
        sample_abundance, n, cov_1
    )
    [theta] = fsolve(lambda x: fn_detected(x[0]), 0.5, maxfev=10000)
    if debug:
        print(f"theta: {theta}")

    if theta < 0 or theta > 1:
        if debug:
            print("theta not in [0, 1]; theta = 1")
        return empirical_result

    p_detected = list(
        map(
            lambda xi: est_detected_rel_abundance(xi, n, theta)
            if xi != 0
            else 0,
            sample_abundance,
        )
    )
    if debug:
        print(f"p_detected: {p_detected}")

    cov_deficit_1 = cov_deficit_first_order(n, fvec[1], 0)
    f0 = ceil(num_undetected_lower_bound(n, fvec[1], 0))
    f0 = min(f0, max_f0)
    if debug:
        print(f"cov_deficit_1: {cov_deficit_1}, f0: {f0}")

    if f0 == 0:
        if debug:
            print("f0 == 0; return empirical_result")
        return empirical_result

    fn_undetected = gen_undetected_adj_model_no_doubletons(n, cov_deficit_1, f0)
    [beta] = fsolve(
        lambda x: fn_undetected(x[0]), 0.5, maxfev=10000
    )  # fsolve returns a vector of solutions
    if debug:
        print(f"beta: {beta}")

    p_undetected = [beta**i for i in range(1, f0 + 1)]
    if debug:
        print(f"p_undetected: {p_undetected}")
    total_prob = sum(p_detected) + sum(p_undetected)  # shouldn't this be 1?

    return p_detected / total_prob, p_undetected / total_prob


def estimate_multinomial(
    sample_abundance: List[int],
    s: int,
    n: int,
    num_non_zero_y: int,
    debug: bool = False,
) -> Tuple[List[float], List[float]]:
    assert all(x >= 0 for x in sample_abundance)

    empirical_result: Tuple[List[float], List[float]] = [
        f / n for f in sample_abundance
    ], []
    fvec = Counter(sample_abundance)

    detected_sample_abundance = list(filter(lambda x: x > 0, sample_abundance))
    max_f0 = num_non_zero_y - len(detected_sample_abundance)

    if fvec[1] == 0 or len(detected_sample_abundance) == s or max_f0 <= 0:
        if debug:
            if fvec[1] == 0:
                print("No singletons", end="; ")
            elif len(detected_sample_abundance) == s:
                print("All y values detected", end="; ")
            else:
                print("max_f0 <= 0", end="; ")
            print("return empirical_result")
        return empirical_result

    if fvec[2] == 0:
        if debug:
            print("No doubletons")
        return estimate_multinomial_no_doubletons(
            sample_abundance, s, n, num_non_zero_y, debug
        )

    if debug:
        print("fvec[1] != 0 and fvec[2] != 0")

    cov_1 = cov_first_order(n, fvec[1], fvec[2])
    if cov_1 == 0:
        if debug:
            print("cov_1 == 0; return empirical_result")
        return empirical_result
    cov_2 = cov_second_order(n, sample_abundance, fvec[2], fvec[3])
    xixi_1 = summation_xi_xi_minus_1(sample_abundance)
    if debug:
        print(f"cov_1: {cov_1}, cov_2: {cov_2}, xixi_1: {xixi_1}")

    fn_detected = gen_detected_adj_model(
        sample_abundance, n, cov_1, cov_2, xixi_1
    )
    lambda_, theta = fsolve(fn_detected, (0.5, 0.5), maxfev=10000)
    if debug:
        print(f"lambda_: {lambda_}, theta: {theta}")

    if not (0 <= theta <= 1):
        if debug:
            print("theta not in [0, 1]; theta = 1")
        theta = 1

    p_detected = list(
        map(
            lambda xi: est_detected_rel_abundance(xi, n, theta, lambda_)
            if xi != 0
            else 0,
            sample_abundance,
        )
    )
    if debug:
        print(f"p_detected: {p_detected}")

    cov_deficit_1 = cov_deficit_first_order(n, fvec[1], fvec[2])
    cov_deficit_2 = cov_deficit_second_order(
        n, sample_abundance, fvec[2], fvec[3]
    )

    f0 = ceil(num_undetected_lower_bound(n, fvec[1], fvec[2]))
    f0 = min(f0, max_f0)
    if debug:
        print(f"cov_deficit_1: {cov_deficit_1}, cov_deficit_2: {cov_deficit_2}")
        print(f"f0: {f0}")

    if f0 == 0:
        if debug:
            print("f0 == 0; return empirical_result")
        return empirical_result

    fn_undetected = gen_undetected_adj_model(
        n, cov_deficit_1, cov_deficit_2, xixi_1, f0
    )
    alpha, beta = fsolve(fn_undetected, (0.5, 0.5), maxfev=10000)
    if debug:
        print(f"alpha: {alpha}, beta: {beta}")

    p_undetected = [alpha * (beta**i) for i in range(1, f0 + 1)]
    if debug:
        print(f"p_undetected: {p_undetected}")
    total_prob = sum(p_detected) + sum(p_undetected)

    return p_detected / total_prob, p_undetected / total_prob
