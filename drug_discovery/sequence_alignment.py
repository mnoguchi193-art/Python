"""
Sequence alignment — Needleman-Wunsch / 配列アラインメント

Global pairwise alignment of biological sequences (DNA, protein). Used in
drug discovery to identify drug targets by homology and to compare protein
sequences. Dynamic programming, standard library only.
"""


def needleman_wunsch(
    seq1: str,
    seq2: str,
    match: int = 1,
    mismatch: int = -1,
    gap: int = -2,
) -> tuple[str, str, int]:
    """Return (aligned1, aligned2, score) for the optimal global alignment."""
    n, m = len(seq1), len(seq2)
    # Score matrix with gap-initialised first row/column.
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        dp[i][0] = i * gap
    for j in range(1, m + 1):
        dp[0][j] = j * gap

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            s = match if seq1[i - 1] == seq2[j - 1] else mismatch
            dp[i][j] = max(
                dp[i - 1][j - 1] + s,   # diagonal: align
                dp[i - 1][j] + gap,     # up: gap in seq2
                dp[i][j - 1] + gap,     # left: gap in seq1
            )

    # Traceback from the bottom-right corner.
    a1, a2 = [], []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0:
            s = match if seq1[i - 1] == seq2[j - 1] else mismatch
            if dp[i][j] == dp[i - 1][j - 1] + s:
                a1.append(seq1[i - 1]); a2.append(seq2[j - 1]); i -= 1; j -= 1
                continue
        if i > 0 and dp[i][j] == dp[i - 1][j] + gap:
            a1.append(seq1[i - 1]); a2.append("-"); i -= 1
        else:
            a1.append("-"); a2.append(seq2[j - 1]); j -= 1

    return "".join(reversed(a1)), "".join(reversed(a2)), dp[n][m]


def identity(aligned1: str, aligned2: str) -> float:
    """Fraction of aligned columns with matching residues."""
    if not aligned1:
        return 0.0
    matches = sum(1 for a, b in zip(aligned1, aligned2) if a == b and a != "-")
    return matches / len(aligned1)


if __name__ == "__main__":
    a1, a2, score = needleman_wunsch("GATTACA", "GCATGCU")
    print(a1)
    print(a2)
    print(f"Score: {score}")
    print(f"Identity: {identity(a1, a2):.1%}")
