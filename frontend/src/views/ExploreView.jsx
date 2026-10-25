import React, { useState, useEffect } from 'react';
import { NAV_GROUPS } from '../data/navGroups';
import PantheonView from './PantheonView';
import FiguresView from './FiguresView';
import MotifsView from './MotifsView';
import ThemesView from './ThemesView';
import ArchitectureView from './ArchitectureView';
import GalleryView from './GalleryView';

// Helper to determine matching sub-view from hash
const readHash = () => {
  const clean = window.location.hash.replace(/^#\/?/, '');
  const parts = clean.split('/');
  const sub = parts[1] || 'pantheon';
  const arg = parts[2] ? decodeURIComponent(parts[2]) : undefined;

  return { clean, sub, arg };
};

export default function ExploreView({ onSelectMyth }) {
  const [{ clean, sub, arg }, setLocation] = useState(readHash);

  useEffect(() => {
    const onHash = () => setLocation(readHash());
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  const go = (route) => {
    window.location.hash = `/${route}`;
  };

  // Determine which subtab is active based on current route/hash
  const isTabActive = (item) => {
    if (item.route === 'explore/gallery/places') {
      return clean === 'explore/gallery/places' || clean === 'explore/places';
    }
    if (item.route === 'explore/gallery/artifacts') {
      return clean === 'explore/gallery/artifacts' || clean === 'explore/artifacts';
    }
    const itemSub = item.route.split('/')[1];
    return sub === itemSub;
  };

  const subTabsNode = (groupKey) => {
    const group = NAV_GROUPS.find(item => item.key === groupKey);
    const tabs = group?.items || [];

    return (
    <div className="sub-tab-bar" role="tablist" aria-label={`${group?.label || 'Explore'} Sections`}>
      {tabs.map(item => {
        const active = isTabActive(item);
        return (
          <button
            key={item.label}
            role="tab"
            aria-selected={active}
            className={`sub-tab-btn ${active ? 'active' : ''}`}
            onClick={() => go(item.route)}
          >
            {item.label}
          </button>
        );
      })}
    </div>
    );
  };

  return (
    <div className="explore-view">
      {sub === 'pantheon' && <PantheonView onSelectMyth={onSelectMyth} initialName={arg} subTabs={subTabsNode('people')} />}
      {sub === 'figures' && <FiguresView onSelectMyth={onSelectMyth} initialName={arg} subTabs={subTabsNode('people')} />}
      {sub === 'motifs' && <MotifsView onSelectMyth={onSelectMyth} subTabs={subTabsNode('insights')} />}
      {(sub === 'gallery' || sub === 'places' || sub === 'artifacts') && (
        <GalleryView initialSection={arg || (sub === 'places' ? 'places' : sub === 'artifacts' ? 'artifacts' : undefined)} subTabs={subTabsNode('world')} />
      )}
      {sub === 'themes' && <ThemesView subTabs={subTabsNode('insights')} />}
      {sub === 'architecture' && <ArchitectureView subTabs={subTabsNode('insights')} />}
    </div>
  );
}
