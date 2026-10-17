import React from 'react';
import Reveal from './Reveal';
import SectionIcon from './SectionIcon';
import { GALLERY } from '../data/gallery';
import { toRoman } from '../utils/roman';
import './WorldSection.css';

const FLOW = [
  {
    tab: 'primer',
    icon: 'laurel',
    title: 'Start Here',
    desc: 'A five-minute primer on who’s who — Titans, Olympians, mortals, creatures — and the handful of themes that recur across every story.',
  },
  {
    tab: 'storybook',
    icon: 'scroll',
    title: 'Read The Myths',
    desc: 'Over a hundred complete myths, told in full. Every unfamiliar name is quietly explained the moment it appears.',
  },
  {
    tab: 'oracle',
    icon: 'eye',
    title: 'Ask The Oracle',
    desc: 'Type a question in plain English. The Oracle answers, remembers what you just asked, and points you to the full story.',
  },
  {
    tab: 'explore',
    icon: 'tree',
    title: 'Explore',
    desc: 'Look up any figure, trace the family tree, spot recurring story patterns, and browse real sculptures and tombs.',
  },
];

const highlightsFor = (totalMyths) => [
  { tab: 'storybook', icon: 'scroll', title: `${totalMyths || 'Over a hundred'} Complete Myths`, desc: 'Not summaries — full retellings, each with its characters and themes.' },
  { tab: 'explore', icon: 'tree', title: 'One Living Family Tree', desc: 'Every god, hero, and monster the myths connect, drawn as a single branching diagram you can click through.' },
  { tab: 'oracle', icon: 'eye', title: 'An Oracle That Remembers', desc: 'Ask a follow-up — "explain it," "tell me more" — and it knows exactly what you meant.' },
  { tab: 'explore', icon: 'column', title: 'Real Sculptures & Tombs', desc: 'Photographs of the actual artifacts behind the stories: the Mask of Agamemnon, the Parthenon, and more.' },
];

function Eyebrow({ index, label }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0', marginBottom: '10px' }}>
      <span className="roman-marker">{toRoman(index)}</span>
      <span style={{ fontSize: '0.72rem', letterSpacing: '3px', textTransform: 'uppercase', color: 'var(--accent-gold)' }}>
        {label}
      </span>
    </div>
  );
}

export default function LandingSections({ onNavigate, totalMyths }) {
  const highlights = highlightsFor(totalMyths);
  // The gallery lives in the Explore tab; deep-link straight to it
  const openGallery = () => { window.location.hash = '/explore/gallery'; };
  return (
    <>
    <section className="steps-band" aria-labelledby="steps-heading">
      <img src="/images/hero/terrace-dawn.jpg" alt="" aria-hidden="true" width="1672" height="941" loading="lazy" className="steps-band-art" />
      <div className="steps-band-inner">
      {/* How it works */}
      <Reveal style={{ textAlign: 'center', marginBottom: '36px' }}>
        <Eyebrow index={1} label="How Chronicle Works" />
        <h2 id="steps-heading" style={{ fontSize: '2rem' }}>Four Steps, No Particular Order</h2>
      </Reveal>

      <div className="steps-grid">
        {FLOW.map((step, i) => (
          <Reveal
            key={step.tab}
            delay={i * 90}
            as="button"
            className="card"
            onClick={() => onNavigate(step.tab)}
            style={{ textAlign: 'left', cursor: 'pointer' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
              <SectionIcon name={step.icon} />
              <span className="roman-marker" style={{ margin: 0 }}>{toRoman(i + 1)}</span>
            </div>
            <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1rem', color: 'var(--text-primary)', marginBottom: '6px' }}>
              {step.title}
            </div>
            <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.55 }}>{step.desc}</p>
          </Reveal>
        ))}
      </div>

      </div>
    </section>

    <section className="world" aria-label="What Chronicle offers">
      {/* One continuous landscape that stays in view while the content scrolls over it */}
      <div className="world-art" aria-hidden="true">
        <img src="/images/hero/kleos-bg.jpg" alt="" width="1915" height="821" loading="lazy" />
      </div>

      <div className="world-panel">
        <div className="world-panel-inner">
          <Reveal className="world-intro">
            <figure className="world-arch">
              <img src="/images/gallery/nike-samothrace.jpg" alt="The Winged Victory of Samothrace" loading="lazy" />
            </figure>
            <div className="world-intro-text">
              <h2 className="world-kleos" lang="grc">&kappa;&lambda;&#941;&omicron;&sigmaf;</h2>
              <p className="world-gloss">(n.) kléos — the glory a story keeps alive after you&apos;re gone</p>
              <p className="world-body">
                It&apos;s the oldest reason anyone told these stories at all. Achilles traded a long quiet life
                for this. Three thousand years later, you&apos;re still reading his name — that&apos;s kléos
                working exactly as intended.
              </p>
            </div>
          </Reveal>

          <div className="world-rule" aria-hidden="true"><span /></div>

          <section aria-labelledby="world-features">
            <Reveal className="world-head">
              <div className="world-eyebrow">More than stories</div>
              <h2 id="world-features">Built To Be Explored, Not Just Read</h2>
            </Reveal>
            <div className="world-cards">
              {highlights.map((h, i) => (
                <Reveal
                  key={h.title}
                  delay={i * 80}
                  as="button"
                  type="button"
                  className="world-card"
                  onClick={() => onNavigate(h.tab)}
                >
                  <span className="world-card-icon"><SectionIcon name={h.icon} /></span>
                  <h3>{h.title}</h3>
                  <p>{h.desc}</p>
                </Reveal>
              ))}
            </div>
          </section>

          <div className="world-rule" aria-hidden="true"><span /></div>

          <section aria-labelledby="world-gallery">
            <Reveal className="world-head">
              <div className="world-eyebrow">See the world behind them</div>
              <h2 id="world-gallery">Carved, Cast, And Still Standing</h2>
              <p>
                The myths you&apos;re about to read weren&apos;t only written down. Real statues, temples, and
                tombs survive today — photographed exactly where they stand.
              </p>
            </Reveal>
            <Reveal className="world-gallery">
              {GALLERY.slice(0, 4).map((item) => (
                <button
                  type="button"
                  key={item.id}
                  className="world-tile"
                  onClick={openGallery}
                  aria-label={`${item.title}, ${item.location}. Open the gallery`}
                >
                  <span className="world-tile-img">
                    <img src={item.image} alt={item.title} loading="lazy" />
                  </span>
                  <span className="world-tile-cap">
                    <strong>{item.title}</strong>
                    <small>{item.location}</small>
                  </span>
                </button>
              ))}
            </Reveal>
            <div className="world-cta">
              <button type="button" className="world-button" onClick={openGallery}>
                See the full gallery <span aria-hidden="true">&rarr;</span>
              </button>
            </div>
          </section>
        </div>
      </div>
    </section>

      {/* Closing CTA: the sunset terrace, with the call to action on the open sky */}
      <section className="closing-band" aria-labelledby="closing-heading">
        <img src="/images/hero/sunset-terrace.jpg" alt="" aria-hidden="true" width="1672" height="941" loading="lazy" className="closing-band-art" />
        <div className="closing-band-inner">
          <h2 id="closing-heading" style={{ fontSize: '2rem', marginBottom: '10px' }}>Ready When You Are</h2>
          <p style={{ marginBottom: '24px' }}>
            No account, no prior knowledge, no homework.
          </p>
          <button className="btn-primary kleos-footer-cta" onClick={() => onNavigate('primer')}>
            Begin Reading
          </button>
        </div>
      </section>
    </>
  );
}
