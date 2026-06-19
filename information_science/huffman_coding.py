"""
Huffman Coding — optimal lossless compression (source coding)

Shannon's source coding theorem says a source cannot be compressed below its
entropy. Huffman's algorithm builds the optimal prefix-free code that gets as
close as possible: frequent symbols get short codes, rare ones long codes, and
no code is a prefix of another (so decoding is unambiguous). Its average code
length lands within one bit of the entropy bound.
"""

from __future__ import annotations

import heapq
from collections import Counter
from math import log2


def build_codes(text: str) -> dict[str, str]:
    """Huffman codebook mapping each symbol to its bit string."""
    freq = Counter(text)
    if len(freq) == 1:                         # single-symbol edge case
        return {next(iter(freq)): "0"}
    # Heap entries: (frequency, tiebreak, subtree). Subtree is char or (left, right).
    heap = [(f, i, ch) for i, (ch, f) in enumerate(freq.items())]
    heapq.heapify(heap)
    counter = len(heap)
    while len(heap) > 1:
        f1, _, left = heapq.heappop(heap)
        f2, _, right = heapq.heappop(heap)
        heapq.heappush(heap, (f1 + f2, counter, (left, right)))
        counter += 1
    codes: dict[str, str] = {}

    def walk(node, prefix=""):
        if isinstance(node, str):
            codes[node] = prefix
        else:
            walk(node[0], prefix + "0")
            walk(node[1], prefix + "1")

    walk(heap[0][2])
    return codes


def encode(text: str, codes: dict[str, str]) -> str:
    return "".join(codes[ch] for ch in text)


def decode(bits: str, codes: dict[str, str]) -> str:
    inverse = {code: ch for ch, code in codes.items()}
    out, buffer = [], ""
    for bit in bits:
        buffer += bit
        if buffer in inverse:
            out.append(inverse[buffer])
            buffer = ""
    return "".join(out)


if __name__ == "__main__":
    text = ("the quick brown fox jumps over the lazy dog "
            "the dog was not amused and the fox ran away again")
    codes = build_codes(text)
    encoded = encode(text, codes)

    # Information-theoretic baseline.
    freq = Counter(text)
    n = len(text)
    h = sum(-(c / n) * log2(c / n) for c in freq.values())

    print("Huffman coding\n")
    print("  sample codes:", {ch: codes[ch] for ch in list(codes)[:5]})
    print(f"\n  symbols          : {len(freq)} distinct, {n} total")
    print(f"  fixed-length (ASCII): {n * 8} bits")
    print(f"  Huffman encoded    : {len(encoded)} bits")
    print(f"  compression ratio  : {len(encoded) / (n * 8):.1%} of original\n")
    print(f"  avg bits/symbol    : {len(encoded) / n:.3f}")
    print(f"  entropy lower bound : {h:.3f} bits/symbol "
          f"(Huffman is within 1 bit, as guaranteed)")
    print(f"\n  lossless round-trip OK? {decode(encoded, codes) == text}")
