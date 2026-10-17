# Chronicle 🏛️

**End-to-End NLP System for Greek Mythology Analysis**

Chronicle reads a corpus of **125 Greek myths** and turns it into structured, explorable knowledge: cleaned text, four kinds of text representations, entity and relation extraction, a curated family tree with kinship reasoning, theme and topic analysis, and an offline chatbot ("the Oracle"). A Flask API serves a hand-built React interface with character profiles, story patterns, a quiz and a family-tree view.

The corpus is 30 hand-written retellings plus 95 passages from Bulfinch's *The Age of Fable* (public domain). Theme, character and place labels on the Bulfinch passages are **automatic and not hand-checked**; see [Evaluation](#evaluation) for what that means for the numbers.

---

## Quick start

```bash
# 1. Install (full stack: API, NLP pipeline, tests)
uv venv --python 3.11
.venv\Scripts\Activate.ps1          # macOS/Linux: source .venv/bin/activate
uv pip install -e ".[ml,dev]"
python scripts/download_models.py   # spaCy, NLTK data, Sentence-BERT

# 2. Build the frontend once
cd frontend && npm install && npm run build && cd ..

# 3. Run the app
chronicle-api                       # http://localhost:8000
```

Serving only (no NLP libraries, much smaller): `uv pip install -e .` then `chronicle-api`. Search uses BM25 keyword ranking, which starts instantly; set `CHRONICLE_ENABLE_SBERT=1` to add Sentence-BERT.

---

## What it does

| Page | What you can do |
|---|---|
| **Start Here** | A plain-language primer: who the gods are, what myths are for, what the themes mean. |
| **Read The Myths** | Browse all 125 stories; filter by theme or source; see similar stories. |
| **Ask The Oracle** | Ask in plain English and get clickable follow-up questions (see below). |
| **Explore → Family Tree** | The pantheon as a forest of family trees, built from stories plus the curated genealogy. |
| **Explore → Figures** | Profile of any character: Roman names, family (with half-siblings), recurring themes, stories, companions; compare any two. |
| **Explore → Story Patterns** | 11 recurring plots (transformation, journey to the underworld, mortal defies a god, divine disguise, ...), each with the passage that shows it. |
| **Explore → Test Yourself** | An 8-question quiz generated from the family records, Greek-Roman names and story casts. |
| **Explore → By The Numbers, Gallery, How It Was Built** | Corpus statistics, photographs of antiquity, and the pipeline. |

### The Oracle

```
Who is Minerva?                         -> profile of Athena (Roman names resolve)
How are Zeus and Hera related?          -> "Zeus is Hera's husband and brother."
Who are Zeus's children?                -> Apollo, Ares, Artemis, Athena, ...
Who is the mother of Perseus?           -> Danae
Compare Athena and Arachne              -> shared stories, shared and distinct themes
Which myths are about hubris?           -> theme list
Which myths have someone turned into a tree?   -> pattern search with quoted passages
which myths mention a golden apple      -> falls back to ranked search, never a dead end
```

Intent detection is rule-based (character, family, relationship, comparison, theme, story pattern, similar myths, summary, follow-up). Conversation memory is kept per session, so follow-ups such as "tell me more" work without sharing state between visitors.

### Family reasoning

`data/annotations/genealogy.json` holds curated parent, spouse, sibling and lover relations (Hesiod, Apollodorus, Homer). `chronicle.ner.kinship.FamilyTree` derives what is not written down: siblings and half-siblings from shared parents, grandparents, aunts and uncles, cousins, ancestors. Examples: *Hera is Zeus's wife and sister*, *Apollo is Athena's half-brother*, *Poseidon is Athena's uncle*. A full-sibling claim requires two known parents on both sides.

---

## Architecture

```
 Bulfinch (Project Gutenberg) + 30 hand-written myths
                    |  scripts/build_corpus.py
                    v
         data/processed/myths.json (125 myths)    data/annotations/ (aliases, genealogy, types)
                    |
      +-------------+--------------+
      v                            v
 NLP pipeline (scripts/run_pipeline.py)      Knowledge layer (chronicle.insights.knowledge)
  preprocessing, TF-IDF, Word2Vec, SBERT,     profiles, comparisons, story patterns, quiz,
  NER + relations, classifiers, BERTopic      BM25 search, kinship (chronicle.ner.kinship)
      |                                        |
      +----------------+-----------------------+
                       v
        ChatEngine: intent -> slots -> retrieval -> response (+ suggestions)
                       v
        Flask API (chronicle.api.app, Waitress)  ->  React + Vite frontend
```

