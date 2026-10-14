"""
Leaky Integrate-and-Fire Neuron — the workhorse of computational neuroscience

A neuron's membrane is a leaky capacitor: input current charges it, leak drains
it, and when the voltage crosses a threshold the neuron fires a spike and resets.
Despite its simplicity the LIF model reproduces the central input-output law of
real neurons — the f-I curve relating injected current to firing rate, with a
rheobase (the minimum current to fire at all) and a refractory ceiling.

    tau_m * dV/dt = -(V - V_rest) + R * I
"""

from __future__ import annotations


def simulate(current: float, t_total: float = 1000.0, dt: float = 0.1,
             tau_m: float = 10.0, v_rest: float = -65.0, v_th: float = -50.0,
             v_reset: float = -70.0, r_m: float = 10.0, refractory: float = 2.0
             ) -> tuple[list[float], list[float]]:
    """Run the LIF model. Returns (voltage trace, spike times) in mV and ms."""
    v = v_rest
    trace, spikes = [v], []
    ref_until = -1e9
    for step in range(1, int(t_total / dt) + 1):
        t = step * dt
        if t < ref_until:
            v = v_reset
        else:
            v += (-(v - v_rest) + r_m * current) / tau_m * dt
            if v >= v_th:
                spikes.append(t)
                v = v_reset
                ref_until = t + refractory
        trace.append(v)
    return trace, spikes


def firing_rate(current: float, **kw) -> float:
    """Mean firing rate in Hz for a constant input current (nA)."""
    t_total = kw.get("t_total", 1000.0)
    _, spikes = simulate(current, **kw)
    return len(spikes) / (t_total / 1000.0)


if __name__ == "__main__":
    print("Leaky Integrate-and-Fire neuron — f-I curve\n")
    print(f"  {'current (nA)':>12}  {'firing rate (Hz)':>16}")
    for current in (0.5, 1.0, 1.5, 2.0, 3.0, 5.0):
        print(f"  {current:>12.1f}  {firing_rate(current):>16.0f}")

    # Rheobase: R*I must lift V_rest (-65) to threshold (-50) => I = 15/R = 1.5 nA.
    print("\n  Below ~1.5 nA the cell never reaches threshold (rheobase); above")
    print("  it, rate rises with current but is capped by the refractory period.")

    trace, spikes = simulate(2.0, t_total=100.0)
    blocks = " .:-=+*#%@"
    lo, hi = min(trace), max(trace)
    step = max(1, len(trace) // 80)
    chart = "".join(blocks[min(8, int((v - lo) / (hi - lo) * 8))]
                    for v in trace[::step])
    print(f"\n  Membrane potential at I = 2.0 nA ({len(spikes)} spikes):\n  {chart}")
