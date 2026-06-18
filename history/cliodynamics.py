"""
Cliodynamics — the mathematical history of "secular cycles"

Cliodynamics (Peter Turchin) treats history quantitatively: empires and dynasties
rise and fall in recurring multi-century waves. A simplified demographic-
structural model couples population to sociopolitical instability, much like a
predator-prey system — population grows in peace, but crowding breeds instability
(elite competition, famine, warfare), which then cuts the population back:

    dN/dt = r N (1 - N/k) - c N W      population: logistic growth minus strife
    dW/dt = a N W - m W                instability: feeds on a dense population

The result is endogenous secular cycles — no external shock required.
"""

from __future__ import annotations


def simulate(n0: float = 0.4, w0: float = 0.06, r: float = 0.03, k: float = 30.0,
             c: float = 0.5, a: float = 0.05, m: float = 0.04,
             years: float = 800, dt: float = 0.2
             ) -> list[tuple[float, float, float]]:
    """Euler-integrate the model. Returns (year, population, instability).

    Weak density dependence (large k) keeps the predator-prey oscillation
    sustained, so several secular cycles play out rather than damping away.
    """
    n, w = n0, w0
    history = [(0.0, n, w)]
    for step in range(1, int(years / dt) + 1):
        dn = r * n * (1 - n / k) - c * n * w
        dw = a * n * w - m * w
        n = max(0.0, n + dn * dt)
        w = max(0.0, w + dw * dt)
        history.append((step * dt, n, w))
    return history


def peaks(series: list[float], gap: int = 50) -> list[int]:
    """Indices of local maxima (used to detect successive cycle crests)."""
    found = []
    for i in range(1, len(series) - 1):
        if series[i] > series[i - 1] and series[i] >= series[i + 1]:
            if not found or i - found[-1] >= gap:
                found.append(i)
    return found


def sparkline(values: list[float]) -> str:
    blocks = " .:-=+*#%@"
    hi = max(values) or 1.0
    return "".join(blocks[min(len(blocks) - 1, int(v / hi * (len(blocks) - 1)))]
                   for v in values)


if __name__ == "__main__":
    history = simulate()
    times = [t for t, _, _ in history]
    pop = [n for _, n, _ in history]
    war = [w for _, _, w in history]

    crest_idx = peaks(pop)
    crest_years = [round(times[i]) for i in crest_idx]
    periods = [crest_years[i + 1] - crest_years[i]
               for i in range(len(crest_years) - 1)]

    print("Cliodynamics — demographic-structural secular cycles\n")
    print(f"  population crests at years: {crest_years}")
    if periods:
        print(f"  mean cycle length: {sum(periods) / len(periods):.0f} years")
    print(f"  peak population: {max(pop):.2f}\n")

    # Sample ~100 points for a compact chart.
    sample = max(1, len(history) // 100)
    print("  population : " + sparkline(pop[::sample]))
    print("  instability: " + sparkline(war[::sample]))
    print("\nInstability lags population: crowding breeds strife, strife thins")
    print("the population, and the cycle begins again — the rhythm of history.")
