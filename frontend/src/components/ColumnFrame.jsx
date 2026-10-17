import React from 'react';

/**
 * A single fluted Doric column — capital, shaft with flutes, and base —
 * used as a flanking ornament around hero content so it reads as standing
 * inside a temple entrance rather than a plain rectangle.
 */
function Column({ height, color = 'var(--accent-gold)' }) {
  return (
    <svg
      viewBox="0 0 28 140"
      preserveAspectRatio="none"
      aria-hidden="true"
      style={{ width: 28, height: height || '100%', flexShrink: 0 }}
    >
      {/* Capital */}
      <rect x="2" y="2" width="24" height="7" fill="none" stroke={color} strokeWidth="1.4" />
      <rect x="6" y="9" width="16" height="5" fill="none" stroke={color} strokeWidth="1.4" />
      {/* Fluted shaft */}
      <line x1="8" y1="14" x2="8" y2="122" stroke={color} strokeWidth="1" opacity="0.8" />
      <line x1="14" y1="14" x2="14" y2="122" stroke={color} strokeWidth="1" opacity="0.8" />
      <line x1="20" y1="14" x2="20" y2="122" stroke={color} strokeWidth="1" opacity="0.8" />
      <rect x="4" y="14" width="20" height="108" fill="none" stroke={color} strokeWidth="1.4" />
      {/* Base */}
      <rect x="4" y="122" width="20" height="6" fill="none" stroke={color} strokeWidth="1.4" />
      <rect x="0" y="128" width="28" height="8" fill="none" stroke={color} strokeWidth="1.4" />
    </svg>
  );
}

/**
 * Wraps `children` with a column standing on either side, like the
 * entrance of a temple framing whatever sits between them.
 */
export default function ColumnFrame({ children, height, color }) {
  return (
    <div style={{ display: 'flex', alignItems: 'stretch', gap: '14px' }}>
      <Column height={height} color={color} />
      <div style={{ flex: 1, minWidth: 0 }}>{children}</div>
      <Column height={height} color={color} />
    </div>
  );
}
