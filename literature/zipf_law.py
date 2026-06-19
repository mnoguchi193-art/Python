"""
Zipf's Law and Lexical Richness — the statistics of literary vocabulary

A robust empirical law of quantitative linguistics: in natural text the r-th
most frequent word appears about proportionally to 1/r. Plotted on log-log axes,
rank vs frequency is a near-straight line whose slope is the Zipf exponent
(typically near -1). We estimate it by least squares and add classic richness
measures used to compare authors and texts.
"""

from __future__ import annotations

import re
from collections import Counter
from math import log


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z']+", text.lower())


def rank_frequency(text: str) -> list[tuple[str, int]]:
    return Counter(tokenize(text)).most_common()


def zipf_exponent(text: str) -> float:
    """Estimate s in frequency ~ 1/rank**s via least-squares on log-log data."""
    freqs = [f for _, f in rank_frequency(text)]
    xs = [log(r) for r in range(1, len(freqs) + 1)]
    ys = [log(f) for f in freqs]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    var = sum((x - mx) ** 2 for x in xs)
    return -cov / var          # slope is negative; exponent is its magnitude


def lexical_richness(text: str) -> dict[str, float]:
    tokens = tokenize(text)
    types = set(tokens)
    counts = Counter(tokens)
    hapax = sum(1 for w in types if counts[w] == 1)
    return {
        "tokens": len(tokens),
        "types": len(types),
        "type_token_ratio": len(types) / len(tokens),
        "hapax_fraction": hapax / len(types),
    }


if __name__ == "__main__":
    # Public-domain text: opening of "Alice's Adventures in Wonderland" (1865).
    text = (
        "Alice was beginning to get very tired of sitting by her sister on the "
        "bank, and of having nothing to do: once or twice she had peeped into the "
        "book her sister was reading, but it had no pictures or conversations in "
        "it, and what is the use of a book, thought Alice, without pictures or "
        "conversations? So she was considering in her own mind, as well as she "
        "could, for the hot day made her feel very sleepy and stupid, whether the "
        "pleasure of making a daisy chain would be worth the trouble of getting "
        "up and picking the daisies, when suddenly a White Rabbit with pink eyes "
        "ran close by her. There was nothing so very remarkable in that, nor did "
        "Alice think it so very much out of the way to hear the Rabbit say to "
        "itself oh dear oh dear I shall be late. But when the Rabbit actually "
        "took a watch out of its waistcoat pocket and looked at it and then "
        "hurried on, Alice started to her feet, for it flashed across her mind "
        "that she had never before seen a rabbit with either a waistcoat pocket "
        "or a watch to take out of it, and burning with curiosity she ran across "
        "the field after it and was just in time to see it pop down a large "
        "rabbit hole under the hedge."
    )

    print("Zipf's law — top words by frequency:\n")
    print(f"  {'rank':>4}  {'word':<12}{'freq':>5}  {'1/rank * top':>12}")
    table = rank_frequency(text)
    top_freq = table[0][1]
    for rank, (word, freq) in enumerate(table[:10], start=1):
        print(f"  {rank:>4}  {word:<12}{freq:>5}  {top_freq / rank:>12.1f}")

    print(f"\n  Estimated Zipf exponent s : {zipf_exponent(text):.2f} "
          f"(natural language ~ 1.0)")

    print("\nLexical richness:")
    for name, value in lexical_richness(text).items():
        shown = f"{value:.3f}" if isinstance(value, float) else f"{value}"
        print(f"  {name:<18}: {shown}")
