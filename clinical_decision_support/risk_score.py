"""
Clinical risk score — logistic model & utility / 臨床リスクスコア

A prognostic model converts patient features into an outcome probability via
logistic regression. Beyond discrimination (see roc_analysis), a useful model
must also be well *calibrated* and clinically *useful*:

  * Brier score   — overall accuracy of probabilistic predictions (lower=better)
  * Decision curve — net benefit of acting on the model at a chosen threshold
"""

import math
from dataclasses import dataclass


@dataclass
class LogisticRiskModel:
    intercept: float
    coefficients: dict[str, float]

    def predict(self, features: dict[str, float]) -> float:
        """Predicted outcome probability: sigmoid(b0 + sum bi*xi)."""
        z = self.intercept + sum(
            self.coefficients.get(k, 0.0) * v for k, v in features.items()
        )
        return 1 / (1 + math.exp(-z))


def brier_score(predictions: list[float], outcomes: list[int]) -> float:
    """Mean squared error between predicted probabilities and outcomes."""
    if len(predictions) != len(outcomes):
        raise ValueError("predictions and outcomes must align")
    return sum((p - y) ** 2 for p, y in zip(predictions, outcomes)) / len(outcomes)


def net_benefit(
    predictions: list[float], outcomes: list[int], threshold: float
) -> float:
    """Decision-curve net benefit of treating when predicted risk >= threshold.

    NB = TP/n - FP/n * (pt / (1 - pt)),  pt = threshold probability.
    """
    if not 0 < threshold < 1:
        raise ValueError("threshold must be in (0, 1)")
    n = len(outcomes)
    tp = sum(1 for p, y in zip(predictions, outcomes) if p >= threshold and y)
    fp = sum(1 for p, y in zip(predictions, outcomes) if p >= threshold and not y)
    weight = threshold / (1 - threshold)
    return tp / n - (fp / n) * weight


if __name__ == "__main__":
    # Mortality risk from age (per decade) and an elevated lactate flag.
    model = LogisticRiskModel(
        intercept=-4.0,
        coefficients={"age_decades": 0.5, "high_lactate": 1.2},
    )
    patients = [
        {"age_decades": 8, "high_lactate": 1},
        {"age_decades": 5, "high_lactate": 0},
        {"age_decades": 7, "high_lactate": 1},
        {"age_decades": 3, "high_lactate": 0},
    ]
    outcomes = [1, 0, 1, 0]
    preds = [model.predict(p) for p in patients]
    for p, risk, y in zip(patients, preds, outcomes):
        print(f"  age_decades={p['age_decades']} lactate={p['high_lactate']} "
              f"-> risk={risk:.3f} (outcome={y})")
    print(f"Brier score: {brier_score(preds, outcomes):.4f}")
    print(f"Net benefit @0.2: {net_benefit(preds, outcomes, 0.2):.4f}")
