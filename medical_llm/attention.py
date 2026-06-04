"""
Self-attention — the Transformer core / 自己注意機構

Scaled dot-product attention lets each token gather information from every
other token, weighted by query-key similarity:

    Attention(Q, K, V) = softmax(Q Kᵀ / sqrt(d)) V

This single operation underlies every modern LLM. Implemented here in pure
Python over lists of vectors. Standard library only.
"""

import math


def softmax(xs: list[float]) -> list[float]:
    m = max(xs)
    exps = [math.exp(x - m) for x in xs]
    total = sum(exps)
    return [e / total for e in exps]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def scaled_dot_product_attention(
    query: list[list[float]],
    key: list[list[float]],
    value: list[list[float]],
) -> tuple[list[list[float]], list[list[float]]]:
    """Return (outputs, attention_weights).

    query/key/value are sequences of vectors. Each output is a weighted
    average of the value vectors, weighted by how much each query attends to
    each key.
    """
    d = len(key[0])
    scale = math.sqrt(d)
    outputs: list[list[float]] = []
    weights: list[list[float]] = []
    dim_v = len(value[0])
    for q in query:
        scores = [_dot(q, k) / scale for k in key]
        attn = softmax(scores)
        weights.append(attn)
        out = [sum(attn[j] * value[j][t] for j in range(len(value))) for t in range(dim_v)]
        outputs.append(out)
    return outputs, weights


if __name__ == "__main__":
    # Three tokens with 4-dim embeddings used as Q, K and V (self-attention).
    tokens = [
        [1.0, 0.0, 1.0, 0.0],   # token 0
        [0.0, 1.0, 0.0, 1.0],   # token 1
        [1.0, 1.0, 0.0, 0.0],   # token 2
    ]
    outputs, weights = scaled_dot_product_attention(tokens, tokens, tokens)
    print("Attention weights (rows = query token):")
    for i, row in enumerate(weights):
        print(f"  token {i}: " + ", ".join(f"{w:.3f}" for w in row))
    print("Contextualised output of token 0:",
          [round(x, 3) for x in outputs[0]])
