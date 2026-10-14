"""
Byte-Pair Encoding — the tokenizer behind large language models

Before an LLM sees text it must be split into tokens. GPT-style models use
byte-pair encoding (BPE): start from individual characters and repeatedly merge
the most frequent adjacent pair into a new symbol. Common words become single
tokens, while rare or unseen words gracefully fall back to subword pieces — so
the vocabulary stays fixed yet nothing is ever out-of-vocabulary.
"""

from __future__ import annotations

from collections import Counter


def learn_bpe(word_freqs: dict[str, int], num_merges: int) -> list[tuple[str, str]]:
    """Learn an ordered list of merge rules from word frequencies."""
    words = {tuple(list(w) + ["</w>"]): c for w, c in word_freqs.items()}
    merges = []
    for _ in range(num_merges):
        pairs: Counter = Counter()
        for symbols, count in words.items():
            for i in range(len(symbols) - 1):
                pairs[(symbols[i], symbols[i + 1])] += count
        if not pairs:
            break
        best = max(pairs, key=pairs.get)
        merges.append(best)
        words = {_apply(symbols, best): c for symbols, c in words.items()}
    return merges


def _apply(symbols: tuple[str, ...], pair: tuple[str, str]) -> tuple[str, ...]:
    out, i = [], 0
    while i < len(symbols):
        if i < len(symbols) - 1 and (symbols[i], symbols[i + 1]) == pair:
            out.append(symbols[i] + symbols[i + 1])
            i += 2
        else:
            out.append(symbols[i])
            i += 1
    return tuple(out)


def encode(word: str, merges: list[tuple[str, str]]) -> list[str]:
    symbols = tuple(list(word) + ["</w>"])
    for pair in merges:
        symbols = _apply(symbols, pair)
    return list(symbols)


if __name__ == "__main__":
    corpus = {"low": 5, "lower": 2, "newest": 6, "widest": 3}
    merges = learn_bpe(corpus, num_merges=10)

    print("Byte-pair encoding\n")
    print(f"  training corpus: {corpus}\n")
    print("  learned merges (most frequent pair first):")
    for i, (a, b) in enumerate(merges, 1):
        print(f"    {i:>2}. {a!r} + {b!r} -> {a + b!r}")

    print("\n  Tokenization:")
    for word in ("newest", "lowest", "slower"):
        print(f"    {word:<8} -> {encode(word, merges)}")
    print("\n  Frequent words collapse to few tokens; an unseen word like 'slower'")
    print("  still tokenizes into known subword pieces — never out-of-vocabulary.")
