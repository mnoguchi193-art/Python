"""
Temporal-Difference Learning — the dopamine reward-prediction error

One of the great bridges between machine learning and the brain. TD learning
predicts future reward by bootstrapping: the TD error

    delta = reward + gamma * V(next) - V(now)

drives the updates. Strikingly, dopamine neurons (Schultz; Montague & Dayan)
carry exactly this signal — and as an animal learns, the burst of activity
*shifts* from the moment of reward to the earliest cue that predicts it, which is
reproduced below.
"""

from __future__ import annotations


def simulate(trials: int = 40, length: int = 7, alpha: float = 0.3,
             gamma: float = 0.95) -> tuple[list[float], list[tuple[int, float, float]]]:
    """Run TD(0) on a cue->...->reward trial. Returns (values, RPE history)."""
    V = [0.0] * (length + 1)        # V[length] is the terminal state (=0)
    history = []
    for trial in range(1, trials + 1):
        V[length] = 0.0
        for t in range(1, length):
            reward = 1.0 if t == length - 1 else 0.0   # reward on the last step
            delta = reward + gamma * V[t + 1] - V[t]
            V[t] += alpha * delta
        cue_rpe = gamma * V[1]                          # prediction error at the cue
        reward_rpe = 1.0 + gamma * V[length] - V[length - 1]
        history.append((trial, cue_rpe, reward_rpe))
    return V, history


if __name__ == "__main__":
    values, history = simulate()

    print("TD learning — the dopamine reward-prediction error shifts to the cue\n")
    print(f"  {'trial':>6}  {'RPE at cue':>11}  {'RPE at reward':>14}")
    for trial, cue, reward in history:
        if trial in (1, 2, 5, 10, 20, 40):
            print(f"  {trial:>6}  {cue:>11.3f}  {reward:>14.3f}")

    print("\n  Early on, the prediction error spikes at REWARD (it's a surprise).")
    print("  After learning, reward is expected (RPE ~ 0) and the error has moved")
    print("  to the CUE that predicts it — exactly what dopamine neurons do.")
