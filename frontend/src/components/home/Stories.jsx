import React from 'react';
import { THEME } from '../../data/theme';
import Reveal from '../Reveal';
import './Stories.css';

const STORY_CARDS = [
  {
    key: 'persephone',
    title: 'PERSEPHONE',
    image: THEME.persephone,
    tagline: 'A journey between worlds',
    matchKey: 'persephone',
  },
  {
    key: 'athena',
    title: 'ATHENA',
    image: THEME.athena,
    tagline: 'Wisdom in a changing world',
    matchKey: 'athena',
  },
  {
    key: 'orpheus',
    title: 'ORPHEUS',
    image: THEME.orpheus,
    tagline: 'A love that crossed death',
    matchKey: 'orpheus',
  },
];

export default function Stories({ myths = [], onSelectMyth, onNavigate }) {
  const findMyth = (keyword) => {
    if (!Array.isArray(myths)) return null;
    const kw = keyword.toLowerCase();
    // 1. Direct case-insensitive title match
    const byTitle = myths.find((m) => m.title && m.title.toLowerCase().includes(kw));
    if (byTitle) return byTitle;
    // 2. Proserpine alias fallback for Persephone
    if (kw === 'persephone') {
      const byProserpine = myths.find(
        (m) => m.title && m.title.toLowerCase().includes('proserpine')
      );
      if (byProserpine) return byProserpine;
    }
    return null;
  };

  const handleCardClick = (matchKey) => {
    const myth = findMyth(matchKey);
    if (myth && onSelectMyth) {
      onSelectMyth(myth.id);
    } else if (onNavigate) {
      onNavigate('storybook');
    }
  };

  return (
    <section id="stories" className="stories-section">
      {/* Background layer (z-index 1, below thread z-index 2) */}
      <div className="stories-bg-layer" aria-hidden="true" />

      <div className="stories-container">
        {/* Left Block */}
        <div className="stories-left">
          <div className="label stories-label">STORIES</div>
          <h2 className="stories-title">
            Every <span className="stories-title-accent">myth</span>
            <br />
            leaves a trace
          </h2>
          <p className="stories-description">
            More than tales of gods and heroes, these are stories of love, power, loss, and everything in between, carried across time.
          </p>
          <button
            type="button"
            className="btn-dark"
            onClick={() => onNavigate && onNavigate('storybook')}
          >
            EXPLORE ALL STORIES
          </button>
        </div>

        {/* Right Block: Three 4:5 Portrait Cards with Staggered Reveal */}
        <div className="stories-cards-grid">
          {STORY_CARDS.map((card, index) => (
            <Reveal
              key={card.key}
              delay={(index + 1) * 120}
              className="story-card-wrapper"
            >
              <div
                role="button"
                tabIndex={0}
                className="story-portrait-card"
                onClick={() => handleCardClick(card.matchKey)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleCardClick(card.matchKey);
                  }
                }}
                aria-label={`Read story of ${card.title}`}
              >
                <div className="story-card-media">
                  <img
                    src={card.image}
                    alt={card.title}
                    className="story-card-img"
                    loading="lazy"
                  />
                </div>
                <div className="story-card-content">
                  <div className="story-card-title">{card.title}</div>
                  <div className="story-card-footer">
                    <p className="story-card-tagline">{card.tagline}</p>
                    <span className="story-card-circle-btn" aria-hidden="true">
                      →
                    </span>
                  </div>
                </div>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
