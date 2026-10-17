"""Vercel serverless entry point.

Vercel runs ``app`` from this module for every ``/api/*`` request (see the
rewrite in ``vercel.json``). The heavy NLP stack is not installed on Vercel, so
semantic search (Sentence-BERT) is switched off and the chatbot falls back to
keyword retrieval.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.environ.setdefault("CHRONICLE_DISABLE_SBERT", "1")
os.environ.setdefault("CHRONICLE_ROOT", str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from chronicle.api.app import app  # noqa: E402,F401  (Vercel looks for `app`)
