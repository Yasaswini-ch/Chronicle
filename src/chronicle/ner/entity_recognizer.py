"""Named Entity Recognition for Greek mythology texts.

Provides a custom NER system that combines spaCy's statistical NER with
a dictionary-based fallback recognizer built from the Chronicle character
aliases dataset.  Entity categories are mythology-specific: GOD, MORTAL,
CREATURE, TITAN, LOCATION, and ARTIFACT.
"""

from __future__ import annotations

import json
import logging
import random
from pathlib import Path
from typing import Any

import spacy
from spacy.tokens import DocBin
from spacy.training import Example
from spacy.util import minibatch, compounding

logger = logging.getLogger(__name__)

# Project root resolved relative to this file: src/chronicle/ner -> project root
_PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Default entity labels used throughout the mythology NER system
ENTITY_LABELS: list[str] = [
    "GOD",
    "MORTAL",
    "CREATURE",
    "TITAN",
    "LOCATION",
    "ARTIFACT",
]

# Canonical mapping of known characters to their entity type.
# This drives the dictionary-based fallback recognizer.
_DEFAULT_ENTITY_TYPES: dict[str, str] = {
    # Olympian gods
    "Zeus": "GOD",
    "Hera": "GOD",
    "Poseidon": "GOD",
    "Athena": "GOD",
    "Apollo": "GOD",
    "Artemis": "GOD",
    "Aphrodite": "GOD",
    "Ares": "GOD",
    "Hermes": "GOD",
    "Hephaestus": "GOD",
    "Demeter": "GOD",
    "Dionysus": "GOD",
    "Hades": "GOD",
    "Persephone": "GOD",
    # Mortals / heroes
    "Heracles": "MORTAL",
    "Odysseus": "MORTAL",
    "Achilles": "MORTAL",
    "Theseus": "MORTAL",
    "Perseus": "MORTAL",
    "Jason": "MORTAL",
    "Orpheus": "MORTAL",
    "Oedipus": "MORTAL",
    "Agamemnon": "MORTAL",
    "Pandora": "MORTAL",
    "Icarus": "MORTAL",
    "Daedalus": "MORTAL",
    "Medea": "MORTAL",
    "Minos": "MORTAL",
    # Creatures
    "Medusa": "CREATURE",
    "Minotaur": "CREATURE",
    # Titans
    "Kronos": "TITAN",
    "Prometheus": "TITAN",
    "Titans": "TITAN",
    # Locations
    "Olympus": "LOCATION",
    "Mount Olympus": "LOCATION",
    "Underworld": "LOCATION",
    "Tartarus": "LOCATION",
    "Elysium": "LOCATION",
    "Styx": "LOCATION",
    "Troy": "LOCATION",
    "Ithaca": "LOCATION",
    "Athens": "LOCATION",
    "Thebes": "LOCATION",
    "Crete": "LOCATION",
    "Colchis": "LOCATION",
    "Delphi": "LOCATION",
    "Argos": "LOCATION",
    "Sparta": "LOCATION",
    "Mycenae": "LOCATION",
    "Corinth": "LOCATION",
    "Aeaea": "LOCATION",
    "Lemnos": "LOCATION",
    "Naxos": "LOCATION",
    "Delos": "LOCATION",
    # Artifacts
    "Golden Fleece": "ARTIFACT",
    "Aegis": "ARTIFACT",
    "Trident": "ARTIFACT",
    "Thunderbolt": "ARTIFACT",
    "Caduceus": "ARTIFACT",
    "Helm of Darkness": "ARTIFACT",
    "Pandora's Box": "ARTIFACT",
    "Labyrinth": "ARTIFACT",
    "Argo": "ARTIFACT",
    "Ichor": "ARTIFACT",
    "Ambrosia": "ARTIFACT",
    "Nectar": "ARTIFACT",
    "Harpe": "ARTIFACT",
    "Winged Sandals": "ARTIFACT",
    "Cap of Invisibility": "ARTIFACT",
}


