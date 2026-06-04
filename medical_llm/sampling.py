"""
Decoding strategies — how an LLM picks the next token / デコーディング戦略

Given the model's output logits, several strategies trade off determinism
against diversity:

    greedy      always the highest-probability token
    temperature flatten (>1) or sharpen (<1) the distribution
    top-k       sample among the k most likely tokens
    top-p       sample among the smallest set whose mass exceeds p (nucleus)

In medical settings, low temperature / greedy decoding is preferred for
factual reliability. Standard library only.
"""

import math
import random


def softmax(logits: list[float], temperature: float = 1.0) -> list[float]:
    if temperature <= 0:
        raise ValueError("temperature must be positive")
    scaled = [x / temperature for x in logits]
    m = max(scaled)
    exps = [math.exp(s - m) for s in scaled]
    total = sum(exps)
    return [e / total for e in exps]


def greedy(logits: list[float]) -> int:
    return max(range(len(logits)), key=lambda i: logits[i])


def sample_top_k(
    logits: list[float], k: int, temperature: float = 1.0, rng=random
) -> int:
    probs = softmax(logits, temperature)
    ranked = sorted(range(len(probs)), key=lambda i: probs[i], reverse=True)[:k]
    mass = sum(probs[i] for i in ranked)
    weights = [probs[i] / mass for i in ranked]
    return rng.choices(ranked, weights=weights, k=1)[0]


def sample_top_p(
    logits: list[float], p: float, temperature: float = 1.0, rng=random
) -> int:
    probs = softmax(logits, temperature)
    ranked = sorted(range(len(probs)), key=lambda i: probs[i], reverse=True)
    nucleus: list[int] = []
    cumulative = 0.0
    for i in ranked:
        nucleus.append(i)
        cumulative += probs[i]
        if cumulative >= p:
            break
    mass = sum(probs[i] for i in nucleus)
    weights = [probs[i] / mass for i in nucleus]
    return rng.choices(nucleus, weights=weights, k=1)[0]


if __name__ == "__main__":
    vocab = ["fever", "rest", "fluids", "emergency", "aspirin"]
    logits = [3.2, 2.1, 1.8, 0.4, 1.0]

    print("Probabilities (T=1.0):",
          [round(p, 3) for p in softmax(logits)])
    print("Probabilities (T=0.5, sharper):",
          [round(p, 3) for p in softmax(logits, temperature=0.5)])
    print("Greedy choice:", vocab[greedy(logits)])

    rng = random.Random(7)
    print("Top-k (k=3) sample:", vocab[sample_top_k(logits, k=3, rng=rng)])
    print("Top-p (p=0.9) sample:", vocab[sample_top_p(logits, p=0.9, rng=rng)])
