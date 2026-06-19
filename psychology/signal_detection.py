"""
Signal Detection Theory — separating sensitivity from bias

A cornerstone of psychophysics, memory, and diagnostics. Raw accuracy confounds
two very different things: how well someone can *discriminate* signal from noise
(sensitivity, d') versus how *willing* they are to say "yes" (response bias, c).

  d' = z(hit rate) - z(false-alarm rate)      -> discriminability
  c  = -0.5 * (z(hit rate) + z(false-alarm rate))  -> bias (>0 conservative)

z() is the inverse standard-normal CDF, available from statistics.NormalDist.
"""

from __future__ import annotations

from statistics import NormalDist


_Z = NormalDist().inv_cdf


def _rate(count: int, total: int) -> float:
    """Proportion with a log-linear correction so z() never sees 0 or 1."""
    return (count + 0.5) / (total + 1)


def sdt(hits: int, misses: int, false_alarms: int, correct_rejections: int
        ) -> dict[str, float]:
    """Compute sensitivity (d'), bias (c) and the underlying rates."""
    hit_rate = _rate(hits, hits + misses)
    fa_rate = _rate(false_alarms, false_alarms + correct_rejections)
    z_hit, z_fa = _Z(hit_rate), _Z(fa_rate)
    return {
        "hit_rate": hit_rate,
        "fa_rate": fa_rate,
        "d_prime": z_hit - z_fa,
        "criterion": -0.5 * (z_hit + z_fa),
        "accuracy": (hits + correct_rejections)
        / (hits + misses + false_alarms + correct_rejections),
    }


if __name__ == "__main__":
    # 100 signal trials and 100 noise trials per observer.
    observers = {
        # A liberal "yes-sayer": many hits, but just as many false alarms.
        "Liberal":      dict(hits=98, misses=2, false_alarms=50, correct_rejections=50),
        # A conservative observer: few hits, but almost no false alarms.
        "Conservative": dict(hits=50, misses=50, false_alarms=2, correct_rejections=98),
    }

    print(f"{'Observer':<13} {'hit%':>5} {'FA%':>5} {'accuracy':>9} "
          f"{'d-prime':>8} {'bias c':>8}")
    for name, counts in observers.items():
        m = sdt(**counts)
        print(f"{name:<13} {m['hit_rate']:>5.0%} {m['fa_rate']:>5.0%} "
              f"{m['accuracy']:>9.0%} {m['d_prime']:>8.2f} {m['criterion']:>+8.2f}")

    print("\nIdentical d' and accuracy, opposite bias: the liberal's far higher")
    print("hit rate is pure response bias (c), not better sensitivity (d').")
