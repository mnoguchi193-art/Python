"""
Social Network Analysis — centrality and brokerage

Who matters in a social network, and why? Degree counts your friends, but
*betweenness* counts how often you sit on the shortest path between others —
the structural signature of a broker who bridges otherwise separate groups
(Granovetter's "strength of weak ties").

Graph is an undirected adjacency map: {person: [friends...]}.
"""

from __future__ import annotations

from collections import deque


Graph = dict[str, list[str]]


def degree_centrality(graph: Graph) -> dict[str, float]:
    n = len(graph)
    return {v: len(graph[v]) / (n - 1) for v in graph}


def closeness_centrality(graph: Graph) -> dict[str, float]:
    """Inverse of mean shortest-path distance to all reachable others."""
    result = {}
    for source in graph:
        dist = _bfs_distances(graph, source)
        reachable = [d for v, d in dist.items() if v != source]
        if reachable:
            result[source] = len(reachable) / sum(reachable)
        else:
            result[source] = 0.0
    return result


def betweenness_centrality(graph: Graph) -> dict[str, float]:
    """Brandes' algorithm, normalized for an undirected graph."""
    cb = {v: 0.0 for v in graph}
    for s in graph:
        stack, pred = [], {v: [] for v in graph}
        sigma = dict.fromkeys(graph, 0.0)
        dist = dict.fromkeys(graph, -1)
        sigma[s], dist[s] = 1.0, 0
        queue = deque([s])
        while queue:
            v = queue.popleft()
            stack.append(v)
            for w in graph[v]:
                if dist[w] < 0:
                    dist[w] = dist[v] + 1
                    queue.append(w)
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    pred[w].append(v)
        delta = dict.fromkeys(graph, 0.0)
        while stack:
            w = stack.pop()
            for v in pred[w]:
                delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w])
            if w != s:
                cb[w] += delta[w]

    n = len(graph)
    scale = 2 / ((n - 1) * (n - 2)) if n > 2 else 1.0
    return {v: cb[v] / 2 * scale for v in graph}   # /2 for undirected double count


def clustering_coefficient(graph: Graph, node: str) -> float:
    """Fraction of a node's friend-pairs that are themselves friends (triadic closure)."""
    friends = graph[node]
    k = len(friends)
    if k < 2:
        return 0.0
    links = sum(1 for i, a in enumerate(friends) for b in friends[i + 1:]
                if b in graph[a])
    return 2 * links / (k * (k - 1))


def _bfs_distances(graph: Graph, source: str) -> dict[str, int]:
    dist = {source: 0}
    queue = deque([source])
    while queue:
        v = queue.popleft()
        for w in graph[v]:
            if w not in dist:
                dist[w] = dist[v] + 1
                queue.append(w)
    return dist


if __name__ == "__main__":
    # Two friend clusters bridged by a single broker, "Dana".
    graph: Graph = {
        "Ann": ["Bob", "Cy", "Dana"],
        "Bob": ["Ann", "Cy"],
        "Cy":  ["Ann", "Bob"],
        "Dana": ["Ann", "Eli"],          # the bridge
        "Eli": ["Dana", "Fay", "Gil"],
        "Fay": ["Eli", "Gil"],
        "Gil": ["Eli", "Fay"],
    }

    deg = degree_centrality(graph)
    clo = closeness_centrality(graph)
    bet = betweenness_centrality(graph)

    print("Person   Degree  Closeness  Betweenness")
    for v in graph:
        print(f"  {v:<5}  {deg[v]:6.2f}  {clo[v]:9.2f}  {bet[v]:11.2f}")

    broker = max(bet, key=bet.get)
    print(f"\nStructural broker: {broker} — modest degree, but the highest")
    print("betweenness because every cross-group path runs through them.")
