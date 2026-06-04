"""
Text analysis — bag of words & TF-IDF / テキスト分析

Large text corpora (social media, news, parliamentary records) are a primary
data source in computational social science. This module tokenises documents
and ranks terms by TF-IDF, which down-weights words common across the whole
corpus. Standard library only.
"""

import math
import re
from collections import Counter


def tokenize(text: str) -> list[str]:
    """Lowercase word tokens."""
    return re.findall(r"\b\w+\b", text.lower())


def term_frequency(text: str) -> dict[str, float]:
    """Relative frequency of each term within a single document."""
    tokens = tokenize(text)
    if not tokens:
        return {}
    counts = Counter(tokens)
    total = len(tokens)
    return {term: n / total for term, n in counts.items()}


def inverse_document_frequency(documents: list[str]) -> dict[str, float]:
    """idf(t) = ln(N / df(t)); rarer terms score higher."""
    n_docs = len(documents)
    doc_freq: Counter[str] = Counter()
    for doc in documents:
        doc_freq.update(set(tokenize(doc)))
    return {term: math.log(n_docs / df) for term, df in doc_freq.items()}


def tf_idf(documents: list[str]) -> list[dict[str, float]]:
    """TF-IDF weight of every term in every document."""
    idf = inverse_document_frequency(documents)
    result = []
    for doc in documents:
        tf = term_frequency(doc)
        result.append({term: weight * idf[term] for term, weight in tf.items()})
    return result


def top_terms(scores: dict[str, float], k: int = 3) -> list[tuple[str, float]]:
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:k]


if __name__ == "__main__":
    corpus = [
        "the economy grew as inflation slowed",
        "the central bank raised the interest rate",
        "inflation and the interest rate shape the economy",
    ]
    for i, scores in enumerate(tf_idf(corpus)):
        print(f"Doc {i} top terms:", top_terms(scores))
