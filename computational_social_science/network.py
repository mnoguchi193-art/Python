"""
Network analysis — undirected graphs / ネットワーク分析

Social networks are central to computational social science. This module
builds a simple undirected graph and computes the descriptive measures used
to characterise social structure: degree centrality, clustering, connected
components, and density. Standard library only.
"""

from collections import deque


class Graph:
    def __init__(self) -> None:
        self._adj: dict[str, set[str]] = {}

    def add_node(self, node: str) -> None:
        self._adj.setdefault(node, set())

    def add_edge(self, u: str, v: str) -> None:
        if u == v:
            return  # ignore self-loops
        self.add_node(u)
        self.add_node(v)
        self._adj[u].add(v)
        self._adj[v].add(u)

    def neighbors(self, node: str) -> set[str]:
        return self._adj[node]

    def nodes(self) -> list[str]:
        return list(self._adj)

    def degree_centrality(self) -> dict[str, float]:
        """Degree normalised by the maximum possible degree (n - 1)."""
        n = len(self._adj)
        if n <= 1:
            return {node: 0.0 for node in self._adj}
        return {node: len(nbrs) / (n - 1) for node, nbrs in self._adj.items()}

    def clustering_coefficient(self, node: str) -> float:
        """Fraction of a node's neighbour pairs that are themselves linked."""
        nbrs = self._adj[node]
        k = len(nbrs)
        if k < 2:
            return 0.0
        links = sum(
            1 for a in nbrs for b in nbrs if a < b and b in self._adj[a]
        )
        return 2 * links / (k * (k - 1))

    def average_clustering(self) -> float:
        if not self._adj:
            return 0.0
        return sum(self.clustering_coefficient(n) for n in self._adj) / len(self._adj)

    def connected_components(self) -> list[set[str]]:
        """Group nodes reachable from one another (BFS)."""
        seen: set[str] = set()
        components: list[set[str]] = []
        for start in self._adj:
            if start in seen:
                continue
            comp: set[str] = set()
            queue = deque([start])
            seen.add(start)
            while queue:
                node = queue.popleft()
                comp.add(node)
                for nbr in self._adj[node]:
                    if nbr not in seen:
                        seen.add(nbr)
                        queue.append(nbr)
            components.append(comp)
        return components

    def density(self) -> float:
        """Ratio of existing edges to all possible edges."""
        n = len(self._adj)
        if n <= 1:
            return 0.0
        edges = sum(len(nbrs) for nbrs in self._adj.values()) / 2
        return 2 * edges / (n * (n - 1))


if __name__ == "__main__":
    g = Graph()
    for u, v in [("A", "B"), ("A", "C"), ("B", "C"), ("C", "D"), ("E", "F")]:
        g.add_edge(u, v)

    print("Degree centrality:")
    for node, c in sorted(g.degree_centrality().items()):
        print(f"  {node}: {c:.3f}")
    print(f"Clustering of C: {g.clustering_coefficient('C'):.3f}")
    print(f"Average clustering: {g.average_clustering():.3f}")
    print(f"Density: {g.density():.3f}")
    print("Connected components:", [sorted(c) for c in g.connected_components()])
