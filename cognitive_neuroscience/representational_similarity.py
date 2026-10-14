"""
Representational Similarity Analysis (RSA) — comparing what systems represent

A method (Kriegeskorte, 2008) that links brains, behavior and models without
mapping neurons one-to-one. For each system, build a Representational
Dissimilarity Matrix (RDM): how different is the activity pattern for every pair
of stimuli? Two systems "represent alike" if their RDMs are correlated — so we
can ask whether a model's internal geometry matches a brain region's, even when
their raw units are nothing alike.
"""

from __future__ import annotations

from itertools import combinations


def _pearson(a: list[float], b: list[float]) -> float:
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a) ** 0.5
    vb = sum((y - mb) ** 2 for y in b) ** 0.5
    return cov / (va * vb) if va and vb else 0.0


def rdm(patterns: dict[str, list[float]]) -> tuple[list[str], list[float]]:
    """Representational dissimilarity (1 - correlation) for each stimulus pair."""
    names = list(patterns)
    dissim = [1 - _pearson(patterns[a], patterns[b])
              for a, b in combinations(names, 2)]
    return names, dissim


def rsa(system_a: dict[str, list[float]], system_b: dict[str, list[float]]
        ) -> float:
    """Correlate two systems' RDMs: how alike is their representational geometry."""
    _, rdm_a = rdm(system_a)
    _, rdm_b = rdm(system_b)
    return _pearson(rdm_a, rdm_b)


if __name__ == "__main__":
    # Four stimuli: two animals, two tools. A brain region groups by category.
    brain = {
        "cat":    [0.9, 0.8, 0.1, 0.0],
        "dog":    [0.8, 0.9, 0.0, 0.1],
        "hammer": [0.1, 0.0, 0.9, 0.8],
        "saw":    [0.0, 0.1, 0.8, 0.9],
    }
    # A model that also groups animals vs tools (different units, same geometry).
    good_model = {
        "cat":    [1.0, 0.2],
        "dog":    [0.9, 0.1],
        "hammer": [0.1, 1.0],
        "saw":    [0.2, 0.9],
    }
    # A model with no category structure.
    poor_model = {
        "cat":    [0.5, 0.9],
        "dog":    [0.1, 0.2],
        "hammer": [0.8, 0.3],
        "saw":    [0.4, 0.7],
    }

    print("Representational Similarity Analysis (RDM correlation)\n")
    print(f"  category-structured model vs brain : RSA = {rsa(brain, good_model):+.3f}")
    print(f"  unstructured model       vs brain : RSA = {rsa(brain, poor_model):+.3f}")

    names, d = rdm(brain)
    print("\n  Brain RDM (1 - correlation; larger = more different):")
    for (a, b), val in zip(combinations(names, 2), d):
        print(f"    {a:>6} vs {b:<6}: {val:.2f}")
    print("\n  A high RSA means the model encodes stimuli with the same geometry")
    print("  as the brain — alike representations, regardless of the raw units.")
