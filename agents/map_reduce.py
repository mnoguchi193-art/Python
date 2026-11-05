"""
Map-Reduce Exploration (マップ・リデュース型の探索) — broad fan-out, then
synthesis

A common reason to spawn many subagents is a broad sweep: split a large
corpus into shards, have one worker summarise each shard independently
(map), then merge the partial findings into one answer (reduce).  No
single worker holds the whole corpus, and the coordinator keeps only the
merged result — the pattern behind "search widely, report the conclusion".

Here each worker counts word frequencies in one document (map); the
reducer sums the partial counts into a global ranking.  Mapping runs in
parallel threads via the standard library.
"""

from __future__ import annotations
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from typing import Callable


# ── Map and reduce steps ──────────────────────────────────────────────────
def map_document(doc: str) -> Counter:
    """One subagent's isolated view: just its own shard."""
    words = (w.strip(".,!?;:'\"").lower() for w in doc.split())
    return Counter(w for w in words if w)


def reduce_counts(partials: list[Counter]) -> Counter:
    total: Counter = Counter()
    for c in partials:
        total.update(c)
    return total


def map_reduce(docs: list[str], mapper: Callable[[str], Counter],
               max_workers: int = 4) -> Counter:
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        partials = list(pool.map(mapper, docs))
    return reduce_counts(partials)


# ── Demo ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    corpus = [
        "the scientist forms a hypothesis and tests the hypothesis",
        "an agent delegates the task to another agent and waits",
        "data from the experiment updates the model of the system",
        "the model predicts data the agent has not yet seen",
        "a hypothesis the data rejects is replaced by a new hypothesis",
    ]
    print(f"Corpus of {len(corpus)} documents, mapped by independent workers.\n")

    partials = [map_document(d) for d in corpus]
    print("Each worker reports only its own shard's top word:")
    for i, c in enumerate(partials):
        word, count = c.most_common(1)[0]
        print(f"  doc {i}: '{word}' x{count}")

    merged = map_reduce(corpus, map_document)
    print("\nReducer merges all partial counts into a global ranking:")
    for word, count in merged.most_common(5):
        bar = "#" * count
        print(f"  {word:12s} {bar} {count}")

    print("\nNo worker saw the whole corpus; the coordinator keeps only the")
    print("merged ranking — fan out to read widely, reduce to one answer.")
