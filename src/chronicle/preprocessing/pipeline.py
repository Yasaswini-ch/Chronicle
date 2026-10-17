"""Preprocessing pipeline orchestrator.

Chains :class:`~chronicle.preprocessing.cleaner.TextCleaner`,
:class:`~chronicle.preprocessing.alias_resolver.AliasResolver`, and
:class:`~chronicle.preprocessing.tokenizer.MythTokenizer` into a single
pipeline that transforms raw myth texts into analysis-ready documents.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .alias_resolver import AliasResolver
from .cleaner import TextCleaner
from .tokenizer import MythTokenizer

logger = logging.getLogger(__name__)


class PreprocessingPipeline:
    """End-to-end preprocessing pipeline for Greek mythology texts.

    Orchestrates three stages:

    1. **Cleaning** — HTML removal, footnote stripping, whitespace and
       punctuation normalisation (:class:`TextCleaner`).
    2. **Alias resolution** — replace character-name variants with canonical
       forms (:class:`AliasResolver`).
    3. **Tokenisation** — word tokenisation, stopword removal, and
       lemmatisation (:class:`MythTokenizer`).

    Each stage's output is stored in the result dict so that downstream
    components can consume whichever representation they need.

    Args:
        alias_path: Optional path to a custom character-alias JSON file.
            If *None*, the default project-relative path is used.
        extra_stopwords: Additional stopwords to pass to the tokenizer.
        text_field: Name of the field in myth dicts that contains the raw
            text.  Defaults to ``"text"``.

    Example::

        pipeline = PreprocessingPipeline()
        result = pipeline.process_single("Zeus hurled his thunderbolts.")
        print(result["cleaned_text"])
        print(result["tokens"])
        print(result["lemmas"])
    """

    def __init__(
        self,
        alias_path: str | Path | None = None,
        extra_stopwords: list[str] | None = None,
        text_field: str = "text",
    ) -> None:
        self._text_field = text_field

        # Initialise pipeline components
        self._cleaner = TextCleaner()

        try:
            self._resolver: AliasResolver | None = AliasResolver(alias_path)
        except FileNotFoundError:
            logger.warning(
                "Character alias file not found; alias resolution will be skipped."
            )
            self._resolver = None

        self._tokenizer = MythTokenizer(extra_stopwords=extra_stopwords)

        logger.info("PreprocessingPipeline initialised.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process(self, text: str) -> str:
        """Run text cleaning and alias resolution on a string.

        Args:
            text: Raw input text.

        Returns:
            Cleaned and normalized text string.
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected str, got {type(text).__name__}")
        cleaned = self._cleaner.clean(text)
        if self._resolver is not None:
            cleaned = self._resolver.resolve_text(cleaned)
        return cleaned

    def process_batch(self, texts: list[str]) -> list[str]:
        """Run text cleaning and alias resolution on a batch of strings.

        Args:
            texts: List of raw input texts.

        Returns:
            List of cleaned and normalized text strings.
        """
        return [self.process(t) for t in texts]

    def process_single(self, text: str) -> dict[str, Any]:
        """Run the full pipeline on a single text string.

        Args:
            text: Raw text to process.

        Returns:
            A dict containing:
                - ``original_text`` — the input text.
                - ``cleaned_text`` — text after cleaning and alias resolution.
                - ``tokens`` — list of processed tokens (lowered, filtered).
                - ``lemmas`` — list of lemmatised tokens.
                - ``sentences`` — list of sentence strings from the cleaned text.

        Raises:
            TypeError: If *text* is not a string.
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected str, got {type(text).__name__}")

        # Stage 1: Clean
        cleaned = self._cleaner.clean(text)

        # Stage 2: Alias resolution
        if self._resolver is not None:
            cleaned = self._resolver.resolve_text(cleaned)

        # Stage 3: Tokenise
        tokens = self._tokenizer.process(cleaned)
        lemmas = self._tokenizer.lemmatize(cleaned)
        sentences = self._tokenizer.get_sentences(cleaned)

        return {
            "original_text": text,
            "cleaned_text": cleaned,
            "tokens": tokens,
            "lemmas": lemmas,
            "sentences": sentences,
        }

    def process_corpus(self, myths: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Process a list of myth dictionaries.

        Each dict is expected to contain a text field (key determined by
        *text_field* at init, default ``"text"``).  The dict is updated
        **in place** with additional keys: ``cleaned_text``, ``tokens``,
        ``lemmas``, and ``sentences``.

        Myths without the expected text field are logged and skipped (the
        original dict is returned unchanged).

        Args:
            myths: List of myth dicts, each containing at least a text field.

        Returns:
            The same list of dicts, enriched with preprocessing results.
            The original dicts are modified in place *and* returned for
            convenience.
        """
        if not isinstance(myths, list):
            raise TypeError(f"Expected list, got {type(myths).__name__}")

        total = len(myths)
        processed_count = 0
        skipped_count = 0

        for idx, myth in enumerate(myths):
            if not isinstance(myth, dict):
                logger.warning(
                    "Skipping item %d: expected dict, got %s",
                    idx,
                    type(myth).__name__,
                )
                skipped_count += 1
                continue

            raw_text = myth.get(self._text_field)
            if raw_text is None:
                logger.warning(
                    "Skipping item %d (%s): missing '%s' field",
                    idx,
                    myth.get("title", "<untitled>"),
                    self._text_field,
                )
                skipped_count += 1
                continue

            if not isinstance(raw_text, str):
                logger.warning(
                    "Skipping item %d (%s): '%s' field is not a string",
                    idx,
                    myth.get("title", "<untitled>"),
                    self._text_field,
                )
                skipped_count += 1
                continue

            result = self.process_single(raw_text)
            myth["cleaned_text"] = result["cleaned_text"]
            myth["tokens"] = result["tokens"]
            myth["lemmas"] = result["lemmas"]
            myth["sentences"] = result["sentences"]
            processed_count += 1

        logger.info(
            "Corpus processing complete: %d/%d processed, %d skipped",
            processed_count,
            total,
            skipped_count,
        )

        return myths

    # ------------------------------------------------------------------
    # Component accessors (for advanced usage / testing)
    # ------------------------------------------------------------------

    @property
    def cleaner(self) -> TextCleaner:
        """Return the underlying :class:`TextCleaner` instance."""
        return self._cleaner

    @property
    def resolver(self) -> AliasResolver | None:
        """Return the underlying :class:`AliasResolver`, or *None*."""
        return self._resolver

    @property
    def tokenizer(self) -> MythTokenizer:
        """Return the underlying :class:`MythTokenizer` instance."""
        return self._tokenizer
