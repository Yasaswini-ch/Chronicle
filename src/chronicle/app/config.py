"""Streamlit application configuration for Chronicle.

Centralises path resolution, theme colours, and default settings
so every component draws from one source of truth.
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

# Walk upward from this file to find the project root.
# Layout: <root>/src/chronicle/app/config.py  →  root is 4 levels up.
_THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT: Path = _THIS_DIR.parent.parent.parent

DATA_DIR: Path = PROJECT_ROOT / "data"
PROCESSED_DIR: Path = DATA_DIR / "processed"
ANNOTATIONS_DIR: Path = DATA_DIR / "annotations"
MODELS_DIR: Path = PROJECT_ROOT / "models"
OUTPUT_DIR: Path = PROJECT_ROOT / "output"

MYTHS_JSON: Path = PROCESSED_DIR / "myths.json"
CHARACTER_ALIASES_JSON: Path = ANNOTATIONS_DIR / "character_aliases.json"

# ---------------------------------------------------------------------------
# Theme colour palette (Refined classical editorial tones: no neon, no rainbow)
# ---------------------------------------------------------------------------

THEME_COLORS: dict[str, str] = {
    "hubris": "#8B2635",      # garnet crimson
    "love": "#9E5A63",        # antique rose terracotta
    "betrayal": "#4A5568",    # deep slate
    "revenge": "#7B3F00",     # umber bronze
    "wisdom": "#2C5E7A",      # Aegean deep blue
    "jealousy": "#4D6A53",    # laurel olive
}

#: Ordered list of all recognised themes.
THEME_LABELS: list[str] = sorted(THEME_COLORS.keys())

# ---------------------------------------------------------------------------
# Character type text categories (zero emojis)
# ---------------------------------------------------------------------------

CHARACTER_ICONS: dict[str, str] = {
    "god": "DEITY",
    "mortal": "MORTAL",
    "creature": "BEAST",
    "titan": "TITAN",
    "location": "LOC",
    "artifact": "RELIC",
}

# ---------------------------------------------------------------------------
# Default application settings
# ---------------------------------------------------------------------------

APP_TITLE: str = "Chronicle: Greek Mythology NLP System"
APP_SUBTITLE: str = "Natural Language Processing System for Classical Lore"
APP_ICON: str | None = None

#: Number of similar myths shown in the embedding view.
DEFAULT_TOP_N_SIMILAR: int = 5

#: Default dimensionality-reduction method.
DEFAULT_REDUCTION_METHOD: str = "tsne"

#: Default t-SNE perplexity.
DEFAULT_PERPLEXITY: float = 8.0

#: Page configuration defaults.
PAGE_CONFIG: dict[str, object] = {
    "page_title": f"{APP_TITLE} - {APP_SUBTITLE}",
    "layout": "wide",
    "initial_sidebar_state": "collapsed",
}
