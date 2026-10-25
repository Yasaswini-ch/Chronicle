import React, { useState, useEffect } from 'react';
import PageHeader from '../components/PageHeader';
import Term from '../components/Term';
import { typeColor, themeColor } from '../utils/colors';
import { mythImageFor, MYTH_IMAGES } from '../data/mythImages';
import { portraitFor, PORTRAITS } from '../data/portraits';
import { THEME } from '../data/theme';
import ThreadDivider from '../components/ThreadDivider';
import './StorybookView.css';

const getThemeClass = (theme) => {
  const t = String(theme || '').trim().toLowerCase();
  const valid = [
    'hubris', 'love', 'betrayal', 'revenge',
    'wisdom', 'jealousy', 'transformation', 'quest', 'loss',
  ];
  return valid.includes(t) ? `theme-${t}` : 'theme-default';
};

const getTypeClass = (type) => {
  const k = String(type || '').trim().toLowerCase();
  const valid = ['god', 'titan', 'mortal', 'creature', 'location', 'artifact'];
  return valid.includes(k) ? `type-${k}` : 'type-figure';
};

export default function StorybookView({ myths, onSelectMyth, selectedMythId }) {
  const [selectedTheme, setSelectedTheme] = useState('all');
  const [selectedSource, setSelectedSource] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeMyth, setActiveMyth] = useState(null);
  const [similarMyths, setSimilarMyths] = useState([]);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const themes = Array.from(
    new Set(myths.flatMap(m => (m.themes && m.themes.length ? m.themes : [m.theme])).filter(Boolean))
  ).sort();

  const filteredMyths = myths.filter(m => {
    const matchesTheme =
      selectedTheme === 'all' ||
      m.theme?.toLowerCase() === selectedTheme.toLowerCase() ||
      (m.themes || []).some(t => t.toLowerCase() === selectedTheme.toLowerCase());
    const matchesSource = selectedSource === 'all' || (m.corpus || 'curated') === selectedSource;
    const q = searchQuery.toLowerCase().trim();
    const matchesQuery =
      !q ||
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

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') setDrawerOpen(false);
    };
    if (drawerOpen) {
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
    }
  }, [drawerOpen]);

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
      `${activeMyth.id || 'myth'}_dossier.json`
    );
  };

  const downloadMarkdown = () => {
    if (!activeMyth) return;
    const chars = (activeMyth.characters || []).map(c => (typeof c === 'string' ? c : c.name)).join(', ');
    const md = `# ${activeMyth.title}\nTheme: ${activeMyth.theme}\nCharacters: ${chars}\nMoral: ${
      activeMyth.moral || 'N/A'
    }\n\n## Narrative\n${activeMyth.text}`;
    saveBlob(new Blob([md], { type: 'text/markdown' }), `${activeMyth.id || 'myth'}_story.md`);
  };

  const getMythArtwork = (myth) => {
    if (!myth) return null;
    if (myth.id === 'myth_icarus') {
      return {
        file: '/images/decor/icarus-falling.png',
        credit: 'Classical depiction of Icarus falling',
      };
    }
    return mythImageFor(myth.id) || null;
  };

  const activeArtwork = getMythArtwork(activeMyth);

  const introText = (
    <>
      {myths.length || 'Every'} complete myths, told in full — not summarized. Every character is labeled by kind
      (<Term word="god">god</Term>, <Term word="titan">titan</Term>, <Term word="mortal">mortal</Term>,
      or <Term word="creature">creature</Term>) so you&apos;re never lost, and each story links to the
      others that share its themes.
    </>
  );

  const renderStoryList = (isMobile = false) => (
    <div className="storybook-sidebar-inner">
      <div className="storybook-list-header">
        <div className="storybook-list-title">All stories</div>
        <div className="storybook-filters">
          <select
            value={selectedTheme}
            onChange={e => setSelectedTheme(e.target.value)}
            className="storybook-select"
            aria-label="Filter by theme"
          >
            <option value="all">Every theme</option>
            {themes.map(t => (
              <option key={t} value={t}>
                {t.charAt(0).toUpperCase() + t.slice(1)}
              </option>
            ))}
          </select>

          <select
            aria-label="Filter by source"
            value={selectedSource}
            onChange={e => setSelectedSource(e.target.value)}
            className="storybook-select"
          >
            <option value="all">Every source</option>
            <option value="curated">Hand-written retellings</option>
            <option value="bulfinch">Bulfinch, The Age of Fable</option>
          </select>

          <input
            type="text"
            placeholder="Search title or character..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="storybook-search"
            aria-label="Search title or character"
          />
        </div>

        <div className="storybook-count">
          Showing {filteredMyths.length} of {myths.length} narratives
        </div>
      </div>

      <div className="storybook-list" role="list">
        {filteredMyths.map(myth => {
          const isSelected = activeMyth && (activeMyth.id === myth.id || activeMyth.title === myth.title);
          const themeCls = getThemeClass(myth.theme);
          const wordCount = (myth.text || '').split(/\s+/).filter(Boolean).length;
          return (
            <button
              type="button"
              key={myth.id || myth.title}
              className={`storybook-row ${isSelected ? 'active' : ''}`}
              aria-current={isSelected ? 'true' : undefined}
              onClick={() => {
                setActiveMyth(myth);
                if (onSelectMyth) onSelectMyth(myth.id);
                if (isMobile) {
                  setDrawerOpen(false);
                  window.scrollTo({ top: 120, behavior: 'smooth' });
                }
              }}
            >
              <div className="storybook-row-title">{myth.title}</div>
              <div className="storybook-row-meta">
                <span className="storybook-row-theme">
                  <span className={`storybook-theme-dot ${themeCls}`} />
                  <span className="storybook-theme-name">{(myth.theme || 'myth').toLowerCase()}</span>
                </span>
                <span className="storybook-row-words">{wordCount} words</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );

  return (
    <div className="page-surface">
      <PageHeader
        label="THE READING ROOM"
        title="Read the myths"
        intro={introText}
        image={THEME.heroBg}
      />

      <div className="section-parchment">
        <div className="storybook-layout">
          {/* Mobile: button above the story that opens a drawer */}
          <button
            type="button"
            className="storybook-mobile-choose-btn"
            onClick={() => setDrawerOpen(true)}
            aria-label="Choose a story"
          >
            <span className="storybook-mobile-choose-label">✦ Choose a story</span>
            <span className="storybook-mobile-choose-meta">
              {activeMyth ? activeMyth.title : `${filteredMyths.length} available`} &rarr;
            </span>
          </button>

          {/* Left Column: 340px sticky list panel */}
          <aside className="storybook-sidebar">
            {renderStoryList(false)}
          </aside>

          {/* Right Column: Story Column with max-width 720px */}
          {activeMyth ? (
            <main key={activeMyth.id || activeMyth.title} className="storybook-reader">
              <div className="storybook-reader-header">
                <div className="storybook-story-eyebrow">The story of</div>
                <div className="storybook-header-top-row">
                  <h1 className="storybook-story-title">{activeMyth.title}</h1>
                  <div className="storybook-export-btns">
                    <button
                      type="button"
                      onClick={downloadJson}
                      className="storybook-btn-ghost"
                    >
                      Export JSON
                    </button>
                    <button
                      type="button"
                      onClick={downloadMarkdown}
                      className="storybook-btn-ghost"
                    >
                      Export Markdown
                    </button>
                  </div>
                </div>

                <div className="storybook-meta-line">
                  <span className={`storybook-theme-chip ${getThemeClass(activeMyth.theme)}`}>
                    <span className={`storybook-theme-dot ${getThemeClass(activeMyth.theme)}`} />
                    {activeMyth.theme}
                  </span>
                  {activeMyth.source && (
                    <span className="storybook-source-label">
                      Source: {activeMyth.source}
                    </span>
                  )}
                </div>
              </div>

              {/* Full column width classical artwork */}
              {activeArtwork?.file && (
                <div className="storybook-artwork-wrap">
                  <img
                    src={activeArtwork.file}
                    alt={`Classical depiction related to ${activeMyth.title}`}
                    className="storybook-artwork-img"
                  />
                  {activeArtwork.credit && (
                    <div className="storybook-artwork-credit">{activeArtwork.credit}</div>
                  )}
                </div>
              )}

              {/* Moral as a pull quote: large Cormorant italic with a gold rule */}
              {activeMyth.moral && (
                <blockquote className="storybook-moral-pullquote">
                  &ldquo;{activeMyth.moral}&rdquo;
                </blockquote>
              )}

              {/* Story text Cormorant 1.3rem, line-height 1.85, gold drop cap */}
              <div className="storybook-story-text">
                <span className="storybook-drop-cap">
                  {(activeMyth.text || '').charAt(0)}
                </span>
                {(activeMyth.text || '').slice(1)}
              </div>

              {/* "Who's in this story" as chips with a small round portrait from PORTRAITS */}
              {activeMyth.characters && activeMyth.characters.length > 0 && (
                <div className="storybook-characters-section">
                  <h3 className="storybook-section-label">
                    Who&apos;s in this story
                  </h3>
                  <div className="storybook-character-chips">
                    {activeMyth.characters.map((c, i) => {
                      const name = typeof c === 'string' ? c : c.name || '?';
                      const rawType = typeof c === 'object' && c.type ? c.type : 'figure';
                      const typeCls = getTypeClass(rawType);
                      const portrait = portraitFor(name);
                      return (
                        <span
                          key={i}
                          className={`storybook-character-chip ${typeCls}`}
                        >
                          {portrait && (
                            <img
                              src={portrait}
                              alt={name}
                              className="storybook-char-portrait"
                              loading="lazy"
                            />
                          )}
                          <span className="storybook-char-name">{name}</span>
                          <Term word={rawType}>
                            <span className="storybook-character-type">
                              [{rawType.toUpperCase()}]
                            </span>
                          </Term>
                        </span>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Connections as one simple row */}
              {activeMyth.relationships && activeMyth.relationships.length > 0 && (
                <div className="storybook-connections-section">
                  <h3 className="storybook-connections-title">
                    How these characters are connected
                  </h3>
                  <div className="storybook-connections-row">
                    {activeMyth.relationships.map((rel, idx) => (
                      <span key={idx} className="storybook-connection-item">
                        <strong className="storybook-connection-node">{rel.source}</strong>
                        <span className="storybook-connection-arrow">&rarr;</span>
                        <em className="storybook-connection-rel">{rel.relation?.replace(/_/g, ' ')}</em>
                        <span className="storybook-connection-arrow">&rarr;</span>
                        <strong className="storybook-connection-node">{rel.target}</strong>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* "If you liked this" as a horizontal row of 3 cards, with image from MYTH_IMAGES */}
              {similarMyths.length > 0 && (
                <div className="storybook-similar-section">
                  <ThreadDivider />
                  <h3 className="storybook-similar-title">
                    If you liked this, try these
                  </h3>
                  <div className="storybook-similar-grid">
                    {similarMyths.slice(0, 3).map((sim, i) => {
                      const simThemeCls = getThemeClass(sim.theme);
                      const simArtwork = sim.id === 'myth_icarus'
                        ? { file: '/images/decor/icarus-falling.png' }
                        : mythImageFor(sim.id);
                      return (
                        <div
                          key={i}
                          className={`card storybook-similar-card ${simThemeCls}`}
                          role="button"
                          tabIndex={0}
                          onClick={() => {
                            setActiveMyth(sim);
                            window.scrollTo({ top: 120, behavior: 'smooth' });
                          }}
                          onKeyDown={e => {
                            if (e.key === 'Enter' || e.key === ' ') {
                              e.preventDefault();
                              setActiveMyth(sim);
                              window.scrollTo({ top: 120, behavior: 'smooth' });
                            }
                          }}
                        >
                          {simArtwork?.file && (
                            <div className="storybook-similar-img-box">
                              <img
                                src={simArtwork.file}
                                alt={sim.title}
                                className="storybook-similar-card-img"
                                loading="lazy"
                              />
                            </div>
                          )}
                          <div className="storybook-similar-content">
                            <h4 className="storybook-similar-card-title">{sim.title}</h4>
                            <div className="storybook-similar-meta">
                              <span className={`storybook-theme-pill ${simThemeCls}`}>
                                <span className={`storybook-theme-dot ${simThemeCls}`} />
                                {sim.theme}
                              </span>
                            </div>
                            <p className="storybook-similar-card-desc">
                              {sim.moral || (sim.text ? sim.text.substring(0, 85) + '…' : '')}
                            </p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </main>
          ) : (
            <div className="storybook-empty">
              Select a myth from the index to begin reading.
            </div>
          )}
        </div>
      </div>

      {/* Mobile Drawer Overlay */}
      {drawerOpen && (
        <div
          className="storybook-drawer-backdrop"
          onClick={() => setDrawerOpen(false)}
          role="dialog"
          aria-modal="true"
          aria-label="Choose a story"
        >
          <div
            className="storybook-drawer-panel"
            onClick={e => e.stopPropagation()}
          >
            <div className="storybook-drawer-header">
              <h3 className="storybook-drawer-title">Choose a story</h3>
              <button
                type="button"
                className="storybook-drawer-close"
                onClick={() => setDrawerOpen(false)}
                aria-label="Close"
              >
                &times;
              </button>
            </div>
            <div className="storybook-drawer-body">
              {renderStoryList(true)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
