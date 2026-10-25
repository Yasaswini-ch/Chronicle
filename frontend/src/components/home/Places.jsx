import React from 'react';
import { THEME } from '../../data/theme';
import Reveal from '../Reveal';
import './Places.css';

const PLACES_CARDS = [
  {
    key: 'delphi',
    title: 'DELPHI',
    image: THEME.delphi,
    region: 'Mount Parnassus',
    tagline: 'The navel of the earth and the sanctuary of Apollo’s oracle.',
  },
  {
    key: 'athens',
    title: 'ATHENS',
    image: THEME.athens,
    region: 'Attica Peninsula',
    tagline: 'Citadel of Athena, where wisdom and democracy rose from stone.',
  },
  {
    key: 'crete',
    title: 'CRETE',
    image: THEME.crete,
    region: 'Aegean Sea',
    tagline: 'Island of King Minos, Daedalus, and the winding Labyrinth.',
  },
];

export default function Places({ onNavigate }) {
  const handleNavigateToGallery = (e) => {
    e.preventDefault();
    if (onNavigate) {
      onNavigate('explore/gallery/places');
    } else {
      window.location.hash = '#/explore/gallery/places';
    }
  };

  return (
    <section id="places" className="places-section">
      <div className="places-container">
        {/* Editorial Journal Header & Atmospheric Panorama Anchor */}
        <div className="places-spread-anchor">
          {/* Panoramic wide vista blending softly into ivory parchment */}
          <div className="places-island-bg places-panorama-frame" aria-hidden="true">
            <img
              src={THEME.placesIsland}
              alt=""
              className="places-island-img places-panorama-img"
              loading="lazy"
            />
            {/* Subtle editorial vignette overlay */}
            <div className="places-panorama-overlay" />
          </div>

          {/* Editorial Travel Journal Title & Call to Action overlaying / anchoring the vista */}
          <div className="places-journal-header">
            <div className="label places-label">ANCIENT GEOGRAPHY</div>
            <h2 className="places-title">Walk where the legends lived</h2>
            <p className="places-description">
              The myths weren’t set in distant imaginary realms, but across the rugged cliffs,
              sunlit sanctuaries, and olive groves of the Mediterranean. Step through the physical
              surviving stones where gods were worshipped and heroes walked.
            </p>
            <div className="places-header-action">
              <a
                href="#/explore/gallery/places"
                className="btn-dark"
                onClick={handleNavigateToGallery}
              >
                EXPLORE THE PLACES
              </a>
            </div>
          </div>
        </div>

        {/* Destination Cards: Delphi, Athens, Crete */}
        <div className="places-cards-grid">
          {PLACES_CARDS.map((place, index) => (
            <Reveal
              key={place.key}
              delay={(index + 1) * 100}
              className="place-card-wrapper"
            >
              <a
                href="#/explore/gallery/places"
                className="place-landscape-card"
                onClick={handleNavigateToGallery}
                aria-label={`Explore ${place.title}`}
              >
                <div className="place-card-media">
                  <img
                    src={place.image}
                    alt={place.title}
                    className="place-card-img"
                    loading="lazy"
                  />
                  <div className="place-card-media-badge">{place.region}</div>
                </div>
                <div className="place-card-content">
                  <div className="place-card-title-row">
                    <span className="place-card-title">{place.title}</span>
                    <span className="place-card-arrow" aria-hidden="true">→</span>
                  </div>
                  <p className="place-card-tagline">{place.tagline}</p>
                </div>
              </a>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
