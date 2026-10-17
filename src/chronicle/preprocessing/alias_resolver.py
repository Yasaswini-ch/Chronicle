"""Character name normalization via alias resolution.

Provides :class:`AliasResolver` which maps variant spellings, epithets, and
Roman equivalents of Greek mythology characters back to their canonical names.
Aliases are loaded from a JSON file (``data/annotations/character_aliases.json``)
and matched case-insensitively using whole-word boundaries.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default location of the alias mapping relative to the project root.
_PROJECT_ROOT = Path(__file__).resolve().parents[3]  # src/chronicle/preprocessing -> root
_DEFAULT_ALIAS_PATH = _PROJECT_ROOT / "data" / "annotations" / "character_aliases.json"


class AliasResolver:
    """Resolve character-name variants to a single canonical form.

    The resolver builds two internal lookup structures on initialisation:

    * ``_alias_to_canonical`` — maps every known alias (lowercased) to its
      canonical name.
    * ``_canonical_to_aliases`` — maps each canonical name to the full list
      of aliases (original casing preserved).

    A compiled regex is also constructed so that :meth:`resolve_text` can
    perform efficient whole-word replacement in a single pass.

    Args:
        alias_path: Path to the JSON alias file.  If *None*, the default
            project-relative path is used.

    Raises:
        FileNotFoundError: If the alias file does not exist.
        json.JSONDecodeError: If the alias file contains invalid JSON.

    Example::

        resolver = AliasResolver()
        resolver.resolve("Jupiter")   # -> "Zeus"
        resolver.resolve("Athene")    # -> "Athena"
    """

    def __init__(self, alias_path: str | Path | None = None) -> None:
        self._alias_path = Path(alias_path) if alias_path else _DEFAULT_ALIAS_PATH
        self._alias_to_canonical: dict[str, str] = {}
        self._canonical_to_aliases: dict[str, list[str]] = {}
        self._pattern: re.Pattern[str] | None = None

        self._load_aliases()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def resolve(self, name: str) -> str:
        """Return the canonical name for *name*, or *name* unchanged.

        Matching is case-insensitive.  If *name* is itself a canonical name
        it is returned as-is.

        Args:
            name: A character name or alias to look up.

        Returns:
            The canonical name if *name* is recognised, otherwise the
            original *name* string.
        """
        if not isinstance(name, str):
            raise TypeError(f"Expected str, got {type(name).__name__}")

        key = name.strip().lower()

        # Check if it is already a canonical name
        if key in {c.lower() for c in self._canonical_to_aliases}:
            # Return with proper casing
            for canonical in self._canonical_to_aliases:
                if canonical.lower() == key:
                    return canonical
            return name  # pragma: no cover – unreachable safety fallback

        return self._alias_to_canonical.get(key, name)

    def resolve_text(self, text: str) -> str:
        """Replace all known aliases in *text* with their canonical names.

        Replacement uses whole-word matching (word boundaries) so that
        substrings within unrelated words are not affected.  The replacement
        is case-insensitive: ``"jupiter"`` and ``"JUPITER"`` both resolve
        to ``"Zeus"``.

        Args:
            text: Input text in which aliases should be resolved.

        Returns:
            Text with all recognised aliases replaced by canonical names.
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected str, got {type(text).__name__}")

        if self._pattern is None:
            return text

        def _replace(match: re.Match[str]) -> str:
            return self._alias_to_canonical.get(match.group(0).lower(), match.group(0))

        return self._pattern.sub(_replace, text)

    def get_aliases(self, canonical: str) -> list[str]:
        """Return all known aliases for *canonical*.

        Args:
            canonical: A canonical character name (case-insensitive lookup).

        Returns:
            List of alias strings.  Returns an empty list if *canonical* is
            not a known canonical name.
        """
        # Case-insensitive canonical lookup
        for key, aliases in self._canonical_to_aliases.items():
            if key.lower() == canonical.strip().lower():
                return list(aliases)
        return []

    def is_known_character(self, name: str) -> bool:
        """Check whether *name* is a recognised character name or alias.

        Args:
            name: Name to check.

        Returns:
            *True* if *name* matches a canonical name or any alias.
        """
        key = name.strip().lower()
        if key in self._alias_to_canonical:
            return True
        return any(c.lower() == key for c in self._canonical_to_aliases)

    @property
    def canonical_names(self) -> list[str]:
        """Return a sorted list of all canonical character names."""
        return sorted(self._canonical_to_aliases.keys())

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_aliases(self) -> None:
        """Load and index the alias mapping from disk."""
        if not self._alias_path.exists():
            raise FileNotFoundError(
                f"Character alias file not found: {self._alias_path}"
            )

        raw: dict[str, Any] = json.loads(self._alias_path.read_text(encoding="utf-8"))

        all_alias_strings: list[str] = []

        for canonical, aliases in raw.items():
            if not isinstance(aliases, list):
                logger.warning(
                    "Skipping canonical name '%s': aliases must be a list, "
                    "got %s",
                    canonical,
                    type(aliases).__name__,
                )
                continue

            self._canonical_to_aliases[canonical] = list(aliases)

            for alias in aliases:
                key = alias.strip().lower()
                if key in self._alias_to_canonical:
                    existing = self._alias_to_canonical[key]
                    if existing != canonical:
                        logger.warning(
                            "Duplicate alias '%s' maps to both '%s' and '%s'; "
                            "keeping first mapping ('%s').",
                            alias,
                            existing,
                            canonical,
                            existing,
                        )
                    continue

                self._alias_to_canonical[key] = canonical
                all_alias_strings.append(re.escape(alias))

        # Build a single regex pattern for efficient replacement.
        # Sort by length (longest first) so longer epithets match before
        # shorter substrings.
        if all_alias_strings:
            all_alias_strings.sort(key=len, reverse=True)
            joined = "|".join(all_alias_strings)
            self._pattern = re.compile(
                rf"\b(?:{joined})\b", re.IGNORECASE
            )

        logger.info(
            "Loaded %d canonical names with %d total aliases from %s",
            len(self._canonical_to_aliases),
            len(self._alias_to_canonical),
            self._alias_path,
        )
