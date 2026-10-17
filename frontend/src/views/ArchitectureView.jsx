import React, { useState, useEffect } from 'react';
import Reveal from '../components/Reveal';
import SectionIcon from '../components/SectionIcon';

export default function ArchitectureView() {
  const [benchmarks, setBenchmarks] = useState(null);

  useEffect(() => {
    fetch('/api/benchmarks')
      .then(res => res.json())
      .then(data => setBenchmarks(data))
      .catch(err => console.error('Failed to load benchmarks:', err));
  }, []);

  const stages = [
    {
      title: 'Stage 1: Ingestion & Archaic Normalization',
      desc: 'Cleans archaic English stop words, unifies bidirectional Greek-Roman deity aliases (Heracles - Hercules, Zeus - Jupiter), and performs linguistic tokenization & lemmatization via spaCy.',
    },
    {
      title: 'Stage 2: Dual Vector Geometry',
      desc: 'Constructs sparse n-gram feature matrices using TF-IDF (1-2 grams, max 5,000 features) alongside dense 384-dimensional Sentence-BERT embeddings (all-MiniLM-L6-v2) for deep contextual semantics.',
    },
    {
      title: 'Stage 3: Supervised Classification & Graph Extraction',
      desc: 'Trains multi-class theme classifiers (Linear SVM, Logistic Regression, Multinomial Naive Bayes, and PyTorch Neural MLP). Extracts entities and genealogical relations into a NetworkX directed knowledge graph.',
    },
    {
      title: 'Stage 4: Conversational Dialogue & Storytelling',
      desc: 'Processes natural language queries through regex/semantic intent detection, entity slot filling, cosine similarity vector search, and structured lore dossier synthesis.',
    },
  ];

  return (
    <div className="architecture-ruins-bg">
      <Reveal style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '4px' }}>
          <SectionIcon name="column" />
          <h2 style={{ fontSize: '1.6rem', margin: 0 }}>How Chronicle Was Built</h2>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          You don&apos;t need this page to enjoy the myths — it&apos;s here for the curious. A look under the
          hood at the language-processing pipeline that reads, classifies, and connects every story in the collection.
        </p>
      </Reveal>

      {/* 4 Pipeline Stages (2x2 layout, no three in a row) */}
      <div className="grid-2" style={{ marginBottom: '32px' }}>
        {stages.map((s, i) => (
          <Reveal key={i} delay={i * 80} className="card" style={{ borderLeft: '3px solid var(--accent-gold)' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--accent-gold)', fontWeight: 600, marginBottom: '6px' }}>
              {s.title}
            </div>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
              {s.desc}
            </p>
          </Reveal>
        ))}
      </div>

      {/* Benchmark Results */}
      <Reveal className="card" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '1.2rem', marginBottom: '12px' }}>Pipeline Execution Telemetry</h3>
        {benchmarks && benchmarks.stages ? (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px', marginBottom: '20px' }}>
              <div style={{ background: 'var(--bg-surface-elevated)', padding: '12px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Preprocessing</div>
                <div style={{ fontSize: '1.1rem', color: 'var(--text-primary)', marginTop: '4px' }}>
                  {benchmarks.stages.preprocessing?.num_texts || 30} Texts Cleaned
                </div>
              </div>

              <div style={{ background: 'var(--bg-surface-elevated)', padding: '12px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>TF-IDF Vocabulary</div>
                <div style={{ fontSize: '1.1rem', color: 'var(--text-primary)', marginTop: '4px' }}>
                  {benchmarks.stages.representations?.tfidf?.num_features || '5,000'} Features
                </div>
              </div>

              <div style={{ background: 'var(--bg-surface-elevated)', padding: '12px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Dense Vector Space</div>
                <div style={{ fontSize: '1.1rem', color: 'var(--text-primary)', marginTop: '4px' }}>
                  384 Dimensions (SBERT)
                </div>
              </div>

              <div style={{ background: 'var(--bg-surface-elevated)', padding: '12px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Execution Runtime</div>
                <div style={{ fontSize: '1.1rem', color: 'var(--text-primary)', marginTop: '4px' }}>
                  {benchmarks.total_time_seconds ? `${benchmarks.total_time_seconds}s End-to-End` : 'Completed'}
                </div>
              </div>
            </div>

            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Artifacts persisted: <code>data/output/pipeline_results.json</code>, <code>data/output/character_leaderboard.json</code>, and <code>data/output/story_cards/</code>.
            </div>
          </div>
        ) : (
          <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Pipeline artifacts generated and ready. Full evaluation metrics available via CLI runner: <code>python scripts/run_pipeline.py</code>.
          </div>
        )}
      </Reveal>
    </div>
  );
}
