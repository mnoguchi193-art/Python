"""
Fairness — measuring algorithmic bias / バイアス(公平性)の測定

A clinical model can perform well overall yet treat demographic groups
unequally. This module computes the standard group-fairness diagnostics from
predictions, true labels and a protected-group attribute:

  * selection rate & demographic parity      (equal positive rates?)
  * disparate impact / the 80% rule          (regulatory bias screen)
  * true-positive rate & equal opportunity    (equal benefit for the sick?)

Standard library only.
"""

from dataclasses import dataclass


@dataclass
class FairnessReport:
    selection_rate: dict[str, float]
    true_positive_rate: dict[str, float]
    demographic_parity_difference: float
    disparate_impact: float
    equal_opportunity_difference: float

    def passes_80_percent_rule(self) -> bool:
        """US EEOC four-fifths rule: disparate impact >= 0.8."""
        return self.disparate_impact >= 0.8


def _rate(values: list[bool]) -> float:
    return sum(values) / len(values) if values else 0.0


def fairness_report(
    predictions: list[int], labels: list[int], groups: list[str]
) -> FairnessReport:
    distinct = sorted(set(groups))
    selection: dict[str, float] = {}
    tpr: dict[str, float] = {}
    for g in distinct:
        preds_g = [p for p, gg in zip(predictions, groups) if gg == g]
        selection[g] = _rate([p == 1 for p in preds_g])
        # TPR uses only the truly positive cases in the group.
        positives = [p for p, y, gg in zip(predictions, labels, groups)
                     if gg == g and y == 1]
        tpr[g] = _rate([p == 1 for p in positives])

    sel_values = list(selection.values())
    tpr_values = list(tpr.values())
    dp_diff = max(sel_values) - min(sel_values)
    di = min(sel_values) / max(sel_values) if max(sel_values) > 0 else 1.0
    eo_diff = max(tpr_values) - min(tpr_values)
    return FairnessReport(selection, tpr, dp_diff, di, eo_diff)


if __name__ == "__main__":
    # Group B is selected far less often than group A.
    predictions = [1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0]
    labels =      [1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1]
    groups =      ["A", "A", "A", "A", "A", "A",
                   "B", "B", "B", "B", "B", "B"]
    report = fairness_report(predictions, labels, groups)
    print("Selection rate:", {k: round(v, 3) for k, v in report.selection_rate.items()})
    print("True-positive rate:", {k: round(v, 3) for k, v in report.true_positive_rate.items()})
    print(f"Demographic parity difference: {report.demographic_parity_difference:.3f}")
    print(f"Disparate impact: {report.disparate_impact:.3f}")
    print(f"Equal opportunity difference: {report.equal_opportunity_difference:.3f}")
    print(f"Passes 80% rule: {report.passes_80_percent_rule()}")
