"""
Signal Discovery in Noisy Data (ノイズからの信号発見) — finding exoplanet
transits in a stellar light curve

Kepler and TESS produce millions of light curves; a transiting planet dims
its star by ~0.1-1 % for a few hours.  Nobody can inspect them all, so the
search is automated.  This module generates a noisy light curve with slow
stellar variability, detrends it, then runs a Box Least Squares (BLS)
periodogram: for each trial period the data are phase-folded and the best
box-shaped dip is scored.  The strongest peak gives the orbital period,
duration and depth, from which the planet's radius follows.
"""

from __future__ import annotations
import math
import random
from dataclasses import dataclass


# ── Synthetic light curve ─────────────────────────────────────────────────
@dataclass
class Planet:
    period: float      # days
    epoch: float       # time of first transit centre (days)
    duration: float    # days
    depth: float       # fractional flux drop


def in_transit(t: float, p: Planet) -> bool:
    phase = ((t - p.epoch) / p.period + 0.5) % 1.0 - 0.5     # in [-0.5, 0.5)
    return abs(phase * p.period) < p.duration / 2


def make_light_curve(planet: Planet, days: float, cadence: float, noise: float,
                     rng: random.Random) -> tuple[list[float], list[float]]:
    times = [i * cadence for i in range(int(days / cadence))]
    flux = []
    for t in times:
        f = 1.0 + 0.002 * math.sin(2 * math.pi * t / 6.3)          # starspot modulation
        f -= planet.depth if in_transit(t, planet) else 0.0
        flux.append(f + rng.gauss(0, noise))
    return times, flux


def detrend(flux: list[float], window: int) -> list[float]:
    """Divide by a running median to remove slow stellar variability."""
    half = window // 2
    out = []
    for i in range(len(flux)):
        seg = sorted(flux[max(0, i - half): i + half + 1])
        out.append(flux[i] / seg[len(seg) // 2])
    return out


# ── Box Least Squares periodogram ─────────────────────────────────────────
@dataclass
class BLSResult:
    period: float
    power: float
    phase_start: float
    duration: float
    depth: float


def bls_power(times: list[float], flux: list[float], period: float,
              n_bins: int = 200, max_width: int = 16) -> BLSResult:
    """Fold at `period`, bin, and find the box that best explains the dip."""
    sums = [0.0] * n_bins
    counts = [0] * n_bins
    for t, f in zip(times, flux):
        b = int(((t / period) % 1.0) * n_bins)
        sums[b] += f
        counts[b] += 1
    n = len(flux)
    mean = sum(sums) / n
    r = [c / n for c in counts]                   # fraction of points per bin
    s = [si - mean * c for si, c in zip(sums, counts)]   # mean-subtracted sum
    best = BLSResult(period, 0.0, 0.0, 0.0, 0.0)
    for start in range(n_bins):
        rs = ss = 0.0
        for width in range(1, max_width + 1):
            b = (start + width - 1) % n_bins
            rs += r[b]
            ss += s[b]
            if ss < 0 and 0 < rs < 1:
                power = ss * ss / (rs * (1 - rs))
                if power > best.power:
                    depth = -ss / (n * rs * (1 - rs))
                    best = BLSResult(period, power, start / n_bins,
                                     width / n_bins * period, depth)
    return best


def bls_search(times: list[float], flux: list[float], p_min: float, p_max: float,
               n_periods: int) -> list[BLSResult]:
    ratio = p_max / p_min
    periods = [p_min * ratio ** (i / (n_periods - 1)) for i in range(n_periods)]
    return sorted((bls_power(times, flux, p) for p in periods),
                  key=lambda r: r.power, reverse=True)


def phase_plot(times: list[float], flux: list[float], best: BLSResult,
               n_bins: int = 24) -> None:
    """Text plot of the phase-folded curve, centred on the detected dip."""
    centre = best.phase_start + best.duration / (2 * best.period)
    sums, counts = [0.0] * n_bins, [0] * n_bins
    for t, f in zip(times, flux):
        phase = ((t / best.period) - centre + 0.5) % 1.0      # dip at 0.5
        b = int(phase * n_bins)
        sums[b] += f
        counts[b] += 1
    means = [s / c for s, c in zip(sums, counts)]
    lo, hi = min(means), max(means)
    for i, m in enumerate(means):
        bar = "#" * int(40 * (m - lo) / (hi - lo + 1e-12))
        print(f"  phase {(i + 0.5) / n_bins - 0.5:+.2f} | {bar:<40} {m:.4f}")


# ── Demo ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    rng = random.Random(2024)
    truth = Planet(period=3.71, epoch=1.3, duration=0.12, depth=0.004)
    times, raw = make_light_curve(truth, days=30.0, cadence=0.015, noise=0.0015, rng=rng)
    flux = detrend(raw, window=67)             # ~1 day window
    print(f"Light curve: {len(times)} points over 30 days, noise {0.0015:.2%} per point,"
          f" transit depth {truth.depth:.1%}")

    results = bls_search(times, flux, p_min=1.0, p_max=12.0, n_periods=600)
    best = results[0]
    print("\nTop BLS peaks:")
    for r in results[:3]:
        print(f"  P={r.period:6.3f} d  power={r.power * 1e3:7.3f}  depth={r.depth:.4f}")

    star_radius_earths = 109.0                 # Sun-like host star
    radius = math.sqrt(best.depth) * star_radius_earths
    print(f"\nDetected: period {best.period:.3f} d (truth {truth.period}),"
          f" duration {best.duration * 24:.1f} h (truth {truth.duration * 24:.1f}),"
          f" depth {best.depth:.4f} (truth {truth.depth})")
    print(f"Planet radius ~ sqrt(depth) * R_star = {radius:.1f} Earth radii")

    print("\nPhase-folded light curve at the detected period:")
    phase_plot(times, flux, best)
