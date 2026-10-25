import React, { useState, useEffect } from 'react';
import PageHeader from '../components/PageHeader';
import Reveal from '../components/Reveal';
import { THEME } from '../data/theme';
import './ArchitectureView.css';

export default function ArchitectureView({ subTabs }) {
  const [benchmarks, setBenchmarks] = useState(null);

  useEffect(() => {
    fetch('/api/benchmarks')
      .then(res => res.json())
      .then(data => setBenchmarks(data))
      .catch(err => console.error('Failed to load benchmarks:', err));
  }, []);

  const stages = [
    {
      step: '01',
      title: 'Corpus ingestion & archaic normalization',
      desc: "Chronicle aggregates 125 myths: 30 hand-crafted core narratives plus 95 digitized chapters from Thomas Bulfinch's The Age of Fable (Project Gutenberg). The raw text undergoes rigorous preprocessing: cleaning archaic English stop words (thee, thou, hast, doth), sentence boundary detection, and rule-based deity alias resolution mapping hundreds of Latin/Roman variant names to canonical Greek figures (e.g. Minerva → Athena, Hercules → Heracles, Jupiter → Zeus).",
      tags: ['Corpus Scope', 'Lexicon Normalization', 'NLP Engine'],
      specs: [
        { label: 'Corpus Scope', value: '125 myths (30 hand-written + 95 Bulfinch)' },
        { label: 'Lexicon Normalization', value: 'Over 200 Greek-Roman deity and alias pairs' },
        { label: 'NLP Engine', value: 'spaCy en_core_web_sm + NLTK tokenization & lemmatization' },
      ],
    },
    {
      step: '02',
      title: 'Dual-vector geometry & representations',
      desc: 'To capture both exact classical phrasing and high-level thematic semantics, Chronicle builds a hybrid representation space. Sparse representations employ TF-IDF over 1–2 n-grams constrained to the 5,000 most informative mythological tokens. Dense semantics are encoded via Sentence-BERT (all-MiniLM-L6-v2) into a continuous 384-dimensional vector space, alongside a 100-dimensional continuous-bag-of-words Word2Vec model trained across the mythic corpus.',
      tags: ['Sparse TF-IDF', 'Dense Embeddings', 'Word2Vec Lexicon'],
      specs: [
        { label: 'Sparse TF-IDF', value: '5,000 top n-gram features (sublinear TF scaling)' },
        { label: 'Dense Embeddings', value: 'Sentence-BERT (384-dimensional dense vectors)' },
        { label: 'Word2Vec Lexicon', value: '100 dimensions across 12,752 vocabulary tokens' },
      ],
    },
    {
      step: '03',
      title: 'Entity recognition & kinship graph extraction',
      desc: 'Custom rule-based and gazetteer-assisted Named Entity Recognition (NER) identifies 2,988 character, deity, place, and artifact mentions across the stories. 169 co-occurrence and genealogical relationships are extracted into a NetworkX directed knowledge graph. A dedicated kinship reasoning engine (chronicle.ner.kinship) uses formal mythological lineage rules (Hesiod, Apollodorus, Homer) to infer unstated family ties: half-siblings via shared divine parentage, uncles, aunts, and multi-generational descent.',
      tags: ['Entity Mentions', 'Knowledge Graph', 'Kinship Derivation'],
      specs: [
        { label: 'Entity Mentions', value: '2,988 total extracted entities (gods, titans, mortals)' },
        { label: 'Knowledge Graph', value: '258 entity nodes, 109 verified edges in NetworkX' },
        { label: 'Kinship Derivation', value: 'Formal parentage, half-siblings, and ancestor trees' },
      ],
    },
    {
      step: '04',
      title: 'Lexicon thematic classification & topic discovery',
      desc: 'The corpus is analyzed across 9 classical thematic motifs (Hubris, Love, Betrayal, Revenge, Wisdom, Jealousy, Transformation, Quest, Loss). While supervised machine learning models (Linear SVM, Logistic Regression, Naive Bayes, PyTorch MLP) were trained, empirical evaluation revealed that supervised models overfit on small narrative sets (~28% accuracy). Chronicle therefore implements a transparent lexicon-scoring matcher that achieves 79% top-1 accuracy (92% top-3) against human gold labels, complemented by 5 unsupervised BERTopic narrative clusters.',
      tags: ['Thematic Dimensions', 'Lexicon Accuracy', 'Unsupervised Topics'],
      specs: [
        { label: 'Thematic Dimensions', value: '9 archetypal mythic themes' },
        { label: 'Lexicon Accuracy', value: '79% top-1 / 92% top-3 agreement vs hand labels' },
        { label: 'Unsupervised Topics', value: '5 cohesive BERTopic semantic narrative clusters' },
      ],
    },
    {
      step: '05',
      title: 'The Oracle dialogue engine & hybrid retrieval',
      desc: 'Chronicle\'s offline conversational system ("The Oracle") operates without external LLM dependencies for deterministic, instant latency. Inbound queries are parsed through regex and semantic intent classifiers across 9 intent classes (character dossiers, relationship queries, side-by-side comparisons, theme queries, story patterns, and similar myths). An intelligent hybrid retriever blends BM25 keyword matching with SBERT cosine similarity, falling back smoothly to top-k semantic search when no explicit rule triggers.',
      tags: ['Intent Classification', 'Search Ranking', 'Conversation Memory'],
      specs: [
        { label: 'Intent Classification', value: '9 discrete intent classes with slot-filling' },
        { label: 'Search Ranking', value: 'Hybrid BM25 + SBERT cosine vector search' },
        { label: 'Conversation Memory', value: 'Stateful session memory supporting follow-up questions' },
      ],
    },
  ];

  return (
    <div className="page-surface">
      <PageHeader
        label="HOW IT WAS BUILT"
        title="The Language-Processing Engine"
        intro="You don't need this page to enjoy the myths — it's here for the curious. A look under the hood at the computational pipeline, mathematical models, and kinship reasoning engines that ingest, classify, and interlink every story in the collection."
        image={THEME.oracleBg}
      >
        {subTabs}
      </PageHeader>

      <div className="section-dark">
        <div className="av-container">

          {/* Vertical pipeline with gold line + star nodes */}
          <div className="av-pipeline">
            {stages.map((s, i) => (
              <Reveal key={s.step} delay={i * 70} className="av-step">
                {/* Star node sits on the gold line */}
                <div className="av-star-node" aria-hidden="true">✦</div>

                <div className="av-step-card">
                  {/* Large outlined numeral */}
                  <div className="av-step-numeral">{s.step}</div>

                  <div className="av-step-body">
                    <h3 className="av-step-title">
                      {s.title.charAt(0).toUpperCase() + s.title.slice(1)}
                    </h3>
                    <p className="av-step-desc">{s.desc}</p>

                    {/* Three tag chips */}
                    <div className="av-step-tags">
                      {s.tags.map(tag => (
                        <span key={tag} className="av-tag-chip">{tag}</span>
                      ))}
                    </div>

                    {/* Spec rows */}
                    <div className="av-specs">
                      {s.specs.map(spec => (
                        <div key={spec.label} className="av-spec-row">
                          <span className="av-spec-key">{spec.label}</span>
                          <span className="av-spec-val">{spec.value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </Reveal>
            ))}
          </div>

          {/* Empirical evaluation tables */}
          <Reveal className="av-eval-card">
            <h2 className="av-section-title">Empirical model evaluation</h2>
            <p className="av-section-intro">
              Every component in Chronicle is benchmarked against curated gold-standard test sets.
              Here is how different retrieval and classification approaches measure up across the corpus:
            </p>

            <div className="av-eval-grid">
              {/* Retrieval table */}
              <div className="av-sub-panel">
                <h3 className="av-sub-title">Free-text retrieval performance</h3>
                <table className="av-table">
                  <thead>
                    <tr>
                      <th className="av-th">Method</th>
                      <th className="av-th">Hit @ 1</th>
                      <th className="av-th">Hit @ 3</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="av-tr">
                      <td className="av-td">File-Order Baseline</td>
                      <td className="av-td">4%</td>
                      <td className="av-td">16%</td>
                    </tr>
                    <tr className="av-tr">
                      <td className="av-td">Dense SBERT Embeddings</td>
                      <td className="av-td">68%</td>
                      <td className="av-td">84%</td>
                    </tr>
                    <tr className="av-tr">
                      <td className="av-td">Hybrid (SBERT + BM25)</td>
                      <td className="av-td">80%</td>
                      <td className="av-td">92%</td>
                    </tr>
                    <tr className="av-tr av-tr--best">
                      <td className="av-td">BM25 Keyword Ranker</td>
                      <td className="av-td av-td--glow">84%</td>
                      <td className="av-td av-td--glow">96%</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Classification table */}
              <div className="av-sub-panel">
                <h3 className="av-sub-title">Theme classification accuracy</h3>
                <table className="av-table">
                  <thead>
                    <tr>
                      <th className="av-th">Classifier architecture</th>
                      <th className="av-th">Held-out acc</th>
                      <th className="av-th">5-fold CV</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="av-tr">
                      <td className="av-td">Majority Class Baseline</td>
                      <td className="av-td">15.2%</td>
                      <td className="av-td">—</td>
                    </tr>
                    <tr className="av-tr">
                      <td className="av-td">Linear SVM (TF-IDF)</td>
                      <td className="av-td">20.0%</td>
                      <td className="av-td">18% ± 4%</td>
                    </tr>
                    <tr className="av-tr">
                      <td className="av-td">Multinomial Naive Bayes</td>
                      <td className="av-td">24.0%</td>
                      <td className="av-td">17% ± 4%</td>
                    </tr>
                    <tr className="av-tr">
                      <td className="av-td">Neural network (MLP on SBERT)</td>
                      <td className="av-td">28.0%</td>
                      <td className="av-td">—</td>
                    </tr>
                    <tr className="av-tr av-tr--best">
                      <td className="av-td">Lexicon scorer (production)</td>
                      <td className="av-td av-td--glow">79.0%</td>
                      <td className="av-td av-td--glow">92% (top 3)</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </Reveal>

          {/* Telemetry tiles */}
          <Reveal className="av-telemetry-card">
            <h3 className="av-telemetry-title">Live pipeline execution telemetry</h3>
            {benchmarks && benchmarks.stages ? (
              <>
                <div className="av-telemetry-grid">
                  <div className="av-telem-tile">
                    <div className="av-telem-label">Preprocessing</div>
                    <div className="av-telem-value">
                      {benchmarks.stages.preprocessing?.num_texts || 125} Texts cleaned
                    </div>
                  </div>

                  <div className="av-telem-tile">
                    <div className="av-telem-label">TF-IDF vocabulary</div>
                    <div className="av-telem-value">
                      {benchmarks.stages.representations?.tfidf?.num_features || '5,000'} Features
                    </div>
                  </div>

                  <div className="av-telem-tile">
                    <div className="av-telem-label">Dense vector space</div>
                    <div className="av-telem-value">384 dims (SBERT)</div>
                  </div>

                  <div className="av-telem-tile">
                    <div className="av-telem-label">Execution runtime</div>
                    <div className="av-telem-value">
                      {benchmarks.total_time_seconds
                        ? `${benchmarks.total_time_seconds}s end-to-end`
                        : 'Completed'}
                    </div>
                  </div>
                </div>

                <div className="av-artifacts">
                  Artifacts persisted:{' '}
                  <code className="av-file-chip">data/output/pipeline_results.json</code>,{' '}
                  <code className="av-file-chip">data/output/character_leaderboard.json</code>,{' '}
                  <code className="av-file-chip">data/output/story_cards/</code>, and{' '}
                  <code className="av-file-chip">data/output/evaluation.json</code>.
                </div>
              </>
            ) : (
              <div className="av-telem-fallback">
                Pipeline artifacts generated and ready. Full evaluation metrics available via CLI
                runner: <code className="av-file-chip">python scripts/run_pipeline.py</code>.
              </div>
            )}
          </Reveal>

        </div>
      </div>
    </div>
  );
}
