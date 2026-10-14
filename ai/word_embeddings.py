"""
Word Embeddings — meaning from the company a word keeps

"You shall know a word by the company it keeps" (Firth). Distributional semantics,
the idea behind word2vec and the embedding layers of every language model,
represents each word by the contexts it appears in. Words used in similar contexts
get similar vectors, so cosine similarity recovers meaning — here straight from
co-occurrence counts, no training loop required. (Function words like "the" are
skipped: they co-occur with everything and would blur the distinctions.)
"""

from __future__ import annotations

from collections import Counter, defaultdict
from math import sqrt


STOPWORDS = {"the", "a", "an", "and", "is", "are", "was", "to", "of", "on",
             "in", "it", "as", "with", "for"}


def build_vectors(sentences: list[str], window: int = 2) -> dict[str, Counter]:
    """Each content word's vector is its co-occurrence counts with content words."""
    vectors: dict[str, Counter] = defaultdict(Counter)
    for sentence in sentences:
        words = sentence.lower().split()
        for i, word in enumerate(words):
            if word in STOPWORDS:
                continue
            lo, hi = max(0, i - window), min(len(words), i + window + 1)
            for j in range(lo, hi):
                if i != j and words[j] not in STOPWORDS:
                    vectors[word][words[j]] += 1
    return vectors


def cosine(a: Counter, b: Counter) -> float:
    shared = set(a) & set(b)
    dot = sum(a[k] * b[k] for k in shared)
    na = sqrt(sum(v * v for v in a.values()))
    nb = sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def most_similar(word: str, vectors: dict[str, Counter], top: int = 3
                 ) -> list[tuple[str, float]]:
    scores = [(other, cosine(vectors[word], vectors[other]))
              for other in vectors if other != word]
    return sorted(scores, key=lambda kv: kv[1], reverse=True)[:top]


if __name__ == "__main__":
    corpus = [
        "the cat chased the mouse",
        "the dog chased the cat",
        "the cat and the dog are playful pets",
        "the dog is a playful loyal pet",
        "the cat is a quiet pet",
        "the king ruled the wealthy kingdom",
        "the queen ruled the peaceful kingdom",
        "the king and the queen ruled the kingdom",
        "the queen wears a royal crown",
        "the king wears a royal crown",
    ]
    vectors = build_vectors(corpus)

    print("Word embeddings from co-occurrence (cosine similarity)\n")
    for query in ("cat", "king", "ruled"):
        sims = most_similar(query, vectors)
        pretty = ", ".join(f"{w} ({s:.2f})" for w, s in sims)
        print(f"  most similar to '{query}': {pretty}")

    print(f"\n  similarity(cat, dog)    = {cosine(vectors['cat'], vectors['dog']):.2f}")
    print(f"  similarity(king, queen) = {cosine(vectors['king'], vectors['queen']):.2f}")
    print(f"  similarity(cat, king)   = {cosine(vectors['cat'], vectors['king']):.2f}")
    print("\n  Within-topic words (cat/dog, king/queen) are far more similar than")
    print("  across-topic ones — distributional meaning, the basis of embeddings.")
