"""
Diagnostic test evaluation / 診断検査の評価

The arithmetic behind clinical decision support: from a 2x2 table of test
results vs. true disease status, derive sensitivity, specificity, predictive
values and likelihood ratios — then use Bayes' theorem to update a patient's
disease probability after the test result.
"""

from dataclasses import dataclass


@dataclass
class DiagnosticTest:
    tp: int  # true positives  (test +, disease +)
    fp: int  # false positives (test +, disease -)
    fn: int  # false negatives (test -, disease +)
    tn: int  # true negatives  (test -, disease -)

    def sensitivity(self) -> float:
        """P(test+ | disease+) — ability to detect disease."""
        return self.tp / (self.tp + self.fn)

    def specificity(self) -> float:
        """P(test- | disease-) — ability to rule out disease."""
        return self.tn / (self.tn + self.fp)

    def ppv(self) -> float:
        """Positive predictive value: P(disease+ | test+)."""
        return self.tp / (self.tp + self.fp)

    def npv(self) -> float:
        """Negative predictive value: P(disease- | test-)."""
        return self.tn / (self.tn + self.fn)

    def accuracy(self) -> float:
        total = self.tp + self.fp + self.fn + self.tn
        return (self.tp + self.tn) / total

    def positive_lr(self) -> float:
        """LR+ = sensitivity / (1 - specificity)."""
        return self.sensitivity() / (1 - self.specificity())

    def negative_lr(self) -> float:
        """LR- = (1 - sensitivity) / specificity."""
        return (1 - self.sensitivity()) / self.specificity()


def post_test_probability(pretest_prob: float, likelihood_ratio: float) -> float:
    """Bayes update: pretest odds * LR = posttest odds -> probability."""
    if not 0 <= pretest_prob < 1:
        raise ValueError("pretest_prob must be in [0, 1)")
    pretest_odds = pretest_prob / (1 - pretest_prob)
    posttest_odds = pretest_odds * likelihood_ratio
    return posttest_odds / (1 + posttest_odds)


if __name__ == "__main__":
    test = DiagnosticTest(tp=90, fp=30, fn=10, tn=870)
    print(f"Sensitivity: {test.sensitivity():.3f}")
    print(f"Specificity: {test.specificity():.3f}")
    print(f"PPV:         {test.ppv():.3f}")
    print(f"NPV:         {test.npv():.3f}")
    print(f"LR+:         {test.positive_lr():.2f}")
    print(f"LR-:         {test.negative_lr():.2f}")

    pre = 0.10  # 10% pretest probability for this patient
    print(f"\nPretest prob: {pre:.2f}")
    print(f"  after positive test: {post_test_probability(pre, test.positive_lr()):.3f}")
    print(f"  after negative test: {post_test_probability(pre, test.negative_lr()):.3f}")
