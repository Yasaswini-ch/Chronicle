import React from 'react';
import Reveal from '../Reveal';
import './KleosBand.css';

export default function KleosBand() {
  return (
    <section id="kleos" className="section-night kleos-band" aria-label="Kléos">
      <div className="kleos-container">
        <Reveal className="kleos-arch" delay={100}>
          <img
            src="/images/gallery/nike-samothrace.jpg"
            alt="The Winged Victory of Samothrace"
            className="kleos-arch-img"
            loading="lazy"
          />
        </Reveal>

        <Reveal className="kleos-content" delay={200}>
          <h2 className="kleos-word" lang="grc">κλέος</h2>
          <p className="kleos-gloss">(n.) kléos — the glory a story keeps alive after you're gone</p>
          <p className="kleos-body">
            It's the oldest reason anyone told these stories at all. Achilles traded a long quiet life
            for this. Three thousand years later, you're still reading his name — that's kléos
            working exactly as intended.
          </p>
        </Reveal>
      </div>
    </section>
  );
}
