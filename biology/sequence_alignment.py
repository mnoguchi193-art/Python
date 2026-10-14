"""
Sequence Alignment — the foundation of bioinformatics

The Needleman-Wunsch algorithm finds the optimal global alignment of two
biological sequences by dynamic programming: it fills a score matrix rewarding
matches and penalizing mismatches and gaps, then traces back the best path. This
is how genomes are compared, mutations spotted, and evolutionary relationships
quantified.
"""

from __future__ import annotations


def needleman_wunsch(a: str, b: str, match: int = 1, mismatch: int = -1,
                     gap: int = -2) -> tuple[str, str, int]:
    """Return (aligned_a, aligned_b, score) for the optimal global alignment."""
    n, m = len(a), len(b)
    h = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        h[i][0] = i * gap
    for j in range(m + 1):
        h[0][j] = j * gap
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            diag = h[i - 1][j - 1] + (match if a[i - 1] == b[j - 1] else mismatch)
            h[i][j] = max(diag, h[i - 1][j] + gap, h[i][j - 1] + gap)

    # Traceback from the bottom-right corner.
    aligned_a, aligned_b = [], []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0 and h[i][j] == h[i - 1][j - 1] + (
                match if a[i - 1] == b[j - 1] else mismatch):
            aligned_a.append(a[i - 1])
            aligned_b.append(b[j - 1])
            i, j = i - 1, j - 1
        elif i > 0 and h[i][j] == h[i - 1][j] + gap:
            aligned_a.append(a[i - 1])
            aligned_b.append("-")
            i -= 1
        else:
            aligned_a.append("-")
            aligned_b.append(b[j - 1])
            j -= 1
    return "".join(reversed(aligned_a)), "".join(reversed(aligned_b)), h[n][m]


if __name__ == "__main__":
    seq1 = "GATTACA"
    seq2 = "GCATGCU"
    a, b, score = needleman_wunsch(seq1, seq2)

    match_line = "".join("|" if x == y and x != "-" else " "
                         for x, y in zip(a, b))
    identity = sum(1 for x, y in zip(a, b) if x == y and x != "-")

    print("Global alignment (Needleman-Wunsch)\n")
    print(f"  {a}")
    print(f"  {match_line}")
    print(f"  {b}\n")
    print(f"  score: {score}")
    print(f"  identity: {identity}/{len(a)} ({identity / len(a):.0%})")
