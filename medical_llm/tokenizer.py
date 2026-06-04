"""
BPE tokenizer — Byte-Pair Encoding / バイトペア符号化トークナイザ

LLMs do not read raw characters; they read sub-word tokens. BPE learns a
vocabulary by repeatedly merging the most frequent adjacent symbol pair,
striking a balance between character- and word-level units. This lets a model
handle rare medical terms ("pneumonoconiosis") from familiar fragments.
Standard library only.
"""

from collections import Counter


class BPETokenizer:
    def __init__(self, num_merges: int = 10) -> None:
        self.num_merges = num_merges
        self.merges: list[tuple[str, str]] = []

    @staticmethod
    def _apply(symbols: list[str], pair: tuple[str, str]) -> list[str]:
        merged: list[str] = []
        i = 0
        while i < len(symbols):
            if i < len(symbols) - 1 and (symbols[i], symbols[i + 1]) == pair:
                merged.append(symbols[i] + symbols[i + 1])
                i += 2
            else:
                merged.append(symbols[i])
                i += 1
        return merged

    def train(self, corpus: list[str]) -> "BPETokenizer":
        freqs = Counter(corpus)
        words = {w: list(w) + ["</w>"] for w in freqs}
        for _ in range(self.num_merges):
            pairs: Counter[tuple[str, str]] = Counter()
            for word, freq in freqs.items():
                symbols = words[word]
                for i in range(len(symbols) - 1):
                    pairs[(symbols[i], symbols[i + 1])] += freq
            if not pairs:
                break
            best = pairs.most_common(1)[0][0]
            self.merges.append(best)
            for word in words:
                words[word] = self._apply(words[word], best)
        return self

    def encode(self, word: str) -> list[str]:
        """Tokenise a single word into learned sub-word units."""
        symbols = list(word) + ["</w>"]
        for pair in self.merges:
            symbols = self._apply(symbols, pair)
        return symbols


if __name__ == "__main__":
    corpus = ["cardiology"] * 5 + ["cardiac"] * 5 + ["cardiogram"] * 3 + ["logic"] * 4
    tok = BPETokenizer(num_merges=12).train(corpus)
    print("Learned merges:", tok.merges[:8])
    for word in ["cardiac", "cardiogram", "cardiomyopathy"]:
        print(f"  {word!r} -> {tok.encode(word)}")
