import React from 'react';
import PageHeader from '../components/PageHeader';
import Term from '../components/Term';
import Reveal from '../components/Reveal';
import { typeColor, themeColor } from '../utils/colors';
import { THEME } from '../data/theme';
import { THEME_GUIDE } from '../data/glossary';
import ThreadDivider from '../components/ThreadDivider';
import './PrimerView.css';

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

const SHAPE_STEPS = [
  'A character wants something',
  'They cross a line a god or fate has drawn',
  'There are consequences — often severe',
  'Something about the world is permanently explained',
];

const EXPLORE_CARDS = [
  {
    tab: 'storybook',
    title: 'Read a story',
    desc: 'Full, unabridged myths with every unfamiliar name explained as you go.',
  },
  {
    tab: 'oracle',
    title: 'Just ask',
    desc: 'Type a question in plain English — "who is Medusa?" — and get a direct answer.',
  },
  {
    tab: 'explore',
    title: 'See the family tree',
    desc: 'A map of how every god, hero, and monster connects to the others — plus real photos of the sculptures, temples, and tombs behind these stories.',
  },
];



export default function PrimerView({ onNavigate }) {
  const introText = (
    <>
      Greek mythology can look like a wall of unfamiliar names and family trees. It isn&apos;t.
      It&apos;s a set of stories people told each other around 3,000 years ago to make sense of love,
      death, pride, and power — and most of them still make perfect sense today. This page gives you
      everything you need in five minutes. Anywhere you see a{' '}
      <Term word="hubris">dotted underline</Term> like that one, hover or tap it for a quick definition.
    </>
  );

  return (
    <div className="page-surface">
      <PageHeader
        label="NO PRIOR KNOWLEDGE REQUIRED"
        title="New Here? Start With This."
        intro={introText}
        image={THEME.heroBg}
      />

      <div className="section-parchment">
        <div className="primer-content">
          <ThreadDivider />

        {/* 1. Who's who */}
        <Reveal as="section" className="primer-section">
          <div className="primer-section-header">
            <h2 className="primer-section-heading">
              <span className="label primer-step-num">01</span>
              Who&apos;s who
            </h2>
            <p className="primer-section-subtitle">
              Every character in this collection falls into one of four groups.
            </p>
          </div>

          <div className="primer-who-grid">
            {WHO.map((w, i) => {
              const borderTopColor = typeColor(w.colorKey);
              return (
                <Reveal
                  key={w.name}
                  delay={i * 80}
                  className="card primer-card"
                  style={{ borderTopColor, borderTopWidth: '3px', borderTopStyle: 'solid' }}
                >
                  <h3
                    className="primer-card-title"
                    style={{ color: borderTopColor }}
                  >
                    <Term word={w.glossaryKey}>{w.name}</Term>
                  </h3>
                  <p className="primer-card-body">{w.blurb}</p>
                </Reveal>
              );
            })}
          </div>
        </Reveal>

        <ThreadDivider />

        {/* 2. The Shape of Almost Every Myth */}
        <Reveal as="section" className="primer-section">
          <div className="primer-section-header">
            <h2 className="primer-section-heading">
              <span className="label primer-step-num">02</span>
              The shape of almost every myth
            </h2>
            <p className="primer-section-subtitle">
              Most of the stories in this archive follow a recognizable rhythm. Once you see it, every myth gets easier to read.
            </p>
          </div>

          <div className="primer-shape-flow">
            {SHAPE_STEPS.map((step, i) => (
              <div key={step} className="primer-shape-step-wrapper">
                <div className="card primer-shape-card">
                  <div className="primer-shape-num">Step 0{i + 1}</div>
                  <p className="primer-shape-text">{step}</p>
                </div>
                {i < SHAPE_STEPS.length - 1 && (
                  <span className="primer-shape-connector" aria-hidden="true">
                    →
                  </span>
                )}
              </div>
            ))}
          </div>

          <p className="primer-shape-note">
            That last step is the point: Greek myths are origin stories. They explain why the echo repeats
            your voice, why spiders spin webs, why laurel trees exist, why people fear the sea. Keep an eye
            out for it as you read.
          </p>
        </Reveal>

        <ThreadDivider />

        {/* 3. Themes */}
        <Reveal as="section" className="primer-section">
          <div className="primer-section-header">
            <h2 className="primer-section-heading">
              <span className="label primer-step-num">03</span>
              The threads running through this collection
            </h2>
            <p className="primer-section-subtitle">
              Chronicle tags every story with a dominant theme (and often a second and third). Here&apos;s what each one means in plain terms.
            </p>
          </div>

          <div className="primer-themes-grid">
            {Object.entries(THEME_GUIDE).map(([theme, desc], i) => {
              const borderTopColor = themeColor(theme);
              return (
                <Reveal
                  key={theme}
                  delay={i * 60}
                  className="card primer-card"
                  style={{ borderTopColor, borderTopWidth: '3px', borderTopStyle: 'solid' }}
                >
                  <h3
                    className="primer-card-title"
                    style={{ color: borderTopColor }}
                  >
                    {theme}
                  </h3>
                  <p className="primer-card-body">{desc}</p>
                </Reveal>
              );
            })}
          </div>
        </Reveal>

        <ThreadDivider />

        {/* 4. How to Explore Chronicle */}
        <Reveal as="section" className="primer-section">
          <div className="primer-section-header">
            <h2 className="primer-section-heading">
              <span className="label primer-step-num">04</span>
              How to explore Chronicle
            </h2>
            <p className="primer-section-subtitle">
              Four ways in — pick whichever matches how you like to learn.
            </p>
          </div>

          <div className="primer-explore-grid">
            {EXPLORE_CARDS.map((c, i) => (
              <Reveal
                key={c.tab}
                delay={i * 80}
                as="button"
                type="button"
                onClick={() => onNavigate && onNavigate(c.tab)}
                className="card primer-card primer-explore-btn"
                style={{ borderTopColor: 'var(--gold)', borderTopWidth: '3px', borderTopStyle: 'solid' }}
              >
                <h3 className="primer-card-title" style={{ color: 'var(--text-primary)' }}>
                  {c.title} →
                </h3>
                <p className="primer-card-body" style={{ color: 'var(--text-secondary)' }}>
                  {c.desc}
                </p>
              </Reveal>
            ))}
          </div>
        </Reveal>

        {/* Final CTA */}
        <Reveal className="primer-cta-wrap">
          <button
            type="button"
            onClick={() => onNavigate && onNavigate('storybook')}
            className="btn-dark primer-cta-btn"
          >
            I&apos;M READY — TAKE ME TO THE STORIES
          </button>
        </Reveal>
        </div>
      </div>
    </div>
  );
}
