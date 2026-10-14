"""
Text Generation — language modeling and the decoding knobs

A language model predicts the next token from the preceding context; generation
just samples from it, over and over. This character-level n-gram model shows the
*decoding strategies* that shape an LLM's output: greedy (always the top choice,
often repetitive), temperature (flattening or sharpening the distribution), and
top-k (sampling only from the k most likely tokens). Same model, very different
text.
"""

from __future__ import annotations

import random
from collections import Counter, defaultdict


def train(text: str, order: int = 4) -> dict[str, Counter]:
    """Count which character follows each length-`order` context."""
    model: dict[str, Counter] = defaultdict(Counter)
    for i in range(len(text) - order):
        model[text[i:i + order]][text[i + order]] += 1
    return model


def generate(model: dict[str, Counter], order: int, seed: str, length: int = 200,
             temperature: float = 1.0, top_k: int | None = None,
             greedy: bool = False, rng: random.Random | None = None) -> str:
    rng = rng or random.Random(0)
    text = seed
    for _ in range(length):
        counts = model.get(text[-order:])
        if not counts:
            break
        items = counts.most_common()
        if greedy:
            text += items[0][0]
            continue
        if top_k:
            items = items[:top_k]
        weights = [c ** (1 / temperature) for _, c in items]
        text += rng.choices([ch for ch, _ in items], weights)[0]
    return text


if __name__ == "__main__":
    corpus = (
        "the quick brown fox jumps over the lazy dog. "
        "a wizard's job is to vex chumps quickly in fog. "
        "the five boxing wizards jump quickly. "
        "pack my box with five dozen liquor jugs. "
        "how vexingly quick daft zebras jump! "
    ) * 6
    order = 4
    model = train(corpus, order)
    seed = "the "

    print(f"Character-level n-gram model (order {order})\n")
    rng = random.Random(1)
    print("  greedy (top choice each step — collapses into a loop):")
    print(f"    {generate(model, order, seed, 80, greedy=True)!r}\n")
    print("  temperature 0.5 (conservative):")
    print(f"    {generate(model, order, seed, 80, temperature=0.5, rng=rng)!r}\n")
    print("  temperature 1.0 (balanced):")
    print(f"    {generate(model, order, seed, 80, temperature=1.0, rng=rng)!r}\n")
    print("  top-k = 2 (only the 2 likeliest next chars):")
    print(f"    {generate(model, order, seed, 80, top_k=2, rng=rng)!r}")
    print("\n  One model, many voices: the decoding strategy trades coherence")
    print("  against diversity — the same dials you set on an LLM.")
