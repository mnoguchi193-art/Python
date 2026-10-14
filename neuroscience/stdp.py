"""
Spike-Timing-Dependent Plasticity — Hebbian learning in time

"Neurons that fire together wire together" — but *order matters*. STDP is the
experimentally measured rule for how a synapse changes with the relative timing
of pre- and post-synaptic spikes:

  pre fires BEFORE post (dt > 0)  -> potentiation (LTP): the synapse strengthens
  post fires BEFORE pre (dt < 0)  -> depression  (LTD): the synapse weakens

The effect decays exponentially with the time gap, giving an asymmetric learning
window — the synaptic basis of causal, predictive learning in the brain.
"""

from __future__ import annotations

from math import exp


def stdp_window(dt: float, a_plus: float = 0.10, a_minus: float = 0.12,
                tau_plus: float = 20.0, tau_minus: float = 20.0) -> float:
    """Weight change for a pre/post spike pair, dt = t_post - t_pre (ms)."""
    if dt > 0:
        return a_plus * exp(-dt / tau_plus)
    if dt < 0:
        return -a_minus * exp(dt / tau_minus)
    return 0.0


def total_weight_change(pre_spikes: list[float], post_spikes: list[float]
                        ) -> float:
    """Net change over all pre/post spike pairs (all-to-all STDP)."""
    return sum(stdp_window(post - pre)
               for pre in pre_spikes for post in post_spikes)


if __name__ == "__main__":
    print("STDP learning window (dt = t_post - t_pre):\n")
    print(f"  {'dt (ms)':>8}  {'weight change':>13}")
    for dt in (-40, -20, -10, -5, 5, 10, 20, 40):
        dw = stdp_window(dt)
        bar = ("+" if dw > 0 else "-") * int(abs(dw) * 100)
        print(f"  {dt:>8}  {dw:>+13.4f}  {bar}")
    print("  (positive dt -> LTP/strengthen, negative dt -> LTD/weaken)\n")

    # Causal pairing: the pre-synaptic neuron reliably fires 5 ms before post.
    pre = [10.0, 30.0, 50.0, 70.0]
    post = [15.0, 35.0, 55.0, 75.0]
    print(f"Causal pairing (pre 5 ms before post): "
          f"net Δw = {total_weight_change(pre, post):+.3f}  -> LTP")

    # Anti-causal: post fires before pre.
    print(f"Anti-causal pairing (post before pre):  "
          f"net Δw = {total_weight_change(post, pre):+.3f}  -> LTD")

    print("\nTiming, not mere co-activity, sets the sign of learning — the synapse")
    print("strengthens connections that were predictive of the neuron's firing.")
