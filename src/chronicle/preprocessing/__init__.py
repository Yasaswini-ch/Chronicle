"""Preprocessing modules for the Chronicle mythology NLP system.

This package provides text cleaning, character-name alias resolution,
tokenisation, and a unified pipeline that chains them together.

Public API
----------
.. autosummary::
    TextCleaner
    AliasResolver
    MythTokenizer
    PreprocessingPipeline
"""

from .alias_resolver import AliasResolver
from .cleaner import TextCleaner
from .pipeline import PreprocessingPipeline
from .tokenizer import MythTokenizer

__all__ = [
    "AliasResolver",
    "MythTokenizer",
    "PreprocessingPipeline",
    "TextCleaner",
]
