import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import OpeningView from './views/OpeningView';
import PrimerView from './views/PrimerView';
import StorybookView from './views/StorybookView';
import OracleView from './views/OracleView';
import ExploreView from './views/ExploreView';

const TABS = [
  { key: 'primer', label: 'Start Here' },
  { key: 'storybook', label: 'Read The Myths' },
  { key: 'oracle', label: 'Ask The Oracle' },
  { key: 'explore', label: 'Explore' },
];
const VALID_TABS = ['opening', ...TABS.map(t => t.key)];
const TITLES = {
  opening: 'Chronicle: Greek Mythology, Told For Everyone',
  primer: 'Start Here · Chronicle',
  storybook: 'Read The Myths · Chronicle',
  oracle: 'Ask The Oracle · Chronicle',
  explore: 'Explore · Chronicle',
};

const tabFromHash = () => {
  const key = window.location.hash.replace(/^#\/?/, '').split('/')[0];
  return VALID_TABS.includes(key) ? key : 'opening';
};

export default function App() {
  const [activeTab, setActiveTabState] = useState(tabFromHash);
  const [myths, setMyths] = useState([]);
  const [selectedMythId, setSelectedMythId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const [pendingOracleQuery, setPendingOracleQuery] = useState(null);

  // Tabs live in the URL hash so the back button, refresh and deep links work.
  const setActiveTab = (pathOrKey) => {
    const clean = pathOrKey.replace(/^#\/?/, '');
    const key = clean.split('/')[0];
    const newHash = `/${clean}`;
    if (window.location.hash !== `#${newHash}`) {
      window.location.hash = newHash;
    }
    setActiveTabState(key);
    window.scrollTo({ top: 0 });
  };

  useEffect(() => {
    const onHash = () => setActiveTabState(tabFromHash());
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  const loadMyths = () => {
    setLoading(true);
    setLoadError(false);
    fetch('/api/myths')
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(data => {
        if (!Array.isArray(data)) throw new Error('Unexpected response');
        setMyths(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load myths:', err);
        setLoadError(true);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadMyths();
  }, []);

  useEffect(() => {
    document.title = TITLES[activeTab] || TITLES.opening;
  }, [activeTab]);

  const handleSelectMyth = (mythIdOrTitle) => {
    setSelectedMythId(mythIdOrTitle);
    setActiveTab('storybook');
  };

  const handleAskOracle = (query) => {
    setPendingOracleQuery(query);
    setActiveTab('oracle');
  };

  const totalWords = myths.reduce((acc, m) => acc + (m.text ? m.text.split(/\s+/).length : 0), 0);
  const uniqueThemes = new Set(myths.map(m => m.theme).filter(Boolean)).size;
  const characterCount = new Set(myths.flatMap(m => (m.characters || []).map(c => c.name))).size;

  return (
    <div className="app-container">
      <a
        href="#main-content"
        className="skip-link"
        onClick={(e) => { e.preventDefault(); document.getElementById('main-content')?.focus(); }}
      >
        Skip to content
      </a>
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Active View Container */}
      <main id="main-content" tabIndex={-1} className={activeTab === 'opening' ? '' : 'content-area'}>
        {activeTab === 'primer' ? (
          <PrimerView onNavigate={setActiveTab} />
        ) : loading ? (
          <div className="state-box" role="status">Retrieving ancient Greek lore archive...</div>
        ) : loadError ? (
          <div className="state-box" role="alert">
            <p>The myth archive could not be reached. Check that the Chronicle server is running.</p>
            <button className="btn-primary" onClick={loadMyths}>Try again</button>
          </div>
        ) : (
          <>
            {activeTab === 'opening' && (
              <OpeningView
                onNavigate={setActiveTab}
                onAskOracle={handleAskOracle}
                totalMyths={myths.length}
                totalWords={totalWords}
                themeCount={uniqueThemes}
                characterCount={characterCount}
                myths={myths}
                onSelectMyth={handleSelectMyth}
              />
            )}
            {activeTab === 'storybook' && (
              <StorybookView
                myths={myths}
                onSelectMyth={handleSelectMyth}
                selectedMythId={selectedMythId}
              />
            )}
            {activeTab === 'oracle' && (
              <OracleView
                onSelectMyth={handleSelectMyth}
                initialQuery={pendingOracleQuery}
                onInitialQueryConsumed={() => setPendingOracleQuery(null)}
              />
            )}
            {activeTab === 'explore' && (
              <ExploreView onSelectMyth={handleSelectMyth} />
            )}
          </>
        )}
      </main>

      <footer className={`chronicle-footer ${activeTab === 'opening' ? 'chronicle-footer--dark' : ''}`}>
        {myths.length} narratives &bull; {totalWords.toLocaleString()} words &bull; {uniqueThemes} themes
      </footer>
    </div>
  );
}
