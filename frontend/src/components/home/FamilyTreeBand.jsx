import React from 'react';
import { THEME } from '../../data/theme';
import Reveal from '../Reveal';
import './FamilyTreeBand.css';

const FIGURES = [
  { key: 'zeus', name: 'Zeus', image: THEME.busts.zeus, tier: 1, x: 50, y: 15.38, size: 'large' },
  { key: 'hera', name: 'Hera', image: THEME.busts.hera, tier: 2, x: 28, y: 36.54, size: 'medium' },
  { key: 'poseidon', name: 'Poseidon', image: THEME.busts.poseidon, tier: 2, x: 72, y: 36.54, size: 'medium' },
  { key: 'demeter', name: 'Demeter', image: THEME.busts.demeter, tier: 3, x: 10.5, y: 73.08, size: 'small' },
  { key: 'athena', name: 'Athena', image: THEME.busts.athena, tier: 3, x: 26.0, y: 73.08, size: 'small' },
  { key: 'apollo', name: 'Apollo', image: THEME.busts.apollo, tier: 3, x: 42.0, y: 73.08, size: 'small' },
  { key: 'artemis', name: 'Artemis', image: THEME.busts.artemis, tier: 3, x: 58.0, y: 73.08, size: 'small' },
  { key: 'ares', name: 'Ares', image: THEME.busts.ares, tier: 3, x: 74.0, y: 73.08, size: 'small' },
  { key: 'aphrodite', name: 'Aphrodite', image: THEME.busts.aphrodite, tier: 3, x: 89.5, y: 73.08, size: 'small' },
];

// 20 star sparkles positioned across the 1000 x 520 viewBox
const SPARKLES = [
  { x: 60, y: 55, r: 2.2, delay: 0.1 },
  { x: 180, y: 110, r: 1.8, delay: 0.7 },
  { x: 370, y: 45, r: 2.5, delay: 1.4 },
  { x: 630, y: 40, r: 2.0, delay: 0.4 },
  { x: 840, y: 85, r: 2.4, delay: 1.9 },
  { x: 940, y: 65, r: 1.6, delay: 1.1 },
  { x: 130, y: 220, r: 2.6, delay: 2.3 },
  { x: 420, y: 150, r: 1.9, delay: 0.9 },
  { x: 580, y: 155, r: 2.2, delay: 1.7 },
  { x: 860, y: 200, r: 2.0, delay: 0.3 },
  { x: 50, y: 320, r: 1.8, delay: 2.1 },
  { x: 210, y: 290, r: 2.4, delay: 1.3 },
  { x: 350, y: 250, r: 1.6, delay: 0.6 },
  { x: 500, y: 195, r: 2.5, delay: 1.8 },
  { x: 650, y: 250, r: 1.7, delay: 2.5 },
  { x: 800, y: 300, r: 2.3, delay: 0.8 },
  { x: 945, y: 310, r: 2.1, delay: 1.5 },
  { x: 170, y: 460, r: 2.4, delay: 0.2 },
  { x: 490, y: 465, r: 1.9, delay: 1.2 },
  { x: 820, y: 460, r: 2.3, delay: 2.0 },
];

