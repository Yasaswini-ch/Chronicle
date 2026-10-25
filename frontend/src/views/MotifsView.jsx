import React, { useState, useEffect } from 'react';
import PageHeader from '../components/PageHeader';
import Reveal from '../components/Reveal';
import { themeColor } from '../utils/colors';
import { THEME } from '../data/theme';
import './MotifsView.css';

function toSentenceCase(str) {
  if (!str) return '';
  const trimmed = str.trim();
  return trimmed.charAt(0).toUpperCase() + trimmed.slice(1);
}

export default function MotifsView({ onSelectMyth, subTabs }) {
  const [motifs, setMotifs] = useState([]);
  const [error, setError] = useState(false);
  const [active, setActive] = useState(null);
  const [rows, setRows] = useState([]);
  const [loadingRows, setLoadingRows] = useState(false);

  useEffect(() => {
    fetch('/api/motifs')
      .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(data => { setMotifs(data); if (data.length) setActive(data[0].id); })
      .catch(() => setError(true));
  }, []);

  useEffect(() => {
    if (!active) return undefined;
    const ctrl = new AbortController();
    setLoadingRows(true);
    fetch(`/api/motifs/${encodeURIComponent(active)}`, { signal: ctrl.signal })
      .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(data => { setRows(data); setLoadingRows(false); })
      .catch(err => { if (err.name !== 'AbortError') { setRows([]); setLoadingRows(false); } });
    return () => ctrl.abort();
  }, [active]);

  const current = motifs.find(m => m.id === active);
  const totalCount = current ? (current.count || rows.length) : rows.length;

  return (
    <div className="page-surface">
      <PageHeader
        label="STORY PATTERNS"
        title="Story Patterns"
        intro="Greek myths reuse the same few plots: someone is turned into a tree, a mortal defies a god, a hero goes down to the underworld. Pick a pattern to see every story that uses it, with the passage that shows it."
        image={THEME.placesIsland}
      >
        {subTabs}
      </PageHeader>

      <div className="section-parchment">
        <div className="motifs-container">
          {error && (
            <p role="alert" className="motifs-alert">
              The pattern index could not be loaded.
            </p>
          )}

          {/* Horizontally scrollable row of pills with story count, active pill filled dark */}
          <div className="motifs-pills-row" role="tablist" aria-label="Story patterns">
            {motifs.map(m => {
              const isActive = m.id === active;
              return (
                <button
                  key={m.id}
                  type="button"
                  role="tab"
                  aria-selected={isActive}
                  className={`motif-pill ${isActive ? 'active' : ''}`}
                  onClick={() => setActive(m.id)}
                >
                  <span className="motif-pill-name">{m.label}</span>
                  <span className="motif-pill-count">{m.count}</span>
                </button>
              );
            })}
          </div>

          {current && (
            <div className="motif-detail-section" aria-live="polite">
              {/* Pattern description in large Cormorant */}
              <p className="motif-large-desc">
                {current.description}
              </p>

              {loadingRows && <p className="motif-loading">Loading stories…</p>}

              {/* Two-column grid of cards */}
              <div className="motifs-cards-grid">
                {rows.slice(0, 12).map((r, i) => {
                  const color = themeColor(r.theme);
                  return (
                    <Reveal key={r.id} delay={(i % 2) * 60} className="card motif-story-card">
                      <div className="motif-card-header">
                        <button
                          type="button"
                          className="motif-card-title-btn"
                          onClick={() => onSelectMyth && onSelectMyth(r.id)}
                        >
                          {r.title}
                        </button>
                        <span
                          className="motif-theme-chip"
                          style={{ borderColor: color, color: color }}
                        >
                          {r.theme}
                        </span>
                      </div>
                      {r.snippet && (
                        <blockquote className="motif-passage-quote">
                          “{toSentenceCase(r.snippet)}”
                        </blockquote>
                      )}
                    </Reveal>
                  );
                })}
              </div>

              {/* Showing the 12 strongest of N stories */}
              {(totalCount > 12 || rows.length > 12) && (
                <p className="motifs-footnote">
                  Showing the 12 strongest of {totalCount} stories.
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
