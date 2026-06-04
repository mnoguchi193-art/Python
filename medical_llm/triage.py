"""
Medical dialogue safety layer / 医療対話AIの安全層

A conversational medical AI must not behave like an unguarded chatbot. Before
any answer is generated, a guardrail layer should:

  * scan for emergency "red-flag" symptoms and escalate immediately,
  * classify urgency to route the conversation,
  * refuse out-of-scope requests (e.g. specific prescription dosing),
  * always attach a non-diagnostic disclaimer.

This is a transparent, rule-based demonstration — NOT a medical device and not
a substitute for professional care. Standard library only.
"""

import re
from dataclasses import dataclass

RED_FLAGS = [
    "chest pain", "difficulty breathing", "shortness of breath",
    "stroke", "slurred speech", "suicidal", "severe bleeding",
    "unconscious", "anaphylaxis", "stiff neck",
]

URGENT_TERMS = ["high fever", "persistent vomiting", "dehydration", "severe pain"]

# Requests the assistant should decline to answer directly.
OUT_OF_SCOPE = ["exact dose", "how much should i take", "prescribe", "dosage"]

DISCLAIMER = (
    "This is general information, not a diagnosis. "
    "Consult a qualified healthcare professional."
)


@dataclass
class TriageResult:
    urgency: str          # "emergency" | "urgent" | "routine"
    matched: list[str]
    refused: bool
    message: str


def _find(text: str, terms: list[str]) -> list[str]:
    low = text.lower()
    return [t for t in terms if re.search(r"\b" + re.escape(t), low)]


def assess(message: str) -> TriageResult:
    red = _find(message, RED_FLAGS)
    if red:
        return TriageResult(
            urgency="emergency",
            matched=red,
            refused=False,
            message=(
                "These symptoms may be a medical emergency. "
                "Call your local emergency number or go to the nearest ER now."
            ),
        )

    out = _find(message, OUT_OF_SCOPE)
    if out:
        return TriageResult(
            urgency="routine",
            matched=out,
            refused=True,
            message=(
                "I can't provide specific medication dosing. Please ask a "
                f"pharmacist or your prescribing clinician. {DISCLAIMER}"
            ),
        )

    urgent = _find(message, URGENT_TERMS)
    if urgent:
        return TriageResult(
            urgency="urgent",
            matched=urgent,
            refused=False,
            message=(
                "Your symptoms may need prompt attention. Consider contacting "
                f"a clinician or urgent-care service today. {DISCLAIMER}"
            ),
        )

    return TriageResult(
        urgency="routine",
        matched=[],
        refused=False,
        message=(
            "Here is some general guidance; monitor your symptoms and seek "
            f"care if they worsen. {DISCLAIMER}"
        ),
    )


if __name__ == "__main__":
    messages = [
        "I have sudden chest pain and shortness of breath.",
        "What is the exact dose of ibuprofen for my child?",
        "I've had a high fever and persistent vomiting since yesterday.",
        "I have a mild runny nose, what can I do?",
    ]
    for msg in messages:
        r = assess(msg)
        print(f"[{r.urgency.upper():9s}] refused={r.refused} matched={r.matched}")
        print(f"    {r.message}\n")