export default function FamilyTreeBand({ onNavigate }) {
  const handleExploreClick = (e) => {
    if (onNavigate) {
      e.preventDefault();
      onNavigate('explore/pantheon');
    }
  };

  const handleNodeClick = (e, name) => {
    if (onNavigate) {
      e.preventDefault();
      onNavigate(`explore/figures/${encodeURIComponent(name)}`);
    }
  };

  const renderNode = (fig) => (
    <a
      key={fig.key}
      href={`#/explore/figures/${encodeURIComponent(fig.name)}`}
      className={`family-node family-node--${fig.size}`}
      style={{
        '--node-x': `${fig.x}%`,
        '--node-y': `${fig.y}%`,
      }}
      onClick={(e) => handleNodeClick(e, fig.name)}
      aria-label={`Explore ${fig.name}`}
    >
      <div className="family-node-avatar ring-gold">
        <img
          src={fig.image}
          alt={fig.name}
          className="family-node-img"
          loading="lazy"
        />
      </div>
      <span className="family-node-name">{fig.name}</span>
    </a>
  );

  return (
    <section id="family" className="family-tree-band">
      {/* Background layer (z-index 1, below thread z-index 2) */}
      <div
        className="family-bg-layer"
        style={{ backgroundImage: `url(${THEME.treeBg})` }}
        aria-hidden="true"
      />
      <div className="family-tree-scrim" aria-hidden="true" />

      <div className="family-tree-container">
        {/* Left Block */}
        <Reveal className="family-left" delay={100}>
          <div className="label family-label">FAMILY TREE</div>
          <h2 className="family-title">A family written in the stars</h2>
          <p className="family-description">
            Explore the divine lineage, their relationships, and the intricate connections that shaped the mythological world.
          </p>
          <a
            href="#/explore/pantheon"
            className="btn-dark family-cta-btn"
            onClick={handleExploreClick}
          >
            EXPLORE THE FAMILY TREE
          </a>
        </Reveal>

        {/* Right Block: Fixed-aspect container (1000 x 520) */}
        <Reveal className="family-tree-diagram" delay={200}>
          {/* Curved SVG connectors & twinkling sparkles */}
          <svg
            className="family-connectors-svg"
            viewBox="0 0 1000 520"
            preserveAspectRatio="xMidYMid meet"
            aria-hidden="true"
          >
            <defs>
              <filter id="familySoftGlow" x="-30%" y="-30%" width="160%" height="160%">
                <feGaussianBlur stdDeviation="2.5" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>

            {/* Constellation Zigzag Connector Paths */}
            <g className="family-connector-group">
              {/* Zeus to Hera (zigzag) */}
              <path d="M 500 80 L 430 115 L 360 140 L 280 190" className="family-connector-path" />

              {/* Zeus to Poseidon (zigzag) */}
              <path d="M 500 80 L 570 115 L 640 140 L 720 190" className="family-connector-path" />

              {/* Celestial Arch: Hera to Poseidon with apex vertices */}
              <path d="M 280 190 L 370 230 L 500 255 L 630 230 L 720 190" className="family-connector-path" />

              {/* Zeus lightning bolt lineage down to central asterism hub */}
              <path d="M 500 80 L 485 145 L 520 195 L 500 255" className="family-connector-path" />

              {/* Zeus direct zigzag to Demeter */}
              <path d="M 500 80 L 380 135 L 240 220 L 140 290 L 105 380" className="family-connector-path" />

              {/* Zeus direct zigzag to Aphrodite */}
              <path d="M 500 80 L 620 135 L 760 220 L 860 290 L 895 380" className="family-connector-path" />

              {/* Lineage zigzags down to each Olympian in the bottom row */}
              {/* Hera to Demeter */}
              <path d="M 280 190 L 210 245 L 175 320 L 105 380" className="family-connector-path" />

              {/* Hub to Athena & Hera to Athena */}
              <path d="M 500 255 L 410 275 L 340 325 L 260 380" className="family-connector-path" />
              <path d="M 280 190 L 315 285 L 260 380" className="family-connector-path" />

              {/* Hub to Apollo (Apollo & Artemis solar/lunar zigzag) */}
              <path d="M 500 255 L 460 290 L 440 335 L 420 380" className="family-connector-path" />

              {/* Hub to Artemis */}
              <path d="M 500 255 L 540 290 L 560 335 L 580 380" className="family-connector-path" />

              {/* Hub to Ares & Poseidon to Ares */}
              <path d="M 500 255 L 590 275 L 660 325 L 740 380" className="family-connector-path" />
              <path d="M 720 190 L 685 285 L 740 380" className="family-connector-path" />

              {/* Poseidon to Aphrodite */}
              <path d="M 720 190 L 790 245 L 825 320 L 895 380" className="family-connector-path" />

              {/* Bottom row constellation polygon bridges */}
              <path d="M 105 380 L 180 355 L 260 380" className="family-connector-path" />
              <path d="M 260 380 L 340 405 L 420 380" className="family-connector-path" />
              <path d="M 420 380 L 500 355 L 580 380" className="family-connector-path" />
              <path d="M 580 380 L 660 405 L 740 380" className="family-connector-path" />
              <path d="M 740 380 L 820 355 L 895 380" className="family-connector-path" />
            </g>

            {/* Constellation Joint Vertices (Star Points) */}
            <g className="family-vertices-group" aria-hidden="true">
              {[
                [430, 115], [360, 140], [570, 115], [640, 140],
                [370, 230], [500, 255], [630, 230],
                [485, 145], [520, 195],
                [380, 135], [240, 220], [140, 290],
                [620, 135], [760, 220], [860, 290],
                [210, 245], [175, 320], [315, 285],
                [410, 275], [340, 325],
                [460, 290], [440, 335],
                [540, 290], [560, 335],
                [590, 275], [660, 325], [685, 285],
                [790, 245], [825, 320],
                [180, 355], [340, 405], [500, 355], [660, 405], [820, 355]
              ].map(([vx, vy], vi) => (
                <circle
                  key={vi}
                  cx={vx}
                  cy={vy}
                  r="2.2"
                  fill="var(--gold, #D9A441)"
                  filter="url(#familySoftGlow)"
                  className="family-constellation-vertex"
                />
              ))}
            </g>

            {/* 20 Small Twinkling Star Sparkles */}
            <g className="family-sparkles-group">
              {SPARKLES.map((s, i) => (
                <g
                  key={i}
                  className="family-star-sparkle"
                  style={{
                    transformOrigin: `${s.x}px ${s.y}px`,
                    animationDelay: `${s.delay}s`,
                  }}
                >
                  <path
                    d={`M ${s.x} ${s.y - s.r * 2.5} Q ${s.x} ${s.y} ${s.x + s.r * 2.5} ${s.y} Q ${s.x} ${s.y} ${s.x} ${s.y + s.r * 2.5} Q ${s.x} ${s.y} ${s.x - s.r * 2.5} ${s.y} Z`}
                    fill="var(--glow, #FFD98A)"
                    opacity="0.9"
                  />
                  <circle cx={s.x} cy={s.y} r={s.r * 0.65} fill="#FFFFFF" />
                </g>
              ))}
            </g>
          </svg>

          {/* Tier 1: Zeus alone */}
          <div className="family-tier family-tier--1">
            {FIGURES.filter((f) => f.tier === 1).map(renderNode)}
          </div>

          {/* Tier 2: Hera and Poseidon */}
          <div className="family-tier family-tier--2">
            {FIGURES.filter((f) => f.tier === 2).map(renderNode)}
          </div>

          {/* Tier 3: The Six (Demeter, Athena, Apollo, Artemis, Ares, Aphrodite) */}
          <div className="family-tier family-tier--3">
            {FIGURES.filter((f) => f.tier === 3).map(renderNode)}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
