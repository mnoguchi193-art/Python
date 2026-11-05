"""
Automated Peer Review (自動査読) — screening a claimed result for validity

Before an AI Scientist reports a discovery it should critique itself the
way a referee would.  Given a controlled experiment (control vs treatment),
this reviewer checks the claim "the treatment has an effect" against four
criteria:

  * significance — a permutation test p-value (no distributional assumptions),
  * effect size  — Cohen's d (is the effect large enough to matter?),
  * power        — is the sample big enough to trust a null result?
  * robustness   — does the verdict survive dropping the most extreme point?

It then returns an accept / reject / inconclusive verdict with reasons,
catching both "significant but trivial" and "promising but underpowered"
results.
"""

from __future__ import annotations
import math
import random
import statistics

Vector = list[float]


# ── Statistics ────────────────────────────────────────────────────────────
def mean_diff(a: Vector, b: Vector) -> float:
    return statistics.mean(b) - statistics.mean(a)


def cohens_d(a: Vector, b: Vector) -> float:
    na, nb = len(a), len(b)
    va, vb = statistics.variance(a), statistics.variance(b)
    pooled = math.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2))
    return (statistics.mean(b) - statistics.mean(a)) / pooled if pooled else 0.0


def permutation_p(a: Vector, b: Vector, iters: int, rng: random.Random) -> float:
    """Two-sided p-value for a difference in means via label shuffling."""
    observed = abs(mean_diff(a, b))
    pool = a + b
    na = len(a)
    hits = 0
    for _ in range(iters):
        rng.shuffle(pool)
        if abs(statistics.mean(pool[na:]) - statistics.mean(pool[:na])) >= observed:
            hits += 1
    return (hits + 1) / (iters + 1)


# ── Reviewer ──────────────────────────────────────────────────────────────
def review(control: Vector, treatment: Vector, rng: random.Random,
           alpha: float = 0.05, min_d: float = 0.5, min_n: int = 20,
           iters: int = 2000) -> dict:
    p = permutation_p(control, treatment, iters, rng)
    d = cohens_d(control, treatment)
    n = min(len(control), len(treatment))

    # Robustness: drop the treatment point farthest from its mean, re-test.
    m = statistics.mean(treatment)
    trimmed = sorted(treatment, key=lambda v: abs(v - m))[:-1]
    p_robust = permutation_p(control, trimmed, iters, rng)

    significant = p < alpha
    meaningful = abs(d) >= min_d
    powered = n >= min_n
    robust = (p_robust < alpha) == significant

    notes = []
    if not significant:
        notes.append(f"not significant (p={p:.3f})")
    if significant and not meaningful:
        notes.append(f"significant but tiny effect (d={d:.2f})")
    if not powered:
        notes.append(f"underpowered (n={n} < {min_n})")
    if not robust:
        notes.append("verdict flips when one outlier is removed")

    if significant and meaningful and powered and robust:
        verdict = "ACCEPT"
    elif not significant and powered:
        verdict = "REJECT (well-powered null)"
    else:
        verdict = "INCONCLUSIVE"
    return {"verdict": verdict, "p": p, "d": d, "n": n,
            "p_robust": p_robust, "notes": notes}


def report(label: str, control: Vector, treatment: Vector, rng: random.Random) -> None:
    r = review(control, treatment, rng)
    print(f"{label}")
    print(f"  p={r['p']:.3f}  Cohen's d={r['d']:+.2f}  n={r['n']}  "
          f"(p after trim={r['p_robust']:.3f})")
    print(f"  -> {r['verdict']}" + (f"  [{'; '.join(r['notes'])}]" if r['notes'] else ""))
    print()


# ── Demo ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Automated reviewer screening four claimed findings")
    print("(each with its own data and an independent permutation test):\n")

    def dataset(mu: float, n: int, seed: int) -> Vector:
        g = random.Random(seed)
        return [g.gauss(mu, 1.0) for _ in range(n)]

    report("1. Real, large effect (mu: 0.0 vs 0.9, n=40):",
           dataset(0.0, 40, 0), dataset(0.9, 40, 1), random.Random(101))

    report("2. No effect, well powered (mu: 0.0 vs 0.0, n=40):",
           dataset(0.0, 40, 20), dataset(0.0, 40, 21), random.Random(102))

    report("3. Significant but trivial effect (mu: 0.0 vs 0.3, n=200):",
           dataset(0.0, 200, 40), dataset(0.3, 200, 41), random.Random(103))

    report("4. Underpowered hint (mu: 0.0 vs 0.8, n=6):",
           dataset(0.0, 6, 62), dataset(0.8, 6, 63), random.Random(104))

    print("The reviewer accepts only claim 1: significant, sizeable, adequately")
    print("powered, and robust. Claim 3 is significant yet too small to matter;")
    print("claim 4 looks strong but has too little data to trust.")
