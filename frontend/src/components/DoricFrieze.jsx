import React from 'react';

/**
 * A continuous Doric frieze: alternating triglyphs (the grooved vertical
 * blocks) and metopes (the plain or inset panels between them), exactly as
 * they run beneath the roofline of a Doric temple. Built as a CSS repeat-x
 * tile so it spans any width without distortion.
 */
export default function DoricFrieze({ height = 22, background = '#F2E9D3', line = '#9C7A3E', accent = '#7A2230' }) {
  const bg = background.replace('#', '%23');
  const ln = line.replace('#', '%23');
  const ac = accent.replace('#', '%23');

  // One repeat unit: a metope (plain inset square) + a triglyph (3 grooves).
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='48' height='22'>
    <rect width='48' height='22' fill='${bg}'/>
    <rect x='2' y='2' width='26' height='18' fill='none' stroke='${ln}' stroke-width='1'/>
    <circle cx='15' cy='11' r='3' fill='none' stroke='${ac}' stroke-width='1'/>
    <rect x='32' y='0' width='14' height='22' fill='${bg}' stroke='${ln}' stroke-width='1'/>
    <line x1='36' y1='1' x2='36' y2='21' stroke='${ln}' stroke-width='1.4'/>
    <line x1='39' y1='1' x2='39' y2='21' stroke='${ln}' stroke-width='1.4'/>
    <line x1='42' y1='1' x2='42' y2='21' stroke='${ln}' stroke-width='1.4'/>
  </svg>`;

  return (
    <div
      role="presentation"
      style={{
        width: '100%',
        height,
        backgroundImage: `url("data:image/svg+xml,${svg}")`,
        backgroundRepeat: 'repeat-x',
        backgroundSize: `48px ${height}px`,
        borderTop: `1px solid ${line}`,
        borderBottom: `1px solid ${line}`,
      }}
    />
  );
}
