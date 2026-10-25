import React, { useState, useEffect, useRef } from 'react';
import { NAV_GROUPS } from '../data/navGroups';
import './Navbar.css';

export default function Navbar({ activeTab, setActiveTab }) {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [exploreOpen, setExploreOpen] = useState(false);
  const [currentHash, setCurrentHash] = useState(() => window.location.hash);
  const exploreContainerRef = useRef(null);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 40);
    };

    const handleHashChange = () => {
      setCurrentHash(window.location.hash);
      setMenuOpen(false);
      setExploreOpen(false);
    };

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        setExploreOpen(false);
      }
    };

    const handleClickOutside = (e) => {
      if (exploreContainerRef.current && !exploreContainerRef.current.contains(e.target)) {
        setExploreOpen(false);
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    window.addEventListener('hashchange', handleHashChange);
    window.addEventListener('keydown', handleKeyDown);
    document.addEventListener('click', handleClickOutside);

    handleScroll();

    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('hashchange', handleHashChange);
      window.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('click', handleClickOutside);
    };
  }, []);

  const handleNavigate = (to) => {
    setActiveTab(to);
    setMenuOpen(false);
    setExploreOpen(false);
  };

  const navClass = [
    'chronicle-navbar',
    scrolled ? 'navbar--scrolled' : '',
  ].filter(Boolean).join(' ');

  const isStoriesActive = activeTab === 'storybook';
  const isOracleActive = activeTab === 'oracle';
  const isExploreActive = activeTab === 'explore';

  return (
    <header className={navClass}>
      <div className="navbar-container">
        {/* Left: Star glyph + Brand */}
        <button
          type="button"
          className="navbar-brand"
          onClick={() => handleNavigate('opening')}
          title="Chronicle Home"
          aria-label="Chronicle Home"
        >
          <span className="navbar-star-glyph" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="20" height="20">
              <path
                d="M12 2 L14.2 8.2 L21 9 L15.8 13.4 L17.4 20 L12 16.4 L6.6 20 L8.2 13.4 L3 9 L9.8 8.2 Z"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.3"
              />
            </svg>
          </span>
          <span className="navbar-brand-title">CHRONICLE</span>
        </button>

        {/* Center: Desktop Navigation Links */}
        <nav className="navbar-links" aria-label="Main Navigation">
          <button
            type="button"
            className={`navbar-link ${isStoriesActive ? 'active' : ''}`}
            aria-current={isStoriesActive ? 'page' : undefined}
            onClick={() => handleNavigate('storybook')}
          >
            STORIES
          </button>

          <button
            type="button"
            className={`navbar-link ${isOracleActive ? 'active' : ''}`}
            aria-current={isOracleActive ? 'page' : undefined}
            onClick={() => handleNavigate('oracle')}
          >
            THE ORACLE
          </button>

          {/* EXPLORE Dropdown Trigger & Panel */}
          <div
            className="navbar-explore-container"
            ref={exploreContainerRef}
            onMouseEnter={() => setExploreOpen(true)}
          >
            <button
              type="button"
              className={`navbar-link navbar-explore-trigger ${isExploreActive ? 'active' : ''} ${exploreOpen ? 'open' : ''}`}
              aria-expanded={exploreOpen}
              aria-haspopup="true"
              onClick={() => setExploreOpen((prev) => !prev)}
            >
              <span>EXPLORE</span>
              <svg
                className="navbar-chevron"
                viewBox="0 0 12 12"
                width="10"
                height="10"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M2.5 4.5L6 8L9.5 4.5" />
              </svg>
            </button>

            {/* Dark glass mega dropdown panel */}
            {exploreOpen && (
              <div className="navbar-explore-panel" role="menu">
                <div className="explore-panel-grid">
                  {NAV_GROUPS.map((group) => (
                    <div key={group.key} className="explore-group-col">
                      <div className="explore-group-label">{group.label}</div>
                      <div className="explore-group-items">
                        {group.items.map((item) => (
                          <button
                            key={item.label}
                            type="button"
                            className="explore-item-btn"
                            role="menuitem"
                            onClick={() => handleNavigate(item.route)}
                          >
                            <span className="explore-item-title">{item.label}</span>
                            <span className="explore-item-desc">{item.desc}</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </nav>

        {/* Right: Search + Pill CTA + Mobile Menu Button */}
        <div className="navbar-actions">
          <button
            type="button"
            className="navbar-search-btn"
            onClick={() => handleNavigate('storybook')}
            aria-label="Search stories"
            title="Search stories"
          >
            <svg
              viewBox="0 0 20 20"
              width="18"
              height="18"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.6"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <circle cx="8.5" cy="8.5" r="5.5" />
              <line x1="12.5" y1="12.5" x2="17" y2="17" />
            </svg>
          </button>

          <button
            type="button"
            className="navbar-journey-btn"
            onClick={() => handleNavigate('primer')}
          >
            <span>✦</span> BEGIN YOUR JOURNEY <span>+</span>
          </button>

          <button
            type="button"
            className="navbar-menu-toggle"
            onClick={() => setMenuOpen((prev) => !prev)}
            aria-expanded={menuOpen}
            aria-label="Toggle navigation menu"
          >
            {menuOpen ? (
              <svg viewBox="0 0 20 20" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                <line x1="4" y1="4" x2="16" y2="16" />
                <line x1="4" y1="16" x2="16" y2="4" />
              </svg>
            ) : (
              <svg viewBox="0 0 20 20" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                <line x1="3" y1="6" x2="17" y2="6" />
                <line x1="3" y1="10" x2="17" y2="10" />
                <line x1="3" y1="14" x2="17" y2="14" />
              </svg>
            )}
            <span>MENU</span>
          </button>
        </div>
      </div>

      {/* Mobile Dropdown (under 768px) */}
      {menuOpen && (
        <nav className="navbar-dropdown" aria-label="Mobile Navigation">
          <button
            type="button"
            className={`navbar-link ${isStoriesActive ? 'active' : ''}`}
            onClick={() => handleNavigate('storybook')}
          >
            STORIES
          </button>
          <button
            type="button"
            className={`navbar-link ${isOracleActive ? 'active' : ''}`}
            onClick={() => handleNavigate('oracle')}
          >
            THE ORACLE
          </button>

          <div className="mobile-explore-section">
            <div className="mobile-explore-header">EXPLORE</div>
            {NAV_GROUPS.map((group) => (
              <div key={group.key} className="mobile-group">
                <div className="mobile-group-title">{group.label}</div>
                {group.items.map((item) => (
                  <button
                    key={item.label}
                    type="button"
                    className="mobile-group-item-btn"
                    onClick={() => handleNavigate(item.route)}
                  >
                    <span className="mobile-item-title">{item.label}</span>
                    <span className="mobile-item-desc">{item.desc}</span>
                  </button>
                ))}
              </div>
            ))}
          </div>

          <button
            type="button"
            className="btn-dark navbar-dropdown-cta"
            onClick={() => handleNavigate('primer')}
          >
            BEGIN YOUR JOURNEY
          </button>
        </nav>
      )}
    </header>
  );
}
