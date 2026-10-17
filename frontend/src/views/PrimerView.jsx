import React from 'react';
import Term from '../components/Term';
import Reveal from '../components/Reveal';
import GreekKeyDivider from '../components/GreekKeyDivider';
import SectionIcon from '../components/SectionIcon';
import ColumnFrame from '../components/ColumnFrame';
import { typeColor } from '../utils/colors';
import { THEME_GUIDE } from '../data/glossary';

const WHO = [
  {
    name: 'The Titans',
    glossaryKey: 'titan',
    colorKey: 'titan',
    blurb:
      'The oldest generation of gods — vast, primal beings who ruled before anyone else existed. Zeus and his brothers and sisters eventually overthrew them in a ten-year war.',
  },
  {
    name: 'The Olympians',
    glossaryKey: 'olympian',
    colorKey: 'god',
    blurb:
      'The twelve gods who rule afterward, named for their home on Mount Olympus. Zeus (sky), Hera (marriage), Athena (wisdom), Poseidon (sea), Aphrodite (love), Ares (war), and others each govern one piece of life.',
  },
  {
    name: 'Mortals',
    glossaryKey: 'mortal',
    colorKey: 'mortal',
    blurb:
      'Humans — kings, inventors, warriors, ordinary people. They can die, which is exactly what makes their stories against the gods so dramatic.',
  },
  {
    name: 'Creatures',
    glossaryKey: 'creature',
    colorKey: 'creature',
    blurb:
      'Monsters and hybrid beings that are neither god nor human: the Sphinx, the Cyclops, Pegasus the winged horse, the Minotaur in his maze.',
  },
];

