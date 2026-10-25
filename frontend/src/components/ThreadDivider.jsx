import React from 'react';
import './ThreadDivider.css';

/**
 * ThreadDivider — Golden thread line and celestial compass star divider
 * Used between sections on inner pages.
 */
export default function ThreadDivider({ className = '' }) {
  return (
    <div className={`thread-divider ${className}`} aria-hidden="true">
      <div className="thread-divider-line thread-divider-line--left" />
      <div className="thread-divider-star">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none">
          <circle cx="12" cy="12" r="2" fill="var(--glow, #FFD98A)" />
          <path
            d="M 12 1 L 14 9 L 22 12 L 14 15 L 12 23 L 10 15 L 2 12 L 10 9 Z"
            fill="var(--gold, #D9A441)"
          />
          <path
            d="M 12 5 L 13.5 10.5 L 19 12 L 13.5 13.5 L 12 19 L 10.5 13.5 L 5 12 L 10.5 10.5 Z"
            fill="#FFF7E0"
          />
        </svg>
      </div>
      <div className="thread-divider-line thread-divider-line--right" />
    </div>
  );
}
