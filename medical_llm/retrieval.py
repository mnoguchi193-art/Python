"""
Retrieval-Augmented Generation (RAG) / 検索拡張生成

Medical LLMs hallucinate when they answer from parametric memory alone. RAG
grounds the answer in a trusted knowledge base: the query is matched against
documents by TF-IDF cosine similarity, and the top passages are returned as
context for the model to cite. Standard library only.
"""

import math
import re
from collections import Counter


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text.lower())


class TfidfRetriever:
    def __init__(self, documents: list[str]) -> None:
        self.documents = documents
        self._tokens = [_tokenize(d) for d in documents]
        self._idf = self._compute_idf()
        self._vectors = [self._vectorize(toks) for toks in self._tokens]

    def _compute_idf(self) -> dict[str, float]:
        n = len(self.documents)
        df: Counter[str] = Counter()
        for toks in self._tokens:
            df.update(set(toks))
        # Smoothed idf keeps weights positive even for ubiquitous terms.
        return {t: math.log((1 + n) / (1 + d)) + 1 for t, d in df.items()}

    def _vectorize(self, tokens: list[str]) -> dict[str, float]:
        if not tokens:
            return {}
        tf = Counter(tokens)
        total = len(tokens)
        return {t: (c / total) * self._idf.get(t, 0.0) for t, c in tf.items()}

    @staticmethod
    def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
        if not a or not b:
            return 0.0
        common = set(a) & set(b)
        dot = sum(a[t] * b[t] for t in common)
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        return dot / (na * nb) if na and nb else 0.0

    def retrieve(self, query: str, k: int = 3) -> list[tuple[str, float]]:
        """Return the top-k documents most similar to the query."""
        qvec = self._vectorize(_tokenize(query))
        scored = [
            (doc, self._cosine(qvec, dvec))
            for doc, dvec in zip(self.documents, self._vectors)
        ]
        return sorted(scored, key=lambda ds: ds[1], reverse=True)[:k]


def build_prompt(query: str, contexts: list[str]) -> str:
    """Assemble a grounded prompt instructing the model to cite context."""
    joined = "\n".join(f"[{i + 1}] {c}" for i, c in enumerate(contexts))
    return (
        "Answer the question using ONLY the context below. "
        "If the context is insufficient, say so.\n\n"
        f"Context:\n{joined}\n\nQuestion: {query}\nAnswer:"
    )


if __name__ == "__main__":
    kb = [
        "Type 2 diabetes is managed with metformin, diet, and exercise.",
        "Hypertension is treated with ACE inhibitors and lifestyle changes.",
        "Metformin can cause gastrointestinal side effects and lactic acidosis.",
        "Influenza presents with fever, cough, and body aches.",
    ]
    retriever = TfidfRetriever(kb)
    query = "What are the side effects of metformin?"
    hits = retriever.retrieve(query, k=2)
    for doc, score in hits:
        print(f"  {score:.3f}  {doc}")
    print("\n--- grounded prompt ---")
    print(build_prompt(query, [doc for doc, _ in hits]))
