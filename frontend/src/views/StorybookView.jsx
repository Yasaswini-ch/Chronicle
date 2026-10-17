import React, { useState, useEffect } from 'react';
import Term from '../components/Term';
import Reveal from '../components/Reveal';
import SectionIcon from '../components/SectionIcon';
import { typeColor, themeColor } from '../utils/colors';
import { mythImageFor } from '../data/mythImages';

export default function StorybookView({ myths, onSelectMyth, selectedMythId }) {
  const [selectedTheme, setSelectedTheme] = useState('all');
  const [selectedSource, setSelectedSource] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeMyth, setActiveMyth] = useState(null);
  const [similarMyths, setSimilarMyths] = useState([]);

  const themes = Array.from(new Set(myths.flatMap(m => m.themes && m.themes.length ? m.themes : [m.theme]).filter(Boolean))).sort();

  const filteredMyths = myths.filter(m => {
    const matchesTheme = selectedTheme === 'all' || m.theme?.toLowerCase() === selectedTheme.toLowerCase() ||
      (m.themes || []).some(t => t.toLowerCase() === selectedTheme.toLowerCase());
    const matchesSource = selectedSource === 'all' || (m.corpus || 'curated') === selectedSource;
    const q = searchQuery.toLowerCase().trim();
    const matchesQuery = !q ||
      m.title?.toLowerCase().includes(q) ||
      m.text?.toLowerCase().includes(q) ||
      (m.characters || []).some(c => (typeof c === 'string' ? c : c.name || '').toLowerCase().includes(q));
    return matchesTheme && matchesSource && matchesQuery;
  });

  useEffect(() => {
    if (selectedMythId) {
      const match = myths.find(m => m.id === selectedMythId || m.title === selectedMythId);
      if (match) setActiveMyth(match);
    } else if (filteredMyths.length > 0 && !activeMyth) {
      setActiveMyth(filteredMyths[0]);
    }
  }, [selectedMythId, myths]);

  // Keep the open story consistent with the active filter.
  useEffect(() => {
    if (!activeMyth || filteredMyths.some(m => m.id === activeMyth.id)) return;
    if (filteredMyths.length > 0) setActiveMyth(filteredMyths[0]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedTheme, selectedSource, searchQuery]);

  useEffect(() => {
    if (!activeMyth) return undefined;
    const ctrl = new AbortController();
    setSimilarMyths([]);
    fetch(`/api/similar/${encodeURIComponent(activeMyth.title)}`, { signal: ctrl.signal })
      .then(res => (res.ok ? res.json() : []))
      .then(data => setSimilarMyths(Array.isArray(data) ? data : []))
      .catch(() => {});
    return () => ctrl.abort();
  }, [activeMyth]);

  const saveBlob = (blob, filename) => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  const downloadJson = () => {
    if (!activeMyth) return;
    saveBlob(
      new Blob([JSON.stringify(activeMyth, null, 2)], { type: 'application/json' }),
      `${activeMyth.id || 'myth'}_dossier.json`,
    );
  };

  const downloadMarkdown = () => {
    if (!activeMyth) return;
    const chars = (activeMyth.characters || []).map(c => typeof c === 'string' ? c : c.name).join(', ');
    const md = `# ${activeMyth.title}\nTheme: ${activeMyth.theme}\nCharacters: ${chars}\nMoral: ${activeMyth.moral || 'N/A'}\n\n## Narrative\n${activeMyth.text}`;
    saveBlob(new Blob([md], { type: 'text/markdown' }), `${activeMyth.id || 'myth'}_story.md`);
  };

  return (
    <div className="storybook-clouds-bg">
      <Reveal style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px' }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '4px' }}>
            <SectionIcon name="scroll" />
            <h2 style={{ fontSize: '1.6rem', margin: 0 }}>The Reading Room</h2>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          {myths.length || 'Every'} complete myths, told in full — not summarized. Every character is labeled by kind
          (<Term word="god">god</Term>, <Term word="titan">titan</Term>, <Term word="mortal">mortal</Term>,
          or <Term word="creature">creature</Term>) so you&apos;re never lost, and each story links to the
          others that share its themes.
          </p>
        </div>
      </Reveal>

      <div className="split-340">
        {/* Navigation Column */}
        <Reveal className="panel" style={{ padding: '16px' }}>
          <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1.5px', color: 'var(--accent-gold)', marginBottom: '12px' }}>
            Find A Story
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '16px' }}>
            <select
              value={selectedTheme}
              onChange={e => setSelectedTheme(e.target.value)}
              style={{ width: '100%' }}
            >
              <option value="all">Every Theme</option>
              {themes.map(t => (
                <option key={t} value={t}>{t.toUpperCase()}</option>
              ))}
            </select>

            <select
              aria-label="Source"
              value={selectedSource}
              onChange={e => setSelectedSource(e.target.value)}
              style={{ width: '100%' }}
            >
              <option value="all">Every Source</option>
              <option value="curated">Hand-written retellings</option>
              <option value="bulfinch">Bulfinch, The Age of Fable</option>
            </select>

            <input
              type="text"
              placeholder="Search title or character..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              style={{ width: '100%' }}
            />
          </div>

          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
            Showing {filteredMyths.length} of {myths.length} narratives
          </div>

          <div className="story-index-list">
            {filteredMyths.map(myth => {
              const isSelected = activeMyth && (activeMyth.id === myth.id || activeMyth.title === myth.title);
              return (
                <button
                  type="button"
                  key={myth.id || myth.title}
                  className="myth-row"
                  aria-current={isSelected ? 'true' : undefined}
                  onClick={() => {
                    if (window.innerWidth < 900) window.scrollTo({ top: 0, behavior: 'smooth' });
                    setActiveMyth(myth);
                    if (onSelectMyth) onSelectMyth(myth.id);
                  }}
                  style={{
                    padding: '10px 12px',
                    cursor: 'pointer',
                    background: isSelected ? 'var(--bg-surface-elevated)' : 'transparent',
                    borderLeft: isSelected ? '3px solid var(--accent-gold)' : '3px solid transparent',
                    borderBottom: '1px solid var(--border-subtle)',
                  }}
                >
                  <div style={{ color: isSelected ? 'var(--text-primary)' : 'var(--text-secondary)', fontWeight: isSelected ? 600 : 400, fontSize: '0.95rem' }}>
                    {myth.title}
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px' }}>
                    <span className="badge-theme" style={{ borderColor: themeColor(myth.theme), color: themeColor(myth.theme) }}>
                      <Term word={myth.theme}>{myth.theme || 'myth'}</Term>
                    </span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {(myth.text || '').split(/\s+/).length} words
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </Reveal>

        {/* Story Reading Room */}
        {activeMyth ? (
          <div
            key={activeMyth.id || activeMyth.title}
            className="story-panel panel"
            style={{ padding: '32px' }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '16px', marginBottom: '20px' }}>
              <div>
                <h1 style={{ fontSize: '1.9rem', marginBottom: '6px' }}>{activeMyth.title}</h1>
                <span className="badge-theme" style={{ borderColor: themeColor(activeMyth.theme), color: themeColor(activeMyth.theme) }}>
                  {activeMyth.theme}
                </span>
                {activeMyth.source && (
                  <span style={{ marginLeft: '12px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    Source: {activeMyth.source}
                  </span>
                )}
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button onClick={downloadJson} className="btn-secondary" style={{ fontSize: '0.75rem' }}>
                  Export JSON
                </button>
                <button onClick={downloadMarkdown} className="btn-secondary" style={{ fontSize: '0.75rem' }}>
                  Export Markdown
                </button>
              </div>
            </div>

            {/* A bespoke illustration for the one myth it's an exact match for */}
            {activeMyth.id === 'myth_icarus' && (
              <div className="icarus-illustration-wrap">
                <img src="/images/decor/icarus-falling.png" alt="Icarus falling from the sky between two columns" />
              </div>
            )}

            {/* Real classical artwork for every other myth with a genuine match */}
            {activeMyth.id !== 'myth_icarus' && mythImageFor(activeMyth.id) && (
              <div className="myth-artwork-wrap">
                <img
                  src={mythImageFor(activeMyth.id).file}
                  alt={`Classical depiction related to ${activeMyth.title}`}
                />
                <div className="myth-artwork-credit">{mythImageFor(activeMyth.id).credit}</div>
              </div>
            )}

            {/* Characters */}
            {activeMyth.characters && activeMyth.characters.length > 0 && (
              <div style={{ marginBottom: '20px' }}>
                <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Who&apos;s In This Story
                </div>
                <div>
                  {activeMyth.characters.map((c, i) => {
                    const name = typeof c === 'string' ? c : c.name || '?';
                    const rawType = typeof c === 'object' && c.type ? c.type : 'figure';
                    return (
                      <span key={i} className="badge-character" style={{ borderLeft: `3px solid ${typeColor(rawType)}` }}>
                        {name}{' '}
                        <Term word={rawType}>
                          <small style={{ color: typeColor(rawType) }}>[{rawType.toUpperCase()}]</small>
                        </Term>
                      </span>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Moral / Core Insight */}
            {activeMyth.moral && (
              <div
                style={{
                  position: 'relative',
                  borderLeft: '3px solid var(--accent-garnet)',
                  background: 'var(--bg-surface-elevated)',
                  padding: '14px 24px 14px 48px',
                  marginBottom: '24px',
                  fontStyle: 'italic',
                  fontSize: '1.08rem',
                  color: 'var(--text-primary)',
                }}
              >
                <span
                  style={{
                    position: 'absolute',
                    left: '10px',
                    top: '0px',
                    fontFamily: 'var(--font-heading)',
                    fontSize: '2.4rem',
                    fontStyle: 'normal',
                    color: 'var(--accent-garnet)',
                    opacity: 0.5,
                    lineHeight: 1,
                  }}
                  aria-hidden="true"
                >
                  &ldquo;
                </span>
                {activeMyth.moral}
              </div>
            )}

            {/* Unabridged Prose Narrative */}
            <div
              className="story-text"
              style={{ fontSize: '1.12rem', lineHeight: '1.8', color: 'var(--text-primary)', marginBottom: '32px', whiteSpace: 'pre-line' }}
            >
              <span className="drop-cap">{(activeMyth.text || '').charAt(0)}</span>
              {(activeMyth.text || '').slice(1)}
            </div>

            {/* Tracked Relationships */}
            {activeMyth.relationships && activeMyth.relationships.length > 0 && (
              <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '20px', marginBottom: '24px' }}>
                <div style={{ fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '1.5px', color: 'var(--accent-gold)', marginBottom: '10px' }}>
                  How These Characters Are Connected
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '8px' }}>
                  {activeMyth.relationships.map((rel, idx) => (
                    <div key={idx} style={{ background: 'var(--bg-surface-elevated)', padding: '8px 12px', border: '1px solid var(--border-subtle)', fontSize: '0.85rem' }}>
                      <strong>{rel.source}</strong> &rarr; <em>{rel.relation?.replace(/_/g, ' ')}</em> &rarr; <strong>{rel.target}</strong>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Semantically Related Narratives */}
            {similarMyths.length > 0 && (
              <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '20px' }}>
                <div style={{ fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '1.5px', color: 'var(--accent-gold)', marginBottom: '12px' }}>
                  If You Liked This, Try These
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '12px' }}>
                  {similarMyths.map((sim, i) => (
                    <div
                      key={i}
                      className="card"
                      role="button"
                      tabIndex={0}
                      onClick={() => setActiveMyth(sim)}
                      onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setActiveMyth(sim); } }}
                      style={{
                        background: 'var(--bg-surface-elevated)',
                        padding: '12px 14px',
                        cursor: 'pointer',
                      }}
                    >
                      <div style={{ color: 'var(--text-primary)', fontWeight: 600, fontSize: '0.95rem' }}>{sim.title}</div>
                      <span className="badge-theme" style={{ marginTop: '4px', borderColor: themeColor(sim.theme), color: themeColor(sim.theme) }}>{sim.theme}</span>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '6px' }}>
                        {sim.moral || (sim.text ? sim.text.substring(0, 90) + '...' : '')}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
            Select a myth from the index to begin reading.
          </div>
        )}
      </div>
    </div>
  );
}
