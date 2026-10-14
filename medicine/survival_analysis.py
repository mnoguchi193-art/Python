"""
Survival Analysis — the Kaplan-Meier estimator

The standard tool for clinical trials and prognosis: estimating the probability
of surviving past time t when some patients are *censored* (they leave the study
or it ends before the event occurs). Censoring is what makes ordinary averages
wrong and survival analysis necessary.

An observation is (time, event): event = 1 if the event (e.g. death) was
observed, 0 if the patient was censored.
"""

from __future__ import annotations


Observation = tuple[float, int]


def kaplan_meier(observations: list[Observation]) -> list[tuple[float, float]]:
    """Return the survival curve as (time, S(t)) step points."""
    event_times = sorted({t for t, e in observations if e == 1})
    curve = [(0.0, 1.0)]
    survival = 1.0
    for t in event_times:
        at_risk = sum(1 for ti, _ in observations if ti >= t)
        deaths = sum(1 for ti, e in observations if ti == t and e == 1)
        survival *= 1 - deaths / at_risk
        curve.append((t, survival))
    return curve


def survival_at(curve: list[tuple[float, float]], t: float) -> float:
    """Estimated survival probability at time t (last step at or before t)."""
    s = 1.0
    for time, prob in curve:
        if time <= t:
            s = prob
        else:
            break
    return s


def median_survival(curve: list[tuple[float, float]]) -> float | None:
    """First time at which survival drops to 0.5 or below (None if it never does)."""
    for time, prob in curve:
        if prob <= 0.5:
            return time
    return None


if __name__ == "__main__":
    # Months of follow-up; '+' in comments marks censored patients.
    treatment = [(6, 1), (7, 1), (10, 0), (15, 1), (16, 0), (22, 1),
                 (28, 0), (30, 1), (32, 0), (36, 1)]
    control = [(3, 1), (4, 1), (5, 1), (8, 1), (9, 0), (11, 1),
               (12, 1), (14, 0), (18, 1), (20, 1)]

    for name, data in (("Treatment", treatment), ("Control", control)):
        curve = kaplan_meier(data)
        median = median_survival(curve)
        print(f"{name} group:")
        print(f"  median survival      : "
              f"{f'{median:.0f} months' if median else 'not reached'}")
        print(f"  survival at 12 months: {survival_at(curve, 12):.0%}")
        print(f"  survival at 24 months: {survival_at(curve, 24):.0%}\n")

    print("Censored patients still contribute 'at-risk' time before dropout —"
          "\nthat is the key correction Kaplan-Meier makes over a naive average.")
