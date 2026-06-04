"""
Explainability — opening the black box / 説明可能性(ブラックボックス問題)

A model that cannot explain itself is hard to trust in medicine. Two
complementary views:

  * permutation importance — global: how much does the model rely on each
    feature? (shuffle a feature and measure the drop in accuracy)
  * additive local explanation — per patient: how does each feature push this
    one prediction above or below the baseline?

Standard library only.
"""

import math
import random
from typing import Callable


def _accuracy(probs: list[float], labels: list[int]) -> float:
    correct = sum((p >= 0.5) == bool(y) for p, y in zip(probs, labels))
    return correct / len(labels)


def permutation_importance(
    predict: Callable[[list[list[float]]], list[float]],
    X: list[list[float]],
    y: list[int],
    feature_names: list[str],
    seed: int = 0,
) -> dict[str, float]:
    """Drop in accuracy when each feature column is randomly shuffled."""
    rng = random.Random(seed)
    baseline = _accuracy(predict(X), y)
    importances: dict[str, float] = {}
    for j, name in enumerate(feature_names):
        permuted = [row[:] for row in X]
        column = [row[j] for row in permuted]
        rng.shuffle(column)
        for i, row in enumerate(permuted):
            row[j] = column[i]
        importances[name] = baseline - _accuracy(predict(permuted), y)
    return importances


def linear_contributions(
    coefficients: dict[str, float],
    features: dict[str, float],
    baseline: dict[str, float],
) -> dict[str, float]:
    """Additive contribution of each feature: coef * (x - baseline_mean).

    Contributions sum to the model's deviation from its baseline score, giving
    a transparent, locally exact explanation of a linear model.
    """
    return {
        name: coefficients.get(name, 0.0) * (value - baseline.get(name, 0.0))
        for name, value in features.items()
    }


if __name__ == "__main__":
    # Synthetic data: feature 0 is informative, feature 1 is pure noise.
    rng = random.Random(0)
    X = [[rng.gauss(0, 1), rng.gauss(0, 1)] for _ in range(200)]
    y = [1 if row[0] > 0 else 0 for row in X]
    weights = [2.5, 0.0]

    def predict(rows: list[list[float]]) -> list[float]:
        return [1 / (1 + math.exp(-sum(w * x for w, x in zip(weights, r)))) for r in rows]

    imp = permutation_importance(predict, X, y, ["informative", "noise"])
    print("Permutation importance:")
    for name, score in sorted(imp.items(), key=lambda kv: kv[1], reverse=True):
        print(f"  {name}: {score:.3f}")

    contribs = linear_contributions(
        coefficients={"age": 0.5, "lactate": 1.2},
        features={"age": 8.0, "lactate": 1.0},
        baseline={"age": 5.0, "lactate": 0.3},
    )
    print("Local contributions:", {k: round(v, 3) for k, v in contribs.items()})
