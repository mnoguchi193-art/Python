"""
Diagnostic Test Evaluation — sensitivity, specificity, Bayes & ROC

Evidence-based medicine lives or dies on interpreting tests correctly. A test
can be 99% accurate yet most positives still be false alarms when the disease is
rare — the base-rate fallacy that misleads doctors and patients alike.

This module computes the standard operating characteristics, the predictive
values via Bayes' theorem, and the ROC AUC of a continuous biomarker.
"""

from __future__ import annotations


def confusion_metrics(tp: int, fp: int, fn: int, tn: int) -> dict[str, float]:
    """Sensitivity, specificity and predictive values from raw counts."""
    return {
        "sensitivity": tp / (tp + fn),          # true positive rate (recall)
        "specificity": tn / (tn + fp),          # true negative rate
        "ppv": tp / (tp + fp),                  # positive predictive value
        "npv": tn / (tn + fn),                  # negative predictive value
        "accuracy": (tp + tn) / (tp + fp + fn + tn),
    }


def ppv_from_prevalence(sensitivity: float, specificity: float,
                        prevalence: float) -> float:
    """Bayes' theorem: P(disease | positive test) given the base rate."""
    true_pos = sensitivity * prevalence
    false_pos = (1 - specificity) * (1 - prevalence)
    return true_pos / (true_pos + false_pos)


def roc_auc(scored: list[tuple[float, int]]) -> float:
    """Area under the ROC curve = P(score of a case > score of a non-case).

    Computed as the normalized count of correctly ordered case/non-case pairs
    (the Mann-Whitney U statistic), with ties counted as half.
    """
    positives = [s for s, label in scored if label == 1]
    negatives = [s for s, label in scored if label == 0]
    if not positives or not negatives:
        raise ValueError("need both positive and negative examples")
    concordant = sum(
        (p > n) + 0.5 * (p == n)
        for p in positives for n in negatives
    )
    return concordant / (len(positives) * len(negatives))


if __name__ == "__main__":
    # A very good screening test...
    sens, spec = 0.99, 0.95
    print(f"Screening test: sensitivity {sens:.0%}, specificity {spec:.0%}\n")
    print("  prevalence   PPV (P[disease | positive])")
    for prevalence in (0.001, 0.01, 0.10, 0.50):
        ppv = ppv_from_prevalence(sens, spec, prevalence)
        print(f"  {prevalence:>8.1%}    {ppv:>6.1%}")
    print("  => for a rare disease, most positives are FALSE positives.\n")

    # Operating characteristics from a 2x2 table.
    metrics = confusion_metrics(tp=90, fp=50, fn=10, tn=850)
    print("Confusion matrix (TP=90, FP=50, FN=10, TN=850):")
    for name, value in metrics.items():
        print(f"  {name:<12}: {value:.1%}")

    # Discriminative power of a continuous biomarker.
    scored = [(0.9, 1), (0.8, 1), (0.7, 0), (0.6, 1),
              (0.55, 0), (0.4, 1), (0.35, 0), (0.2, 0)]
    print(f"\nBiomarker ROC AUC: {roc_auc(scored):.3f}  (0.5 = useless, 1.0 = perfect)")