### Project layout

| Path | Description |
|---|---|
| `src/chronicle/preprocessing` | Cleaning, NLTK tokenisation, alias resolution (Roman and variant names to canonical Greek names). |
| `src/chronicle/representation` | TF-IDF, Word2Vec, Sentence-BERT, t-SNE/UMAP visualiser. |
| `src/chronicle/text` | Dependency-free BM25 ranker. |
| `src/chronicle/classifier` | SVM, Naive Bayes, neural classifier and evaluator. |
| `src/chronicle/ner` | Entity recogniser, relation extractor, knowledge graph, kinship reasoning. |
| `src/chronicle/insights` | Knowledge layer, summariser, BERTopic/LDA topic modeller, dashboard charts. |
| `src/chronicle/chatbot` | Intents, slots, retriever (hybrid SBERT + BM25), response generator, engine. |
| `src/chronicle/api` | Flask API with validation, session memory, error handling. |
| `src/chronicle/app` | Original Streamlit dashboard (legacy). |
| `frontend/` | React 19 + Vite interface. |
| `scripts/` | `build_corpus.py`, `run_pipeline.py`, `evaluate.py`, `download_models.py`, `generate_dataset.py`. |
| `data/` | `processed/` corpus, `annotations/` aliases, types and genealogy, `eval/` gold sets, `output/` generated results, `raw/` downloaded source text (not committed). |
| `tests/` | pytest suites (about 200 tests). |

---

## Commands

### Rebuild the corpus

```bash
python scripts/build_corpus.py            # downloads Bulfinch (cached in data/raw/), re-annotates, rewrites myths.json
python scripts/build_corpus.py --offline  # use the cached download only
```

The 30 hand-written myths are preserved; the script is safe to re-run.

### Run the NLP pipeline

```bash
python scripts/run_pipeline.py
```

Preprocessing, representations, classifiers, entities and relations, knowledge graph, topics, embedding map, similarity search, leaderboard and story cards, about 4 minutes. Results go to `data/output/` (`pipeline_results.json` and others).

### Evaluate against the gold sets

```bash
python scripts/evaluate.py          # chatbot, search, theme labels (standard library plus scikit-learn)
python scripts/evaluate.py --sbert  # also compare Sentence-BERT and hybrid search
```

Writes `data/output/evaluation.json`.

### Tests

```bash
pytest
```

### Frontend development

```bash
cd frontend
npm run dev      # http://localhost:5173, proxies /api to port 8000
npm run build    # outputs frontend/dist, which the Flask app serves
```

### Docker

```bash
docker build -t chronicle .
docker run -p 8000:8000 chronicle
```

### Streamlit dashboard (legacy)

```bash
streamlit run src/chronicle/app/main.py
```

---

## API

| Endpoint | Purpose |
|---|---|
| `GET /api/health`, `GET /api/ready` | Liveness and readiness probes |
| `GET /api/myths`, `GET /api/myths/<id>` | List (filter `theme`, `search`) or fetch myths |
| `POST /api/chat` | `{"query": str, "session_id"?: str}`; returns answer, intent, story card, suggestions, session id |
| `GET /api/characters`, `GET /api/characters/<name>` | Character list (filter `type`) and profile |
| `GET /api/compare?a=&b=` | Side-by-side comparison of two characters |
| `GET /api/motifs`, `GET /api/motifs/<id>` | Story patterns and the myths showing each |
| `GET /api/search?q=&top_k=` | Ranked free-text search |
| `GET /api/quiz?n=&seed=` | Quiz questions |
| `GET /api/similar/<myth>` | Similar myths |
| `GET /api/graph`, `GET /api/graph/path` | People graph (places listed separately) and shortest path |
| `GET /api/analytics`, `GET /api/benchmarks` | Corpus statistics and pipeline results |

Inputs are validated strictly (types, lengths, integer ranges) and errors are returned as JSON.

### Configuration

| Variable | Default | Purpose |
|---|---|---|
| `CHRONICLE_HOST` / `CHRONICLE_PORT` | `127.0.0.1` / `8000` | Bind address |
| `CHRONICLE_CORS_ORIGINS` | unset (CORS off) | Comma-separated allowed origins |
| `CHRONICLE_ENABLE_SBERT` | unset (off) | `1` also loads Sentence-BERT in the background (needs the `ml` extra); search then combines it with BM25. Off by default: the server starts instantly on BM25. |
| `CHRONICLE_ROOT` | source checkout | Folder containing `data/` and `frontend/dist` |
| `CHRONICLE_LOG_LEVEL` | `INFO` | Logging level |

