"""
Difference-in-Differences (DiD) / 差の差分析

When treatment is not randomized but we have before/after data for a treated
and a control group, DiD removes both fixed group differences and common time
trends, under the *parallel trends* assumption.

    DiD = (Y_treat_post - Y_treat_pre) - (Y_control_post - Y_control_pre)
"""

from statistics import mean


def did_from_means(
    treat_pre: float,
    treat_post: float,
    control_pre: float,
    control_post: float,
) -> float:
    """Classic 2x2 DiD from the four group-period means."""
    return (treat_post - treat_pre) - (control_post - control_pre)


def did_from_data(
    outcomes: list[float],
    treated_group: list[int],
    post_period: list[int],
) -> float:
    """DiD computed from unit-level data via the four cell means."""
    cells: dict[tuple[int, int], list[float]] = {
        (0, 0): [], (0, 1): [], (1, 0): [], (1, 1): []
    }
    for y, g, t in zip(outcomes, treated_group, post_period):
        cells[(g, t)].append(y)
    return did_from_means(
        treat_pre=mean(cells[(1, 0)]),
        treat_post=mean(cells[(1, 1)]),
        control_pre=mean(cells[(0, 0)]),
        control_post=mean(cells[(0, 1)]),
    )


if __name__ == "__main__":
    # Card & Krueger style: a minimum-wage rise in the treated state.
    effect = did_from_means(
        treat_pre=20.0, treat_post=21.0,
        control_pre=20.0, control_post=18.0,
    )
    print(f"DiD (from means): {effect:.3f}")

    outcomes = [20, 22, 21, 19, 18, 20, 17, 19]
    treated = [1, 1, 0, 0, 1, 1, 0, 0]
    post = [0, 1, 0, 1, 0, 1, 0, 1]
    print(f"DiD (from data):  {did_from_data(outcomes, treated, post):.3f}")
