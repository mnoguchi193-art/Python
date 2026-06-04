"""
Regulatory — Software as a Medical Device (SaMD) / 薬事規制(SaMD)

Medical AI is regulated. The IMDRF framework classifies a SaMD by combining:

  * the state of the healthcare situation it addresses (critical / serious /
    non-serious), and
  * the significance of the information it provides (treat-or-diagnose /
    drive clinical management / inform clinical management).

The pair yields a risk category (I lowest .. IV highest). A premarket
readiness checklist models Good Machine Learning Practice (GMLP) gating.
This is an educational simplification, not regulatory advice. Standard library
only.
"""

from dataclasses import dataclass

# IMDRF risk matrix: [significance][situation] -> category (I..IV).
_MATRIX = {
    "treat_or_diagnose": {"critical": "IV", "serious": "III", "non_serious": "II"},
    "drive_management":  {"critical": "III", "serious": "II", "non_serious": "I"},
    "inform_management": {"critical": "II", "serious": "I", "non_serious": "I"},
}

_RISK_RANK = {"I": 1, "II": 2, "III": 3, "IV": 4}


def samd_category(significance: str, situation: str) -> str:
    """Return the IMDRF SaMD category ('I'..'IV')."""
    if significance not in _MATRIX:
        raise ValueError(f"unknown significance: {significance!r}")
    if situation not in _MATRIX[significance]:
        raise ValueError(f"unknown situation: {situation!r}")
    return _MATRIX[significance][situation]


@dataclass
class PremarketChecklist:
    """Good Machine Learning Practice (GMLP) readiness gating."""
    clinical_validation: bool = False
    bias_assessment: bool = False
    explainability_documented: bool = False
    data_privacy_safeguards: bool = False
    change_control_plan: bool = False
    human_oversight_defined: bool = False
    post_market_monitoring: bool = False

    def completed(self) -> list[str]:
        return [k for k, v in vars(self).items() if v]

    def outstanding(self) -> list[str]:
        return [k for k, v in vars(self).items() if not v]

    def readiness(self) -> float:
        items = vars(self)
        return sum(items.values()) / len(items)

    def is_release_ready(self, category: str) -> bool:
        """Higher-risk categories require full completion before release."""
        threshold = 1.0 if _RISK_RANK[category] >= 3 else 0.8
        return self.readiness() >= threshold


if __name__ == "__main__":
    # A sepsis early-warning tool that drives management in a critical setting.
    category = samd_category("drive_management", "critical")
    print(f"SaMD risk category: {category}")

    checklist = PremarketChecklist(
        clinical_validation=True,
        bias_assessment=True,
        explainability_documented=True,
        data_privacy_safeguards=True,
        change_control_plan=False,
        human_oversight_defined=True,
        post_market_monitoring=False,
    )
    print(f"Readiness: {checklist.readiness():.0%}")
    print(f"Outstanding: {checklist.outstanding()}")
    print(f"Release-ready for category {category}: "
          f"{checklist.is_release_ready(category)}")
