import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Hero from '../components/home/Hero';
import Stories from '../components/home/Stories';
import FamilyTreeBand from '../components/home/FamilyTreeBand';
import OracleBand from '../components/home/OracleBand';
import Places from '../components/home/Places';
import Artifacts from '../components/home/Artifacts';
import KleosBand from '../components/home/KleosBand';
import FooterCta from '../components/home/FooterCta';
import CursorSparkles from '../components/home/CursorSparkles';
import './OpeningView.css';
import '../components/home/SceneMorph.css';

gsap.registerPlugin(ScrollTrigger);

export default function OpeningView({
  onNavigate,
  onAskOracle,
  totalMyths,
  totalWords,
  themeCount,
  characterCount,
  myths,
  onSelectMyth,
}) {
  const containerRef = useRef(null);
  const heroRef = useRef(null);
  const storiesRef = useRef(null);
  const familyRef = useRef(null);
  const oracleRef = useRef(null);
  const placesRef = useRef(null);
  const artifactsRef = useRef(null);
  const kleosRef = useRef(null);
  const footerCtaRef = useRef(null);

  useEffect(() => {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return;

    const ctx = gsap.context(() => {
      // 1. Hero -> Stories Cinematic Camera & Cloud Drift
      // Moves camera toward the goddess hand and drifts clouds / petals downward
      const heroBg = heroRef.current?.querySelector('.hero-section--exact');
      const clouds = heroRef.current?.querySelector('.morph-hero-clouds');

      if (heroRef.current && heroBg) {
        gsap.to(heroBg, {
          backgroundPosition: 'center 42%',
          scrollTrigger: {
            trigger: heroRef.current,
            start: 'top top',
            end: 'bottom top',
            scrub: 0.8,
          },
        });
      }

      if (clouds) {
        gsap.to(clouds, {
          y: -60,
          opacity: 0.2,
          scrollTrigger: {
            trigger: heroRef.current,
            start: 'center top',
            end: 'bottom top',
            scrub: 0.8,
          },
        });
      }

      // 2. Stories -> Family Tree: Parchment melts into celestial star field
      if (storiesRef.current && familyRef.current) {
        const storyCards = storiesRef.current.querySelectorAll('.story-portrait-card');
        gsap.fromTo(
          storyCards,
          { y: 0 },
          {
            y: -25,
            stagger: 0.05,
            scrollTrigger: {
              trigger: storiesRef.current,
              start: 'bottom 85%',
              end: 'bottom 20%',
              scrub: 0.7,
            },
          }
        );
      }

      // 3. Family Tree -> Oracle: Stars converge into Oracle Sun, temple columns emerge
      if (familyRef.current && oracleRef.current) {
        const oracleSun = oracleRef.current.querySelector('.oracle-sun-wrap');
        if (oracleSun) {
          gsap.fromTo(
            oracleSun,
            { scale: 0.85, opacity: 0.6, rotation: -20 },
            {
              scale: 1,
              opacity: 1,
              rotation: 0,
              scrollTrigger: {
                trigger: oracleRef.current,
                start: 'top 85%',
                end: 'top 30%',
                scrub: 0.8,
              },
            }
          );
        }
      }

      // 4. Oracle -> Places: Temple incense dissolves into Aegean sea mist & distant island
      if (oracleRef.current && placesRef.current) {
        const islandBg = placesRef.current.querySelector('.places-island-bg');
        if (islandBg) {
          gsap.fromTo(
            islandBg,
            { opacity: 0.3, x: 40 },
            {
              opacity: 0.9,
              x: 0,
              scrollTrigger: {
                trigger: placesRef.current,
                start: 'top 85%',
                end: 'top 35%',
                scrub: 0.8,
              },
            }
          );
        }
      }

      // 5. Places -> Artifacts: Sunlit landscape transforms into carved sculpture shadows
      if (placesRef.current && artifactsRef.current) {
        const artifactCards = artifactsRef.current.querySelectorAll('.artifact-card');
        gsap.fromTo(
          artifactCards,
          { opacity: 0.8, y: 30 },
          {
            opacity: 1,
            y: 0,
            stagger: 0.06,
            scrollTrigger: {
              trigger: artifactsRef.current,
              start: 'top 85%',
              end: 'top 40%',
              scrub: 0.8,
            },
          }
        );
      }

      // 6. Kleos & Artifacts -> Footer CTA: Horizon return & goddess welcoming
      if (footerCtaRef.current) {
        const footerGoddess = footerCtaRef.current.querySelector('.footer-cta-goddess-wrap');
        const footerStar = footerCtaRef.current.querySelector('.footer-cta-star');

        if (footerGoddess) {
          gsap.fromTo(
            footerGoddess,
            { y: 50, opacity: 0.7 },
            {
              y: 0,
              opacity: 1,
              scrollTrigger: {
                trigger: footerCtaRef.current,
                start: 'top 80%',
                end: 'center center',
                scrub: 0.8,
              },
            }
          );
        }

        if (footerStar) {
          gsap.fromTo(
            footerStar,
            { scale: 0.6, rotation: -45 },
            {
              scale: 1.1,
              rotation: 0,
              scrollTrigger: {
                trigger: footerCtaRef.current,
                start: 'top 75%',
                end: 'center center',
                scrub: 0.6,
              },
            }
          );
        }
      }
    }, containerRef);

    return () => ctx.revert();
  }, []);

  return (
    <div ref={containerRef} className="opening-page">
      {/* Delicate Cursor Movement Sparkles */}
      <CursorSparkles />

      {/* 1. Hero Section with Clouds & Golden Particles */}
      <div ref={heroRef} className="scene-morph-wrap">
        <Hero
          onNavigate={onNavigate}
          totalMyths={totalMyths}
          characterCount={characterCount}
          themeCount={themeCount}
          totalWords={totalWords}
        />

        {/* Ambient drift clouds transitioning to Stories */}
        <div className="morph-hero-clouds" aria-hidden="true" />

        {/* Golden floating particles in the atmosphere */}
        <div className="morph-particles-emitter" aria-hidden="true">
          {Array.from({ length: 14 }, (_, i) => (
            <span
              key={i}
              className="morph-particle"
              style={{
                width: `${4 + (i % 4) * 2}px`,
                height: `${4 + (i % 4) * 2}px`,
                top: `${15 + (i * 6)}%`,
                left: `${10 + ((i * 17) % 80)}%`,
                animationDelay: `${(i * 0.45).toFixed(2)}s`,
                animationDuration: `${6 + (i % 3) * 2}s`,
              }}
            />
          ))}
        </div>
      </div>

      {/* 2. Stories Section */}
      <div ref={storiesRef} className="scene-morph-wrap">
        <Stories
          myths={myths}
          onSelectMyth={onSelectMyth}
          onNavigate={onNavigate}
        />

        {/* Dissolve into Celestial Starry Navy */}
        <div className="morph-parchment-to-stars" aria-hidden="true" />
      </div>

      {/* 3. Family Tree Section */}
      <div ref={familyRef} className="scene-morph-wrap">
        <FamilyTreeBand onNavigate={onNavigate} />

        {/* Transition into Oracle temple twilight */}
        <div className="morph-stars-to-temple" aria-hidden="true" />
      </div>

      {/* 4. Oracle Section */}
      <div ref={oracleRef} className="scene-morph-wrap">
        <div className="morph-temple-smoke" aria-hidden="true" />
        <OracleBand
          onAskOracle={onAskOracle}
          onNavigate={onNavigate}
        />

        {/* Temple dissolves into Aegean Sea mist */}
        <div className="morph-oracle-to-places" aria-hidden="true" />
      </div>

      {/* 5. Places Section */}
      <div ref={placesRef} className="scene-morph-wrap">
        <div className="morph-sea-mist" aria-hidden="true" />
        <Places onNavigate={onNavigate} />

        {/* Sunlit coastline dissolves into museum artifacts */}
        <div className="morph-places-to-artifacts" aria-hidden="true" />
      </div>

      {/* 6. Artifacts Section */}
      <div ref={artifactsRef} className="scene-morph-wrap">
        <Artifacts onNavigate={onNavigate} />
      </div>

      {/* 7. Kleos Band */}
      <div ref={kleosRef} className="scene-morph-wrap">
        <KleosBand />

        {/* Artifacts & Kleos dissolve into Sunset Coastline */}
        <div className="morph-artifacts-to-footer" aria-hidden="true" />
      </div>

      {/* 8. Footer CTA: Horizon return */}
      <div ref={footerCtaRef} className="scene-morph-wrap">
        <FooterCta onNavigate={onNavigate} />
      </div>
    </div>
  );
}
