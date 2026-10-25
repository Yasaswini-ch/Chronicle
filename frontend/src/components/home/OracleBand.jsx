import React, { useState } from 'react';
import { THEME } from '../../data/theme';
import './OracleBand.css';

const TABS = ['ASK', 'EXPLORE', 'REFLECT'];

const CHIPS_DATA = {
  ASK: [
    { text: 'Who is Medusa, and why could no one look at her?', type: 'query' },
    { text: 'What happened to Icarus?', type: 'query' },
    { text: 'Tell me about Zeus and his family', type: 'query' },
    { text: 'Why do echoes repeat what you say?', type: 'query' },
  ],
  EXPLORE: [
    { text: 'Browse the figures', type: 'link', href: '#/explore/figures' },
    { text: 'See story patterns', type: 'link', href: '#/explore/motifs' },
    { text: 'Open the family tree', type: 'link', href: '#/explore/pantheon' },
    { text: 'Visit the gallery', type: 'link', href: '#/explore/gallery' },
  ],
  REFLECT: [
    { text: 'Which myths are about hubris?', type: 'query' },
    { text: 'Which myths are about loss?', type: 'query' },
    { text: 'Which myths have someone turned into a tree?', type: 'query' },
    { text: 'Compare Athena and Arachne', type: 'query' },
  ],
};

export default function OracleBand({ onAskOracle, onNavigate }) {
  const [activeTab, setActiveTab] = useState('ASK');
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) return; // Empty submit does nothing
    if (onAskOracle) {
      onAskOracle(trimmed);
    }
  };

  const handleChipClick = (chip) => {
    if (chip.type === 'query') {
      if (onAskOracle) {
        onAskOracle(chip.text);
      }
    } else if (chip.type === 'link') {
      if (chip.href.startsWith('#/')) {
        const cleanPath = chip.href.slice(2);
        if (onNavigate) {
          onNavigate(cleanPath);
        } else {
          window.location.hash = chip.href;
        }
      }
    }
  };

  return (
    <section id="oracle" className="oracle-section">
      {/* Background layer (z-index 1, below thread z-index 2) */}
      <div
        className="oracle-bg-layer"
        style={{ backgroundImage: `url(${THEME.oracleBg})` }}
        aria-hidden="true"
      />
      {/* Darkened Gradient Overlay */}
      <div className="oracle-overlay" aria-hidden="true" />

      <div className="oracle-container">
        {/* Left: Text and Slowly Rotating Sun Medallion */}
        <div className="oracle-left">
          <div className="oracle-text-wrap">
            <div className="label oracle-label">THE ORACLE</div>
            <h2 className="oracle-title">Ask what the myths remember</h2>
            <p className="oracle-description">
              Pose a question. Receive a path. Let the wisdom of the ancient stories guide your next step.
            </p>
          </div>

          <div className="oracle-sun-wrap" aria-hidden="true">
            <img
              src={THEME.oracleSun}
              alt=""
              className="oracle-sun-img"
              loading="lazy"
            />
          </div>
        </div>

        {/* Right: Parchment Card with Paper Grain Texture, Tabs, Input and Chips */}
        <div
          className="oracle-card"
          style={{ backgroundImage: `url(${THEME.paperGrain})` }}
        >
          {/* Tabs */}
          <div className="oracle-tabs" role="tablist">
            {TABS.map((tab) => (
              <button
                key={tab}
                type="button"
                role="tab"
                aria-selected={activeTab === tab}
                className={`oracle-tab-btn ${activeTab === tab ? 'active' : ''}`}
                onClick={() => setActiveTab(tab)}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Form */}
          <form className="oracle-form" onSubmit={handleSubmit}>
            <div className="oracle-input-row">
              <input
                type="text"
                className="oracle-input"
                placeholder="What do you seek guidance on?"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <button
                type="submit"
                className="oracle-submit-btn"
                aria-label="Submit Question"
              >
                →
              </button>
            </div>
          </form>

          {/* Chips */}
          <div className="oracle-chips-header">Try asking...</div>
          <div className="oracle-chips-grid">
            {CHIPS_DATA[activeTab].map((chip) =>
              chip.type === 'link' ? (
                <a
                  key={chip.text}
                  href={chip.href}
                  className="oracle-chip"
                  onClick={(e) => {
                    e.preventDefault();
                    handleChipClick(chip);
                  }}
                >
                  {chip.text}
                </a>
              ) : (
                <button
                  key={chip.text}
                  type="button"
                  className="oracle-chip"
                  onClick={() => handleChipClick(chip)}
                >
                  {chip.text}
                </button>
              )
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
