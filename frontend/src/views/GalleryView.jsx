import React, { useState, useEffect, useCallback } from 'react';
import PageHeader from '../components/PageHeader';
import Reveal from '../components/Reveal';
import { GALLERY } from '../data/gallery';
import { THEME } from '../data/theme';
import './GalleryView.css';

const PLACE_KINDS = [
  'temple',
  'fortification entrance',
  'tholos tomb',
  'tholos (beehive) tomb',
  'sanctuary',
  'theatre',
  'theater',
  'palace',
  'gateway',
  'treasury (building)',
];

function isPlace(item) {
  const k = (item.kind || '').toLowerCase();
  return PLACE_KINDS.some(p => k.includes(p));
}

const placesItems    = GALLERY.filter(item =>  isPlace(item));
const artifactsItems = GALLERY.filter(item => !isPlace(item));

export default function GalleryView({ initialSection, subTabs }) {
  const [active, setActive] = useState(null);
  const showPlaces = !initialSection || initialSection === 'places';
  const showArtifacts = !initialSection || initialSection === 'artifacts';
  const pageTitle = showPlaces && !showArtifacts
    ? 'Walk where the legends lived'
    : showArtifacts && !showPlaces
      ? 'What time could not erase'
      : 'Surviving Works of the Ancient World';
  const pageLabel = showPlaces && !showArtifacts
    ? 'PLACES'
    : showArtifacts && !showPlaces
      ? 'ARTIFACTS'
      : 'GALLERY OF ANTIQUITY';
  const pageIntro = showPlaces && !showArtifacts
    ? 'Temples, theatres, palaces, and royal tombs — places still standing where the myths unfolded.'
    : showArtifacts && !showPlaces
      ? 'Sculpture, bronze, and gold unearthed from sanctuaries, shipwrecks, and royal graves.'
      : 'The myths you\'ve been reading weren\'t only written down — they were carved, cast in bronze, and built into mountainsides. These are real surviving sculptures, temples, and tombs, photographed where they stand today.';

  // Close on Escape
  useEffect(() => {
    if (!active) return;
    const onKey = e => { if (e.key === 'Escape') setActive(null); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [active]);

  const openRandom = useCallback(() => {
    const items = showPlaces && showArtifacts ? GALLERY : showPlaces ? placesItems : artifactsItems;
    setActive(items[Math.floor(Math.random() * items.length)]);
  }, [showPlaces, showArtifacts]);

  return (
    <div className="page-surface">
      <PageHeader
        label={pageLabel}
        title={pageTitle}
        intro={pageIntro}
        image={THEME.delphi}
        light={true}
      >
        {subTabs}
      </PageHeader>

      <div className="section-night">
        <div className="gv-container">

          {/* Top action bar — Surprise Me */}
          <div className="gv-actions-bar">
            <button type="button" className="gv-btn-ghost" onClick={openRandom}>
              ✦ Surprise me
            </button>
          </div>

          {/* ── PLACES ──────────────────────────────────────────── */}
          {showPlaces && <section id="places" className="gv-section">
            <div className="gv-section-header">
              <span className="gv-section-label label">Places</span>
              <h2 className="gv-section-h2">Walk where the legends lived</h2>
              <p className="gv-section-intro">
                Temples, theatres, palaces, and royal tombs — places still standing where the myths unfolded.
              </p>
            </div>

            <div className="gv-grid">
              {placesItems.map((item, i) => (
                <GalleryCard key={item.id} item={item} delay={(i % 4) * 60} onOpen={setActive} />
              ))}
            </div>
          </section>}

          {/* ── ARTIFACTS ────────────────────────────────────────── */}
          {showArtifacts && <section id="artifacts" className="gv-section">
            <div className="gv-section-header">
              <span className="gv-section-label label">Artifacts</span>
              <h2 className="gv-section-h2">What time could not erase</h2>
              <p className="gv-section-intro">
                Sculpture, bronze, and gold unearthed from sanctuaries, shipwrecks, and royal graves.
              </p>
            </div>

            <div className="gv-grid">
              {artifactsItems.map((item, i) => (
                <GalleryCard key={item.id} item={item} delay={(i % 4) * 60} onOpen={setActive} />
              ))}
            </div>
          </section>}

          {/* ── Credits footer ──────────────────────────────────── */}
          <footer className="gv-credits">
            <span>
              Photography &amp; images courtesy of <strong>Wikimedia Commons</strong>, public domain &amp; Creative Commons contributors.
            </span>
            <span>
              Collections preserved at the Musée du Louvre, National Archaeological Museum Athens, Delphi Museum, and Vatican Museums.
            </span>
          </footer>

        </div>
      </div>

      {/* ── Lightbox ─────────────────────────────────────────────── */}
      {active && (
        <div
          className="gv-lightbox-overlay"
          onClick={() => setActive(null)}
          role="dialog"
          aria-modal="true"
          aria-label={active.title}
        >
          <div
            className="gv-lightbox-dialog"
            onClick={e => e.stopPropagation()}
          >
            <button
              type="button"
              className="gv-lightbox-close"
              onClick={() => setActive(null)}
              aria-label="Close"
            >
              &times;
            </button>

            <div className="gv-lightbox-img-wrap">
              <img
                src={active.image}
                alt={active.title}
                className="gv-lightbox-img"
              />
            </div>

            <div className="gv-lightbox-body">
              <h3 className="gv-lightbox-title">{active.title}</h3>

              <div className="gv-lightbox-meta">
                {active.greek && <span>{active.greek} &bull; </span>}
                <span>{active.kind}</span>
              </div>
              <div className="gv-lightbox-location">{active.location}</div>

              {/* Extended place fields */}
              {(active.date || active.architect || active.material) && (
                <dl className="gv-lightbox-specs">
                  {active.date && (
                    <div className="gv-spec-item">
                      <dt className="gv-spec-key">Date</dt>
                      <dd className="gv-spec-val">{active.date}</dd>
                    </div>
                  )}
                  {active.architect && (
                    <div className="gv-spec-item">
                      <dt className="gv-spec-key">Architect</dt>
                      <dd className="gv-spec-val">{active.architect}</dd>
                    </div>
                  )}
                  {active.material && (
                    <div className="gv-spec-item">
                      <dt className="gv-spec-key">Material</dt>
                      <dd className="gv-spec-val">{active.material}</dd>
                    </div>
                  )}
                </dl>
              )}

              <p className="gv-lightbox-blurb">{active.blurb}</p>

              {active.mythLink && (
                <div className="gv-lightbox-myth-link">
                  ✦ Connected myth: <span className="gv-lightbox-myth-name">{active.mythLink}</span>
                </div>
              )}

              <div className="gv-lightbox-credit">
                Photograph licensed under CC / Public Domain via Wikimedia Commons &bull; {active.location}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ── Card sub-component ────────────────────────────────────────── */
function GalleryCard({ item, delay, onOpen }) {
  return (
    <Reveal
      delay={delay}
      className="gv-card"
      onClick={() => onOpen(item)}
      role="button"
      tabIndex={0}
      onKeyDown={e => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onOpen(item);
        }
      }}
    >
      <div className="gv-card-img-wrap">
        <img src={item.image} alt={item.title} loading="lazy" className="gv-card-img" />
      </div>
      <div className="gv-card-body">
        <h3 className="gv-card-title">{item.title}</h3>
        <div className="gv-card-kind">{item.kind}</div>
        <div className="gv-card-location">{item.location}</div>
        <p className="gv-card-blurb">{item.blurb}</p>
      </div>
    </Reveal>
  );
}
