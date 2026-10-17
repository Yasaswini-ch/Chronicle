import React, { useState, useEffect } from 'react';
import Reveal from '../components/Reveal';
import SectionIcon from '../components/SectionIcon';
import { themeColor } from '../utils/colors';

export default function MotifsView({ onSelectMyth }) {
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

  return (
    <div>
      <Reveal style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '4px' }}>
          <SectionIcon name="scroll" />
          <h2 style={{ fontSize: '1.6rem', margin: 0 }}>Story Patterns</h2>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Greek myths reuse the same few plots: someone is turned into a tree, a mortal defies a god, a hero
          goes down to the underworld. Pick a pattern to see every story that uses it, with the passage that shows it.
        </p>
      </Reveal>

      {error && <p role="alert" style={{ color: 'var(--accent-garnet)' }}>The pattern index could not be loaded.</p>}

      <div className="motif-grid" role="tablist" aria-label="Story patterns">
        {motifs.map(m => (
          <button key={m.id} type="button" role="tab" aria-selected={m.id === active}
            className={`motif-card ${m.id === active ? 'active' : ''}`} onClick={() => setActive(m.id)}>
            <span className="motif-label">{m.label}</span>
            <span className="motif-count">{m.count} {m.count === 1 ? 'story' : 'stories'}</span>
          </button>
        ))}
      </div>

      {current && (
        <div className="panel" style={{ padding: '22px 26px', marginTop: '20px' }} aria-live="polite">
          <h3 style={{ margin: '0 0 4px', fontSize: '1.4rem' }}>{current.label}</h3>
          <p style={{ color: 'var(--text-secondary)', marginTop: 0 }}>{current.description}</p>
          {loadingRows && <p style={{ color: 'var(--text-muted)' }}>Loading…</p>}
          <ol className="motif-list">
            {rows.slice(0, 12).map(r => (
              <li key={r.id}>
                <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '10px' }}>
                  <button type="button" className="fig-link" style={{ fontSize: '1.05rem' }} onClick={() => onSelectMyth && onSelectMyth(r.id)}>
                    {r.title}
                  </button>
                  <span className="badge-theme" style={{ borderColor: themeColor(r.theme), color: themeColor(r.theme) }}>{r.theme}</span>
                </div>
                {r.snippet && <blockquote className="motif-quote">{r.snippet}</blockquote>}
              </li>
            ))}
          </ol>
          {rows.length > 12 && <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Showing the 12 strongest of {rows.length} stories.</p>}
        </div>
      )}
    </div>
  );
}