---

## Deploy to Vercel

The repo includes `vercel.json`, `api/index.py`, `requirements.txt` and `.vercelignore`. Vercel builds the React frontend as static files and runs the Flask API as a serverless function under `/api/*`.

```bash
npm i -g vercel
vercel          # preview deployment (first run links the project)
vercel --prod   # production deployment
```

- Only the slim base dependencies are installed (Flask, NetworkX, Plotly, NumPy), because the full ML stack exceeds Vercel's ~250 MB function limit. Semantic search is off and the Oracle uses BM25.
- Chat memory lives in the function instance. Vercel may route requests to different instances, so a follow-up can occasionally lose context.
- The Vercel configuration has not been exercised on Vercel itself. If the API reports "Myth corpus not found", check the `includeFiles` pattern in `vercel.json`.
- For full semantic search in production use the Docker image on a container host.

---

## Evaluation

All numbers are produced by `scripts/run_pipeline.py` and `scripts/evaluate.py` (saved in `data/output/`). Gold sets are in `data/eval/` and were written by hand from the myths; **they should be reviewed by a person** before being treated as authoritative.

**Oracle** (28 questions). Intent 100%, answer content 100%. These questions were written alongside the features, so this is a regression check, not a blind test.

**Search** (25 plain-English descriptions of a myth; correct story first / in top 3):

| Method | Hit@1 | Hit@3 |
|---|---|---|
| First 3 myths in file order (baseline) | 4% | 16% |
| BM25 | 84% | 96% |
| Sentence-BERT + BM25 (what the full app uses) | 80% | 92% |
| Sentence-BERT alone | 68% | 84% |

Sentence-BERT alone probably scores lower because it truncates long myths (not verified). With 25 queries, one query is 4 points, so the BM25 and hybrid rows are not meaningfully different.

**Theme classification** (9 themes, 125 myths):

| Method | Held-out accuracy | 5-fold CV |
|---|---|---|
| Always predict the most common theme | 15% | n/a |
| SVM on TF-IDF | 20% | 18% ± 4% |
| Naive Bayes on TF-IDF | 24% | 17% ± 4% |
| Neural network on Sentence-BERT | 28% | n/a |
| Automatic lexicon labels vs. 52 hand-labelled myths | 79% (top theme), 92% (any of top 3) | n/a |
| Classifiers trained on 73 myths, tested on the hand labels | 21% (logistic regression), 31% (SVM) | n/a |

The supervised classifiers are barely above chance, so the application uses the lexicon scorer instead. An earlier version of the pipeline reported 100% accuracy because it scored models on their own training data; that was corrected.

**Other pipeline results:** 2,988 entity mentions, 169 extracted relations, 5 BERTopic topics (e.g. a love-and-metamorphosis cluster; an Aeneid/Odyssey cluster), Word2Vec 100-dim, SBERT 384-dim, TF-IDF 5,000 features. Tests: about 197 passing across preprocessing, representations, classifiers, entities, chatbot, knowledge layer and API.

---

## Known limitations

- Characters, places and themes of the 95 Bulfinch passages are automatic. Morals on them are a generic line per theme; the interface shows the story's opening sentences instead.
- Family data covers the major figures only. Many minor characters have no recorded relatives.
- Story-pattern matching is keyword-based; some matches are weak.
- The Oracle is rule-based and will not understand every phrasing; unmatched questions fall back to ranked search.
- Hand-labelled gold sets are small (52 myths, 25 search queries, 28 questions).
- On Windows, if Python processes hang while importing large libraries, stuck processes may be locking files in `site-packages`; restarting the PC clears this.

---

## Dataset sources

- **Bulfinch**, *The Age of Fable* (1855), via [Project Gutenberg #4928](https://www.gutenberg.org/ebooks/4928), public domain.
- **Hand-written retellings** (30), adapted from Ovid, Homer, Hesiod and Apollodorus.
- **Genealogy**: Hesiod's *Theogony*, Pseudo-Apollodorus' *Bibliotheca*, Homer; entered by hand.

## License

MIT License. Bulfinch's text is in the public domain.
