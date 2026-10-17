"""Generate spaCy NER training data from the annotated mythology dataset.

Scans myth text for known entity names (characters, locations, artifacts)
and produces training examples in the format required by spaCy's NER
training loop.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Project root resolved relative to this file
_PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Default entity type assignments (mirrors entity_recognizer.py)
_DEFAULT_ENTITY_TYPES: dict[str, str] = {
    # Olympian gods
    "Zeus": "GOD", "Hera": "GOD", "Poseidon": "GOD", "Athena": "GOD",
    "Apollo": "GOD", "Artemis": "GOD", "Aphrodite": "GOD", "Ares": "GOD",
    "Hermes": "GOD", "Hephaestus": "GOD", "Demeter": "GOD",
    "Dionysus": "GOD", "Hades": "GOD", "Persephone": "GOD",
    # Mortals
    "Heracles": "MORTAL", "Odysseus": "MORTAL", "Achilles": "MORTAL",
    "Theseus": "MORTAL", "Perseus": "MORTAL", "Jason": "MORTAL",
    "Orpheus": "MORTAL", "Oedipus": "MORTAL", "Agamemnon": "MORTAL",
    "Pandora": "MORTAL", "Icarus": "MORTAL", "Daedalus": "MORTAL",
    "Medea": "MORTAL", "Minos": "MORTAL",
    # Creatures
    "Medusa": "CREATURE", "Minotaur": "CREATURE",
    # Titans
    "Kronos": "TITAN", "Prometheus": "TITAN", "Titans": "TITAN",
}


class NERTrainingDataGenerator:
    """Generate spaCy NER training data from the Chronicle myth dataset.

    Matches known entity names, their aliases, locations, and artifacts
    against myth text to produce training examples automatically.

    Parameters
    ----------
    aliases_path : str | Path | None
        Path to ``character_aliases.json``.  Defaults to the project's
        canonical location.
    entity_types : dict[str, str] | None
        Mapping of canonical entity names to label strings.  Merged with
        the built-in defaults.

    Example::

        gen = NERTrainingDataGenerator()
        myths = json.load(open("data/processed/myths.json"))
        training_data = gen.generate_from_myths(myths)
        gen.save_training_data(training_data, "data/training/ner_train.json")
    """

    def __init__(
        self,
        aliases_path: str | Path | None = None,
        entity_types: dict[str, str] | None = None,
    ) -> None:
        self._entity_types: dict[str, str] = dict(_DEFAULT_ENTITY_TYPES)
        if entity_types:
            self._entity_types.update(entity_types)

        # name/alias → (canonical_name, entity_type)
        self._lookup: dict[str, tuple[str, str]] = {}
        self._build_lookup(aliases_path)

    # ------------------------------------------------------------------
    # Lookup construction
    # ------------------------------------------------------------------

    def _build_lookup(self, aliases_path: str | Path | None) -> None:
        """Build the surface-form → (canonical, type) lookup table."""
        # Load aliases
        if aliases_path is None:
            aliases_path = (
                _PROJECT_ROOT / "data" / "annotations" / "character_aliases.json"
            )
        aliases_path = Path(aliases_path)

        aliases: dict[str, list[str]] = {}
        if aliases_path.exists():
            with open(aliases_path, encoding="utf-8") as f:
                aliases = json.load(f)

        # Register canonical names + their aliases
        for canonical, alias_list in aliases.items():
            etype = self._entity_types.get(canonical, "MORTAL")
            self._lookup[canonical] = (canonical, etype)
            for alias in alias_list:
                self._lookup[alias] = (canonical, etype)

        # Register any entity types not covered by aliases
        for name, etype in self._entity_types.items():
            if name not in self._lookup:
                self._lookup[name] = (name, etype)

        logger.info(
            "NER training data generator: %d surface forms registered",
            len(self._lookup),
        )

    # ------------------------------------------------------------------
    # Training data generation
    # ------------------------------------------------------------------

    def generate_from_myths(
        self,
        myths: list[dict[str, Any]],
    ) -> list[tuple[str, dict[str, list[tuple[int, int, str]]]]]:
        """Auto-generate spaCy NER training examples from annotated myths.

        For each myth, the generator:

        1. Collects all entity names relevant to that myth (characters,
           locations, artifacts) plus their known aliases.
        2. Scans the myth text for exact matches (longest-first, word-
           boundary-aware).
        3. Resolves overlapping spans, keeping the longest match.
        4. Emits a ``(text, {"entities": [(start, end, label), ...]})``
           training example.

        Parameters
        ----------
        myths :
            List of myth documents from the Chronicle dataset.

        Returns
        -------
        list[tuple[str, dict]]
            spaCy-format training data.
        """
        training_data: list[tuple[str, dict[str, list[tuple[int, int, str]]]]] = []

        for myth in myths:
            text = myth.get("text", myth.get("summary", ""))
            if not text or len(text.strip()) < 20:
                continue

            # Gather entity names specific to this myth
            myth_entities = self._collect_myth_entities(myth)

            # Merge with global lookup for comprehensive matching
            all_entities = dict(self._lookup)
            for name, etype in myth_entities.items():
                if name not in all_entities:
                    all_entities[name] = (name, etype)

            # Find entity spans in text
            spans = self._find_entity_spans(text, all_entities)

            if spans:
                training_data.append((text, {"entities": spans}))

        logger.info(
            "Generated %d training examples from %d myths",
            len(training_data),
            len(myths),
        )
        return training_data

    def _collect_myth_entities(
        self,
        myth: dict[str, Any],
    ) -> dict[str, str]:
        """Extract entity names and types from a single myth document."""
        entities: dict[str, str] = {}

        # Characters
        for char in myth.get("characters", []):
            if isinstance(char, str):
                name = char
                etype = self._entity_types.get(name, "MORTAL")
            else:
                name = char.get("name", "")
                role = char.get("role", "").upper()
                etype = self._entity_types.get(
                    name,
                    role if role in ("GOD", "MORTAL", "CREATURE", "TITAN") else "MORTAL",
                )
            if name:
                entities[name] = etype

        # Locations
        for loc in myth.get("locations", []):
            loc_name = loc if isinstance(loc, str) else loc.get("name", "")
            if loc_name:
                entities[loc_name] = "LOCATION"

        # Artifacts
        for art in myth.get("artifacts", []):
            art_name = art if isinstance(art, str) else art.get("name", "")
            if art_name:
                entities[art_name] = "ARTIFACT"

        return entities

    def _find_entity_spans(
        self,
        text: str,
        entities: dict[str, tuple[str, str]],
    ) -> list[tuple[int, int, str]]:
        """Find non-overlapping entity spans in *text*.

        Uses longest-match-first and word-boundary checks.

        Returns
        -------
        list[tuple[int, int, str]]
            ``(start, end, label)`` tuples.
        """
        spans: list[tuple[int, int, str]] = []

        # Sort surface forms by length descending for longest-match-first
        sorted_forms = sorted(entities.keys(), key=len, reverse=True)
        occupied: list[tuple[int, int]] = []

        for surface_form in sorted_forms:
            _, entity_type = entities[surface_form]

            # Build a regex pattern with word boundaries
            pattern = re.compile(
                r"\b" + re.escape(surface_form) + r"\b",
                re.IGNORECASE,
            )

            for match in pattern.finditer(text):
                start, end = match.start(), match.end()

                # Check for overlap with already-claimed spans
                if any(
                    not (end <= occ_start or start >= occ_end)
                    for occ_start, occ_end in occupied
                ):
                    continue

                spans.append((start, end, entity_type))
                occupied.append((start, end))

        # Sort by start position
        spans.sort(key=lambda s: s[0])
        return spans

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_training_data(
        self,
        data: list[tuple[str, dict[str, list[tuple[int, int, str]]]]],
        path: str | Path,
    ) -> None:
        """Save training data to a JSON file.

        The format is a list of ``[text, {"entities": [[start, end, label], ...]}]``
        entries (tuples are serialised as lists in JSON).

        Parameters
        ----------
        data :
            Training data as returned by :meth:`generate_from_myths`.
        path :
            Output file path.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Convert tuples to lists for JSON serialisation
        serialisable = [
            [text, {"entities": [list(span) for span in annot["entities"]]}]
            for text, annot in data
        ]

        with open(path, "w", encoding="utf-8") as f:
            json.dump(serialisable, f, indent=2, ensure_ascii=False)

        logger.info("Training data saved to %s (%d examples)", path, len(data))

    @staticmethod
    def load_training_data(
        path: str | Path,
    ) -> list[tuple[str, dict[str, list[tuple[int, int, str]]]]]:
        """Load training data from a JSON file.

        Parameters
        ----------
        path :
            Path to the JSON file saved by :meth:`save_training_data`.

        Returns
        -------
        list[tuple[str, dict]]
            Training data in spaCy format.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Training data not found: {path}")

        with open(path, encoding="utf-8") as f:
            raw = json.load(f)

        # Convert lists back to tuples
        training_data: list[tuple[str, dict[str, list[tuple[int, int, str]]]]] = []
        for entry in raw:
            text = entry[0]
            entities = [tuple(span) for span in entry[1]["entities"]]
            training_data.append((text, {"entities": entities}))

        logger.info("Loaded %d training examples from %s", len(training_data), path)
        return training_data

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @property
    def surface_form_count(self) -> int:
        """Number of registered surface forms for entity matching."""
        return len(self._lookup)

    def get_entity_type_distribution(
        self,
        data: list[tuple[str, dict[str, list[tuple[int, int, str]]]]],
    ) -> dict[str, int]:
        """Count entity annotations by type across training data.

        Parameters
        ----------
        data :
            Training data in spaCy format.

        Returns
        -------
        dict[str, int]
            Mapping from entity label to count.
        """
        from collections import Counter
        counts: Counter[str] = Counter()
        for _, annot in data:
            for _, _, label in annot["entities"]:
                counts[label] += 1
        return dict(counts)

    def __repr__(self) -> str:
        return (
            f"NERTrainingDataGenerator(surface_forms={len(self._lookup)}, "
            f"entity_types={len(self._entity_types)})"
        )
