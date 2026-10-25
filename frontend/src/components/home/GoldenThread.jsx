import React, { useEffect, useRef, useState, useId } from 'react';
import './GoldenThread.css';

/**
 * Catmull-Rom to Cubic Bezier curve chain generator.
 * Produces silky-smooth, continuous curves with zero sharp kinks.
 */
function buildSmoothCubicBezier(points) {
  if (points.length < 2) return '';
  let d = `M ${points[0].x.toFixed(1)} ${points[0].y.toFixed(1)}`;
  for (let i = 0; i < points.length - 1; i++) {
    const p0 = i > 0 ? points[i - 1] : points[i];
    const p1 = points[i];
    const p2 = points[i + 1];
    const p3 = i < points.length - 2 ? points[i + 2] : p2;

    const cp1x = p1.x + (p2.x - p0.x) / 6;
    const cp1y = p1.y + (p2.y - p0.y) / 6;
    const cp2x = p2.x - (p3.x - p1.x) / 6;
    const cp2y = p2.y - (p3.y - p1.y) / 6;

    d += ` C ${cp1x.toFixed(1)} ${cp1y.toFixed(1)}, ${cp2x.toFixed(1)} ${cp2y.toFixed(1)}, ${p2.x.toFixed(1)} ${p2.y.toFixed(1)}`;
  }
  return d;
}

const STAR_FRACTIONS = [0.18, 0.38, 0.56, 0.74, 0.90];

