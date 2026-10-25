import React, { useState, useEffect, useMemo } from 'react';
import PageHeader from '../components/PageHeader';
import Reveal from '../components/Reveal';
import { typeColor, themeColor } from '../utils/colors';
import { portraitFor } from '../data/portraits';
import { THEME } from '../data/theme';
import './FiguresView.css';

const TYPES = ['all', 'god', 'titan', 'mortal', 'creature'];

export default function FiguresView({ onSelectMyth, initialName, subTabs }) {
  const [figures, setFigures] = useState([]);
  const [error, setError] = useState(false);
  const [type, setType] = useState('all');
  const [filter, setFilter] = useState('');
  const [name, setName] = useState(initialName || 'Athena');
  const [profile, setProfile] = useState(null);
  const [loadingProfile, setLoadingProfile] = useState(false);
  const [other, setOther] = useState('');
  const [comparison, setComparison] = useState(null);
  const [compareError, setCompareError] = useState('');

  useEffect(() => {
    fetch('/api/characters')
      .then(r => {
        if (!r.ok) throw new Error(r.status);
        return r.json();
      })
      .then(setFigures)
      .catch(() => setError(true));
  }, []);

  useEffect(() => {
    if (!name) return undefined;
    const ctrl = new AbortController();
    setLoadingProfile(true);
    setComparison(null);
    setCompareError('');
    fetch(`/api/characters/${encodeURIComponent(name)}`, { signal: ctrl.signal })
      .then(r => {
        if (!r.ok) throw new Error(r.status);
        return r.json();
      })
      .then(p => {
        setProfile(p);
        setLoadingProfile(false);
      })
      .catch(err => {
        if (err.name !== 'AbortError') {
          setProfile(null);
          setLoadingProfile(false);
        }
      });
    return () => ctrl.abort();
  }, [name]);

  const visible = useMemo(() => {
    const q = filter.trim().toLowerCase();
    return figures.filter(
      f =>
        (type === 'all' || f.type === type) &&
        (!q || f.name.toLowerCase().includes(q) || (f.roman_name || '').toLowerCase().includes(q))
    );
  }, [figures, type, filter]);

  const pick = (n) => {
    setName(n);
    window.location.hash = `/explore/figures/${encodeURIComponent(n)}`;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const runCompare = (e) => {
    e.preventDefault();
    if (!other.trim() || !profile) return;
    setCompareError('');
    fetch(`/api/compare?a=${encodeURIComponent(profile.name)}&b=${encodeURIComponent(other.trim())}`)
      .then(r => {
        if (!r.ok) throw new Error(r.status);
        return r.json();
      })
      .then(setComparison)
      .catch(() => {
        setComparison(null);
        setCompareError(`I could not find “${other}”. Pick a name from the list.`);
      });
  };

  const maxTheme = profile ? Math.max(1, ...profile.themes.map(t => t.count)) : 1;
  const fam = profile?.family;
  const famRows = fam
    ? [
        ['Parents', fam.parents],
        ['Spouses', fam.spouses],
        ['Siblings', fam.siblings],
        ['Half-siblings', fam.half_siblings],
        ['Children', fam.children],
        ['Lovers', fam.lovers],
      ].filter(([, list]) => list && list.length)
    : [];

  const portrait = profile ? portraitFor(profile.name) : null;
  const profileColor = profile ? typeColor(profile.type) : 'var(--gold, #D9A441)';
  const treeReturnName = initialName || profile?.name;

  const introText = (
    <>
      Look up any god, hero or monster: who their family is, which stories they appear in, and what those
      stories are about. Roman names such as Jupiter or Minerva work too.
    </>
  );

  return (
    <div className="page-surface">
      <PageHeader
        label="FIGURES"
        title="Gods, heroes and monsters"
        intro={introText}
        image={THEME.footerBg}
      >
        {subTabs}
      </PageHeader>

      <div className="section-parchment">
        {treeReturnName && (
          <a
            className="figures-back-tree"
            href={`#/explore/pantheon/${encodeURIComponent(treeReturnName)}`}
          >
            ← Back to Family Tree
          </a>
        )}
        {error && (
          <p role="alert" className="figures-alert">
            The figure index could not be loaded.
          </p>
        )}

        <div className="figures-page-layout">
          {/* Left Column: Sticky Cream List Panel */}
          <aside className="figures-sidebar" aria-label="Figure Directory">
            <input
              type="search"
              aria-label="Filter figures"
              placeholder="Find a figure…"
              value={filter}
              onChange={e => setFilter(e.target.value)}
              className="figures-search-input"
            />

            {/* Type Filter Chips */}
            <div className="figures-type-chips" role="group" aria-label="Filter by kind">
              {TYPES.map(t => (
                <button
                  key={t}
                  type="button"
                  aria-pressed={type === t}
                  className={`figures-type-chip ${type === t ? 'active' : ''}`}
                  onClick={() => setType(t)}
                >
                  {t}
                </button>
              ))}
            </div>

            {/* Figures Rows List */}
            <div className="figures-list" role="listbox" aria-label="Figures">
              {visible.map(f => {
                const isSelected = f.name === profile?.name;
                const fColor = typeColor(f.type);
                return (
                  <button
                    key={f.name}
                    type="button"
                    role="option"
                    aria-selected={isSelected}
                    className={`figures-row ${isSelected ? 'active' : ''}`}
                    onClick={() => pick(f.name)}
                  >
                    <span className="figures-row-name">{f.name}</span>
                    <span className="figures-row-meta">
                      <span className="figures-row-type" style={{ color: fColor }}>
                        {f.type}
                      </span>{' '}
                      &bull; {f.myth_count}
                    </span>
                  </button>
                );
              })}
              {visible.length === 0 && (
                <div className="figures-empty">No figures match.</div>
              )}
            </div>
          </aside>

          {/* Right Column: Unboxed Profile Content */}
          <main className="figures-profile-pane" aria-live="polite">
            {loadingProfile && !profile && (
              <p className="figures-empty">Loading…</p>
            )}

            {!loadingProfile && !profile && (
              <p className="figures-empty">Choose a figure from the list.</p>
            )}

            {profile && (
              <>
                {/* Profile Header: Round portrait at 140px with a gold ring next to name, type pill and Roman name */}
                <header className="figures-profile-header">
                  <div className="figures-profile-avatar ring-gold">
                    {portrait ? (
                      <img
                        src={portrait}
                        alt={profile.name}
                        className="figures-profile-avatar-img"
                      />
                    ) : (
                      <div
                        className="figures-profile-avatar-initial"
                        style={{ color: profileColor }}
                      >
                        {(profile.name || '?').charAt(0).toUpperCase()}
                      </div>
                    )}
                  </div>

                  <div className="figures-profile-info">
                    <div className="figures-profile-title-row">
                      <h2 className="figures-profile-name">{profile.name}</h2>
                      <span
                        className="figures-type-pill"
                        style={{
                          borderColor: profileColor,
                          color: profileColor,
                        }}
                      >
                        {profile.type}
                      </span>
                    </div>

                    {(profile.roman_name || profile.aliases.length > 0) && (
                      <p className="figures-profile-aliases">
                        {profile.roman_name && profile.roman_name !== profile.name && (
                          <span className="figures-roman-name">
                            Roman name: <strong>{profile.roman_name}</strong>.{' '}
                          </span>
                        )}
                        {profile.aliases.filter(a => !a.includes(profile.name) && a !== profile.roman_name).length > 0 && (
                          <span className="figures-aliases-list">
                            Also called{' '}
                            {profile.aliases
                              .filter(a => !a.includes(profile.name) && a !== profile.roman_name)
                              .slice(0, 4)
                              .join(', ')}
                            .
                          </span>
                        )}
                      </p>
                    )}
                  </div>
                </header>

                {/* Family as chips with gold underlined links */}
                {famRows.length > 0 && (
                  <section className="figures-section">
                    <h3 className="figures-section-heading">Family</h3>
                    <div className="figures-family-chips">
                      {famRows.map(([label, list]) => (
                        <div key={label} className="figures-family-chip">
                          <span className="figures-family-chip-role">{label}:</span>
                          <span className="figures-family-chip-names">
                            {list.map((n, i) => (
                              <React.Fragment key={n}>
                                {i > 0 && ', '}
                                <button
                                  type="button"
                                  className="figures-gold-link"
                                  onClick={() => pick(n)}
                                >
                                  {n}
                                </button>
                              </React.Fragment>
                            ))}
                          </span>
                        </div>
                      ))}
                    </div>
                  </section>
                )}

                {/* Recurring themes as thin bars in the existing theme colors, lowercase labels */}
                {profile.themes.length > 0 && (
                  <section className="figures-section">
                    <h3 className="figures-section-heading">Recurring themes</h3>
                    <div className="figures-theme-bars">
                      {profile.themes.slice(0, 6).map(t => (
                        <div key={t.theme} className="figures-bar-row">
                          <span className="figures-bar-label">{t.theme.toLowerCase()}</span>
                          <span className="figures-bar-track" aria-hidden="true">
                            <span
                              className="figures-bar-fill"
                              style={{
                                width: `${(t.count / maxTheme) * 100}%`,
                                backgroundColor: themeColor(t.theme),
                              }}
                            />
                          </span>
                          <span className="figures-bar-count">{t.count}</span>
                        </div>
                      ))}
                    </div>
                  </section>
                )}

                {/* "Appears in N stories" as a two-column list of titles with small theme dots */}
                <section className="figures-section">
                  <h3 className="figures-section-heading">
                    Appears in {profile.myths.length} {profile.myths.length === 1 ? 'story' : 'stories'}
                  </h3>
                  {profile.myths.length === 0 ? (
                    <p className="figures-muted-text">
                      No story in this collection centres on them, but they appear in the family tree.
                    </p>
                  ) : (
                    <ul className="figures-myths-two-col">
                      {profile.myths.slice(0, 12).map(m => (
                        <li key={m.id} className="figures-myth-col-item">
                          <span
                            className="figures-theme-dot"
                            style={{ backgroundColor: themeColor(m.theme) }}
                            aria-hidden="true"
                            title={m.theme}
                          />
                          <button
                            type="button"
                            className="figures-gold-link figures-myth-title-link"
                            onClick={() => onSelectMyth && onSelectMyth(m.id)}
                          >
                            {m.title}
                          </button>
                        </li>
                      ))}
                    </ul>
                  )}
                  {profile.myths.length > 12 && (
                    <p className="figures-more-text">
                      &hellip;and {profile.myths.length - 12} more in Read The Myths.
                    </p>
                  )}
                </section>

                {/* "Often appears alongside" as portrait chips */}
                {profile.companions.length > 0 && (
                  <section className="figures-section">
                    <h3 className="figures-section-heading">Often appears alongside</h3>
                    <div className="figures-companions-row">
                      {profile.companions.map(c => {
                        const cPortrait = portraitFor(c.name);
                        return (
                          <button
                            key={c.name}
                            type="button"
                            className="figures-portrait-chip"
                            onClick={() => pick(c.name)}
                          >
                            <span className="figures-companion-avatar">
                              {cPortrait ? (
                                <img
                                  src={cPortrait}
                                  alt=""
                                  className="figures-companion-avatar-img"
                                />
                              ) : (
                                <span className="figures-companion-avatar-initial">
                                  {c.name.charAt(0)}
                                </span>
                              )}
                            </span>
                            <span className="figures-companion-name">{c.name}</span>
                          </button>
                        );
                      })}
                    </div>
                  </section>
                )}

                {/* Compare with another figure: inline input with a dark button */}
                <section className="figures-section">
                  <h3 className="figures-section-heading">Compare with another figure</h3>
                  <form onSubmit={runCompare} className="figures-compare-inline-form">
                    <input
                      list="fig-names"
                      aria-label="Figure to compare with"
                      placeholder="e.g. Ares"
                      value={other}
                      onChange={e => setOther(e.target.value)}
                      className="figures-compare-input"
                    />
                    <datalist id="fig-names">
                      {figures.map(f => (
                        <option key={f.name} value={f.name} />
                      ))}
                    </datalist>
                    <button
                      type="submit"
                      className="btn-dark figures-compare-btn"
                      disabled={!other.trim()}
                    >
                      Compare
                    </button>
                  </form>

                  {compareError && (
                    <p role="alert" className="figures-compare-error">
                      {compareError}
                    </p>
                  )}

                  {comparison && (
                    <div className="figures-compare-result">
                      <p className="figures-compare-rel">
                        {comparison.relationship || 'No family tie is recorded between them.'}
                      </p>
                      <p>
                        <strong>Together in:</strong>{' '}
                        {comparison.shared_myths.length
                          ? comparison.shared_myths.join(', ')
                          : 'no story in this collection'}
                      </p>
                      {comparison.shared_themes.length > 0 && (
                        <p>
                          <strong>Both explore:</strong> {comparison.shared_themes.join(', ')}
                        </p>
                      )}
                      {comparison.only_a_themes.length > 0 && (
                        <p>
                          <strong>Only {comparison.a.name}:</strong> {comparison.only_a_themes.join(', ')}
                        </p>
                      )}
                      {comparison.only_b_themes.length > 0 && (
                        <p>
                          <strong>Only {comparison.b.name}:</strong> {comparison.only_b_themes.join(', ')}
                        </p>
                      )}
                    </div>
                  )}
                </section>
              </>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}
