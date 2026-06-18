"""
Information Theory — measuring information itself (Shannon, 1948)

The mathematical foundation of the digital age. Entropy quantifies uncertainty
(the irreducible bits needed to describe a source); KL divergence measures how
one distribution differs from another; mutual information measures how much one
variable tells you about another; and channel capacity sets the hard limit on
reliable communication over a noisy line.
"""

from __future__ import annotations

from math import log2


def entropy(probs: list[float]) -> float:
    """Shannon entropy H(X) in bits."""
    return -sum(p * log2(p) for p in probs if p > 0) + 0.0   # normalize -0.0


def kl_divergence(p: list[float], q: list[float]) -> float:
    """Relative entropy D(p||q): the cost in bits of assuming q when truth is p."""
    return sum(pi * log2(pi / qi) for pi, qi in zip(p, q) if pi > 0)


def mutual_information(joint: dict[tuple[str, str], float]) -> float:
    """I(X;Y) from a joint distribution over (x, y) pairs."""
    px: dict[str, float] = {}
    py: dict[str, float] = {}
    for (x, y), p in joint.items():
        px[x] = px.get(x, 0.0) + p
        py[y] = py.get(y, 0.0) + p
    return sum(p * log2(p / (px[x] * py[y]))
               for (x, y), p in joint.items() if p > 0)


def bsc_capacity(crossover: float) -> float:
    """Capacity of a binary symmetric channel with bit-flip probability p."""
    return 1.0 - entropy([crossover, 1 - crossover])


if __name__ == "__main__":
    print("Entropy of a single bit source:")
    for label, dist in [("fair coin", [0.5, 0.5]),
                        ("biased 90/10", [0.9, 0.1]),
                        ("certain", [1.0, 0.0])]:
        print(f"  {label:<14} H = {entropy(dist):.3f} bits")

    print("\nNoisy channel capacity (binary symmetric channel):")
    for p in (0.0, 0.01, 0.1, 0.5):
        print(f"  bit-flip p={p:<4} capacity = {bsc_capacity(p):.3f} bits/use")

    print("\nKL divergence is asymmetric:")
    p, q = [0.5, 0.5], [0.9, 0.1]
    print(f"  D(p||q) = {kl_divergence(p, q):.3f}   "
          f"D(q||p) = {kl_divergence(q, p):.3f}")

    print("\nMutual information:")
    correlated = {("0", "0"): 0.45, ("0", "1"): 0.05,
                  ("1", "0"): 0.05, ("1", "1"): 0.45}
    independent = {("0", "0"): 0.25, ("0", "1"): 0.25,
                   ("1", "0"): 0.25, ("1", "1"): 0.25}
    print(f"  correlated variables : I(X;Y) = {mutual_information(correlated):.3f} bits")
    print(f"  independent variables: I(X;Y) = {mutual_information(independent):.3f} bits")
