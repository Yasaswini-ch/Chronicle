"""Text representation module for Chronicle.

Provides TF-IDF, Word2Vec, Sentence-BERT embedding methods,
visualization utilities, and an orchestration pipeline.
"""

from .tfidf import TfidfRepresentation

try:
    from .word2vec import Word2VecRepresentation
except ImportError:
    Word2VecRepresentation = None  # type: ignore

try:
    from .sbert import SBERTRepresentation
except ImportError:
    SBERTRepresentation = None  # type: ignore

from .visualizer import EmbeddingVisualizer
from .pipeline import RepresentationPipeline

__all__ = [
    "TfidfRepresentation",
    "Word2VecRepresentation",
    "SBERTRepresentation",
    "EmbeddingVisualizer",
    "RepresentationPipeline",
]
