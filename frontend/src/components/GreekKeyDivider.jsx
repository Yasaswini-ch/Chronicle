import React from 'react';

/**
 * A tiled classical meander (Greek key) pattern used as a section divider —
 * a small, authentic graphic touch rather than a plain rule. Built as a CSS
 * repeat-x background (not an SVG viewBox) so it tiles correctly at any
 * container width instead of stretching or scaling oddly. `colors` cycles
 * the motif through a pottery-style palette instead of one gold tone.
 */
export default function GreekKeyDivider({ height = 16, opacity = 0.6, colors, margin }) {
  const palette = colors && colors.length ? colors : ['#9C7A3E'];
  const tileWidth = 24 * palette.length;

  const paths = palette
    .map((color, i) => `<path d='M${i * 24} 14 H${i * 24 + 8} V2 H${i * 24 + 16} V14 H${i * 24 + 24}' fill='none' stroke='${color.replace('#', '%23')}' stroke-width='1.6'/>`)
    .join('');

  const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='${tileWidth}' height='16'>${paths}</svg>`;

  return (
    <div
      role="presentation"
      style={{
        width: '100%',
        height,
        margin: margin ?? '28px 0',
        opacity,
        backgroundImage: `url("data:image/svg+xml,${svg}")`,
        backgroundRepeat: 'repeat-x',
        backgroundSize: `${tileWidth}px ${height}px`,
      }}
    />
  );
}
