import React from 'react';
import { THEME } from '../../data/theme';
import Reveal from '../Reveal';
import './Artifacts.css';

const ARTIFACT_ITEMS = [
  {
    id: 'marble-statue',
    title: 'MARBLE STATUE',
    kind: 'Unknown Goddess',
    location: '5th century BCE',
    image: THEME.statue || '/images/theme/statue.jpg',
  },
  {
    id: 'attic-pottery',
    title: 'ATTIC RED-FIGURE POTTERY',
    kind: 'Scene from a Dionysian ritual',
    location: 'c. 410 BCE',
    image: THEME.pottery || '/images/theme/pottery.jpg',
  },
  {
    id: 'ancient-coin',
    title: 'ANCIENT COIN',
    kind: 'Athena / Owl',
    location: 'c. 440 BCE',
    image: THEME.coin || '/images/theme/coin.jpg',
  },
  {
    id: 'sculpted-fragment',
    title: 'SCULPTED FRAGMENT',
    kind: 'Temple relief',
    location: 'c. 430 BCE',
    image: THEME.fragment || '/images/theme/fragment.jpg',
  },
];

export default function Artifacts({ onNavigate }) {
  const handleNavigateToGallery = (e) => {
    if (onNavigate) {
      e.preventDefault();
      onNavigate('explore/gallery/artifacts');
    }
  };

  return (
    <section id="artifacts" className="artifacts-section">
      {/* Background layer (z-index 1, below thread z-index 2) */}
      <div
        className="artifacts-bg-layer"
        style={{
          backgroundImage: `linear-gradient(to bottom, rgba(20, 16, 12, 0.88), rgba(20, 16, 12, 0.94)), url(${THEME.oracleBg})`,
        }}
        aria-hidden="true"
      />
      {/* Ambient candlelit temple glow */}
      <div className="artifacts-ambient-glow" aria-hidden="true" />

      <div className="artifacts-container">
        {/* Left Block */}
        <Reveal className="artifacts-left" delay={100}>
          <div className="label artifacts-label">ARTIFACTS</div>
          <h2 className="artifacts-title">What time could not erase</h2>
          <p className="artifacts-description">
            Real sculptures, pottery, inscriptions and objects that keep the myths alive in our world today.
          </p>
          <a
            href="#/explore/gallery/artifacts"
            className="btn-dark artifacts-btn"
            onClick={handleNavigateToGallery}
          >
            EXPLORE THE ARTIFACTS
          </a>
        </Reveal>

        {/* Right Block: Four Dark Cards with Thin Gold Border in 4-column row */}
        <div className="artifacts-cards-grid">
          {ARTIFACT_ITEMS.map((item, index) => (
            <Reveal
              key={item.id}
              delay={(index + 1) * 120}
              className="artifact-card-wrapper"
            >
              <a
                href="#/explore/gallery/artifacts"
                className="artifact-card"
                onClick={handleNavigateToGallery}
                aria-label={`Explore ${item.title}`}
              >
                <div className="artifact-card-media">
                  <img
                    src={item.image}
                    alt={item.title}
                    className="artifact-card-img"
                    loading="lazy"
                  />
                </div>
                <div className="artifact-card-content">
                  <div className="artifact-card-info">
                    <h3 className="artifact-card-title">{item.title}</h3>
                    <div className="artifact-card-meta">
                      <span className="artifact-card-kind">{item.kind}</span>
                      <span className="artifact-card-location">{item.location}</span>
                    </div>
                  </div>
                  <span className="artifact-card-circle-btn" aria-hidden="true">
                    →
                  </span>
                </div>
              </a>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
