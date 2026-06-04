"""
ROC analysis — discrimination of a prediction model / ROC解析

A clinical prediction model outputs a risk score; the ROC curve shows the
trade-off between true-positive and false-positive rates across all decision
thresholds. The area under the curve (AUC / c-statistic) summarises how well
the model ranks a random patient with the outcome above one without it.
"""


def roc_points(scores: list[float], labels: list[int]) -> list[tuple[float, float]]:
    """Return (FPR, TPR) points along the ROC curve, ordered by threshold."""
    n_pos = sum(labels)
    n_neg = len(labels) - n_pos
    if n_pos == 0 or n_neg == 0:
        raise ValueError("need both positive and negative cases")

    ordered = sorted(zip(scores, labels), key=lambda sl: sl[0], reverse=True)
    points = [(0.0, 0.0)]
    tp = fp = 0
    for _, label in ordered:
        if label:
            tp += 1
        else:
            fp += 1
        points.append((fp / n_neg, tp / n_pos))
    return points


def auc(scores: list[float], labels: list[int]) -> float:
    """AUC via the Mann-Whitney statistic (ties count as half)."""
    pos = [s for s, y in zip(scores, labels) if y]
    neg = [s for s, y in zip(scores, labels) if not y]
    if not pos or not neg:
        raise ValueError("need both positive and negative cases")
    wins = 0.0
    for p in pos:
        for q in neg:
            if p > q:
                wins += 1
            elif p == q:
                wins += 0.5
    return wins / (len(pos) * len(neg))


def youden_threshold(scores: list[float], labels: list[int]) -> tuple[float, float]:
    """Optimal cutoff maximising Youden's J = sensitivity + specificity - 1."""
    n_pos = sum(labels)
    n_neg = len(labels) - n_pos
    best_j, best_threshold = -1.0, 0.0
    for threshold in sorted(set(scores), reverse=True):
        tp = sum(1 for s, y in zip(scores, labels) if s >= threshold and y)
        fp = sum(1 for s, y in zip(scores, labels) if s >= threshold and not y)
        sensitivity = tp / n_pos
        specificity = 1 - fp / n_neg
        j = sensitivity + specificity - 1
        if j > best_j:
            best_j, best_threshold = j, threshold
    return best_threshold, best_j


if __name__ == "__main__":
    scores = [0.9, 0.8, 0.7, 0.6, 0.55, 0.5, 0.4, 0.3, 0.2, 0.1]
    labels = [1, 1, 0, 1, 1, 0, 1, 0, 0, 0]
    print(f"AUC (c-statistic): {auc(scores, labels):.3f}")
    thr, j = youden_threshold(scores, labels)
    print(f"Youden-optimal threshold: {thr:.2f}  (J = {j:.3f})")
    print("ROC points (FPR, TPR):")
    for fpr, tpr in roc_points(scores, labels):
        print(f"  ({fpr:.2f}, {tpr:.2f})")
