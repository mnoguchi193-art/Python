"""
Stylometry — authorship attribution with Burrows's Delta

The flagship method of computational literary studies. Authorship leaves a
fingerprint not in rare, conscious vocabulary but in the *function words* (the,
of, and, I, that...) used unconsciously and at stable rates. Burrows's Delta
compares an anonymous text to candidate authors by the mean absolute difference
of their z-scored function-word frequencies — and usually picks the right one.
"""

from __future__ import annotations

import re
from statistics import mean, pstdev


FUNCTION_WORDS = [
    "the", "of", "and", "to", "a", "in", "that", "it", "is", "was", "i", "my",
    "me", "he", "she", "they", "with", "as", "for", "but", "not", "this", "you",
    "her", "his", "which", "upon", "then", "said", "would", "could",
]


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z']+", text.lower())


def function_word_freqs(text: str) -> dict[str, float]:
    tokens = tokenize(text)
    n = len(tokens) or 1
    return {w: tokens.count(w) / n for w in FUNCTION_WORDS}


def burrows_delta(candidates: dict[str, str], unknown: str) -> dict[str, float]:
    """Delta distance from `unknown` to each candidate author (lower = closer)."""
    freqs = {name: function_word_freqs(text) for name, text in candidates.items()}
    unknown_freq = function_word_freqs(unknown)

    # Corpus mean and std per function word, across candidate authors.
    stats = {}
    for w in FUNCTION_WORDS:
        values = [freqs[name][w] for name in candidates]
        stats[w] = (mean(values), pstdev(values))

    def zscore(freq, w):
        mu, sd = stats[w]
        return (freq[w] - mu) / sd if sd > 0 else 0.0

    deltas = {}
    for name in candidates:
        diffs = [abs(zscore(freqs[name], w) - zscore(unknown_freq, w))
                 for w in FUNCTION_WORDS]
        deltas[name] = mean(diffs)
    return deltas


if __name__ == "__main__":
    candidates = {
        "Formal historian": (
            "The history of the nation, of which so much has been written, must "
            "be understood in the light of the institutions upon which it was "
            "founded. The records of the period, and the testimony of those whom "
            "we regard as authorities, indicate that the structure of the state "
            "was the product of the circumstances of the age. It is to these "
            "circumstances that the student of the subject must turn."
        ),
        "Plain narrator": (
            "She opened the door and he came in. Then she smiled and he laughed. "
            "They walked and they talked and the day went on. He said it was good "
            "and she said it was better. And then the rain came down and they ran "
            "and ran. He held her hand and she held his and they were happy."
        ),
        "First-person voice": (
            "I remember that day as if it were my own shadow. I was young, and I "
            "thought that my life was mine to shape. My mother told me that I "
            "would understand, but I did not. I wanted more than I could say, and "
            "I kept my secrets close. It was my way, and I would not change it."
        ),
    }
    unknown = (
        "I recall my childhood as a quiet dream that I could not hold. I was "
        "small, and I believed that my world was mine alone. My father warned me "
        "that I would learn, and I did not listen. I longed for more than I could "
        "name, and I held my thoughts near. It was my nature, and I would not yield."
    )

    deltas = burrows_delta(candidates, unknown)
    print("Burrows's Delta to the anonymous text (lower = more likely author):\n")
    for name, d in sorted(deltas.items(), key=lambda kv: kv[1]):
        print(f"  {name:<20} Delta = {d:.3f}")

    best = min(deltas, key=deltas.get)
    print(f"\nMost likely author: {best}")
