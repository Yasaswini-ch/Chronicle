"""Text cleaning pipeline for Greek mythology texts.

Provides a configurable cleaning pipeline that strips HTML, removes footnotes
and bracketed references, normalizes whitespace and punctuation, and fixes
common encoding issues found in digitized classical texts.
"""

from __future__ import annotations

import html
import re
import unicodedata


class TextCleaner:
    """Multi-stage text cleaning pipeline for mythology corpus documents.

    The cleaner applies a sequence of transformations to raw text to produce
    a normalized version suitable for downstream NLP processing. Each stage
    can also be invoked independently.

    Example::

        cleaner = TextCleaner()
        raw = "<p>Zeus&mdash;king of the gods[1]</p>"
        cleaned = cleaner.clean(raw)
        # -> "Zeus—king of the gods"
    """

    # Regex patterns compiled once at class level for performance
    _HTML_TAG_RE = re.compile(r"<[^>]+>", re.DOTALL)
    _HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
    _CDATA_RE = re.compile(r"<!\[CDATA\[.*?\]\]>", re.DOTALL)

    # Footnote markers: [1], [23], [iv], [*], [†], superscript digits
    _FOOTNOTE_BRACKET_RE = re.compile(
        r"\[\s*(?:\d+|[ivxlcdm]+|[*†‡§¶])\s*\]", re.IGNORECASE
    )
    # Superscript digits (Unicode range)
    _SUPERSCRIPT_DIGIT_RE = re.compile(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]+")
    # Inline footnote text patterns like "(see note 3)" or "(cf. footnote 12)"
    _INLINE_FOOTNOTE_RE = re.compile(
        r"\(\s*(?:see\s+)?(?:note|footnote|fn\.?)\s*\d+\s*\)", re.IGNORECASE
    )

    # Whitespace normalization
    _MULTI_SPACE_RE = re.compile(r"[ \t]+")
    _MULTI_NEWLINE_RE = re.compile(r"\n{3,}")
    _TRAILING_SPACE_RE = re.compile(r"[ \t]+$", re.MULTILINE)
    _LEADING_SPACE_RE = re.compile(r"^[ \t]+", re.MULTILINE)

    # Punctuation normalization maps
    _QUOTE_MAP: dict[str, str] = {
        "\u2018": "'",   # '
        "\u2019": "'",   # '
        "\u201a": "'",   # ‚
        "\u201b": "'",   # ‛
        "\u201c": '"',   # "
        "\u201d": '"',   # "
        "\u201e": '"',   # „
        "\u201f": '"',   # ‟
        "\u2039": "'",   # ‹
        "\u203a": "'",   # ›
        "\u00ab": '"',   # «
        "\u00bb": '"',   # »
    }

    _DASH_MAP: dict[str, str] = {
        "\u2013": "—",   # en-dash -> em-dash
        "\u2014": "—",   # em-dash (keep)
        "\u2015": "—",   # horizontal bar -> em-dash
        "\u2012": "-",   # figure dash -> hyphen
        "\u2010": "-",   # hyphen (keep)
        "\u2011": "-",   # non-breaking hyphen -> hyphen
    }

    _ELLIPSIS_RE = re.compile(r"\.{3,}")
    _MULTI_DASH_RE = re.compile(r"-{2,}")

    def clean(self, text: str) -> str:
        """Apply the full cleaning pipeline to a text.

        Pipeline order:
            1. Fix encoding issues (HTML entities, mojibake)
            2. Remove HTML/XML tags
            3. Remove footnotes and references
            4. Normalize punctuation
            5. Normalize whitespace

        Args:
            text: Raw input text, potentially containing HTML, footnotes,
                  and encoding artifacts.

        Returns:
            Cleaned and normalized text string.

        Raises:
            TypeError: If *text* is not a string.
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected str, got {type(text).__name__}")

        if not text.strip():
            return ""

        result = self._fix_encoding(text)
        result = self.remove_html(result)
        result = self.remove_footnotes(result)
        result = self.normalize_punctuation(result)
        result = self.normalize_whitespace(result)
        return result

    # ------------------------------------------------------------------
    # Individual pipeline stages
    # ------------------------------------------------------------------

    def remove_html(self, text: str) -> str:
        """Strip HTML and XML tags from *text*.

        Also removes HTML comments and CDATA sections. After tag removal
        the text is stripped of any residual empty lines caused by block
        elements.

        Args:
            text: Input text potentially containing HTML markup.

        Returns:
            Text with all HTML/XML tags removed.
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected str, got {type(text).__name__}")

        result = self._HTML_COMMENT_RE.sub("", text)
        result = self._CDATA_RE.sub("", result)
        result = self._HTML_TAG_RE.sub("", result)
        return result

    def remove_footnotes(self, text: str) -> str:
        """Remove footnote markers and bracketed references from *text*.

        Handles:
            - Bracketed numbers/roman numerals: ``[1]``, ``[iv]``
            - Bracketed symbols: ``[*]``, ``[†]``
            - Unicode superscript digits
            - Inline footnote references: ``(see note 3)``

        Args:
            text: Input text potentially containing footnote markers.

        Returns:
            Text with footnote markers removed.
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected str, got {type(text).__name__}")

        result = self._FOOTNOTE_BRACKET_RE.sub("", text)
        result = self._SUPERSCRIPT_DIGIT_RE.sub("", result)
        result = self._INLINE_FOOTNOTE_RE.sub("", result)
        return result

    def normalize_whitespace(self, text: str) -> str:
        """Collapse multiple spaces and newlines into single occurrences.

        - Multiple spaces/tabs on a line become a single space.
        - Three or more consecutive newlines become two (one blank line).
        - Leading/trailing whitespace on each line is stripped.
        - The entire string is stripped.

        Args:
            text: Input text with potentially irregular whitespace.

        Returns:
            Text with normalized whitespace.
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected str, got {type(text).__name__}")

        result = self._TRAILING_SPACE_RE.sub("", text)
        result = self._LEADING_SPACE_RE.sub("", result)
        result = self._MULTI_SPACE_RE.sub(" ", result)
        result = self._MULTI_NEWLINE_RE.sub("\n\n", result)
        return result.strip()

    def normalize_punctuation(self, text: str) -> str:
        """Standardize quotation marks, dashes, and other punctuation.

        - Curly/fancy quotes → straight quotes.
        - Various Unicode dashes → em-dash or hyphen.
        - Multiple dots → ellipsis character (``…``).
        - Multiple dashes → em-dash.

        Args:
            text: Input text with potentially mixed punctuation styles.

        Returns:
            Text with standardized punctuation.
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected str, got {type(text).__name__}")

        # Replace curly quotes
        for char, replacement in self._QUOTE_MAP.items():
            text = text.replace(char, replacement)

        # Replace dashes
        for char, replacement in self._DASH_MAP.items():
            text = text.replace(char, replacement)

        # Normalize ellipses
        text = self._ELLIPSIS_RE.sub("…", text)

        # Collapse multiple dashes
        text = self._MULTI_DASH_RE.sub("—", text)

        return text

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _fix_encoding(text: str) -> str:
        """Fix common encoding artifacts.

        - Decode HTML entities (``&amp;``, ``&#39;``, etc.).
        - Normalize Unicode to NFC form to merge combining characters.
        - Replace common mojibake sequences.
        """
        # Decode HTML entities (run twice for double-encoded entities)
        result = html.unescape(html.unescape(text))

        # Normalize Unicode to NFC
        result = unicodedata.normalize("NFC", result)

        # Common mojibake fixes (UTF-8 decoded as Latin-1)
        _mojibake_map: dict[str, str] = {
            "â\x80\x93": "–",
            "â\x80\x94": "—",
            "â\x80\x98": "'",
            "â\x80\x99": "'",
            "â\x80\x9c": "\u201c",
            "â\x80\x9d": "\u201d",
            "Ã©": "é",
            "Ã¨": "è",
            "Ã¼": "ü",
        }
        for bad, good in _mojibake_map.items():
            result = result.replace(bad, good)

        return result
