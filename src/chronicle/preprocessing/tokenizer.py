"""Tokenization and text processing for Greek mythology texts.

Provides :class:`MythTokenizer` which wraps NLTK tokenisation, lemmatisation,
and stopword filtering with a custom stopword list tailored for archaic and
mythological English prose.
"""

from __future__ import annotations

import logging
from typing import Sequence

import nltk
from nltk.corpus import stopwords as nltk_stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Ensure required NLTK data packages are available
# ---------------------------------------------------------------------------
_REQUIRED_NLTK_DATA = ["punkt", "punkt_tab", "stopwords", "wordnet", "omw-1.4"]


def _ensure_nltk_data() -> None:
    """Download NLTK data packages if they are not already present."""
    for package in _REQUIRED_NLTK_DATA:
        try:
            nltk.data.find(f"tokenizers/{package}" if "punkt" in package else package)
        except LookupError:
            try:
                nltk.download(package, quiet=True)
            except Exception:  # noqa: BLE001
                logger.warning("Failed to download NLTK package '%s'", package)


_ensure_nltk_data()

# ---------------------------------------------------------------------------
# Custom mythology stopwords
# ---------------------------------------------------------------------------
# Archaic English words and common narrative verbs that appear frequently in
# mythology texts but carry little semantic value for analysis.
MYTHOLOGY_STOPWORDS: frozenset[str] = frozenset(
    {
        # Archaic pronouns & determiners
        "thou",
        "thee",
        "thy",
        "thine",
        "ye",
        "thyself",
        # Archaic verb forms
        "hath",
        "hast",
        "doth",
        "dost",
        "shalt",
        "wilt",
        "wouldst",
        "shouldst",
        "art",  # 'thou art'
        "wert",
        # Archaic adverbs & conjunctions
        "thus",
        "hence",
        "thereof",
        "therein",
        "thereon",
        "thereof",
        "thereupon",
        "whereupon",
        "whence",
        "hither",
        "thither",
        "herein",
        "thereof",
        "withal",
        "forsooth",
        "nay",
        "aye",
        "verily",
        "lo",
        "behold",
        # Common narrative verbs
        "said",
        "told",
        "spoke",
        "replied",
        "answered",
        "cried",
        "exclaimed",
        "went",
        "came",
        "upon",
        "took",
        "gave",
        "made",
        "saw",
        "knew",
        "heard",
        # Filler words in mythology retellings
        "also",
        "yet",
        "still",
        "even",
        "much",
        "many",
        "great",
        "would",
        "could",
        "might",
        "shall",
        "one",
        "may",
    }
)


class MythTokenizer:
    """Tokenizer and text processor tuned for mythology corpus analysis.

    Combines NLTK's word/sentence tokenizers with a mythology-specific
    stopword list and WordNet lemmatisation.

    Args:
        extra_stopwords: Additional stopwords to include beyond NLTK
            defaults and the built-in mythology set.

    Example::

        tok = MythTokenizer()
        tokens = tok.process("Zeus hurled his thunderbolts upon the Titans.")
        # -> ['zeus', 'hurl', 'thunderbolt', 'titan']
    """

    def __init__(self, extra_stopwords: Sequence[str] | None = None) -> None:
        self._lemmatizer = WordNetLemmatizer()

        # Build combined stopword set
        try:
            base_stopwords = set(nltk_stopwords.words("english"))
        except LookupError:
            logger.warning("NLTK English stopwords not found; using empty base set")
            base_stopwords = set()

        self._stopwords: frozenset[str] = frozenset(
            base_stopwords | MYTHOLOGY_STOPWORDS | set(extra_stopwords or [])
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def tokenize(self, text: str, remove_stopwords: bool = True) -> list[str]:
        """Tokenize *text* into words using NLTK's word tokenizer.

        Punctuation tokens are excluded from the result.

        Args:
            text: Input text string.
            remove_stopwords: Whether to filter out stopwords (default: True).

        Returns:
            List of word tokens (original casing preserved).

        Raises:
            TypeError: If *text* is not a string.
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected str, got {type(text).__name__}")

        tokens = word_tokenize(text)
        # Filter out pure punctuation tokens
        tokens = [t for t in tokens if any(c.isalnum() for c in t)]
        if remove_stopwords:
            tokens = [t for t in tokens if t.lower() not in self._stopwords]
        return tokens

    def lemmatize(self, text: str) -> list[str]:
        """Lemmatize *text* and return a list of lemmas.

        Each word is tokenized, lowercased, and lemmatized using the
        WordNet lemmatizer.

        Args:
            text: Input text string.

        Returns:
            List of lemmatized word tokens.
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected str, got {type(text).__name__}")

        tokens = self.tokenize(text, remove_stopwords=False)
        return [self._lemmatizer.lemmatize(t.lower()) for t in tokens]

    def remove_stopwords(self, tokens: list[str]) -> list[str]:
        """Remove stopwords from a token list.

        Uses the combined set of NLTK English stopwords, mythology-specific
        stopwords, and any extra stopwords supplied at initialisation.

        Args:
            tokens: List of word tokens.

        Returns:
            Filtered list with stopwords removed.
        """
        return [t for t in tokens if t.lower() not in self._stopwords]

    def process(self, text: str) -> list[str]:
        """Apply the full processing pipeline to *text*.

        Pipeline:
            1. Tokenize into words.
            2. Lowercase all tokens.
            3. Remove stopwords.
            4. Lemmatize remaining tokens.

        Args:
            text: Input text string.

        Returns:
            List of processed (lowercased, filtered, lemmatized) tokens.
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected str, got {type(text).__name__}")

        if not text.strip():
            return []

        tokens = self.tokenize(text, remove_stopwords=False)
        lowered = [t.lower() for t in tokens]
        filtered = self.remove_stopwords(lowered)
        lemmas = [self._lemmatizer.lemmatize(t) for t in filtered]
        # Remove any single-character tokens that slipped through
        return [t for t in lemmas if len(t) > 1]

    def get_sentences(self, text: str) -> list[str]:
        """Split *text* into sentences using NLTK's sentence tokenizer.

        Args:
            text: Input text string.

        Returns:
            List of sentence strings.

        Raises:
            TypeError: If *text* is not a string.
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected str, got {type(text).__name__}")

        if not text.strip():
            return []

        return sent_tokenize(text)

    @property
    def stopwords(self) -> frozenset[str]:
        """Return the combined stopword set."""
        return self._stopwords
