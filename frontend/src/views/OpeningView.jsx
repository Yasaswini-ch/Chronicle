import React, { useState } from 'react';
import LandingSections from '../components/LandingSections';
import './OpeningView.css';

const PROMPT_IDEAS = [
  'Who is Medusa, and why could no one look at her?',
  'What happened to Icarus?',
  'Tell me about Zeus and his family',
  'Why do echoes repeat what you say?',
];

export default function OpeningView({ onNavigate, onAskOracle, totalMyths, totalWords, themeCount, characterCount }) {
  const [query, setQuery] = useState('');

  const submit = (text) => {
    const q = (text ?? query).trim();
    if (!q) {
      onNavigate('primer');
      return;
    }
    onAskOracle(q);
  };

  return (
    <div className="opening-page">
      {/* Self-contained light nav, matching a landing page rather than the app chrome */}
      <nav className="opening-nav">
        <div className="opening-nav-brand" onClick={() => onNavigate('opening')}>
          <span className="opening-logo-mark" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="22" height="22">
              <path
                d="M12 2 L14.2 8.2 L21 9 L15.8 13.4 L17.4 20 L12 16.4 L6.6 20 L8.2 13.4 L3 9 L9.8 8.2 Z"
                fill="none"
                stroke="#7C6A3F"
                strokeWidth="1.3"
              />
            </svg>
          </span>
          CHRONICLE
        </div>
        <div className="opening-nav-links">
          <button onClick={() => onNavigate('primer')}>New Here?</button>
          <button onClick={() => onNavigate('storybook')}>Myths</button>
          <button onClick={() => onNavigate('oracle')}>Oracle</button>
          <button onClick={() => onNavigate('explore')}>Explore</button>
        </div>
        <button className="opening-nav-cta" onClick={() => onNavigate('primer')}>
          Begin Reading <span aria-hidden="true">&#8599;</span>
        </button>
      </nav>

      <div className="opening-hero">
      <img
        src="/images/hero/mythic-ruins.jpg"
        alt=""
        aria-hidden="true"
        width="1672"
        height="941"
        fetchpriority="high"
        className="opening-hero-vista-photo"
      />

      <div className="opening-hero-content">
        <div className="opening-eyebrow">Greek Mythology, Told For Everyone</div>

        <h1 className="opening-title">
          Timeless myths, <em>told plainly</em>
          <br />
          for readers who&apos;ve never met a Titan.
        </h1>

        <p className="opening-subtitle">
          {totalMyths ? `${totalMyths} ` : ''}Greek myths — gods, mortals, and monsters — retold in full, with every
          unfamiliar name quietly explained as you go. No homework required.
        </p>

        {/* The Oracle quick-ask bar, styled after a search / command box */}
        <form
          className="oracle-bar"
          onSubmit={(e) => {
            e.preventDefault();
            submit();
          }}
        >
          <div className="oracle-bar-label">Ask the Oracle</div>
          <div className="oracle-bar-row">
            <button
              type="button"
              className="oracle-bar-icon"
              title="See a few things you could ask"
              onClick={() => setQuery(PROMPT_IDEAS[Math.floor(Math.random() * PROMPT_IDEAS.length)])}
            >
              +
            </button>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask about any god, hero, or myth…"
            />
            <span className="oracle-bar-mode">Classic Telling &#9662;</span>
            <button type="submit" className="oracle-bar-submit" aria-label="Ask">
              &#8599;
            </button>
          </div>
        </form>

        <div className="oracle-bar-ideas">
          {PROMPT_IDEAS.slice(0, 3).map((p) => (
            <button key={p} onClick={() => submit(p)}>
              {p}
            </button>
          ))}
        </div>

        <div className="opening-stats-panel">
          <div className="opening-stats">
          {[
            { value: totalMyths || '—', label: 'Complete Myths' },
            { value: characterCount || '—', label: 'Gods, Heroes & Monsters' },
            { value: themeCount || '—', label: 'Universal Themes' },
            { value: (totalWords || 4381).toLocaleString(), label: 'Words, Unabridged' },
          ].map(({ value, label }) => (
            <div key={label} className="opening-stat">
              <div className="opening-stat-value">{value}</div>
              <div className="opening-stat-label">{label}</div>
            </div>
          ))}
          </div>
        </div>
      </div>
      </div>

      <LandingSections onNavigate={onNavigate} />
    </div>
  );
}
