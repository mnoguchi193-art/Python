"""
Epidemic Modeling — the SIR compartmental model

The mathematical backbone of modern epidemiology (and of COVID-19 forecasting).
A population flows through three compartments:

  S (susceptible) -> I (infectious) -> R (recovered/removed)

with transmission rate beta and recovery rate gamma. The basic reproduction
number R0 = beta / gamma decides everything: if R0 > 1 an epidemic takes off,
and herd immunity is reached once a fraction 1 - 1/R0 is immune.

Integrated with simple Euler steps — standard library only.
"""

from __future__ import annotations


def simulate(n: int, i0: int, beta: float, gamma: float,
             days: float = 160, dt: float = 0.1) -> list[tuple[float, float, float, float]]:
    """Return the (day, S, I, R) trajectory of an SIR epidemic."""
    s, i, r = n - i0, float(i0), 0.0
    history = [(0.0, s, i, r)]
    for step in range(1, int(days / dt) + 1):
        new_infections = beta * s * i / n
        new_recoveries = gamma * i
        s -= new_infections * dt
        i += (new_infections - new_recoveries) * dt
        r += new_recoveries * dt
        history.append((step * dt, s, i, r))
    return history


def peak(history) -> tuple[float, float]:
    """(day, count) of peak infections."""
    day, _, infected, _ = max(history, key=lambda row: row[2])
    return day, infected


def sparkline(values: list[float]) -> str:
    blocks = " .:-=+*#%@"
    hi = max(values) or 1.0
    return "".join(blocks[min(len(blocks) - 1, int(v / hi * (len(blocks) - 1)))]
                   for v in values)


if __name__ == "__main__":
    N, I0 = 1_000_000, 10
    beta, gamma = 0.4, 0.1          # mean infectious period = 1/gamma = 10 days
    r0 = beta / gamma

    history = simulate(N, I0, beta, gamma)
    peak_day, peak_inf = peak(history)
    attack_rate = history[-1][3] / N      # fraction ever infected

    print(f"SIR epidemic  (N={N:,}, beta={beta}, gamma={gamma})\n")
    print(f"  R0 (basic reproduction number) : {r0:.1f}")
    print(f"  Herd immunity threshold        : {1 - 1 / r0:.1%}")
    print(f"  Peak infections                : {peak_inf:,.0f} on day {peak_day:.0f}")
    print(f"  Final attack rate              : {attack_rate:.1%} of population")

    # Sample the infectious curve once per ~10 days for a compact chart.
    sampled = [row[2] for row in history[::100]]
    print(f"\n  Infectious over time:\n  {sparkline(sampled)}")
