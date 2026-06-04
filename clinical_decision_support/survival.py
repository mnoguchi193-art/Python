"""
Survival analysis — Kaplan-Meier estimator / 生存時間解析(カプラン・マイヤー法)

Prognosis prediction often asks "what fraction of patients survive past time
t?" when some patients are censored (lost to follow-up before the event). The
Kaplan-Meier estimator handles censoring by updating survival only at observed
event times:

    S(t) = product over event times t_i <= t of (1 - d_i / n_i)

where d_i is events at t_i and n_i is the number still at risk.
"""

from dataclasses import dataclass


@dataclass
class KaplanMeier:
    times: list[float]   # observed time for each subject
    events: list[int]    # 1 = event occurred, 0 = censored

    def survival_function(self) -> list[tuple[float, float]]:
        """Return (time, survival probability) at each distinct event time."""
        n = len(self.times)
        order = sorted(range(n), key=lambda i: self.times[i])
        curve = [(0.0, 1.0)]
        survival = 1.0
        at_risk = n
        i = 0
        sorted_times = [self.times[k] for k in order]
        sorted_events = [self.events[k] for k in order]
        while i < n:
            t = sorted_times[i]
            # Count events and total subjects sharing this time.
            deaths = tied = 0
            while i < n and sorted_times[i] == t:
                deaths += sorted_events[i]
                tied += 1
                i += 1
            if deaths:
                survival *= 1 - deaths / at_risk
                curve.append((t, survival))
            at_risk -= tied
        return curve

    def survival_at(self, t: float) -> float:
        """Survival probability at time t (step function)."""
        prob = 1.0
        for time, survival in self.survival_function():
            if time <= t:
                prob = survival
            else:
                break
        return prob

    def median_survival(self) -> float | None:
        """Earliest time at which survival drops to 0.5 or below."""
        for time, survival in self.survival_function():
            if survival <= 0.5:
                return time
        return None  # not reached within follow-up


if __name__ == "__main__":
    # times in months; 1 = death observed, 0 = censored.
    km = KaplanMeier(
        times=[2, 3, 5, 6, 6, 8, 10, 12, 14, 18],
        events=[1, 1, 0, 1, 1, 0, 1, 1, 0, 1],
    )
    print("Kaplan-Meier survival curve:")
    for t, s in km.survival_function():
        print(f"  t={t:5.1f}  S(t)={s:.3f}")
    print(f"Survival at t=6:  {km.survival_at(6):.3f}")
    median = km.median_survival()
    print(f"Median survival:  {median} months")
