"""
Privacy — differential privacy & k-anonymity / プライバシー保護

Health data is highly sensitive. Two foundational techniques:

  * differential privacy — add calibrated Laplace noise so that any single
    patient's presence barely changes a query's output (privacy budget eps).
  * k-anonymity — ensure every combination of quasi-identifiers is shared by
    at least k records, so individuals cannot be singled out.

Standard library only.
"""

import math
import random
from collections import Counter


def _laplace(scale: float, rng: random.Random) -> float:
    """Sample Laplace(0, scale) via inverse CDF."""
    u = rng.random() - 0.5
    return -scale * math.copysign(1.0, u) * math.log(1 - 2 * abs(u))


def private_count(
    true_count: int, epsilon: float, sensitivity: float = 1.0,
    rng: random.Random | None = None,
) -> float:
    """Differentially private count: add Laplace(sensitivity / epsilon)."""
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")
    rng = rng or random.Random()
    return true_count + _laplace(sensitivity / epsilon, rng)


def private_mean(
    values: list[float], lower: float, upper: float, epsilon: float,
    rng: random.Random | None = None,
) -> float:
    """DP mean of bounded values; sensitivity of the sum is (upper - lower)."""
    rng = rng or random.Random()
    n = len(values)
    noisy_sum = sum(values) + _laplace((upper - lower) / epsilon, rng)
    return noisy_sum / n


def k_anonymity(records: list[dict], quasi_identifiers: list[str]) -> int:
    """Return the smallest equivalence-class size (the dataset's k)."""
    groups = Counter(
        tuple(rec[q] for q in quasi_identifiers) for rec in records
    )
    return min(groups.values())


def is_k_anonymous(records: list[dict], quasi_identifiers: list[str], k: int) -> bool:
    return k_anonymity(records, quasi_identifiers) >= k


if __name__ == "__main__":
    rng = random.Random(1)
    true = 100
    print("Differentially private counts (true = 100):")
    for eps in [0.1, 1.0, 10.0]:
        noisy = private_count(true, epsilon=eps, rng=rng)
        print(f"  eps={eps:4.1f} -> {noisy:7.2f}  (smaller eps = more privacy/noise)")

    records = [
        {"age_band": "30-39", "zip3": "100", "dx": "flu"},
        {"age_band": "30-39", "zip3": "100", "dx": "cold"},
        {"age_band": "40-49", "zip3": "200", "dx": "flu"},
        {"age_band": "40-49", "zip3": "200", "dx": "asthma"},
    ]
    print(f"\nDataset k-anonymity: k = {k_anonymity(records, ['age_band', 'zip3'])}")
    print(f"Is 2-anonymous: {is_k_anonymous(records, ['age_band', 'zip3'], 2)}")
