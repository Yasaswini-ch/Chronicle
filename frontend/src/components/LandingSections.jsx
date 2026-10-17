import React from 'react';
import Reveal from './Reveal';
import SectionIcon from './SectionIcon';
import GreekKeyDivider from './GreekKeyDivider';
import { GALLERY } from '../data/gallery';
import { toRoman } from '../utils/roman';

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
    desc: 'Look up any figure, trace the family tree, spot recurring story patterns, test yourself with a quiz, and browse real sculptures and tombs.',
  },
];

const HIGHLIGHTS = [
  { tab: 'storybook', icon: 'scroll', title: '30 Unabridged Myths', desc: 'Not summaries — full retellings, each with its characters, themes, and a moral insight.' },
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

export default function LandingSections({ onNavigate }) {
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

    <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '56px 24px 0 24px' }}>
      <GreekKeyDivider />

      {/* A dramatic mid-page moment — a real statue, not an illustration */}
      <Reveal className="kleos-moment">
        <div className="kleos-portrait-wrap">
          <div className="kleos-portrait-glow" />
          <img src="/images/gallery/nike-samothrace.jpg" alt="The Winged Victory of Samothrace" className="kleos-portrait" />
        </div>
        <div className="kleos-moment-text">
          <div className="kleos-word">&kappa;&lambda;&#941;&omicron;&sigmaf;</div>
          <div className="kleos-gloss">(n.) kléos — the glory a story keeps alive after you&apos;re gone</div>
          <p style={{ color: 'var(--text-on-dark)', opacity: 0.85, fontSize: '0.95rem', lineHeight: 1.65, maxWidth: '440px' }}>
            It&apos;s the oldest reason anyone told these stories at all. Achilles traded a long quiet life
            for this. Three thousand years later, you&apos;re still reading his name — that&apos;s kléos
            working exactly as intended.
          </p>
        </div>
      </Reveal>

      <GreekKeyDivider />

      {/* What's inside */}
      <Reveal style={{ textAlign: 'center', marginBottom: '36px' }}>
        <Eyebrow index={2} label="What You'll Find" />
        <h2 style={{ fontSize: '2rem' }}>Built To Be Explored, Not Just Read</h2>
      </Reveal>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '18px', marginBottom: '20px' }}>
        {HIGHLIGHTS.map((h, i) => (
          <Reveal
            key={h.title}
            delay={i * 80}
            as="button"
            className="card"
            onClick={() => onNavigate(h.tab)}
            style={{ textAlign: 'left', cursor: 'pointer', borderTop: '3px solid var(--accent-gold)' }}
          >
            <div style={{ marginBottom: '10px' }}>
              <SectionIcon name={h.icon} />
            </div>
            <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1rem', color: 'var(--text-primary)', marginBottom: '6px' }}>
              {h.title}
            </div>
            <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.55 }}>{h.desc}</p>
          </Reveal>
        ))}
      </div>

      <GreekKeyDivider />

      {/* Gallery teaser */}
      <Reveal style={{ textAlign: 'center', marginBottom: '28px' }}>
        <Eyebrow index={3} label="Not Just Stories" />
        <h2 style={{ fontSize: '2rem', marginBottom: '10px' }}>Carved, Cast, And Still Standing</h2>
        <p style={{ color: 'var(--text-secondary)', maxWidth: '620px', margin: '0 auto', fontSize: '0.95rem', lineHeight: 1.6 }}>
          The myths you&apos;re about to read weren&apos;t only written down. Real statues, temples, and
          tombs survive today — photographed exactly where they stand.
        </p>
      </Reveal>

      <Reveal style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '14px', marginBottom: '24px' }}>
        {GALLERY.slice(0, 4).map((item) => (
          <div key={item.id} className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <div className="gallery-card-image-wrap" style={{ aspectRatio: '1 / 1' }}>
              <img src={item.image} alt={item.title} loading="lazy" className="gallery-card-image" />
            </div>
          </div>
        ))}
      </Reveal>

      <Reveal style={{ textAlign: 'center', marginBottom: '56px' }}>
        <button className="btn-secondary" onClick={() => onNavigate('explore')}>
          See The Full Gallery &rarr;
        </button>
      </Reveal>
      </div>

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
