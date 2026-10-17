import React from 'react';

/**
 * Small hand-drawn-feeling glyphs that give each section its own visual
 * identity instead of a bare text heading — an open scroll for the reading
 * room, a laurel for the primer, an eye for the Oracle, a branching tree for
 * the pantheon, a rising bar motif for themes, and a column for the engine.
 */
const PATHS = {
  scroll: (
    <>
      <path d="M6 5c0-1.7 1.3-3 3-3s3 1.3 3 3v14c0 1.7 1.3 3 3 3s3-1.3 3-3" />
      <path d="M9 2H19c1.7 0 3 1.3 3 3v2H9" />
      <path d="M12 9h7M12 13h7M12 17h5" />
    </>
  ),
  laurel: (
    <>
      <path d="M12 3v18" />
      <path d="M12 6c-2 0-5 1-6 4 3 0 5-1 6-3" />
      <path d="M12 10c-2.4 0-5.6 1-6.8 4.2 3.4 0 6-1.2 6.8-3.4" />
      <path d="M12 14c-2.6 0-6 1.2-7.2 4.6 3.6 0 6.4-1.3 7.2-3.6" />
      <path d="M12 6c2 0 5 1 6 4-3 0-5-1-6-3" />
      <path d="M12 10c2.4 0 5.6 1 6.8 4.2-3.4 0-6-1.2-6.8-3.4" />
      <path d="M12 14c2.6 0 6 1.2 7.2 4.6-3.6 0-6.4-1.3-7.2-3.6" />
    </>
  ),
  eye: (
    <>
      <path d="M2 12c3-5 8-7 10-7s7 2 10 7c-3 5-8 7-10 7s-7-2-10-7Z" />
      <circle cx="12" cy="12" r="3" />
    </>
  ),
  tree: (
    <>
      <circle cx="12" cy="5" r="2.4" />
      <circle cx="5" cy="13" r="2.2" />
      <circle cx="19" cy="13" r="2.2" />
      <circle cx="9" cy="20" r="2" />
      <circle cx="17" cy="20" r="2" />
      <path d="M12 7.4V11M12 11 5 13M12 11l7 2M5 15.2 9 18M19 15.2 17 18" />
    </>
  ),
  bars: (
    <>
      <path d="M4 20V11M10 20V7M16 20V13M20 20V4" />
    </>
  ),
  column: (
    <>
      <path d="M4 4h16M4 20h16M7 7v10M11 7v10M13 7v10M17 7v10" />
    </>
  ),
};

export default function SectionIcon({ name, size = 28 }) {
  const path = PATHS[name];
  if (!path) return null;
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="var(--accent-gold)"
      strokeWidth="1.3"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      style={{ flexShrink: 0 }}
    >
      {path}
    </svg>
  );
}
