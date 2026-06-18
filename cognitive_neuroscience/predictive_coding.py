"""
Predictive Coding — perception as hierarchical inference

The leading theory of cortical computation (Rao & Ballard; Friston's free-energy
principle): the brain is a prediction machine. Higher levels predict the activity
of lower levels, only the *prediction error* travels upward, and the network
settles by minimizing error across the hierarchy. Crucially, errors are weighted
by their *precision* (reliability) — when the senses are unreliable, prior
expectations dominate, which is exactly how perceptual illusions arise.

Here a two-level model infers the hidden causes (x1, x2) of a sensory input.
"""

from __future__ import annotations


def infer(sensory: float, prior: float, pi0: float = 1.0, pi1: float = 1.0,
          pi2: float = 1.0, lr: float = 0.05, iters: int = 300
          ) -> tuple[float, float, list[float]]:
    """Gradient descent on the free energy (sum of precision-weighted errors).

    Returns (level-1 estimate, level-2 estimate, total-error history).
    """
    x1 = x2 = 0.0
    history = []
    for _ in range(iters):
        e0 = sensory - x1          # sensory prediction error
        e1 = x1 - x2               # level-1 prediction error
        e2 = x2 - prior            # top-down prior error
        x1 += lr * (pi0 * e0 - pi1 * e1)
        x2 += lr * (pi1 * e1 - pi2 * e2)
        history.append(pi0 * e0 ** 2 + pi1 * e1 ** 2 + pi2 * e2 ** 2)
    return x1, x2, history


if __name__ == "__main__":
    sensory, prior = 4.0, 0.0

    print("Predictive coding — inferring the cause of a sensory input\n")
    print(f"  sensory input = {sensory},  prior expectation = {prior}\n")

    # Reliable senses: high sensory precision -> perception follows the input.
    x1, x2, hist = infer(sensory, prior, pi0=8.0, pi1=1.0, pi2=1.0)
    print("Reliable senses (high sensory precision):")
    print(f"  inferred percept x1 = {x1:.2f}  (tracks the sensory input)")
    print(f"  total prediction error: {hist[0]:.2f} -> {hist[-1]:.4f}\n")

    # Unreliable senses: low sensory precision -> the prior pulls perception down.
    x1, x2, hist = infer(sensory, prior, pi0=0.3, pi1=1.0, pi2=2.0)
    print("Unreliable senses (low sensory precision):")
    print(f"  inferred percept x1 = {x1:.2f}  (pulled toward the prior)")
    print("  => precision-weighting: weak evidence lets expectations win,")
    print("     the computational signature of a perceptual illusion.")
