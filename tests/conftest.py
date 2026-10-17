"""Shared pytest fixtures for the Chronicle test suite.

Provides reusable sample data and configured objects that multiple
test modules rely on.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Path fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the Chronicle project root directory."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def data_dir(project_root: Path) -> Path:
    """Return the path to the data/ directory."""
    return project_root / "data"


# ---------------------------------------------------------------------------
# Sample myth data
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def sample_myths() -> list[dict[str, Any]]:
    """Return five sample myth dictionaries with rich annotations.

    Each myth has: title, category, text, characters, themes, source.
    """
    return [
        {
            "title": "Prometheus Brings Fire",
            "category": "creation",
            "text": (
                "Prometheus, the wisest of the Titans, stole fire from the forge "
                "of Hephaestus on Mount Olympus. He carried the divine flame hidden "
                "inside a hollow fennel stalk and delivered it to humankind. Zeus, "
                "enraged by this defiance, ordered Prometheus chained to a rock in "
                "the Caucasus mountains, where an eagle devoured his liver each day, "
                "only for it to regenerate each night."
            ),
            "characters": ["Prometheus", "Zeus", "Hephaestus"],
            "themes": ["defiance", "punishment", "gift to humanity"],
            "source": "Hesiod, Theogony",
        },
        {
            "title": "The Twelve Labours of Heracles",
            "category": "heroic",
            "text": (
                "Heracles, the mightiest of all Greek heroes and son of Zeus, was "
                "driven mad by Hera and slew his own children. To atone for this "
                "terrible crime, the Oracle at Delphi commanded him to serve King "
                "Eurystheus and perform twelve impossible labours. The first was to "
                "slay the Nemean Lion, whose golden fur was impervious to weapons. "
                "Heracles strangled the beast with his bare hands and wore its pelt "
                "as armor."
            ),
            "characters": ["Heracles", "Zeus", "Hera", "Eurystheus"],
            "themes": ["atonement", "heroism", "divine punishment"],
            "source": "Apollodorus, Bibliotheca",
        },
        {
            "title": "Persephone and the Underworld",
            "category": "divine",
            "text": (
                "Hades, lord of the underworld, abducted Persephone, the daughter "
                "of Demeter, while she gathered flowers in a meadow. Demeter searched "
                "the earth in grief, and in her sorrow all crops withered and famine "
                "spread across the land. Zeus intervened, commanding Hades to release "
                "Persephone. But because she had eaten pomegranate seeds in the "
                "underworld, she was bound to return for part of each year, thus "
                "giving rise to the seasons."
            ),
            "characters": ["Hades", "Persephone", "Demeter", "Zeus"],
            "themes": ["abduction", "grief", "seasons", "compromise"],
            "source": "Homeric Hymn to Demeter",
        },
        {
            "title": "Odysseus and the Cyclops",
            "category": "heroic",
            "text": (
                "During his long voyage home from Troy, Odysseus and his men landed "
                "on the island of the Cyclopes. They entered the cave of Polyphemus, "
                "a one-eyed giant and son of Poseidon. The Cyclops trapped them and "
                "began devouring the crew. Odysseus devised a cunning plan: he offered "
                "Polyphemus strong wine and, when the giant fell into a drunken sleep, "
                "drove a sharpened stake into his single eye. Odysseus told Polyphemus "
                "his name was 'Nobody', so when Polyphemus cried for help, the other "
                "Cyclopes ignored him."
            ),
            "characters": ["Odysseus", "Polyphemus", "Poseidon"],
            "themes": ["cunning", "survival", "hubris"],
            "source": "Homer, Odyssey",
        },
        {
            "title": "Pandora's Box",
            "category": "creation",
            "text": (
                "After Prometheus stole fire for humanity, Zeus sought revenge on "
                "mortals. He ordered Hephaestus to craft a beautiful woman from clay, "
                "and the gods each bestowed upon her a gift. They named her Pandora, "
                "meaning 'all-gifted'. Zeus gave Pandora a sealed jar and sent her to "
                "Epimetheus, brother of Prometheus. Overcome by curiosity, Pandora "
                "opened the jar, releasing all evils—disease, suffering, and death—"
                "into the world. Only Hope remained inside when she closed the lid."
            ),
            "characters": ["Pandora", "Zeus", "Hephaestus", "Prometheus", "Epimetheus"],
            "themes": ["curiosity", "punishment", "hope"],
            "source": "Hesiod, Works and Days",
        },
    ]


@pytest.fixture(scope="session")
def sample_texts(sample_myths: list[dict[str, Any]]) -> list[str]:
    """Return the cleaned text bodies from sample myths."""
    return [myth["text"] for myth in sample_myths]


@pytest.fixture(scope="session")
def sample_categories(sample_myths: list[dict[str, Any]]) -> list[str]:
    """Return category labels corresponding to sample_myths."""
    return [myth["category"] for myth in sample_myths]


# ---------------------------------------------------------------------------
# Alias resolver fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def alias_map() -> dict[str, list[str]]:
    """Return a small alias map for testing."""
    return {
        "Zeus": ["Jupiter", "Jove", "Father Zeus", "Cloud-Gatherer", "Thunderer"],
        "Hera": ["Juno", "Queen of the Gods", "Ox-Eyed Hera"],
        "Poseidon": ["Neptune", "Earth-Shaker", "Lord of the Sea"],
        "Athena": ["Minerva", "Pallas", "Pallas Athena", "Grey-Eyed Athena"],
        "Heracles": ["Hercules", "Herakles", "Alcides"],
        "Odysseus": ["Ulysses", "Man of Many Wiles"],
        "Hades": ["Pluto", "Lord of the Dead", "Unseen One"],
    }


@pytest.fixture(scope="session")
def alias_resolver(alias_map: dict[str, list[str]]):
    """Return a configured AliasResolver, or skip if not yet implemented."""
    try:
        from chronicle.preprocessing.aliases import AliasResolver
    except ImportError:
        pytest.skip("AliasResolver not yet implemented")
    return AliasResolver(alias_map)


# ---------------------------------------------------------------------------
# HTML / dirty text samples
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def dirty_html_text() -> str:
    """Return a sample myth text laden with HTML, footnotes, and encoding issues."""
    return (
        '<div class="myth-text">\n'
        "<p>Zeus&mdash;king of the gods[1]&mdash;hurled his thunderbolt "
        "at the Titans.</p>\n"
        "<p>Hera, his wife (see note 3), watched from Mount Olympus.</p>\n"
        "<!-- editorial comment -->\n"
        "<p>The battle raged for ten years\u00b2.</p>\n"
        "</div>"
    )