class MythEntityRecognizer:
    """Custom Named Entity Recognizer for Greek mythology texts.

    Combines a trainable spaCy NER pipeline with a dictionary-based
    fallback that leverages the character aliases catalogue to recognise
    known mythology entities even without a trained model.

    Parameters
    ----------
    model_name : str
        Base spaCy model to start from.  Pass ``"blank"`` to create a
        blank English model (useful for training from scratch).
    entity_labels : list[str] | None
        Entity labels to register.  Defaults to :data:`ENTITY_LABELS`.

    Example::

        ner = MythEntityRecognizer()
        entities = ner.predict("Zeus hurled his thunderbolt at Typhon.")
        # [{'text': 'Zeus', 'label': 'GOD', 'start': 0, 'end': 4}, ...]
    """

    def __init__(
        self,
        model_name: str = "blank",
        entity_labels: list[str] | None = None,
    ) -> None:
        self._labels = entity_labels or list(ENTITY_LABELS)
        self._model_name = model_name

        # --- Initialise spaCy pipeline ---
        if model_name == "blank":
            self._nlp = spacy.blank("en")
        else:
            self._nlp = spacy.load(model_name)

        # Ensure NER component exists
        if "ner" not in self._nlp.pipe_names:
            ner = self._nlp.add_pipe("ner", last=True)
        else:
            ner = self._nlp.get_pipe("ner")

        for label in self._labels:
            ner.add_label(label)

        self._is_trained = False

        # --- Build dictionary-based lookup ---
        self._alias_lookup: dict[str, str] = {}
        self._build_alias_lookup()

        logger.info(
            "MythEntityRecognizer initialised  |  labels=%s  |  aliases=%d",
            self._labels,
            len(self._alias_lookup),
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def train(
        self,
        training_data: list[tuple[str, dict[str, Any]]],
        n_iter: int = 30,
        drop: float = 0.35,
        learn_rate: float = 0.001,
    ) -> dict[str, Any]:
        """Train or fine-tune the spaCy NER model.

        Parameters
        ----------
        training_data :
            spaCy-format training examples::

                [("Zeus is a god.", {"entities": [(0, 4, "GOD")]}), ...]

        n_iter :
            Number of training iterations.
        drop :
            Dropout rate during training.
        learn_rate :
            Initial learning rate for the optimizer.

        Returns
        -------
        dict
            Training metrics with per-iteration losses.
        """
        if not training_data:
            raise ValueError("training_data must be a non-empty list")

        # Prepare the pipeline for training
        other_pipes = [
            pipe for pipe in self._nlp.pipe_names if pipe != "ner"
        ]

        losses_history: list[dict[str, float]] = []

        with self._nlp.disable_pipes(*other_pipes):
            if not self._is_trained:
                self._nlp.begin_training()

            optimizer = self._nlp.create_optimizer()

            for iteration in range(n_iter):
                random.shuffle(training_data)
                losses: dict[str, float] = {}
                batches = minibatch(training_data, size=compounding(4.0, 32.0, 1.001))

                for batch in batches:
                    examples: list[Example] = []
                    for text, annotations in batch:
                        doc = self._nlp.make_doc(text)
                        example = Example.from_dict(doc, annotations)
                        examples.append(example)
                    self._nlp.update(examples, drop=drop, losses=losses, sgd=optimizer)

                losses_history.append(dict(losses))
                if (iteration + 1) % 5 == 0 or iteration == 0:
                    logger.info(
                        "Iteration %d/%d  |  losses: %s",
                        iteration + 1,
                        n_iter,
                        {k: f"{v:.4f}" for k, v in losses.items()},
                    )

        self._is_trained = True
        return {
            "n_iter": n_iter,
            "final_loss": losses_history[-1] if losses_history else {},
            "losses_history": losses_history,
        }

    def predict(self, text: str) -> list[dict[str, Any]]:
        """Extract mythology entities from *text*.

        If the statistical model has been trained, its predictions are used.
        Otherwise the dictionary-based fallback is applied.  When the model
        *is* trained, the fallback still supplements any entities the model
        missed.

        Parameters
        ----------
        text :
            Input text to analyse.

        Returns
        -------
        list[dict]
            Each dict has keys ``text``, ``label``, ``start``, ``end``.
        """
        if not text or not text.strip():
            return []

        entities: list[dict[str, Any]] = []
        seen_spans: set[tuple[int, int]] = set()

        # 1. Statistical model predictions (if trained)
        if self._is_trained:
            doc = self._nlp(text)
            for ent in doc.ents:
                span_key = (ent.start_char, ent.end_char)
                if span_key not in seen_spans:
                    entities.append(
                        {
                            "text": ent.text,
                            "label": ent.label_,
                            "start": ent.start_char,
                            "end": ent.end_char,
                        }
                    )
                    seen_spans.add(span_key)

        # 2. Dictionary-based fallback / supplement
        fallback_entities = self._dictionary_predict(text)
        for ent in fallback_entities:
            span_key = (ent["start"], ent["end"])
            # Don't add if it overlaps with an existing entity
            if span_key not in seen_spans and not self._overlaps(span_key, seen_spans):
                entities.append(ent)
                seen_spans.add(span_key)

        # Sort by start position
        entities.sort(key=lambda e: e["start"])
        return entities

    def extract(self, text: str) -> list[dict[str, Any]]:
        """Extract entities and ensure general CHARACTER/LOCATION labels are mapped."""
        entities = self.predict(text)
        result: list[dict[str, Any]] = []
        for ent in entities:
            item = dict(ent)
            label = item.get("label", "")
            if label in ("GOD", "MORTAL", "CREATURE", "TITAN"):
                item["type"] = label
                item["label"] = "CHARACTER"
            result.append(item)
        return result

    def evaluate(
        self,
        test_data: list[tuple[str, dict[str, Any]]],
    ) -> dict[str, Any]:
        """Evaluate the model on held-out test data.

        Parameters
        ----------
        test_data :
            Same format as *training_data*.

        Returns
        -------
        dict
            Overall and per-entity-type precision, recall, and F1 scores.
        """
        # Per-label tallies
        tp: dict[str, int] = {label: 0 for label in self._labels}
        fp: dict[str, int] = {label: 0 for label in self._labels}
        fn: dict[str, int] = {label: 0 for label in self._labels}

        for text, annotations in test_data:
            gold_entities = {
                (start, end, label)
                for start, end, label in annotations.get("entities", [])
            }
            pred_entities_raw = self.predict(text)
            pred_entities = {
                (e["start"], e["end"], e["label"]) for e in pred_entities_raw
            }

            for label in self._labels:
                gold_label = {(s, e) for s, e, l in gold_entities if l == label}
                pred_label = {(s, e) for s, e, l in pred_entities if l == label}
                tp[label] += len(gold_label & pred_label)
                fp[label] += len(pred_label - gold_label)
                fn[label] += len(gold_label - pred_label)

        per_type: dict[str, dict[str, float]] = {}
        total_tp = total_fp = total_fn = 0

        for label in self._labels:
            precision = (
                tp[label] / (tp[label] + fp[label])
                if (tp[label] + fp[label]) > 0
                else 0.0
            )
            recall = (
                tp[label] / (tp[label] + fn[label])
                if (tp[label] + fn[label]) > 0
                else 0.0
            )
            f1 = (
                2 * precision * recall / (precision + recall)
                if (precision + recall) > 0
                else 0.0
            )
            per_type[label] = {
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1": round(f1, 4),
                "support": tp[label] + fn[label],
            }
            total_tp += tp[label]
            total_fp += fp[label]
            total_fn += fn[label]

        overall_precision = (
            total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
        )
        overall_recall = (
            total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
        )
        overall_f1 = (
            2 * overall_precision * overall_recall / (overall_precision + overall_recall)
            if (overall_precision + overall_recall) > 0
            else 0.0
        )

        return {
            "overall": {
                "precision": round(overall_precision, 4),
                "recall": round(overall_recall, 4),
                "f1": round(overall_f1, 4),
            },
            "per_type": per_type,
        }

    def save(self, path: str | Path) -> None:
        """Persist the trained spaCy model to disk.

        Parameters
        ----------
        path :
            Directory to save the model to.
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        self._nlp.to_disk(path)
        logger.info("Model saved to %s", path)

    def load(self, path: str | Path) -> None:
        """Load a previously saved spaCy model from disk.

        Parameters
        ----------
        path :
            Directory containing the saved model.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Model directory not found: {path}")
        self._nlp = spacy.load(path)
        self._is_trained = True
        logger.info("Model loaded from %s", path)

    # ------------------------------------------------------------------
    # Dictionary-based fallback
    # ------------------------------------------------------------------

    def _build_alias_lookup(self) -> None:
        """Construct the alias → (canonical_name, entity_type) lookup table.

        Reads ``data/annotations/character_aliases.json`` and optionally
        ``data/processed/myths.json`` to populate the lookup with every
        known surface form of every mythology entity.
        """
        # 1. Load character aliases
        aliases_path = _PROJECT_ROOT / "data" / "annotations" / "character_aliases.json"
        aliases: dict[str, list[str]] = {}
        if aliases_path.exists():
            with open(aliases_path, encoding="utf-8") as f:
                aliases = json.load(f)
            logger.debug("Loaded %d character alias entries", len(aliases))
        else:
            logger.warning("character_aliases.json not found at %s", aliases_path)

        # 2. Register canonical names and their aliases
        for canonical_name, alias_list in aliases.items():
            entity_type = _DEFAULT_ENTITY_TYPES.get(canonical_name, "MORTAL")
            # Register the canonical name itself
            self._alias_lookup[canonical_name] = entity_type
            # Register every alias
            for alias in alias_list:
                self._alias_lookup[alias] = entity_type

        # 3. Register entities from the default type map that aren't characters
        #    (locations, artifacts, etc.)
        for name, etype in _DEFAULT_ENTITY_TYPES.items():
            if name not in self._alias_lookup:
                self._alias_lookup[name] = etype

        # 4. Try to enrich from myths.json
        myths_path = _PROJECT_ROOT / "data" / "processed" / "myths.json"
        if myths_path.exists():
            try:
                with open(myths_path, encoding="utf-8") as f:
                    myths = json.load(f)
                self._enrich_from_myths(myths)
            except (json.JSONDecodeError, KeyError) as exc:
                logger.warning("Could not parse myths.json: %s", exc)

    def _enrich_from_myths(self, myths: list[dict[str, Any]]) -> None:
        """Extract additional entity names from the annotated myth dataset."""
        for myth in myths:
            # Characters
            for char in myth.get("characters", []):
                name = char if isinstance(char, str) else char.get("name", "")
                if name and name not in self._alias_lookup:
                    role = ""
                    if isinstance(char, dict):
                        role = char.get("role", "").upper()
                    entity_type = _DEFAULT_ENTITY_TYPES.get(
                        name,
                        role if role in ENTITY_LABELS else "MORTAL",
                    )
                    self._alias_lookup[name] = entity_type

            # Locations
            for loc in myth.get("locations", []):
                loc_name = loc if isinstance(loc, str) else loc.get("name", "")
                if loc_name and loc_name not in self._alias_lookup:
                    self._alias_lookup[loc_name] = "LOCATION"

            # Artifacts / objects
            for artifact in myth.get("artifacts", []):
                art_name = artifact if isinstance(artifact, str) else artifact.get("name", "")
                if art_name and art_name not in self._alias_lookup:
                    self._alias_lookup[art_name] = "ARTIFACT"

    def _dictionary_predict(self, text: str) -> list[dict[str, Any]]:
        """Find known entities in *text* using exact and case-insensitive matching.

        Performs longest-match-first scanning to avoid partial overlaps.

        Returns
        -------
        list[dict]
            Entities found via the dictionary lookup.
        """
        entities: list[dict[str, Any]] = []

        if not self._alias_lookup:
            return entities

        # Sort aliases by length descending for longest-match-first
        sorted_aliases = sorted(
            self._alias_lookup.keys(), key=len, reverse=True
        )

        text_lower = text.lower()
        occupied: list[tuple[int, int]] = []

        for alias in sorted_aliases:
            alias_lower = alias.lower()
            search_start = 0

            while True:
                idx = text_lower.find(alias_lower, search_start)
                if idx == -1:
                    break

                end_idx = idx + len(alias)
                search_start = end_idx

                # Check word boundaries to avoid matching inside other words
                if idx > 0 and text[idx - 1].isalnum():
                    continue
                if end_idx < len(text) and text[end_idx].isalnum():
                    continue

                # Check for overlap with already-found entities
                span = (idx, end_idx)
                if any(
                    not (span[1] <= occ[0] or span[0] >= occ[1])
                    for occ in occupied
                ):
                    continue

                # Use the original text's casing for the surface form
                surface_text = text[idx:end_idx]
                entity_type = self._alias_lookup[alias]

                entities.append(
                    {
                        "text": surface_text,
                        "label": entity_type,
                        "start": idx,
                        "end": end_idx,
                    }
                )
                occupied.append(span)

        return entities

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _overlaps(
        span: tuple[int, int],
        existing: set[tuple[int, int]],
    ) -> bool:
        """Return *True* if *span* overlaps with any span in *existing*."""
        for s, e in existing:
            if not (span[1] <= s or span[0] >= e):
                return True
        return False

    @property
    def labels(self) -> list[str]:
        """Currently registered entity labels."""
        return list(self._labels)

    @property
    def alias_count(self) -> int:
        """Number of entries in the dictionary lookup."""
        return len(self._alias_lookup)

    def __repr__(self) -> str:
        return (
            f"MythEntityRecognizer(model={self._model_name!r}, "
            f"labels={self._labels}, aliases={len(self._alias_lookup)}, "
            f"trained={self._is_trained})"
        )
