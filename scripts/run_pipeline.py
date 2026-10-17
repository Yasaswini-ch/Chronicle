#!/usr/bin/env python
"""Chronicle — End-to-end pipeline runner.

Executes the full NLP pipeline on the Greek mythology corpus:

    1. Load myths from data/processed/myths.json
    2. Run the preprocessing pipeline
    3. Build representations (TF-IDF, Word2Vec, SBERT)
    4. Train classifiers and compare
    5. Run NER and build a knowledge graph
    6. Generate summaries and topic model
    7. Save all outputs to data/output/

Usage:
    python scripts/run_pipeline.py [--data PATH] [--output PATH]
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Resolve project root (one level up from scripts/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("chronicle.pipeline")


# ---------------------------------------------------------------------------
# Timer context manager
# ---------------------------------------------------------------------------

class StageTimer:
    """Context manager that logs elapsed time for a pipeline stage."""

    def __init__(self, stage_name: str) -> None:
        self.stage_name = stage_name
        self.elapsed: float = 0.0

    def __enter__(self) -> "StageTimer":
        logger.info("▶ Starting stage: %s", self.stage_name)
        self._start = time.perf_counter()
        return self

    def __exit__(self, *exc: object) -> None:
        self.elapsed = time.perf_counter() - self._start
        logger.info(
            "✓ Completed stage: %s (%.2fs)", self.stage_name, self.elapsed,
        )


# ---------------------------------------------------------------------------
# Pipeline stages
# ---------------------------------------------------------------------------

def load_myths(data_path: Path) -> list[dict[str, Any]]:
    """Load myth data from a JSON file."""
    with StageTimer("Load myths"):
        if not data_path.exists():
            logger.warning("Data file not found: %s — using built-in samples", data_path)
            return _builtin_sample_myths()
        with open(data_path, encoding="utf-8") as fh:
            myths = json.load(fh)
        logger.info("Loaded %d myths from %s", len(myths), data_path)
        return myths


def run_preprocessing(myths: list[dict[str, Any]]) -> list[str]:
    """Run the preprocessing pipeline on myth texts."""
    with StageTimer("Preprocessing"):
        from chronicle.preprocessing.cleaner import TextCleaner
        cleaner = TextCleaner()

        cleaned_texts: list[str] = []
        for myth in myths:
            raw = myth.get("text", "")
            cleaned = cleaner.clean(raw)
            cleaned_texts.append(cleaned)

        # Try the full pipeline if available
        try:
            from chronicle.preprocessing.pipeline import PreprocessingPipeline
            pipeline = PreprocessingPipeline()
            cleaned_texts = pipeline.process_batch(
                [m.get("text", "") for m in myths],
            )
            logger.info("Used full PreprocessingPipeline")
        except ImportError:
            logger.info("PreprocessingPipeline not available, used TextCleaner only")

        logger.info("Preprocessed %d texts", len(cleaned_texts))
        return cleaned_texts


def build_representations(
    texts: list[str],
    output_dir: Path,
) -> dict[str, Any]:
    """Build TF-IDF, Word2Vec, and SBERT representations."""
    results: dict[str, Any] = {}

    # --- TF-IDF -----------------------------------------------------------
    with StageTimer("TF-IDF representation"):
        from chronicle.representation.tfidf import TfidfRepresentation
        tfidf = TfidfRepresentation(
            ngram_range=(1, 2), max_features=5000, min_df=1, max_df=0.95,
        )
        tfidf_matrix = tfidf.fit_transform(texts)
        tfidf.save(output_dir / "tfidf_model.pkl")
        results["tfidf"] = {
            "num_features": tfidf_matrix.shape[1],
            "num_documents": tfidf_matrix.shape[0],
            "sample_top_terms": {},
        }
        for i, text in enumerate(texts[:5]):
            top = tfidf.get_top_terms(text, n=5)
            results["tfidf"]["sample_top_terms"][f"doc_{i}"] = [
                {"term": t, "score": round(s, 4)} for t, s in top
            ]
        logger.info(
            "TF-IDF: %d docs × %d features",
            tfidf_matrix.shape[0],
            tfidf_matrix.shape[1],
        )

    # --- Word2Vec ---------------------------------------------------------
    with StageTimer("Word2Vec representation"):
        try:
            from chronicle.representation.word2vec import Word2VecRepresentation
            tokenised = [text.lower().split() for text in texts]
            w2v = Word2VecRepresentation(vector_size=100, min_count=1, epochs=50)
            w2v.train(tokenised)
            w2v.save(output_dir / "word2vec_model.bin")
            results["word2vec"] = {
                "vector_size": 100,
                "vocab_size": len(w2v.vocabulary),
            }
            logger.info("Word2Vec: vocab_size=%d", len(w2v.vocabulary))
        except ImportError:
            logger.warning("Word2VecRepresentation not available — skipping")
            results["word2vec"] = {"status": "not_available"}

    # --- SBERT ------------------------------------------------------------
    with StageTimer("SBERT representation"):
        try:
            from chronicle.representation.sbert import SBERTRepresentation
            sbert = SBERTRepresentation(model_name="all-MiniLM-L6-v2")
            embeddings = sbert.encode_batch(texts)
            results["sbert"] = {
                "embedding_dim": int(embeddings.shape[1]),
                "num_documents": int(embeddings.shape[0]),
            }
            logger.info(
                "SBERT: %d docs × %d dims",
                embeddings.shape[0],
                embeddings.shape[1],
            )
        except ImportError:
            logger.warning("SBERTRepresentation not available — skipping")
            results["sbert"] = {"status": "not_available"}

    return results


def train_classifiers(
    texts: list[str],
    labels: list[str],
) -> dict[str, Any]:
    """Train classifiers and compare their performance."""
    results: dict[str, Any] = {}

    with StageTimer("Classifier training & evaluation"):
        # Classical classifiers
        try:
            from chronicle.classifier.classical import ClassicalClassifier

            counts = Counter(labels)
            results["majority_baseline"] = {
                "accuracy": max(counts.values()) / len(labels),
                "n_docs": len(labels),
                "n_classes": len(counts),
            }
            for model_type in ("svm", "naive_bayes"):
                # train() scores a held-out 20% split, then refits on everything. Scoring
                # the refit model on the same texts would only measure memorisation.
                clf = ClassicalClassifier(model_type=model_type)
                report = dict(clf.train(texts, labels))
                n_folds = min(5, min(counts.values()))
                if n_folds >= 2:
                    cv = ClassicalClassifier(model_type=model_type).cross_validate(texts, labels, n_folds=n_folds)
                    report.update(
                        cv_folds=n_folds,
                        cv_accuracy_mean=cv["accuracy_mean"], cv_accuracy_std=cv["accuracy_std"],
                        cv_f1_macro_mean=cv["f1_macro_mean"],
                    )
                report["evaluation"] = "held-out 20% split and stratified k-fold cross-validation"
                results[model_type] = report
                logger.info(
                    "%s held-out accuracy %.3f | CV accuracy %.3f (majority baseline %.3f)",
                    model_type, report.get("accuracy", 0), report.get("cv_accuracy_mean", float("nan")),
                    results["majority_baseline"]["accuracy"],
                )
        except ImportError:
            logger.warning("ClassicalClassifier not available — skipping")
            results["classical"] = {"status": "not_available"}

        # Neural classifier
        try:
            from chronicle.classifier.neural import NeuralClassifier

            clf = NeuralClassifier(epochs=20, batch_size=4)
            history = clf.train(texts, labels)
            results["neural"] = {
                "accuracy": history.get("accuracy"),  # validation split, not training data
                "f1_macro": history.get("f1_macro"),
                "final_loss": history["loss"][-1] if history and "loss" in history else None,
                "final_val_loss": history["val_losses"][-1] if history and history.get("val_losses") else None,
                "epochs": 20,
                "evaluation": "20% validation split",
            }
            logger.info("Neural classifier trained")
        except ImportError:
            logger.warning("NeuralClassifier not available — skipping")
            results["neural"] = {"status": "not_available"}

        # Evaluator comparison
        try:
            from chronicle.classifier.evaluator import ClassifierEvaluator

            evaluator = ClassifierEvaluator()
            comparison = evaluator.generate_comparison_report(results)
            results["comparison_report"] = comparison
        except ImportError:
            logger.warning("ClassifierEvaluator not available — skipping")

    return results


def run_ner_and_knowledge_graph(
    texts: list[str],
    myths: list[dict[str, Any]],
    output_dir: Path,
) -> dict[str, Any]:
    """Run NER and build a knowledge graph."""
    results: dict[str, Any] = {}

    with StageTimer("NER & Knowledge Graph"):
        # Entity recognition
        try:
            from chronicle.ner.recognizer import MythEntityRecognizer

            recognizer = MythEntityRecognizer()
            all_entities: list[list[dict[str, str]]] = []
            for text in texts:
                entities = recognizer.extract(text)
                all_entities.append(entities)
            results["entities"] = {
                "total_entities": sum(len(ents) for ents in all_entities),
                "documents_processed": len(texts),
            }
            logger.info(
                "Extracted %d entities from %d documents",
                results["entities"]["total_entities"],
                len(texts),
            )
        except ImportError:
            logger.warning("MythEntityRecognizer not available — skipping")
            results["entities"] = {"status": "not_available"}

        # Relation extraction
        try:
            from chronicle.ner.relations import RelationExtractor

            extractor = RelationExtractor()
            annotations = [
                m for m in myths if "relations" in m or "characters" in m
            ]
            if annotations:
                relations = extractor.extract_from_annotations(annotations)
                results["relations"] = {
                    "total_relations": len(relations),
                }
                logger.info("Extracted %d relations", len(relations))
            else:
                results["relations"] = {"total_relations": 0}
        except ImportError:
            logger.warning("RelationExtractor not available — skipping")
            results["relations"] = {"status": "not_available"}

        # Knowledge graph
        try:
            from chronicle.ner.knowledge_graph import KnowledgeGraph

            kg = KnowledgeGraph()
            annotations = [
                m for m in myths if "relations" in m or "characters" in m
            ]
            if annotations:
                kg.build_from_annotations(annotations)
                stats = kg.statistics()
                results["knowledge_graph"] = stats
                logger.info(
                    "Knowledge graph: %d nodes, %d edges",
                    stats.get("num_nodes", 0),
                    stats.get("num_edges", 0),
                )
            else:
                results["knowledge_graph"] = {"num_nodes": 0, "num_edges": 0}
        except ImportError:
            logger.warning("KnowledgeGraph not available — skipping")
            results["knowledge_graph"] = {"status": "not_available"}

    return results


def generate_insights(
    texts: list[str],
    myths: list[dict[str, Any]],
) -> dict[str, Any]:
    """Generate summaries and topic models."""
    results: dict[str, Any] = {}

    with StageTimer("Insights & Topic Modelling"):
        try:
            from chronicle.insights.topic_modeler import MythTopicModeler
        except ImportError:
            logger.warning("MythTopicModeler not available — skipping")
            results["topics"] = {"status": "not_available"}
        else:
            # BERTopic needs far more documents than a 30-myth corpus gives
            # HDBSCAN to cluster, so fall back to LDA when it fails or finds
            # nothing.
            for method, n_topics in (("bertopic", None), ("lda", 6)):
                try:
                    modeler = MythTopicModeler(method=method, n_topics=n_topics)
                    modeler.fit(texts)
                    topics = modeler.get_topics()
                    if not topics:
                        raise RuntimeError("no topics discovered")
                    results["topics"] = {"method": method, "topics": topics}
                    logger.info("Discovered %d topics with %s", len(topics), method)
                    break
                except Exception as exc:  # noqa: BLE001 - try the next backend
                    logger.warning("Topic modelling with %s failed: %s", method, exc)
            else:
                results["topics"] = {"status": "failed"}

        try:
            from chronicle.insights.summarizer import MythSummarizer

            summarizer = MythSummarizer()
            summaries = []
            for myth in myths[:5]:
                summary = summarizer.summarize(myth.get("text", ""))
                summaries.append(
                    {"title": myth.get("title", ""), "summary": summary},
                )
            results["summaries"] = summaries
            logger.info("Generated %d summaries", len(summaries))
        except ImportError:
            logger.warning("MythSummarizer not available — skipping")
            results["summaries"] = {"status": "not_available"}

    return results


def generate_extra_outputs(
    myths: list[dict[str, Any]],
    cleaned_texts: list[str],
    output_dir: Path,
) -> dict[str, Any]:
    """Generate extra outputs 6 through 10:
    - Output 6: Embedding Visualization Map (HTML)
    - Output 7: Similarity Search ("Myths Like This")
    - Output 8: Theme Distribution Dashboard (HTML)
    - Output 9: Character Leaderboard (JSON)
    - Output 10: Exportable Story Cards (JSON & Markdown)
    """
    results: dict[str, Any] = {}

    with StageTimer("Extra Outputs (6-10: Maps, Similarity, Dashboards, Leaderboards, Cards)"):
        # Output 6: Embedding Visualization Map
        try:
            from chronicle.representation.sbert import SBERTRepresentation
            from chronicle.representation.visualizer import EmbeddingVisualizer

            sbert = SBERTRepresentation(model_name="all-MiniLM-L6-v2")
            embeddings = sbert.encode_batch(cleaned_texts)

            labels = [m.get("theme") or m.get("category", "mythology") for m in myths]
            titles = [m.get("title", f"Myth {i}") for i, m in enumerate(myths)]

            reduced = EmbeddingVisualizer.reduce_dimensions(
                embeddings, method="tsne", n_components=2, perplexity=min(10.0, max(2.0, len(myths) - 1))
            )
            fig_map = EmbeddingVisualizer.plot_embeddings(
                reduced,
                labels=titles,
                themes=labels,
                title="Myth Embedding Space (t-SNE 2D)",
            )
            map_path = output_dir / "embedding_map.html"
            fig_map.write_html(str(map_path))
            results["output_6_embedding_map"] = str(map_path)
            logger.info("Saved Output 6 (Embedding Map) to %s", map_path)
        except Exception as exc:
            logger.warning("Could not generate Output 6 embedding map: %s", exc)
            results["output_6_embedding_map"] = {"error": str(exc)}

        # Output 7: Similarity Search
        try:
            from chronicle.chatbot.retriever import MythRetriever
            retriever = MythRetriever(myths=myths)
            sample_query_myth = myths[0].get("title", "The Fall of Icarus")
            similar = retriever.retrieve_similar(sample_query_myth, top_k=3)
            results["output_7_similarity_search"] = {
                "query_myth": sample_query_myth,
                "top_similar": [
                    {"title": m.get("title"), "theme": m.get("theme"), "moral": m.get("moral")}
                    for m in similar
                ],
            }
            logger.info("Generated Output 7 (Similarity search for '%s')", sample_query_myth)
        except Exception as exc:
            logger.warning("Could not run Output 7 similarity search: %s", exc)
            results["output_7_similarity_search"] = {"error": str(exc)}

        # Output 8: Theme Distribution Dashboard
        try:
            from chronicle.insights.dashboard import InsightsDashboard
            dash = InsightsDashboard()
            theme_fig = dash.theme_distribution(myths)
            theme_path = output_dir / "theme_distribution.html"
            theme_fig.write_html(str(theme_path))
            results["output_8_theme_distribution"] = str(theme_path)
            logger.info("Saved Output 8 (Theme Distribution) to %s", theme_path)
        except Exception as exc:
            logger.warning("Could not generate Output 8 theme distribution: %s", exc)
            results["output_8_theme_distribution"] = {"error": str(exc)}

        # Output 9: Character Leaderboard
        try:
            from chronicle.insights.dashboard import InsightsDashboard
            dash = InsightsDashboard()
            leaderboard_stats = dash.get_leaderboard_stats(myths)
            leaderboard_path = output_dir / "character_leaderboard.json"
            with open(leaderboard_path, "w", encoding="utf-8") as fh:
                json.dump(leaderboard_stats, fh, indent=2)
            results["output_9_character_leaderboard"] = leaderboard_stats
            logger.info("Saved Output 9 (Character Leaderboard) to %s", leaderboard_path)
        except Exception as exc:
            logger.warning("Could not generate Output 9 character leaderboard: %s", exc)
            results["output_9_character_leaderboard"] = {"error": str(exc)}

        # Output 10: Exportable Story Cards
        try:
            from chronicle.chatbot.response import ResponseGenerator
            resp_gen = ResponseGenerator()
            cards_dir = output_dir / "story_cards"
            cards_dir.mkdir(parents=True, exist_ok=True)
            exported_cards = []
            for myth in myths[:5]:
                card = resp_gen.format_story_card(myth)
                slug = re.sub(r"[^a-z0-9]+", "_", myth.get("title", "myth").lower()).strip("_")
                card_file = cards_dir / f"{slug}_story_card.json"
                with open(card_file, "w", encoding="utf-8") as fh:
                    json.dump(card, fh, indent=2)
                exported_cards.append(str(card_file))
            results["output_10_story_cards"] = exported_cards
            logger.info("Saved Output 10 (%d Story Cards) to %s", len(exported_cards), cards_dir)
        except Exception as exc:
            logger.warning("Could not generate Output 10 story cards: %s", exc)
            results["output_10_story_cards"] = {"error": str(exc)}

    return results


# ---------------------------------------------------------------------------
# Built-in sample data
# ---------------------------------------------------------------------------

def _builtin_sample_myths() -> list[dict[str, Any]]:
    """Fallback sample myths when no data file is available."""
    return [
        {
            "title": "Prometheus Brings Fire",
            "category": "creation",
            "text": (
                "Prometheus, the wisest of the Titans, stole fire from the "
                "forge of Hephaestus on Mount Olympus and gave it to humanity."
            ),
            "characters": ["Prometheus", "Hephaestus", "Zeus"],
        },
        {
            "title": "The Twelve Labours of Heracles",
            "category": "heroic",
            "text": (
                "Heracles, driven mad by Hera, slew his own children. To "
                "atone he performed twelve impossible labours for King Eurystheus."
            ),
            "characters": ["Heracles", "Hera", "Eurystheus"],
        },
        {
            "title": "Persephone and the Underworld",
            "category": "divine",
            "text": (
                "Hades abducted Persephone, daughter of Demeter. In her grief "
                "Demeter let all crops wither until Zeus commanded Hades to "
                "release her."
            ),
            "characters": ["Hades", "Persephone", "Demeter", "Zeus"],
        },
        {
            "title": "Odysseus and the Cyclops",
            "category": "heroic",
            "text": (
                "Odysseus and his men entered the cave of Polyphemus. The "
                "cunning hero blinded the Cyclops and escaped by clinging to "
                "the bellies of sheep."
            ),
            "characters": ["Odysseus", "Polyphemus"],
        },
        {
            "title": "Pandora's Box",
            "category": "creation",
            "text": (
                "Zeus ordered Hephaestus to craft Pandora from clay. She "
                "opened a sealed jar releasing all evils; only Hope remained."
            ),
            "characters": ["Zeus", "Hephaestus", "Pandora"],
        },
    ]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the full Chronicle pipeline."""
    parser = argparse.ArgumentParser(description="Chronicle NLP Pipeline Runner")
    parser.add_argument(
        "--data",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "myths.json",
        help="Path to the input myths JSON file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data" / "output",
        help="Directory to save pipeline outputs",
    )
    args = parser.parse_args()

    output_dir: Path = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    pipeline_start = time.perf_counter()
    pipeline_results: dict[str, Any] = {
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "stages": {},
    }

    print("=" * 65)
    print("  Chronicle — End-to-End NLP Pipeline")
    print("=" * 65)
    print()

    # 1. Load data
    myths = load_myths(args.data)
    pipeline_results["num_myths"] = len(myths)

    # 2. Preprocessing
    cleaned_texts = run_preprocessing(myths)
    pipeline_results["stages"]["preprocessing"] = {
        "num_texts": len(cleaned_texts),
        "avg_length": (
            round(sum(len(t) for t in cleaned_texts) / len(cleaned_texts), 1)
            if cleaned_texts else 0
        ),
    }

    # 3. Representations
    repr_results = build_representations(cleaned_texts, output_dir)
    pipeline_results["stages"]["representations"] = repr_results

    # 4. Classification
    labels = [m.get("theme") or m.get("category", "hubris") for m in myths]
    clf_results = train_classifiers(cleaned_texts, labels)
    pipeline_results["stages"]["classification"] = clf_results

    # 5. NER & Knowledge Graph
    ner_results = run_ner_and_knowledge_graph(cleaned_texts, myths, output_dir)
    pipeline_results["stages"]["ner"] = ner_results

    # 6. Insights
    insight_results = generate_insights(cleaned_texts, myths)
    pipeline_results["stages"]["insights"] = insight_results

    # 7. Extra Outputs (6 to 10: Embedding Map, Similarity Search, Theme Dashboard, Character Leaderboard, Story Cards)
    extra_results = generate_extra_outputs(myths, cleaned_texts, output_dir)
    pipeline_results["stages"]["extra_outputs_6_to_10"] = extra_results

    # 8. Save results
    pipeline_elapsed = time.perf_counter() - pipeline_start
    pipeline_results["total_time_seconds"] = round(pipeline_elapsed, 2)

    results_path = output_dir / "pipeline_results.json"
    with open(results_path, "w", encoding="utf-8") as fh:
        json.dump(pipeline_results, fh, indent=2, default=str)
    logger.info("Saved pipeline results to %s", results_path)

    # Summary
    print()
    print("=" * 65)
    print("  Pipeline Complete")
    print("=" * 65)
    print(f"  Myths processed:  {len(myths)}")
    print(f"  Total time:       {pipeline_elapsed:.2f}s")
    print(f"  Output directory: {output_dir}")
    print(f"  Results file:     {results_path}")
    print()


if __name__ == "__main__":
    main()
