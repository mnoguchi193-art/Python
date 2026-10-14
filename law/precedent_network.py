"""
Precedent Networks — ranking case law by citation influence

Legal informatics treats case law as a directed graph: a judgment *cites*
earlier judgments. The most authoritative precedents are those cited (directly
or transitively) by many other influential cases. That is exactly what PageRank
measures, so we can compute the "leading cases" purely from citation structure.

The graph maps each case to the list of earlier cases it cites.
"""

from __future__ import annotations


Graph = dict[str, list[str]]


def pagerank(graph: Graph, damping: float = 0.85,
             max_iter: int = 100, tol: float = 1e-9) -> dict[str, float]:
    """Influence score per case. Higher = more authoritative precedent."""
    nodes = list(graph)
    n = len(nodes)
    rank = {node: 1 / n for node in nodes}

    for _ in range(max_iter):
        # Dangling cases (cite nothing) leak rank; redistribute it uniformly.
        dangling = sum(rank[u] for u in nodes if not graph[u])
        new = {}
        for v in nodes:
            inflow = sum(
                rank[u] / len(graph[u])
                for u in nodes if v in graph[u]
            )
            new[v] = (1 - damping) / n + damping * (inflow + dangling / n)
        if max(abs(new[v] - rank[v]) for v in nodes) < tol:
            rank = new
            break
        rank = new
    return rank


def leading_cases(graph: Graph, top: int = 5) -> list[tuple[str, float]]:
    scores = pagerank(graph)
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:top]


if __name__ == "__main__":
    # A stylized U.S. constitutional-law citation graph (newer cites older).
    citations: Graph = {
        "Marbury (1803)": [],
        "McCulloch (1819)": ["Marbury (1803)"],
        "Plessy (1896)": ["Marbury (1803)"],
        "Brown (1954)": ["Marbury (1803)", "Plessy (1896)"],
        "Griswold (1965)": ["Marbury (1803)", "Brown (1954)"],
        "Roe (1973)": ["Brown (1954)", "Griswold (1965)"],
        "Obergefell (2015)": ["Brown (1954)", "Roe (1973)", "Griswold (1965)"],
    }

    print("Most influential precedents by citation PageRank:\n")
    for rank, (case, score) in enumerate(leading_cases(citations), start=1):
        print(f"  {rank}. {case:<20} {score:.4f}")

    print("\nFoundational cases attract rank even when they cite nothing —"
          "\nauthority flows backward along citations to the precedents.")
