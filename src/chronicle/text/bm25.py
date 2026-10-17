"""Pure-Python BM25 ranking (no numpy / scikit-learn required).

Used as the retrieval backbone when Sentence-BERT is unavailable (for example
on serverless hosts), and as a lexical signal alongside embeddings.
"""

from __future__ import annotations

import math
import re
from collections import Counter

_TOKEN = re.compile(r"[a-z]+(?:'[a-z]+)?")
_STOP = frozenset(
    "a an and are as at be been but by for from had has have he her his i in into is it its me my of on or our "
    "she so that the their them then there these they this those to was were what when where which who whom "
    "why will with would you your about tell story myth myths".split()
)


def tokenize(text: str) -> list[str]:
    """Lower-case word tokens with stop-words removed and plural 's' folded."""
    out = []
    for tok in _TOKEN.findall(text.lower()):
        if tok in _STOP:
            continue
        if len(tok) > 3 and tok.endswith("s") and not tok.endswith("ss"):
            tok = tok[:-1]
        out.append(tok)
    return out


class BM25:
    """Okapi BM25 over a fixed list of documents."""

    def __init__(self, docs: list[str], k1: float = 1.5, b: float = 0.75) -> None:
        self.k1, self.b = k1, b
        self._tfs = [Counter(tokenize(d)) for d in docs]
        self._lens = [sum(tf.values()) for tf in self._tfs]
        self._avg = (sum(self._lens) / len(docs)) if docs else 0.0
        df: Counter[str] = Counter()
        for tf in self._tfs:
            df.update(tf.keys())
        n = len(docs)
        self._idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}

    def scores(self, query: str) -> list[float]:
        q = tokenize(query)
        out = []
        for tf, ln in zip(self._tfs, self._lens):
            s = 0.0
            norm = self.k1 * (1 - self.b + self.b * ln / self._avg) if self._avg else self.k1
            for t in q:
                f = tf.get(t, 0)
                if f:
                    s += self._idf.get(t, 0.0) * f * (self.k1 + 1) / (f + norm)
            out.append(s)
        return out

    def top(self, query: str, k: int = 3) -> list[tuple[int, float]]:
        """Indices and scores of the best *k* documents with a non-zero score."""
        ranked = sorted(enumerate(self.scores(query)), key=lambda x: x[1], reverse=True)
        return [(i, s) for i, s in ranked[:k] if s > 0]
