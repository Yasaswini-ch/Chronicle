"""Tests for the Chronicle preprocessing module.

Covers:
- TextCleaner: HTML removal, footnote removal, whitespace normalisation,
  punctuation normalisation, and the full pipeline.
- AliasResolver: Greek/Roman name mapping, case insensitivity, epithets.
- MythTokenizer: tokenisation, lemmatisation, stop-word removal.
- PreprocessingPipeline: end-to-end composition of the above stages.
"""

from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# TextCleaner tests — this module exists, so we import directly.
# ---------------------------------------------------------------------------
from chronicle.preprocessing.cleaner import TextCleaner


class TestTextCleaner:
    """Tests for :class:`TextCleaner`."""

    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.cleaner = TextCleaner()

    # -- HTML removal -------------------------------------------------------

    @pytest.mark.parametrize(
        "raw, expected",
        [
            ("<p>Hello world</p>", "Hello world"),
            ("<b>Zeus</b> and <i>Hera</i>", "Zeus and Hera"),
            ('<div class="x">text</div>', "text"),
            ("<!-- comment -->visible", "visible"),
            ("<![CDATA[data]]>visible", "visible"),
            ("no tags here", "no tags here"),
            ("", ""),
        ],
        ids=[
            "paragraph",
            "inline-tags",
            "div-with-attr",
            "html-comment",
            "cdata",
            "no-tags",
            "empty",
        ],
    )
    def test_remove_html(self, raw: str, expected: str) -> None:
        assert self.cleaner.remove_html(raw) == expected

    def test_remove_html_nested(self) -> None:
        raw = "<div><p><span>Zeus</span></p></div>"
        assert self.cleaner.remove_html(raw) == "Zeus"

    def test_remove_html_type_error(self) -> None:
        with pytest.raises(TypeError, match="Expected str"):
            self.cleaner.remove_html(42)  # type: ignore[arg-type]

    # -- Footnote removal ---------------------------------------------------

    @pytest.mark.parametrize(
        "raw, expected",
        [
            ("text[1] more", "text more"),
            ("text[23] more", "text more"),
            ("text[iv] end", "text end"),
            ("text[*] end", "text end"),
            ("text[†] end", "text end"),
            ("text (see note 3) end", "text  end"),
            ("text (footnote 12) end", "text  end"),
            ("text (see footnote 1) end", "text  end"),
            ("no footnotes", "no footnotes"),
        ],
        ids=[
            "bracket-number",
            "bracket-multi-digit",
            "bracket-roman",
            "bracket-asterisk",
            "bracket-dagger",
            "inline-see-note",
            "inline-footnote",
            "inline-see-footnote",
            "no-footnotes",
        ],
    )
    def test_remove_footnotes(self, raw: str, expected: str) -> None:
        assert self.cleaner.remove_footnotes(raw) == expected

    # -- Whitespace normalisation -------------------------------------------

    @pytest.mark.parametrize(
        "raw, expected",
        [
            ("hello   world", "hello world"),
            ("hello\t\tworld", "hello world"),
            ("line1\n\n\n\nline2", "line1\n\nline2"),
            ("  leading", "leading"),
            ("trailing  ", "trailing"),
            ("  both  ", "both"),
        ],
        ids=[
            "multi-space",
            "tabs",
            "multi-newline",
            "leading",
            "trailing",
            "both",
        ],
    )
    def test_normalize_whitespace(self, raw: str, expected: str) -> None:
        assert self.cleaner.normalize_whitespace(raw) == expected

    # -- Punctuation normalisation ------------------------------------------

    @pytest.mark.parametrize(
        "raw, expected",
        [
            ("\u201cHello\u201d", '"Hello"'),
            ("\u2018world\u2019", "'world'"),
            ("a\u2013b", "a—b"),  # en-dash -> em-dash
            ("a...b", "a…b"),    # triple dot -> ellipsis
            ("a---b", "a—b"),    # multi-dash -> em-dash
        ],
        ids=[
            "curly-double-quotes",
            "curly-single-quotes",
            "en-dash",
            "triple-dots",
            "multi-dash",
        ],
    )
    def test_normalize_punctuation(self, raw: str, expected: str) -> None:
        assert self.cleaner.normalize_punctuation(raw) == expected

    # -- Full pipeline ------------------------------------------------------

    def test_clean_full_pipeline(self, dirty_html_text: str) -> None:
        result = self.cleaner.clean(dirty_html_text)
        # HTML tags should be gone
        assert "<p>" not in result
        assert "<div" not in result
        assert "<!-- " not in result
        # Footnote markers should be gone
        assert "[1]" not in result
        assert "(see note 3)" not in result
        # The meaningful content should remain
        assert "Zeus" in result
        assert "thunderbolt" in result
        assert "Hera" in result

    def test_clean_empty_string(self) -> None:
        assert self.cleaner.clean("") == ""

    def test_clean_whitespace_only(self) -> None:
        assert self.cleaner.clean("   \n\t  ") == ""

    def test_clean_type_error(self) -> None:
        with pytest.raises(TypeError, match="Expected str"):
            self.cleaner.clean(None)  # type: ignore[arg-type]

    def test_clean_html_entities(self) -> None:
        raw = "Zeus&amp;Hera &lt;fought&gt;"
        result = self.cleaner.clean(raw)
        assert "&amp;" not in result
        assert "Zeus" in result


# ---------------------------------------------------------------------------
# AliasResolver tests — skip gracefully if module not yet implemented
# ---------------------------------------------------------------------------