export default function GoldenThread({ containerRef }) {
  const svgRef = useRef(null);
  const pathRef = useRef(null);
  const [pathD, setPathD] = useState('');
  const [viewSize, setViewSize] = useState({ width: 1440, height: 6000 });
  const [scrollProgress, setScrollProgress] = useState(0);
  const [headPos, setHeadPos] = useState({ x: 0, y: 0 });
  const [stars, setStars] = useState([]);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  const uid = useId().replace(/:/g, '');
  const gradId = `threadGrad-${uid}`;
  const glowId = `threadGlow-${uid}`;
  const headGlowId = `headGlow-${uid}`;

  // Check prefers-reduced-motion
  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mq.matches);
    const handler = (e) => setPrefersReducedMotion(e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);

  // Measure section positions and generate smooth Bezier path
  const measureAndBuildPath = () => {
    const container = containerRef?.current;
    if (!container) return;

    const containerRect = container.getBoundingClientRect();
    const width = container.clientWidth || window.innerWidth;
    const height = container.scrollHeight;
    setViewSize({ width, height });

    // Helper to get element center / offset relative to container
    const getPos = (el) => {
      if (!el) return null;
      const rect = el.getBoundingClientRect();
      return {
        x: rect.left - containerRect.left + rect.width / 2,
        y: rect.top - containerRect.top + rect.height / 2,
        top: rect.top - containerRect.top,
        bottom: rect.bottom - containerRect.top,
        left: rect.left - containerRect.left,
        right: rect.right - containerRect.left,
        width: rect.width,
        height: rect.height,
      };
    };

    // 1. Hero Section (#hero)
    const heroEl = document.getElementById('hero');
    const heroTop = heroEl ? heroEl.offsetTop : 0;
    const heroHeight = heroEl ? heroEl.offsetHeight : 900;
    const goddessWrap = heroEl?.querySelector('.hero-figure-wrap--centered');
    const goddessPos = getPos(goddessWrap);

    // Starts near the goddess's outstretched hand in the hero
    const pStart = {
      x: goddessPos ? goddessPos.left + goddessPos.width * 0.52 : width * 0.58,
      y: goddessPos ? goddessPos.top + goddessPos.height * 0.44 : heroTop + heroHeight * 0.48,
    };

    // Transition down towards bottom of Hero
    const pHeroExit = {
      x: width * 0.42,
      y: heroTop + heroHeight * 0.92,
    };

    // 2. Stories Section (#stories)
    const storiesEl = document.getElementById('stories');
    const storiesTop = storiesEl ? storiesEl.offsetTop : heroHeight;
    const storiesHeight = storiesEl ? storiesEl.offsetHeight : 800;
    const storiesHeading = storiesEl?.querySelector('.stories-title') || storiesEl?.querySelector('.stories-left');
    const headingPos = getPos(storiesHeading);

    // Swings to the left edge by the Stories heading
    const pStoriesHeading = {
      x: headingPos ? Math.max(36, headingPos.left + 24) : width * 0.12,
      y: headingPos ? headingPos.y : storiesTop + storiesHeight * 0.22,
    };

    // Crosses between the cards
    const storiesCards = storiesEl?.querySelectorAll('.story-portrait-card, .story-card-wrapper');
    const card1Pos = storiesCards?.[0] ? getPos(storiesCards[0]) : null;
    const card2Pos = storiesCards?.[1] ? getPos(storiesCards[1]) : null;

    const pStoriesMid = {
      x: card1Pos && card2Pos ? (card1Pos.x + card2Pos.x) / 2 : width * 0.52,
      y: card1Pos ? card1Pos.y + 40 : storiesTop + storiesHeight * 0.54,
    };

    const pStoriesExit = {
      x: card2Pos ? Math.min(width - 40, card2Pos.right + 40) : width * 0.82,
      y: storiesTop + storiesHeight * 0.82,
    };

    // 3. Family Tree Section (#family)
    const familyEl = document.getElementById('family');
    const familyTop = familyEl ? familyEl.offsetTop : storiesTop + storiesHeight;
    const familyHeight = familyEl ? familyEl.offsetHeight : 800;
    const familyDiagram = familyEl?.querySelector('.family-tree-diagram');
    const diagramPos = getPos(familyDiagram);

    // Loops around the Family Tree block (enters top-left, curves around right, sweeps below)
    const pFamilyLoopTop = {
      x: diagramPos ? diagramPos.left + diagramPos.width * 0.48 : width * 0.62,
      y: diagramPos ? diagramPos.top + 30 : familyTop + familyHeight * 0.24,
    };

    const pFamilyLoopRight = {
      x: diagramPos ? Math.min(width - 32, diagramPos.right + 20) : width * 0.88,
      y: diagramPos ? diagramPos.y + 20 : familyTop + familyHeight * 0.54,
    };

    const pFamilyLoopBottom = {
      x: diagramPos ? diagramPos.left + diagramPos.width * 0.35 : width * 0.44,
      y: diagramPos ? diagramPos.bottom + 20 : familyTop + familyHeight * 0.86,
    };

    // 4. Oracle Section (#oracle)
    const oracleEl = document.getElementById('oracle');
    const oracleTop = oracleEl ? oracleEl.offsetTop : familyTop + familyHeight;
    const oracleHeight = oracleEl ? oracleEl.offsetHeight : 800;
    const oracleSun = oracleEl?.querySelector('.oracle-sun-wrap') || oracleEl?.querySelector('.oracle-sun');
    const sunPos = getPos(oracleSun);

    // Circles the oracle sun
    const sunCenterX = sunPos ? sunPos.x : width * 0.32;
    const sunCenterY = sunPos ? sunPos.y : oracleTop + oracleHeight * 0.5;
    const sunR = sunPos ? Math.max(50, Math.min(sunPos.width / 2 + 25, 95)) : 75;

    const pOracleSunTop = {
      x: sunCenterX - sunR * 0.4,
      y: sunCenterY - sunR * 0.9,
    };
    const pOracleSunRight = {
      x: sunCenterX + sunR * 1.05,
      y: sunCenterY - sunR * 0.1,
    };
    const pOracleSunBottom = {
      x: sunCenterX + sunR * 0.2,
      y: sunCenterY + sunR * 1.05,
    };
    const pOracleSunLeft = {
      x: sunCenterX - sunR * 0.9,
      y: sunCenterY + sunR * 0.4,
    };

    // 5. Places Section (#places)
    const placesEl = document.getElementById('places');
    const placesTop = placesEl ? placesEl.offsetTop : oracleTop + oracleHeight;
    const placesHeight = placesEl ? placesEl.offsetHeight : 800;
    const placesGrid = placesEl?.querySelector('.places-cards-grid');
    const placesGridPos = getPos(placesGrid);

    // Crosses Places diagonally through the landscape cards
    const pPlacesEntry = {
      x: placesGridPos ? placesGridPos.left + placesGridPos.width * 0.2 : width * 0.32,
      y: placesTop + placesHeight * 0.32,
    };
    const pPlacesExit = {
      x: placesGridPos ? placesGridPos.left + placesGridPos.width * 0.75 : width * 0.74,
      y: placesTop + placesHeight * 0.72,
    };

    // 6. Artifacts Section (#artifacts)
    const artifactsEl = document.getElementById('artifacts');
    const artifactsTop = artifactsEl ? artifactsEl.offsetTop : placesTop + placesHeight;
    const artifactsHeight = artifactsEl ? artifactsEl.offsetHeight : 800;
    const artifactsGrid = artifactsEl?.querySelector('.artifacts-cards-grid');
    const artGridPos = getPos(artifactsGrid);

    // Crosses Artifacts
    const pArtifactsEntry = {
      x: artGridPos ? artGridPos.left + artGridPos.width * 0.28 : width * 0.36,
      y: artifactsTop + artifactsHeight * 0.38,
    };
    const pArtifactsExit = {
      x: artGridPos ? artGridPos.left + artGridPos.width * 0.82 : width * 0.78,
      y: artifactsTop + artifactsHeight * 0.74,
    };

    // 7. Footer Section (#footer)
    const footerEl = document.getElementById('footer');
    const footerTop = footerEl ? footerEl.offsetTop : artifactsTop + artifactsHeight;
    const footerHeight = footerEl ? footerEl.offsetHeight : 600;
    const footerStarEl = footerEl?.querySelector('.footer-cta-star');
    const starPos = getPos(footerStarEl);

    // Ends at the footer CTA star
    const pFooterEnd = {
      x: starPos ? starPos.x : width * 0.5,
      y: starPos ? starPos.y : footerTop + footerHeight * 0.42,
    };

    // Chain all landmark points into a smooth cubic Bezier path
    const landmarks = [
      pStart,
      pHeroExit,
      pStoriesHeading,
      pStoriesMid,
      pStoriesExit,
      pFamilyLoopTop,
      pFamilyLoopRight,
      pFamilyLoopBottom,
      pOracleSunTop,
      pOracleSunRight,
      pOracleSunBottom,
      pOracleSunLeft,
      pPlacesEntry,
      pPlacesExit,
      pArtifactsEntry,
      pArtifactsExit,
      pFooterEnd,
    ];

    const d = buildSmoothCubicBezier(landmarks);
    setPathD(d);
  };

  // ResizeObserver on container and window resize
  useEffect(() => {
    const container = containerRef?.current;
    if (!container) return;

    measureAndBuildPath();

    const ro = new ResizeObserver(() => {
      measureAndBuildPath();
    });
    ro.observe(container);

    const handleResize = () => {
      measureAndBuildPath();
    };
    window.addEventListener('resize', handleResize);

    return () => {
      ro.disconnect();
      window.removeEventListener('resize', handleResize);
    };
  }, [containerRef]);

  // Compute 5 compass-star coordinates using path.getPointAtLength at fixed fractions
  useEffect(() => {
    const pathEl = pathRef.current;
    if (!pathEl || !pathD) return;

    try {
      const totalLen = pathEl.getTotalLength();
      if (totalLen > 0) {
        const starCoords = STAR_FRACTIONS.map((frac) => {
          const pt = pathEl.getPointAtLength(frac * totalLen);
          return { x: pt.x, y: pt.y, fraction: frac };
        });
        setStars(starCoords);
      }
    } catch {
      // Fallback if browser hasn't attached path yet
    }
  }, [pathD]);

  // Passive scroll listener throttled with requestAnimationFrame
  useEffect(() => {
    if (prefersReducedMotion) {
      setScrollProgress(1);
      return;
    }

    let rAFId = null;

    const onScroll = () => {
      if (rAFId) return;
      rAFId = requestAnimationFrame(() => {
        rAFId = null;
        const container = containerRef?.current;
        if (!container) return;
        const maxScroll = container.scrollHeight - window.innerHeight;
        const p = maxScroll > 0 ? Math.min(1, Math.max(0, window.scrollY / maxScroll)) : 0;
        setScrollProgress(p);

        // Update head point coordinate along the path
        const pathEl = pathRef.current;
        if (pathEl) {
          try {
            const totalLen = pathEl.getTotalLength();
            if (totalLen > 0) {
              const pt = pathEl.getPointAtLength(p * totalLen);
              setHeadPos({ x: pt.x, y: pt.y });
            }
          } catch {
            // Ignore geometry update during tear-down
          }
        }
      });
    };

    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    return () => {
      window.removeEventListener('scroll', onScroll);
      if (rAFId) cancelAnimationFrame(rAFId);
    };
  }, [containerRef, prefersReducedMotion, pathD]);

  const effectiveProgress = prefersReducedMotion ? 1 : scrollProgress;
  const dashOffset = 1 - effectiveProgress;

  return (
    <svg
      ref={svgRef}
      className="golden-thread-canvas"
      width={viewSize.width}
      height={viewSize.height}
      viewBox={`0 0 ${viewSize.width} ${viewSize.height}`}
      aria-hidden="true"
    >
      <defs>
        {/* Luminous gradient from --gold to --glow to --gold */}
        <linearGradient id={gradId} x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="var(--gold, #D9A441)" />
          <stop offset="45%" stopColor="var(--glow, #FFD98A)" />
          <stop offset="85%" stopColor="var(--gold, #D9A441)" />
          <stop offset="100%" stopColor="var(--glow, #FFD98A)" />
        </linearGradient>

        {/* Soft golden glow filter */}
        <filter id={glowId} x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="3.2" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>

        {/* Draw head halo glow filter */}
        <filter id={headGlowId} x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="4.5" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {pathD && (
        <>
          {/* Faint full-length track path underneath at 15% opacity */}
          <path
            d={pathD}
            fill="none"
            stroke={`url(#${gradId})`}
            strokeWidth="2.5"
            strokeLinecap="round"
            opacity="0.15"
          />

          {/* Active drawing thread with pathLength="1" */}
          <path
            ref={pathRef}
            d={pathD}
            fill="none"
            stroke={`url(#${gradId})`}
            strokeWidth="2.5"
            strokeLinecap="round"
            pathLength="1"
            strokeDasharray="1"
            strokeDashoffset={dashOffset}
            filter={`url(#${glowId})`}
          />

          {/* Bright glowing dot at the draw head */}
          {effectiveProgress > 0.005 && effectiveProgress < 0.998 && headPos.x > 0 && (
            <g transform={`translate(${headPos.x}, ${headPos.y})`}>
              <circle r="6" fill="var(--glow, #FFD98A)" opacity="0.6" filter={`url(#${headGlowId})`} />
              <circle r="3.2" fill="#FFFFFF" />
              <circle r="1.5" fill="var(--glow, #FFD98A)" />
            </g>
          )}

          {/* 5 Small Compass-Star Glyphs placed at fixed fractions */}
          {stars.map((star, idx) => {
            const isPassed = effectiveProgress >= star.fraction;
            return (
              <g
                key={idx}
                className={`thread-compass-star ${isPassed ? 'thread-compass-star--visible' : ''}`}
                transform={`translate(${star.x}, ${star.y}) scale(${isPassed ? 1 : 0.4})`}
                opacity={isPassed ? 1 : 0}
              >
                {/* 8-point compass star */}
                <circle cx="0" cy="0" r="2.2" fill="#FFFFFF" />
                <path
                  d="M 0 -9 L 2 -2.5 L 9 0 L 2 2.5 L 0 9 L -2 2.5 L -9 0 L -2 -2.5 Z"
                  fill="var(--gold, #D9A441)"
                  filter={`url(#${glowId})`}
                />
                <path
                  d="M 0 -5.5 L 1.2 -1.2 L 5.5 0 L 1.2 1.2 L 0 5.5 L -1.2 1.2 L -5.5 0 L -1.2 -1.2 Z"
                  fill="#FFF7E0"
                />
              </g>
            );
          })}
        </>
      )}
    </svg>
  );
}
