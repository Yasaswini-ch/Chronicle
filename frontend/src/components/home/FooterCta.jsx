import React from 'react';
import { THEME } from '../../data/theme';
import Reveal from '../Reveal';
import './FooterCta.css';

export default function FooterCta({ onNavigate }) {
  const handleBeginJourney = (e) => {
    if (onNavigate) {
      e.preventDefault();
      onNavigate('primer');
    }
  };

  return (
    <section id="footer" className="footer-cta-section" aria-label="Begin your journey">
      {/* Background layer (z-index 1, below thread z-index 2) */}
      <div
        className="footer-bg-layer"
        style={{ backgroundImage: `url(${THEME.footerBg})` }}
        aria-hidden="true"
      />
      {/* Background Scrim */}
      <div className="footer-cta-scrim" aria-hidden="true" />



      {/* Decorative Goddess on the left */}
      <div className="footer-cta-goddess-wrap" aria-hidden="true">
        <img
          src={THEME.footerGoddess}
          alt=""
          className="footer-cta-goddess"
          loading="lazy"
        />
      </div>

      {/* Decorative Vine top-right */}
      <div className="footer-cta-vine-wrap" aria-hidden="true">
        <img
          src={THEME.vineRight}
          alt=""
          className="footer-cta-vine"
          loading="lazy"
        />
      </div>

      {/* Centered Content */}
      <div className="footer-cta-container">
        <Reveal className="footer-cta-center" delay={100}>
          {/* Small Star Glyph */}
          <div className="footer-cta-star" aria-hidden="true">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path
                d="M12 0L14.5 9.5L24 12L14.5 14.5L12 24L9.5 14.5L0 12L9.5 9.5L12 0Z"
                fill="var(--gold, #D9A441)"
              />
            </svg>
          </div>

          <h2 className="footer-cta-title">The legends are yours to follow</h2>

          <p className="footer-cta-description">
            Stories, people, places and artifacts, all connected by a world that still speaks.
          </p>

          <a
            href="#/primer"
            className="btn-dark footer-cta-btn"
            onClick={handleBeginJourney}
          >
            BEGIN YOUR JOURNEY
          </a>
        </Reveal>
      </div>

      {/* Bottom right quote in italic */}
      <div className="footer-cta-tagline">
        <em>Some stories never end. They just find new explorers.</em>
      </div>
    </section>
  );
}
