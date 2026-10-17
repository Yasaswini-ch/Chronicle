#!/usr/bin/env python
"""Measure Chronicle against the hand-written gold sets in ``data/eval/``.

Reports:
  * chatbot  - intent accuracy and answer-contains rate
  * retrieval - hit@1 / hit@3 of free-text myth search (BM25; SBERT too with --sbert)
  * themes   - how often the automatic theme labels agree with the gold labels, and how a
               classifier trained on the *other* myths does on the gold ones

Everything except the classifier runs on the standard library, so it works in the slim install.

Usage:
    python scripts/evaluate.py            # prints a report, writes data/output/evaluation.json
    python scripts/evaluate.py --sbert    # also evaluate embedding retrieval (needs the ml extra)
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from chronicle.chatbot.engine import ChatEngine  # noqa: E402
from chronicle.insights.knowledge import MythKnowledge  # noqa: E402

EVAL = ROOT / "data" / "eval"
MYTHS = json.loads((ROOT / "data" / "processed" / "myths.json").read_text(encoding="utf-8"))


def load(name: str) -> dict:
    return json.loads((EVAL / name).read_text(encoding="utf-8"))


def eval_chat(engine: ChatEngine) -> dict:
    cases = load("chat_gold.json")["cases"]
    intent_ok = answer_ok = 0
    misses = []
    for c in cases:
        out = engine.chat(c["query"], history=[])
        i_ok = out["intent"] == c["intent"]
        a_ok = all(s.lower() in out["response"].lower() for s in c["contains"])
        intent_ok += i_ok
        answer_ok += a_ok
        if not (i_ok and a_ok):
            misses.append({"query": c["query"], "expected_intent": c["intent"], "got_intent": out["intent"],
                           "missing": [s for s in c["contains"] if s.lower() not in out["response"].lower()]})
    n = len(cases)
    return {"cases": n, "intent_accuracy": intent_ok / n, "answer_accuracy": answer_ok / n, "misses": misses}


def eval_retrieval(engine: ChatEngine, use_sbert: bool) -> dict:
    queries = load("retrieval_gold.json")["queries"]
    knowledge = engine.knowledge

    def run(search) -> dict:
        h1 = h3 = 0
        misses = []
        for q in queries:
            titles = [m["title"] for m in search(q["query"])]
            hit = lambda ts: any(any(e.lower() in t.lower() for e in q["expect"]) for t in ts)  # noqa: E731
            h1 += hit(titles[:1])
            ok3 = hit(titles[:3])
            h3 += ok3
            if not ok3:
                misses.append({"query": q["query"], "top3": titles[:3]})
        n = len(queries)
        return {"queries": n, "hit_at_1": h1 / n, "hit_at_3": h3 / n, "misses": misses}

    result = {"bm25": run(lambda q: knowledge.search(q, top_k=3))}
    # Baseline the BM25 numbers should beat: the first three myths in file order.
    result["baseline_file_order"] = run(lambda q: MYTHS[:3])
    if use_sbert:
        from chronicle.representation.sbert import SBERTRepresentation

        retriever = ChatEngine(myths=MYTHS, sbert_model=SBERTRepresentation(), knowledge=knowledge).retriever
        result["hybrid_sbert_bm25"] = run(lambda q: retriever.retrieve_by_query(q, top_k=3))  # what the app uses
        bm25, retriever._bm25 = retriever._bm25, None  # dense ranking only
        result["sbert_only"] = run(lambda q: retriever.retrieve_by_query(q, top_k=3))
        retriever._bm25 = bm25
    return result


def eval_themes() -> dict:
    gold = load("gold_themes.json")["labels"]
    by_title = {m["title"]: m for m in MYTHS}
    rows = [(by_title[t], accept) for t, accept in gold.items() if t in by_title]
    top1 = sum(m["theme"] in accept for m, accept in rows)
    top3 = sum(bool(set(m.get("themes", [m["theme"]])) & set(accept)) for m, accept in rows)
    majority = Counter(accept[0] for _, accept in rows).most_common(1)[0]
    rng = random.Random(0)
    all_themes = load("gold_themes.json")["themes"]
    rand = sum(rng.choice(all_themes) in accept for _, accept in rows) / len(rows)
    out = {
        "gold_myths": len(rows),
        "label_agreement_top1": top1 / len(rows),
        "label_agreement_any_of_top3": top3 / len(rows),
        "baseline_random": rand,
        "baseline_majority": sum(majority[0] in accept for _, accept in rows) / len(rows),
        "majority_theme": majority[0],
    }

    try:  # classifier trained on the myths that are NOT in the gold set
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.svm import LinearSVC
    except ImportError:
        out["classifier"] = "scikit-learn not installed"
        return out

    gold_ids = {m["id"] for m, _ in rows}
    train = [m for m in MYTHS if m["id"] not in gold_ids]
    vec = TfidfVectorizer(sublinear_tf=True, stop_words="english", min_df=2)
    x_train = vec.fit_transform([m["text"] for m in train])
    y_train = [m["theme"] for m in train]
    x_test = vec.transform([m["text"] for m, _ in rows])
    out["classifier"] = {"train_myths": len(train)}
    for name, model in (("logreg_tfidf", LogisticRegression(max_iter=2000)), ("linear_svm_tfidf", LinearSVC())):
        model.fit(x_train, y_train)
        pred = model.predict(x_test)
        out["classifier"][name] = sum(p in accept for p, (_, accept) in zip(pred, rows)) / len(rows)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sbert", action="store_true", help="also evaluate Sentence-BERT retrieval")
    args = ap.parse_args()

    engine = ChatEngine(myths=MYTHS, knowledge=MythKnowledge(MYTHS))
    report = {"corpus_myths": len(MYTHS), "chatbot": eval_chat(engine),
              "retrieval": eval_retrieval(engine, args.sbert), "themes": eval_themes()}
    (ROOT / "data" / "output").mkdir(parents=True, exist_ok=True)
    (ROOT / "data" / "output" / "evaluation.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    c, r, t = report["chatbot"], report["retrieval"], report["themes"]
    print(f"Corpus: {report['corpus_myths']} myths\n")
    print(f"CHATBOT ({c['cases']} questions)")
    print(f"  intent accuracy  {c['intent_accuracy']:.0%}\n  answer correct   {c['answer_accuracy']:.0%}")
    for m in c["misses"]:
        print(f"  miss: {m['query']!r} -> {m['got_intent']} (wanted {m['expected_intent']}); missing {m['missing']}")
    print("\nRETRIEVAL (hit@1 / hit@3)")
    for name, v in r.items():
        print(f"  {name:20} {v['hit_at_1']:.0%} / {v['hit_at_3']:.0%}   ({v['queries']} queries)")
    for m in r["bm25"]["misses"]:
        print(f"  miss: {m['query']!r} -> {m['top3']}")
    print(f"\nTHEMES ({t['gold_myths']} hand-labelled myths)")
    print(f"  automatic labels, top theme in gold set  {t['label_agreement_top1']:.0%}")
    print(f"  automatic labels, any of top 3           {t['label_agreement_any_of_top3']:.0%}")
    print(f"  baselines: random {t['baseline_random']:.0%}, always '{t['majority_theme']}' {t['baseline_majority']:.0%}")
    if isinstance(t["classifier"], dict):
        cl = t["classifier"]
        print(f"  classifiers trained on {cl['train_myths']} other myths: logreg {cl['logreg_tfidf']:.0%}, svm {cl['linear_svm_tfidf']:.0%}")


if __name__ == "__main__":
    main()
