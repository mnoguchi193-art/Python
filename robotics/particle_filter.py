"""
Particle Filter — Monte Carlo localization

Where am I? A Kalman filter assumes a single Gaussian belief; a particle filter
represents belief as a cloud of weighted samples, so it can start completely lost
(global localization) and track multiple hypotheses at once. Each step: move the
particles by the control (with noise), weight them by how well their predicted
sensor reading matches reality, then resample toward the likely ones. The cloud
collapses onto the true location.
"""

from __future__ import annotations

import math
import random


LANDMARKS = [10.0, 35.0, 70.0]      # positions a sensor can range to
WORLD = 100.0


def sense(position: float, noise: float, rng: random.Random) -> float:
    """Noisy distance to the nearest landmark."""
    return min(abs(position - lm) for lm in LANDMARKS) + rng.gauss(0, noise)


def _likelihood(expected: float, measured: float, sigma: float) -> float:
    return math.exp(-((expected - measured) ** 2) / (2 * sigma ** 2))


def localize(steps: int = 12, n: int = 1000, move: float = 5.0,
             sense_noise: float = 2.0, move_noise: float = 1.0, seed: int = 0):
    rng = random.Random(seed)
    particles = [rng.uniform(0, WORLD) for _ in range(n)]    # uniform = "lost"
    true_pos = 8.0
    print(f"  {'step':>4}  {'true':>6}  {'estimate':>9}  {'spread':>7}")
    for step in range(steps):
        true_pos = (true_pos + move) % WORLD
        particles = [(p + move + rng.gauss(0, move_noise)) % WORLD
                     for p in particles]
        measured = sense(true_pos, sense_noise, rng)
        weights = [_likelihood(min(abs(p - lm) for lm in LANDMARKS),
                               measured, sense_noise) + 1e-12 for p in particles]
        particles = rng.choices(particles, weights=weights, k=n)   # resample
        est = sum(particles) / n
        spread = (sum((p - est) ** 2 for p in particles) / n) ** 0.5
        if step % 2 == 0 or step == steps - 1:
            print(f"  {step:>4}  {true_pos:>6.1f}  {est:>9.1f}  {spread:>7.1f}")
    return true_pos, sum(particles) / n


if __name__ == "__main__":
    print("Particle filter (Monte Carlo localization), starting fully lost\n")
    true_pos, est = localize()
    print(f"\n  final: true {true_pos:.1f}, estimate {est:.1f}, "
          f"error {abs(true_pos - est):.1f}")
    print("\n  From a uniform 'I could be anywhere' cloud, repeated sense-and-")
    print("  resample steps converge the particles onto the true position.")
