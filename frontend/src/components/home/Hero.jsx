import React from 'react';
import { THEME } from '../../data/theme';
import './Hero.css';

const ANCHORS = [
  { num: '01', label: 'STORIES', target: 'stories' },
  { num: '02', label: 'FAMILY TREE', target: 'family' },
  { num: '03', label: 'THE ORACLE', target: 'oracle' },
  { num: '04', label: 'PLACES', target: 'places' },
  { num: '05', label: 'ARTIFACTS', target: 'artifacts' },
];

export default function Hero({ onNavigate, totalMyths, characterCount, themeCount, totalWords }) {
  const handleScroll = (e, targetId) => {
    e.preventDefault();
    const el = document.getElementById(targetId);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    } else {
      window.location.hash = `#${targetId}`;
    }
  };

  return (
    <>
      <section id="hero" className="hero-section hero-section--layered">
        {/* Background Layer (z-index 1, behind GoldenThread z-index 2) */}
        <div
          className="hero-bg-layer"
          style={{ backgroundImage: `url(${THEME.heroBg})` }}
          aria-hidden="true"
        />

        {/* Subtle warm ambient scrim */}
        <div className="hero-scrim hero-scrim--layered" aria-hidden="true" />

        {/* Goddess Marble Figure positioned in center-right with celestial golden halo astrolabe */}
        <div className="hero-figure-wrap hero-figure-wrap--centered" aria-hidden="true">
          {/* Celestial Halo Astrolabe behind goddess head */}
          <div className="hero-astrolabe-wrap hero-astrolabe-wrap--centered">
            <svg
              viewBox="0 0 500 500"
              className="hero-astrolabe-svg"
              aria-hidden="true"
            >
              <defs>
                <filter id="astrolabeGlowExact" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="2.5" result="blur" />
                  <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
              </defs>

              <g filter="url(#astrolabeGlowExact)" stroke="var(--gold, #D9A441)" fill="none">
                {/* Outer limbus rings */}
                <circle cx="250" cy="250" r="242" strokeWidth="1.5" opacity="0.8" />
                <circle cx="250" cy="250" r="236" strokeWidth="0.8" strokeDasharray="3 3" opacity="0.6" />
                <circle cx="250" cy="250" r="226" strokeWidth="1.2" opacity="0.75" />

                {/* Degree tick graduation marks */}
                {Array.from({ length: 72 }, (_, i) => {
                  const deg = i * 5;
                  const isMajor = deg % 30 === 0;
                  const isMid = deg % 10 === 0;
                  return (
                    <line
                      key={deg}
                      x1="250"
                      y1={isMajor ? "10" : isMid ? "14" : "18"}
                      x2="250"
                      y2="24"
                      strokeWidth={isMajor ? 1.6 : 0.8}
                      strokeOpacity={isMajor ? 0.95 : 0.65}
                      transform={`rotate(${deg} 250 250)`}
                    />
                  );
                })}

                {/* 12 Astrolabe hour / house dots */}
                {Array.from({ length: 12 }, (_, i) => (
                  <circle
                    key={`dot-${i}`}
                    cx="250"
                    cy="32"
                    r="2.5"
                    fill="var(--gold, #D9A441)"
                    transform={`rotate(${i * 30} 250 250)`}
                  />
                ))}

                {/* Inner coordinate rings */}
                <circle cx="250" cy="250" r="195" strokeWidth="0.9" strokeOpacity="0.7" />
                <circle cx="250" cy="250" r="150" strokeWidth="1" strokeDasharray="6 3" strokeOpacity="0.65" />
                <circle cx="250" cy="250" r="105" strokeWidth="0.8" strokeOpacity="0.6" />
                <circle cx="250" cy="250" r="55" strokeWidth="1" strokeOpacity="0.75" />

                {/* Astrolabe off-center Zodiac / Ecliptic ring (rete) */}
                <circle cx="250" cy="205" r="95" strokeWidth="1.4" strokeOpacity="0.85" />
                <circle cx="250" cy="205" r="90" strokeWidth="0.7" strokeDasharray="4 2" strokeOpacity="0.55" />

                {/* Astrolabe star pointer curved arcs */}
                <path d="M 250 110 Q 285 155 345 205 Q 305 220 250 205" strokeWidth="1.2" strokeOpacity="0.75" />
                <path d="M 250 110 Q 215 155 155 205 Q 195 220 250 205" strokeWidth="1.2" strokeOpacity="0.75" />
                <path d="M 250 295 Q 295 345 330 380 Q 280 370 250 350" strokeWidth="1" strokeOpacity="0.65" />
                <path d="M 250 295 Q 205 345 170 380 Q 220 370 250 350" strokeWidth="1" strokeOpacity="0.65" />

                {/* Axis meridian & horizon lines */}
                <line x1="250" y1="24" x2="250" y2="476" strokeWidth="0.8" strokeDasharray="8 4" strokeOpacity="0.45" />
                <line x1="24" y1="250" x2="476" y2="250" strokeWidth="0.8" strokeDasharray="8 4" strokeOpacity="0.45" />

                {/* Center hub pin */}
                <circle cx="250" cy="250" r="14" fill="rgba(20, 16, 12, 0.4)" strokeWidth="1.5" />
                <circle cx="250" cy="250" r="4.5" fill="var(--gold, #D9A441)" />

                {/* 8 Cardinal pointer diamonds */}
                {Array.from({ length: 8 }, (_, i) => (
                  <polygon
                    key={`star-${i}`}
                    points="250,185 253,195 250,205 247,195"
                    fill="var(--gold, #D9A441)"
                    transform={`rotate(${i * 45} 250 250)`}
                  />
                ))}
              </g>
            </svg>
          </div>

          {/* Marble Goddess Statue Layer */}
          <img
            src={THEME.heroGoddess}
            alt="Greek Goddess"
            className="hero-goddess hero-goddess--centered"
            loading="eager"
          />
        </div>

        {/* Floating petals drifting down */}
        <div className="hero-rose-petals" aria-hidden="true">
          {Array.from({ length: 8 }, (_, i) => (
            <span key={i} className={`hero-rose-petal hero-petal-${i + 1}`} />
          ))}
        </div>



        {/* Right quotation ornament */}
        <aside className="hero-right-quote" aria-hidden="true">
          <div className="hero-quote-compass">✦</div>
          <blockquote className="hero-quote-text">
            “THE STORIES<br />
            THAT SHAPED<br />
            A WORLD<br />
            STILL SPEAK.”
          </blockquote>
        </aside>

        {/* Main Stage: Left Column & Bottom Anchors */}
        <div className="hero-stage hero-stage--layered">
          <div className="hero-left-col hero-left-col--layered">
            <div className="hero-label hero-label--exact">
              MYTHS · GODS · HEROES · PLACES · ARTIFACTS
            </div>

            <h1 className="hero-title hero-title--exact">
              <span className="hero-title-line">LEGENDS</span>
              <span className="hero-title-line">
                <span className="hero-title-word--still">STILL</span>{' '}
                <span className="hero-title-compass" aria-hidden="true">
                  <svg viewBox="0 0 60 60" width="34" height="34" fill="none">
                    <circle cx="30" cy="30" r="14" stroke="currentColor" strokeWidth="1" opacity="0.65" />
                    <circle cx="30" cy="30" r="22" stroke="currentColor" strokeWidth="0.8" strokeDasharray="2 2" opacity="0.45" />
                    <line x1="30" y1="2" x2="30" y2="58" stroke="currentColor" strokeWidth="1.2" />
                    <line x1="2" y1="30" x2="58" y2="30" stroke="currentColor" strokeWidth="1.2" />
                    <polygon points="30,8 33,26 30,30 27,26" fill="currentColor" />
                    <polygon points="30,52 33,34 30,30 27,34" fill="currentColor" />
                    <polygon points="8,30 26,27 30,30 26,33" fill="currentColor" />
                    <polygon points="52,30 34,27 30,30 34,33" fill="currentColor" />
                  </svg>
                </span>
              </span>
              <span className="hero-title-line">LIVE HERE</span>
            </h1>

            <p className="hero-description hero-description--exact">
              Explore the stories, people, places and artifacts of Greek mythology — not just as history, but as a living world.
            </p>

            <div className="hero-cta">
              <button
                type="button"
                className="hero-outline-btn"
                onClick={() => onNavigate('storybook')}
              >
                <span>EXPLORE THE STORIES</span>
                <span className="hero-btn-arrow" aria-hidden="true">→</span>
              </button>
            </div>
          </div>

          {/* Bottom row of smooth-scroll anchors: Classical horizontal line with compass star in center */}
          <nav className="hero-anchors-exact" aria-label="Page sections">
            <div className="hero-anchors-line hero-anchors-line--left" aria-hidden="true" />

            {ANCHORS.map((item) => (
              <a
                key={item.target}
                href={`#${item.target}`}
                className={`hero-anchor-exact ${item.target === 'oracle' ? 'hero-anchor-exact--center' : ''}`}
                onClick={(e) => handleScroll(e, item.target)}
              >
                {item.target === 'oracle' && (
                  <span className="hero-center-sunburst" aria-hidden="true">
                    <svg viewBox="0 0 40 40" width="22" height="22" fill="none">
                      <circle cx="20" cy="20" r="3.5" fill="currentColor" />
                      {Array.from({ length: 12 }, (_, i) => (
                        <line
                          key={i}
                          x1="20"
                          y1="6"
                          x2="20"
                          y2="12"
                          stroke="currentColor"
                          strokeWidth="1"
                          transform={`rotate(${i * 30} 20 20)`}
                        />
                      ))}
                    </svg>
                  </span>
                )}
                <span className="hero-anchor-num-exact">{item.num}</span>
                <span className="hero-anchor-title-exact">{item.label}</span>
              </a>
            ))}

            <div className="hero-anchors-line hero-anchors-line--right" aria-hidden="true" />
          </nav>
        </div>
      </section>

      {/* Slim cream strip with four stats below the hero */}
      <div className="hero-stats-strip" aria-label="Chronicle statistics">
        <div className="hero-stats-container">
          {[
            { value: totalMyths || '—', label: 'Complete Myths' },
            { value: characterCount || '—', label: 'Gods, Heroes & Monsters' },
            { value: themeCount || '—', label: 'Universal Themes' },
            { value: (totalWords || 4381).toLocaleString(), label: 'Words, Unabridged' },
          ].map(({ value, label }) => (
            <div key={label} className="hero-stat-cell">
              <span className="hero-stat-number">{value}</span>
              <span className="hero-stat-title">{label}</span>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
