import React, { useState, useEffect, useMemo } from 'react';
import Reveal from '../components/Reveal';
import SectionIcon from '../components/SectionIcon';
import { typeColor, themeColor } from '../utils/colors';

const TYPES = ['all', 'god', 'titan', 'mortal', 'creature'];

function NameLink({ name, onPick }) {
  return (
    <button type="button" className="fig-link" onClick={() => onPick(name)}>
      {name}
    </button>
  );
}

function LinkList({ names, onPick }) {
  return names.map((n, i) => (
    <React.Fragment key={n}>
      {i > 0 && ', '}
      <NameLink name={n} onPick={onPick} />
    </React.Fragment>
  ));
}

export default function FiguresView({ onSelectMyth, initialName }) {
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
      .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
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
      .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(p => { setProfile(p); setLoadingProfile(false); })
      .catch(err => { if (err.name !== 'AbortError') { setProfile(null); setLoadingProfile(false); } });
    return () => ctrl.abort();
  }, [name]);

  const visible = useMemo(() => {
    const q = filter.trim().toLowerCase();
    return figures.filter(f => (type === 'all' || f.type === type) &&
      (!q || f.name.toLowerCase().includes(q) || (f.roman_name || '').toLowerCase().includes(q)));
  }, [figures, type, filter]);

  const pick = (n) => {
    setName(n);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const runCompare = (e) => {
    e.preventDefault();
    if (!other.trim() || !profile) return;
    setCompareError('');
    fetch(`/api/compare?a=${encodeURIComponent(profile.name)}&b=${encodeURIComponent(other.trim())}`)
      .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(setComparison)
      .catch(() => { setComparison(null); setCompareError(`I could not find “${other}”. Pick a name from the list.`); });
  };

  const maxTheme = profile ? Math.max(1, ...profile.themes.map(t => t.count)) : 1;
  const fam = profile?.family;
  const famRows = fam ? [
    ['Parents', fam.parents], ['Spouses', fam.spouses], ['Siblings', fam.siblings],
    ['Half-siblings', fam.half_siblings], ['Children', fam.children], ['Lovers', fam.lovers],
  ].filter(([, list]) => list && list.length) : [];

  return (
    <div>
      <Reveal style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '4px' }}>
          <SectionIcon name="laurel" />
          <h2 style={{ fontSize: '1.6rem', margin: 0 }}>Figures</h2>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Look up any god, hero or monster: who their family is, which stories they appear in, and what those
          stories are about. Roman names such as Jupiter or Minerva work too.
        </p>
      </Reveal>

      {error && <p role="alert" style={{ color: 'var(--accent-garnet)' }}>The figure index could not be loaded.</p>}

      <div className="fig-layout">
        <div>
          <input
            type="search"
            aria-label="Filter figures"
            placeholder="Find a figure…"
            value={filter}
            onChange={e => setFilter(e.target.value)}
            style={{ width: '100%', marginBottom: '8px' }}
          />
          <div className="fig-types" role="group" aria-label="Filter by kind">
            {TYPES.map(t => (
              <button key={t} type="button" aria-pressed={type === t}
                className={`fig-type-btn ${type === t ? 'active' : ''}`} onClick={() => setType(t)}>
                {t}
              </button>
            ))}
          </div>
          <div className="fig-list" role="listbox" aria-label="Figures">
            {visible.map(f => (
              <button key={f.name} type="button" role="option" aria-selected={f.name === profile?.name}
                className={`fig-row ${f.name === profile?.name ? 'active' : ''}`} onClick={() => pick(f.name)}>
                <span>{f.name}</span>
                <span className="fig-row-meta">
                  <span style={{ color: typeColor(f.type) }}>{f.type}</span> · {f.myth_count}
                </span>
              </button>
            ))}
            {visible.length === 0 && <div style={{ padding: '16px', color: 'var(--text-muted)' }}>No figures match.</div>}
          </div>
        </div>

        <div className="panel" style={{ padding: '24px 28px', minHeight: '320px' }} aria-live="polite">
          {loadingProfile && !profile && <p style={{ color: 'var(--text-muted)' }}>Loading…</p>}
          {!loadingProfile && !profile && <p style={{ color: 'var(--text-muted)' }}>Choose a figure from the list.</p>}
          {profile && (
            <>
              <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'baseline', gap: '12px', marginBottom: '6px' }}>
                <h3 style={{ fontSize: '1.9rem', margin: 0 }}>{profile.name}</h3>
                <span className="badge-theme" style={{ borderColor: typeColor(profile.type), color: typeColor(profile.type) }}>
                  {profile.type}
                </span>
              </div>
              {(profile.roman_name || profile.aliases.length > 0) && (
                <p style={{ color: 'var(--text-secondary)', margin: '0 0 16px' }}>
                  {profile.roman_name && profile.roman_name !== profile.name && <>Roman name: <strong>{profile.roman_name}</strong>. </>}
                  {profile.aliases.filter(a => !a.includes(profile.name) && a !== profile.roman_name).length > 0 &&
                    <>Also called {profile.aliases.filter(a => !a.includes(profile.name) && a !== profile.roman_name).slice(0, 4).join(', ')}.</>}
                </p>
              )}

              {famRows.length > 0 && (
                <section className="fig-section">
                  <h4>Family</h4>
                  <dl className="fig-family">
                    {famRows.map(([label, list]) => (
                      <React.Fragment key={label}>
                        <dt>{label}</dt>
                        <dd><LinkList names={list} onPick={pick} /></dd>
                      </React.Fragment>
                    ))}
                  </dl>
                </section>
              )}

              {profile.themes.length > 0 && (
                <section className="fig-section">
                  <h4>Recurring themes</h4>
                  <div className="fig-bars">
                    {profile.themes.slice(0, 6).map(t => (
                      <div key={t.theme} className="fig-bar-row">
                        <span className="fig-bar-label">{t.theme}</span>
                        <span className="fig-bar-track" aria-hidden="true">
                          <span className="fig-bar-fill" style={{ width: `${(t.count / maxTheme) * 100}%`, background: themeColor(t.theme) }} />
                        </span>
                        <span className="fig-bar-n">{t.count}</span>
                      </div>
                    ))}
                  </div>
                </section>
              )}

              <section className="fig-section">
                <h4>Appears in {profile.myths.length} {profile.myths.length === 1 ? 'story' : 'stories'}</h4>
                {profile.myths.length === 0 && <p style={{ color: 'var(--text-muted)', margin: 0 }}>No story in this collection centres on them, but they appear in the family tree.</p>}
                <ul className="fig-myths">
                  {profile.myths.slice(0, 12).map(m => (
                    <li key={m.id}>
                      <button type="button" className="fig-link" onClick={() => onSelectMyth && onSelectMyth(m.id)}>{m.title}</button>
                      <span className="badge-theme" style={{ marginLeft: '8px', borderColor: themeColor(m.theme), color: themeColor(m.theme) }}>{m.theme}</span>
                    </li>
                  ))}
                </ul>
                {profile.myths.length > 12 && <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>…and {profile.myths.length - 12} more in Read The Myths.</p>}
              </section>

              {profile.companions.length > 0 && (
                <section className="fig-section">
                  <h4>Often appears alongside</h4>
                  <p style={{ margin: 0 }}><LinkList names={profile.companions.map(c => c.name)} onPick={pick} /></p>
                </section>
              )}

              <section className="fig-section">
                <h4>Compare with another figure</h4>
                <form onSubmit={runCompare} className="fig-compare-form">
                  <input list="fig-names" aria-label="Figure to compare with" placeholder="e.g. Ares"
                    value={other} onChange={e => setOther(e.target.value)} style={{ flex: 1, minWidth: 0 }} />
                  <datalist id="fig-names">{figures.map(f => <option key={f.name} value={f.name} />)}</datalist>
                  <button type="submit" className="btn-primary" disabled={!other.trim()}>Compare</button>
                </form>
                {compareError && <p role="alert" style={{ color: 'var(--accent-garnet)', fontSize: '0.9rem' }}>{compareError}</p>}
                {comparison && (
                  <div className="fig-compare">
                    <p style={{ fontWeight: 600, marginTop: 0 }}>
                      {comparison.relationship || 'No family tie is recorded between them.'}
                    </p>
                    <p>
                      <strong>Together in:</strong>{' '}
                      {comparison.shared_myths.length ? comparison.shared_myths.join(', ') : 'no story in this collection'}
                    </p>
                    {comparison.shared_themes.length > 0 && <p><strong>Both explore:</strong> {comparison.shared_themes.join(', ')}</p>}
                    {comparison.only_a_themes.length > 0 && <p><strong>Only {comparison.a.name}:</strong> {comparison.only_a_themes.join(', ')}</p>}
                    {comparison.only_b_themes.length > 0 && <p><strong>Only {comparison.b.name}:</strong> {comparison.only_b_themes.join(', ')}</p>}
                  </div>
                )}
              </section>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
