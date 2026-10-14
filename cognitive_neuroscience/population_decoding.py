"""
Population Decoding — reading a stimulus out of many noisy neurons

Single neurons are broadly tuned and noisy, yet the brain represents quantities
(movement direction, orientation) precisely by pooling across a *population*.
Georgopoulos's population-vector method decodes the encoded direction as the
vector sum of each neuron's preferred direction weighted by its firing rate —
the conceptual foundation of motor brain-computer interfaces.
"""

from __future__ import annotations

import math
import random


def tuning_rate(theta: float, preferred: float,
                baseline: float = 5.0, gain: float = 20.0) -> float:
    """Cosine tuning curve: peak firing when the stimulus matches preference."""
    return baseline + gain * max(0.0, math.cos(theta - preferred))


def population_vector(rates: list[float], preferred: list[float]) -> float:
    """Decode the stimulus angle as the population vector's direction."""
    x = sum(r * math.cos(p) for r, p in zip(rates, preferred))
    y = sum(r * math.sin(p) for r, p in zip(rates, preferred))
    return math.atan2(y, x)


def angular_error_deg(decoded: float, true: float) -> float:
    diff = (decoded - true + math.pi) % (2 * math.pi) - math.pi
    return abs(math.degrees(diff))


def decode_once(n_neurons: int, true_theta: float, rng: random.Random) -> float:
    preferred = [2 * math.pi * i / n_neurons for i in range(n_neurons)]
    rates = []
    for p in preferred:
        mu = tuning_rate(true_theta, p)
        rates.append(max(0.0, rng.gauss(mu, math.sqrt(mu))))  # Poisson-like noise
    return population_vector(rates, preferred)


if __name__ == "__main__":
    rng = random.Random(1)
    true_theta = math.radians(40)

    print("Population vector decoding (true direction = 40 deg)\n")
    decoded = decode_once(8, true_theta, rng)
    print(f"  8 noisy neurons -> decoded {math.degrees(decoded):.1f} deg "
          f"(error {angular_error_deg(decoded, true_theta):.1f} deg)\n")

    print("  Decoding error shrinks as the population grows:")
    print(f"  {'neurons':>8}  {'mean error (deg)':>16}")
    for n in (4, 8, 16, 32, 64):
        errors = [angular_error_deg(decode_once(n, true_theta, rng), true_theta)
                  for _ in range(400)]
        print(f"  {n:>8}  {sum(errors) / len(errors):>16.2f}")

    print("\nNo single neuron is precise, but the population code is — robust,")
    print("distributed representation is how the brain (and a BCI) reads intent.")
