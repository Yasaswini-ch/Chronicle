#!/usr/bin/env python
"""Download all NLP models and data required by Chronicle.

Downloads:
1. spaCy English model (en_core_web_sm)
2. NLTK data packages (punkt, wordnet, stopwords, averaged_perceptron_tagger)
3. Sentence-transformers model (all-MiniLM-L6-v2) via pre-import caching

Run once before first use:
    python scripts/download_models.py
"""

from __future__ import annotations

import subprocess
import sys
import time


def _print_status(name: str, success: bool, elapsed: float) -> None:
    """Print a coloured status line."""
    icon = "✓" if success else "✗"
    status = "OK" if success else "FAILED"
    print(f"  {icon} {name:<50s} {status}  ({elapsed:.1f}s)")


def download_spacy_model() -> bool:
    """Download the spaCy English model."""
    print("\n[1/3] Downloading spaCy model: en_core_web_sm")
    start = time.perf_counter()
    try:
        subprocess.check_call(
            [sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        elapsed = time.perf_counter() - start
        _print_status("spacy / en_core_web_sm", True, elapsed)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        elapsed = time.perf_counter() - start
        _print_status(f"spacy / en_core_web_sm ({exc})", False, elapsed)
        return False


def download_nltk_data() -> bool:
    """Download required NLTK data packages."""
    print("\n[2/3] Downloading NLTK data packages")
    packages = [
        "punkt",
        "punkt_tab",
        "wordnet",
        "stopwords",
        "averaged_perceptron_tagger",
        "averaged_perceptron_tagger_eng",
        "omw-1.4",
    ]
    all_ok = True
    try:
        import nltk  # noqa: E402
    except ImportError:
        print("  ✗ nltk is not installed. Run: pip install nltk")
        return False

    for pkg in packages:
        start = time.perf_counter()
        try:
            nltk.download(pkg, quiet=True)
            elapsed = time.perf_counter() - start
            _print_status(f"nltk / {pkg}", True, elapsed)
        except Exception as exc:
            elapsed = time.perf_counter() - start
            _print_status(f"nltk / {pkg} ({exc})", False, elapsed)
            all_ok = False
    return all_ok


def download_sentence_transformers_model() -> bool:
    """Download the sentence-transformers model by importing it.

    The ``SentenceTransformer`` constructor automatically downloads and
    caches the model on first use.
    """
    model_name = "all-MiniLM-L6-v2"
    print(f"\n[3/3] Downloading sentence-transformers model: {model_name}")
    start = time.perf_counter()
    try:
        from sentence_transformers import SentenceTransformer

        _ = SentenceTransformer(model_name)
        elapsed = time.perf_counter() - start
        _print_status(f"sentence-transformers / {model_name}", True, elapsed)
        return True
    except ImportError:
        elapsed = time.perf_counter() - start
        _print_status(
            f"sentence-transformers / {model_name} (not installed)", False, elapsed,
        )
        return False
    except Exception as exc:
        elapsed = time.perf_counter() - start
        _print_status(
            f"sentence-transformers / {model_name} ({exc})", False, elapsed,
        )
        return False


def main() -> None:
    """Run all downloads and print a summary."""
    print("=" * 65)
    print("  Chronicle — Model & Data Downloader")
    print("=" * 65)

    results: dict[str, bool] = {}
    overall_start = time.perf_counter()

    results["spaCy"] = download_spacy_model()
    results["NLTK"] = download_nltk_data()
    results["sentence-transformers"] = download_sentence_transformers_model()

    overall_elapsed = time.perf_counter() - overall_start

    # Summary
    print("\n" + "=" * 65)
    print("  Summary")
    print("=" * 65)
    for name, ok in results.items():
        icon = "✓" if ok else "✗"
        print(f"  {icon} {name}")

    all_ok = all(results.values())
    print(f"\nTotal time: {overall_elapsed:.1f}s")
    if all_ok:
        print("\n  All downloads completed successfully! ✓")
    else:
        failed = [k for k, v in results.items() if not v]
        print(f"\n  Some downloads failed: {', '.join(failed)}")
        print("  Install missing packages and re-run this script.")
    print()


if __name__ == "__main__":
    main()
