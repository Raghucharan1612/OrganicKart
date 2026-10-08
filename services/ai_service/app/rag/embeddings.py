import math
import re
from typing import Sequence


class LocalEmbeddingService:
    """
    Lightweight, zero-dependency local embedding generator using TF-IDF n-gram 
    vector representations with L2 normalization for cosine similarity search.
    """

    def __init__(self, vocabulary: Sequence[str] | None = None):
        self.vocabulary = list(vocabulary) if vocabulary else []
        self._idf: dict[str, float] = {}

    def _tokenize(self, text: str) -> list[str]:
        words = re.findall(r"\b\w+\b", text.lower())
        bigrams = [f"{words[i]}_{words[i+1]}" for i in range(len(words) - 1)]
        return words + bigrams

    def fit(self, documents: list[str]) -> None:
        doc_count = len(documents)
        if doc_count == 0:
            return

        term_doc_counts: dict[str, int] = {}
        for doc in documents:
            tokens = set(self._tokenize(doc))
            for token in tokens:
                term_doc_counts[token] = term_doc_counts.get(token, 0) + 1

        self.vocabulary = sorted(term_doc_counts.keys())
        self._idf = {
            term: math.log((1 + doc_count) / (1 + count)) + 1.0
            for term, count in term_doc_counts.items()
        }

    def embed_text(self, text: str) -> list[float]:
        if not self.vocabulary:
            tokens = self._tokenize(text)
            self.vocabulary = sorted(set(tokens))
            self._idf = {t: 1.0 for t in self.vocabulary}

        tokens = self._tokenize(text)
        term_freqs: dict[str, int] = {}
        for token in tokens:
            term_freqs[token] = term_freqs.get(token, 0) + 1

        vector: list[float] = []
        for term in self.vocabulary:
            tf = term_freqs.get(term, 0)
            idf = self._idf.get(term, 1.0)
            vector.append(tf * idf)

        # L2 norm
        norm = math.sqrt(sum(val * val for val in vector))
        if norm > 0:
            vector = [val / norm for val in vector]

        return vector

    @staticmethod
    def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
        if len(vec1) != len(vec2) or not vec1:
            return 0.0
        return sum(a * b for a, b in zip(vec1, vec2))
