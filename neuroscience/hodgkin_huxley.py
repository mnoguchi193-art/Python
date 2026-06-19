"""
The Hodgkin-Huxley Model — the biophysics of an action potential

The Nobel-winning (1963) model of how a neuron fires. Unlike the simplified
leaky integrate-and-fire model, Hodgkin and Huxley described the *mechanism*:
voltage-gated sodium and potassium channels, whose opening and closing (gating
variables m, h, n) produce the sharp spike and its recovery. Injecting current
above threshold makes the membrane fire repetitively — reproduced here by
integrating the original 1952 equations.
"""

from __future__ import annotations

import math


# Membrane capacitance, conductances (mS/cm^2) and reversal potentials (mV).
CM, GNA, GK, GL = 1.0, 120.0, 36.0, 0.3
ENA, EK, EL = 50.0, -77.0, -54.4


def _alpha_m(v): return 1.0 if abs(v + 40) < 1e-6 else 0.1 * (v + 40) / (1 - math.exp(-(v + 40) / 10))
def _beta_m(v): return 4.0 * math.exp(-(v + 65) / 18)
def _alpha_h(v): return 0.07 * math.exp(-(v + 65) / 20)
def _beta_h(v): return 1.0 / (1 + math.exp(-(v + 35) / 10))
def _alpha_n(v): return 0.1 if abs(v + 55) < 1e-6 else 0.01 * (v + 55) / (1 - math.exp(-(v + 55) / 10))
def _beta_n(v): return 0.125 * math.exp(-(v + 65) / 80)


def simulate(current: float, t_end: float = 50.0, dt: float = 0.01
             ) -> tuple[list[float], int]:
    """Integrate the HH equations under injected current. Returns (V trace, spikes)."""
    v, m, h, n = -65.0, 0.05, 0.6, 0.32
    trace, spikes, above = [v], 0, False
    for _ in range(int(t_end / dt)):
        i_na = GNA * m ** 3 * h * (v - ENA)
        i_k = GK * n ** 4 * (v - EK)
        i_l = GL * (v - EL)
        v += dt * (current - i_na - i_k - i_l) / CM
        m += dt * (_alpha_m(v) * (1 - m) - _beta_m(v) * m)
        h += dt * (_alpha_h(v) * (1 - h) - _beta_h(v) * h)
        n += dt * (_alpha_n(v) * (1 - n) - _beta_n(v) * n)
        if v > 0 and not above:        # upward zero-crossing = a spike
            spikes += 1
            above = True
        elif v < 0:
            above = False
        trace.append(v)
    return trace, spikes


if __name__ == "__main__":
    print("Hodgkin-Huxley neuron — injected current vs firing\n")
    print(f"  {'current (uA/cm^2)':>17}  {'spikes / 50 ms':>14}  {'rate (Hz)':>9}")
    for current in (2, 5, 10, 20, 40):
        _, spikes = simulate(current)
        print(f"  {current:>17}  {spikes:>14}  {spikes / 0.05:>9.0f}")

    trace, spikes = simulate(10)
    peak = max(trace)
    print(f"\n  At 10 uA/cm^2: {spikes} action potentials, peak {peak:.0f} mV "
          f"(rest -65 mV)")

    blocks = " .:-=+*#%@"
    lo, hi = min(trace), max(trace)
    step = max(1, len(trace) // 78)
    chart = "".join(blocks[min(8, int((v - lo) / (hi - lo) * 8))]
                    for v in trace[::step])
    print(f"\n  Membrane potential (spike train):\n  {chart}")
    print("\n  The Na+/K+ channel dance turns a steady input into discrete spikes.")
