"""
Narrative Arcs — the emotional "shapes of stories"

Kurt Vonnegut argued that stories have measurable emotional shapes; large-scale
text analysis (Reagan et al., 2016) confirmed a small family of recurring arcs.
We trace sentiment across narrative time using a valence lexicon, smooth it, and
classify the arc:

  rags to riches   steady rise        tragedy        steady fall
  man in a hole    fall then rise     Icarus         rise then fall
"""

from __future__ import annotations

import re


POSITIVE = {
    "happy", "joy", "joyful", "smiled", "smile", "laughed", "laugh", "bright",
    "warm", "love", "loved", "hope", "hopeful", "wonderful", "good", "better",
    "best", "light", "glad", "peace", "gentle", "sweet", "won", "triumph",
    "safe", "free", "delight", "dream", "beautiful", "alive",
}
NEGATIVE = {
    "sad", "fear", "afraid", "dark", "cold", "cried", "wept", "pain", "death",
    "died", "lost", "loss", "alone", "despair", "broken", "anger", "angry",
    "hate", "grief", "sorrow", "terrible", "worse", "worst", "fell", "trapped",
    "sick", "tears", "empty", "ruin", "silence",
}


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z']+", text.lower())


def emotional_arc(text: str, segments: int = 10) -> list[float]:
    """Mean sentiment (-1..+1) over `segments` equal slices of the narrative."""
    tokens = tokenize(text)
    size = max(1, len(tokens) // segments)
    arc = []
    for i in range(segments):
        chunk = tokens[i * size:(i + 1) * size] if i < segments - 1 \
            else tokens[i * size:]
        score = sum((w in POSITIVE) - (w in NEGATIVE) for w in chunk)
        matched = sum((w in POSITIVE) or (w in NEGATIVE) for w in chunk)
        arc.append(score / matched if matched else 0.0)
    return arc


def classify(arc: list[float], threshold: float = 0.15) -> str:
    third = max(1, len(arc) // 3)
    start = sum(arc[:third]) / third
    middle = sum(arc[third:2 * third]) / third
    end = sum(arc[2 * third:]) / len(arc[2 * third:])
    dip = middle - (start + end) / 2
    rise = end - start
    if dip < -threshold:
        return "man in a hole (fall then rise)"
    if dip > threshold:
        return "Icarus (rise then fall)"
    if rise > threshold:
        return "rags to riches (steady rise)"
    if rise < -threshold:
        return "tragedy (steady fall)"
    return "flat / steady"


def sparkline(values: list[float]) -> str:
    blocks = "▁▂▃▄▅▆▇█"
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1.0
    return "".join(blocks[min(len(blocks) - 1, int((v - lo) / span * (len(blocks) - 1)))]
                   for v in values)


if __name__ == "__main__":
    # A "man in a hole" story: contentment, descent into loss, recovery.
    story = (
        "The morning was bright and warm and the children laughed in the "
        "garden, happy and free and full of hope. Life was good and the days "
        "were sweet. "
        "Then the cold came. A terrible sickness fell upon the house and the "
        "laughter died. They were afraid, and grief and silence filled the dark "
        "rooms. Alone and broken, they wept, lost in despair and pain, sure that "
        "all was ruin. "
        "But slowly the light returned. A gentle hope, then a smile, then warm "
        "laughter again. They were safe, and love and peace came back, and the "
        "house was alive and bright once more, joyful and free."
    )

    arc = emotional_arc(story, segments=9)
    print("Emotional arc across narrative time:\n")
    print(f"  {sparkline(arc)}")
    print(f"  values: {[round(v, 2) for v in arc]}\n")
    print(f"  Detected shape: {classify(arc)}")
