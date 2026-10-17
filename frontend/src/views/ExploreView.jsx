import React, { useState, useEffect } from 'react';
import PantheonView from './PantheonView';
import FiguresView from './FiguresView';
import MotifsView from './MotifsView';
import QuizView from './QuizView';
import ThemesView from './ThemesView';
import ArchitectureView from './ArchitectureView';
import GalleryView from './GalleryView';

const SUB_TABS = [
  { key: 'pantheon', label: 'Family Tree' },
  { key: 'figures', label: 'Figures' },
  { key: 'motifs', label: 'Story Patterns' },
  { key: 'quiz', label: 'Test Yourself' },
  { key: 'gallery', label: 'Gallery of Antiquity' },
  { key: 'themes', label: 'By The Numbers' },
  { key: 'architecture', label: 'How It Was Built' },
];
const VALID = SUB_TABS.map(t => t.key);

// "#/explore/figures/Athena" -> { sub: 'figures', arg: 'Athena' }
const readHash = () => {
  const parts = window.location.hash.replace(/^#\/?/, '').split('/');
  const arg = parts[2] ? decodeURIComponent(parts[2]) : undefined;
  return { sub: VALID.includes(parts[1]) ? parts[1] : 'pantheon', arg };
};

export default function ExploreView({ onSelectMyth }) {
  const [{ sub, arg }, setLocation] = useState(readHash);

  useEffect(() => {
    const onHash = () => setLocation(readHash());
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  const go = (key) => {
    window.location.hash = `/explore/${key}`;
  };

  return (
    <div className="explore-olympus-bg">
      <div className="sub-tab-bar" role="tablist" aria-label="Explore">
        {SUB_TABS.map(t => (
          <button
            key={t.key}
            role="tab"
            aria-selected={sub === t.key}
            className={`sub-tab-btn ${sub === t.key ? 'active' : ''}`}
            onClick={() => go(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {sub === 'pantheon' && <PantheonView onSelectMyth={onSelectMyth} />}
      {sub === 'figures' && <FiguresView onSelectMyth={onSelectMyth} initialName={arg} />}
      {sub === 'motifs' && <MotifsView onSelectMyth={onSelectMyth} />}
      {sub === 'quiz' && <QuizView />}
      {sub === 'gallery' && <GalleryView />}
      {sub === 'themes' && <ThemesView />}
      {sub === 'architecture' && <ArchitectureView />}
    </div>
  );
}
