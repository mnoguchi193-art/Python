"""
Self-Attention — the heart of the Transformer (and of every LLM)

The mechanism that powers GPT and modern language models. Each token forms a
query and compares it (dot product) against every token's key; the softmax of
those scores says how much to attend to each token, and the output is the
attention-weighted sum of their values. "Attention is all you need" — this single
operation lets every position gather context from the whole sequence.

Here Q = K = V = the token embeddings (self-attention), in pure Python.
"""

from __future__ import annotations

import math


def softmax(xs: list[float]) -> list[float]:
    m = max(xs)
    exps = [math.exp(x - m) for x in xs]
    total = sum(exps)
    return [e / total for e in exps]


def attention(queries: list[list[float]], keys: list[list[float]],
              values: list[list[float]]
              ) -> tuple[list[list[float]], list[list[float]]]:
    """Scaled dot-product attention. Returns (outputs, attention weights)."""
    d = len(keys[0])
    scale = math.sqrt(d)
    weights = []
    for q in queries:
        scores = [sum(qi * ki for qi, ki in zip(q, k)) / scale for k in keys]
        weights.append(softmax(scores))
    outputs = []
    for w in weights:
        out = [sum(w[j] * values[j][f] for j in range(len(values)))
               for f in range(len(values[0]))]
        outputs.append(out)
    return outputs, weights


if __name__ == "__main__":
    # Two semantic groups: royalty and fruit. Embeddings within a group align,
    # so each token should attend mostly to its own group.
    tokens = ["king", "queen", "throne", "apple", "banana", "fruit"]
    embeddings = [
        [1.0, 1.0, 0.0, 0.0],   # king
        [1.0, 0.9, 0.0, 0.0],   # queen
        [0.9, 1.0, 0.0, 0.0],   # throne
        [0.0, 0.0, 1.0, 1.0],   # apple
        [0.0, 0.0, 1.0, 0.9],   # banana
        [0.0, 0.0, 0.9, 1.0],   # fruit
    ]

    _, weights = attention(embeddings, embeddings, embeddings)

    print("Self-attention weights (row = query token attends to columns)\n")
    print("           " + "".join(f"{t[:6]:>8}" for t in tokens))
    for token, row in zip(tokens, weights):
        print(f"  {token:<8} " + "".join(f"{w:>8.2f}" for w in row))

    print("\n  Strongest attention for each token:")
    for token, row in zip(tokens, weights):
        j = max(range(len(row)), key=lambda k: row[k] if tokens[k] != token else -1)
        print(f"    {token:<8} -> {tokens[j]}")
    print("\nWithout being told the groups, attention routes each token to its")
    print("semantic neighbours — the contextual mixing that LLMs are built on.")
