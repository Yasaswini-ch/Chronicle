import React, { useState } from 'react';
import Reveal from '../components/Reveal';
import SectionIcon from '../components/SectionIcon';
import { GALLERY } from '../data/gallery';

export default function GalleryView() {
  const [active, setActive] = useState(null);
  const thumbs = GALLERY.slice(0, 9);
  const scrollToGrid = () => document.getElementById('gallery-full-grid')?.scrollIntoView({ behavior: 'smooth' });

  return (
    <div>
      <Reveal className="card gallery-hero" style={{ marginBottom: '32px', padding: 0, overflow: 'hidden' }}>
        <div className="gallery-hero-text gallery-hero-text-vista">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '10px' }}>
            <SectionIcon name="column" />
            <h2 style={{ fontSize: '1.6rem', margin: 0 }}>Gallery of Antiquity</h2>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: 1.6 }}>
            The myths you&apos;ve been reading weren&apos;t only written down — they were carved, cast in
            bronze, and built into mountainsides. These are real surviving sculptures, temples, and tombs,
            photographed where they stand today.
          </p>
          <div style={{ display: 'flex', gap: '10px', marginTop: '18px', flexWrap: 'wrap' }}>
            <button className="btn-primary" onClick={scrollToGrid}>Browse All {GALLERY.length}</button>
            <button
              className="btn-secondary"
              onClick={() => setActive(GALLERY[Math.floor(Math.random() * GALLERY.length)])}
            >
              Surprise Me
            </button>
          </div>
        </div>
        <div className="gallery-hero-grid">
          {thumbs.map((item) => (
            <button
              key={item.id}
              className="gallery-hero-thumb"
              onClick={() => setActive(item)}
              aria-label={item.title}
            >
              <img src={item.image} alt={item.title} loading="lazy" />
            </button>
          ))}
        </div>
      </Reveal>

      <div id="gallery-full-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '18px' }}>
        {GALLERY.map((item, i) => (
          <Reveal
            key={item.id}
            delay={(i % 4) * 70}
            className="card gallery-card"
            style={{ padding: 0, cursor: 'pointer', overflow: 'hidden' }}
            onClick={() => setActive(item)}
          >
            <div className="gallery-card-image-wrap">
              <img src={item.image} alt={item.title} loading="lazy" className="gallery-card-image" />
            </div>
            <div style={{ padding: '14px 16px' }}>
              <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1rem', color: 'var(--text-primary)', marginBottom: '2px' }}>
                {item.title}
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--accent-gold)', fontStyle: 'italic' }}>{item.kind}</div>
            </div>
          </Reveal>
        ))}
      </div>

      {active && (
        <div className="gallery-lightbox" onClick={() => setActive(null)}>
          <div className="gallery-lightbox-panel" onClick={(e) => e.stopPropagation()}>
            <button className="gallery-lightbox-close" onClick={() => setActive(null)} aria-label="Close">
              &times;
            </button>
            <img src={active.image} alt={active.title} className="gallery-lightbox-image" />
            <div className="gallery-lightbox-info">
              <h3 style={{ fontSize: '1.3rem', marginBottom: '2px' }}>{active.title}</h3>
              <div style={{ fontSize: '0.85rem', color: 'var(--accent-gold)', fontStyle: 'italic', marginBottom: '2px' }}>
                {active.greek} &bull; {active.kind}
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '12px' }}>
                {active.location}
              </div>
              <p style={{ fontSize: '0.95rem', lineHeight: 1.6, color: 'var(--text-primary)' }}>{active.blurb}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