export default function PrimerView({ onNavigate }) {
  return (
    <div className="primer-vista-bg" style={{ maxWidth: '920px', margin: '0 auto' }}>
      <Reveal className="primer-gateway">
        <img src="/images/decor/statues-flanking-arch.png" alt="Two classical statues flanking a stone archway" />
      </Reveal>

      <Reveal style={{ marginBottom: '32px' }}>
        <ColumnFrame color="var(--accent-gold)">
        <div style={{ padding: '4px 20px 16px 20px' }}>
        <div
          style={{
            fontSize: '0.72rem',
            letterSpacing: '3px',
            color: 'var(--accent-gold)',
            textTransform: 'uppercase',
            marginBottom: '10px',
          }}
        >
          No Prior Knowledge Required
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '10px' }}>
          <SectionIcon name="laurel" size={34} />
          <h1 style={{ fontSize: '2rem', margin: 0 }}>New Here? Start With This.</h1>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.02rem', lineHeight: 1.7, maxWidth: '720px' }}>
          Greek mythology can look like a wall of unfamiliar names and family trees. It isn&apos;t.
          It&apos;s a set of stories people told each other around 3,000 years ago to make sense of love,
          death, pride, and power — and most of them still make perfect sense today. This page gives you
          everything you need in five minutes. Anywhere you see a <Term word="hubris">dotted underline</Term>{' '}
          like that one, hover or tap it for a quick definition.
        </p>
        </div>
        </ColumnFrame>
      </Reveal>

      <GreekKeyDivider />

      {/* Who's who */}
      <Reveal as="section" style={{ marginBottom: '40px' }}>
        <h2 style={{ fontSize: '1.3rem', marginBottom: '6px' }}>1. Who&apos;s Who</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '18px', fontSize: '0.95rem' }}>
          Every character in this collection falls into one of four groups.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '14px' }}>
          {WHO.map((w, i) => (
            <Reveal key={w.name} delay={i * 80} className="card" style={{ borderTop: `4px solid ${typeColor(w.colorKey)}` }}>
              <div
                style={{
                  fontFamily: 'var(--font-heading)',
                  fontSize: '1.05rem',
                  color: typeColor(w.colorKey),
                  marginBottom: '8px',
                }}
              >
                <Term word={w.glossaryKey}>{w.name}</Term>
              </div>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-primary)', lineHeight: 1.6 }}>{w.blurb}</p>
            </Reveal>
          ))}
        </div>
      </Reveal>

      <GreekKeyDivider />

      {/* The one plot pattern */}
      <Reveal as="section" style={{ marginBottom: '40px' }}>
        <h2 style={{ fontSize: '1.3rem', marginBottom: '6px' }}>2. The Shape of Almost Every Myth</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '18px', fontSize: '0.95rem' }}>
          Most of the stories in this archive follow a recognizable rhythm. Once you see it, every myth gets easier to read.
        </p>
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            gap: '10px',
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            padding: '20px',
          }}
        >
          {['A character wants something', 'They cross a line a god or fate has drawn', 'There are consequences — often severe', 'Something about the world is permanently explained'].map(
            (step, i, arr) => (
              <React.Fragment key={step}>
                <div
                  style={{
                    flex: '1 1 180px',
                    background: 'var(--bg-surface-elevated)',
                    border: '1px solid var(--border-subtle)',
                    padding: '12px 14px',
                    fontSize: '0.85rem',
                    color: 'var(--text-primary)',
                  }}
                >
                  <span style={{ color: 'var(--accent-gold)', fontFamily: 'var(--font-heading)', marginRight: '6px' }}>
                    {i + 1}.
                  </span>
                  {step}
                </div>
                {i < arr.length - 1 && (
                  <span style={{ color: 'var(--text-muted)', fontSize: '1.1rem' }}>&rarr;</span>
                )}
              </React.Fragment>
            )
          )}
        </div>
        <p style={{ color: 'var(--text-secondary)', marginTop: '14px', fontSize: '0.9rem', lineHeight: 1.6 }}>
          That last step is the point: Greek myths are origin stories. They explain why the echo repeats
          your voice, why spiders spin webs, why laurel trees exist, why people fear the sea. Keep an eye
          out for it as you read.
        </p>
      </Reveal>

      <GreekKeyDivider />

      {/* Themes */}
      <Reveal as="section" style={{ marginBottom: '40px' }}>
        <h2 style={{ fontSize: '1.3rem', marginBottom: '6px' }}>3. The Threads Running Through This Collection</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '18px', fontSize: '0.95rem' }}>
          Chronicle tags every story with a dominant theme (and often a second and third). Here&apos;s what each one means in plain terms.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '12px' }}>
          {Object.entries(THEME_GUIDE).map(([theme, desc], i) => (
            <Reveal
              key={theme}
              delay={i * 70}
              style={{ borderLeft: '3px solid var(--accent-gold)', background: 'var(--bg-surface)', padding: '12px 16px' }}
            >
              <div style={{ textTransform: 'uppercase', letterSpacing: '1px', fontSize: '0.85rem', color: 'var(--accent-gold)', marginBottom: '4px' }}>
                {theme}
              </div>
              <div style={{ fontSize: '0.88rem', color: 'var(--text-primary)', lineHeight: 1.5 }}>{desc}</div>
            </Reveal>
          ))}
        </div>
      </Reveal>

      <GreekKeyDivider />

      {/* How to use the site */}
      <Reveal as="section" style={{ marginBottom: '48px' }}>
        <h2 style={{ fontSize: '1.3rem', marginBottom: '6px' }}>4. How To Explore Chronicle</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '18px', fontSize: '0.95rem' }}>
          Four ways in — pick whichever matches how you like to learn.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '14px' }}>
          {[
            { tab: 'storybook', title: 'Read a Story', desc: 'Full, unabridged myths with every unfamiliar name explained as you go.' },
            { tab: 'oracle', title: 'Just Ask', desc: 'Type a question in plain English — "who is Medusa?" — and get a direct answer.' },
            { tab: 'explore', title: 'See the Family Tree', desc: 'A map of how every god, hero, and monster connects to the others — plus real photos of the sculptures, temples, and tombs behind these stories.' },
          ].map((c, i) => (
            <Reveal key={c.tab} delay={i * 80} as="button"
              onClick={() => onNavigate && onNavigate(c.tab)}
              className="card"
              style={{ textAlign: 'left', cursor: 'pointer', border: '1px solid var(--border-subtle)' }}
            >
              <div style={{ fontFamily: 'var(--font-heading)', color: 'var(--text-primary)', fontSize: '1rem', marginBottom: '6px' }}>
                {c.title} &rarr;
              </div>
              <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{c.desc}</div>
            </Reveal>
          ))}
        </div>
      </Reveal>

      <Reveal style={{ textAlign: 'center', paddingBottom: '24px' }}>
        <button onClick={() => onNavigate && onNavigate('storybook')} className="btn-primary">
          I&apos;m Ready — Take Me To The Stories
        </button>
      </Reveal>
    </div>
  );
}