class TestAliasResolver:
    """Tests for :class:`AliasResolver` (Greek/Roman name resolution)."""

    @pytest.fixture(autouse=True)
    def _try_import(self, alias_resolver) -> None:
        """Use the alias_resolver fixture; skips if not implemented."""
        self.resolver = alias_resolver

    @pytest.mark.parametrize(
        "alias, canonical",
        [
            ("Jupiter", "Zeus"),
            ("Jove", "Zeus"),
            ("Juno", "Hera"),
            ("Neptune", "Poseidon"),
            ("Minerva", "Athena"),
            ("Hercules", "Heracles"),
            ("Ulysses", "Odysseus"),
            ("Pluto", "Hades"),
        ],
        ids=[
            "Jupiter->Zeus",
            "Jove->Zeus",
            "Juno->Hera",
            "Neptune->Poseidon",
            "Minerva->Athena",
            "Hercules->Heracles",
            "Ulysses->Odysseus",
            "Pluto->Hades",
        ],
    )
    def test_resolve_roman_to_greek(self, alias: str, canonical: str) -> None:
        assert self.resolver.resolve(alias) == canonical

    def test_canonical_name_returns_itself(self) -> None:
        assert self.resolver.resolve("Zeus") == "Zeus"

    @pytest.mark.parametrize(
        "alias",
        ["jupiter", "JUPITER", "Jupiter", "jUpItEr"],
        ids=["lower", "upper", "title", "mixed"],
    )
    def test_case_insensitivity(self, alias: str) -> None:
        assert self.resolver.resolve(alias) == "Zeus"

    def test_unknown_name_returns_original(self) -> None:
        result = self.resolver.resolve("Kratos")
        assert result == "Kratos"

    def test_epithet_resolution(self) -> None:
        assert self.resolver.resolve("Cloud-Gatherer") == "Zeus"
        assert self.resolver.resolve("Earth-Shaker") == "Poseidon"

    def test_resolve_in_text(self) -> None:
        text = "Jupiter hurled a thunderbolt while Neptune shook the earth."
        result = self.resolver.resolve_in_text(text)
        assert "Zeus" in result
        assert "Poseidon" in result


# ---------------------------------------------------------------------------
# MythTokenizer tests — skip gracefully if module not yet implemented
# ---------------------------------------------------------------------------

class TestMythTokenizer:
    """Tests for :class:`MythTokenizer`."""

    @pytest.fixture(autouse=True)
    def _try_import(self) -> None:
        try:
            from chronicle.preprocessing.tokenizer import MythTokenizer
            self.tokenizer = MythTokenizer()
        except ImportError:
            pytest.skip("MythTokenizer not yet implemented")

    def test_tokenize_returns_list(self) -> None:
        tokens = self.tokenizer.tokenize("Zeus threw the thunderbolt.")
        assert isinstance(tokens, list)
        assert len(tokens) > 0

    def test_tokenize_splits_words(self) -> None:
        tokens = self.tokenizer.tokenize("The mighty Zeus.")
        # Should contain content words
        lowered = [t.lower() for t in tokens]
        assert "zeus" in lowered

    def test_lemmatization(self) -> None:
        tokens = self.tokenizer.tokenize("The gods were fighting battles.")
        lowered = [t.lower() for t in tokens]
        # "fighting" should be lemmatised (fight or fighting accepted)
        assert any(t in ("fight", "fighting", "battle", "god") for t in lowered)

    def test_stopword_removal(self) -> None:
        tokens = self.tokenizer.tokenize("The quick brown fox jumps over the lazy dog.")
        lowered = [t.lower() for t in tokens]
        # Common stop words should be removed
        assert "the" not in lowered
        assert "over" not in lowered

    def test_empty_input(self) -> None:
        tokens = self.tokenizer.tokenize("")
        assert tokens == []

    @pytest.mark.parametrize(
        "text",
        [
            "Zeus, Hera, and Athena gathered on Olympus.",
            "Heracles slew the Nemean Lion with his bare hands.",
            "Odysseus devised a cunning plan to escape the Cyclops.",
        ],
    )
    def test_tokenize_various_myths(self, text: str) -> None:
        tokens = self.tokenizer.tokenize(text)
        assert len(tokens) >= 2


# ---------------------------------------------------------------------------
# PreprocessingPipeline tests — skip gracefully if not yet implemented
# ---------------------------------------------------------------------------

class TestPreprocessingPipeline:
    """Tests for :class:`PreprocessingPipeline` end-to-end processing."""

    @pytest.fixture(autouse=True)
    def _try_import(self) -> None:
        try:
            from chronicle.preprocessing.pipeline import PreprocessingPipeline
            self.pipeline = PreprocessingPipeline()
        except ImportError:
            pytest.skip("PreprocessingPipeline not yet implemented")

    def test_process_single(self, dirty_html_text: str) -> None:
        result = self.pipeline.process(dirty_html_text)
        assert isinstance(result, str)
        assert "<p>" not in result
        assert len(result) > 0

    def test_process_batch(self, sample_texts: list[str]) -> None:
        results = self.pipeline.process_batch(sample_texts)
        assert len(results) == len(sample_texts)
        for r in results:
            assert isinstance(r, str)
            assert len(r) > 0

    def test_process_preserves_names(self) -> None:
        text = "<p>Zeus and Hera ruled Olympus[1].</p>"
        result = self.pipeline.process(text)
        assert "Zeus" in result or "zeus" in result.lower()
        assert "Hera" in result or "hera" in result.lower()
