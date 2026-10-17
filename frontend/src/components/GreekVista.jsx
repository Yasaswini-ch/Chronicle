import React from 'react';

/**
 * A painterly illustration of the Aegean coast at golden hour: hazy headland,
 * a sunlit sea, an island temple, a cliffside ruin, and olive groves — built
 * entirely from layered SVG gradients, blur, and grain so it reads as a
 * soft gouache painting rather than flat vector clip-art. No external
 * image asset required.
 */
export default function GreekVista({ className }) {
  return (
    <svg
      className={className}
      viewBox="0 0 1600 900"
      preserveAspectRatio="xMidYMax slice"
      xmlns="http://www.w3.org/2000/svg"
      style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#FCF6E8" />
          <stop offset="38%" stopColor="#F8ECCF" />
          <stop offset="70%" stopColor="#F3DEAE" />
          <stop offset="100%" stopColor="#EACB8E" />
        </linearGradient>

        <radialGradient id="sunGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#FFF9E6" stopOpacity="1" />
          <stop offset="28%" stopColor="#FCE8A8" stopOpacity="0.75" />
          <stop offset="60%" stopColor="#F3C978" stopOpacity="0.28" />
          <stop offset="100%" stopColor="#F3C978" stopOpacity="0" />
        </radialGradient>

        <linearGradient id="haze1" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#D9C9B3" stopOpacity="0.55" />
          <stop offset="100%" stopColor="#C9B79E" stopOpacity="0.35" />
        </linearGradient>

        <linearGradient id="ridgeFar" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#B7B6C2" />
          <stop offset="100%" stopColor="#9FA2AE" />
        </linearGradient>

        <linearGradient id="ridgeMid" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#95A687" />
          <stop offset="100%" stopColor="#748A68" />
        </linearGradient>

        <linearGradient id="seaGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#C9DCD4" />
          <stop offset="18%" stopColor="#A9CAC4" />
          <stop offset="55%" stopColor="#7FAFAE" />
          <stop offset="100%" stopColor="#5F9494" />
        </linearGradient>

        <linearGradient id="sunPath" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#FFF3C4" stopOpacity="0.9" />
          <stop offset="100%" stopColor="#FFE9A8" stopOpacity="0" />
        </linearGradient>

        <linearGradient id="hillLeft" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#8CA26E" />
          <stop offset="55%" stopColor="#6E8C58" />
          <stop offset="100%" stopColor="#53713F" />
        </linearGradient>

        <linearGradient id="groundFront" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#6B8A4D" />
          <stop offset="45%" stopColor="#577239" />
          <stop offset="100%" stopColor="#425A2A" />
        </linearGradient>

        <linearGradient id="groundFrontR" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#789657" />
          <stop offset="100%" stopColor="#4E6936" />
        </linearGradient>

        <linearGradient id="marbleLit" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#FBF4E2" />
          <stop offset="100%" stopColor="#E3D5B2" />
        </linearGradient>
        <linearGradient id="marbleShadow" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#CBBD9C" />
          <stop offset="100%" stopColor="#AFA183" />
        </linearGradient>

        <filter id="blurLg" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="9" />
        </filter>
        <filter id="blurMd" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="4" />
        </filter>
        <filter id="blurSm" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="1.4" />
        </filter>

        {/* Painterly paper grain, screened softly over the whole scene */}
        <filter id="paperGrain" x="0" y="0" width="100%" height="100%">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" result="noise" />
          <feColorMatrix in="noise" type="matrix" values="0 0 0 0 0.35  0 0 0 0 0.3  0 0 0 0 0.2  0 0 0 0.05 0" />
        </filter>
        <filter id="canvasTexture" x="0" y="0" width="100%" height="100%">
          <feTurbulence type="fractalNoise" baseFrequency="0.012 0.02" numOctaves="3" seed="4" result="n" />
          <feColorMatrix in="n" type="matrix" values="0 0 0 0 1  0 0 0 0 0.97  0 0 0 0 0.88  0 0 0 0.035 0" />
        </filter>
      </defs>

      {/* Sky */}
      <rect x="0" y="0" width="1600" height="900" fill="url(#sky)" />
      <rect x="0" y="0" width="1600" height="900" filter="url(#canvasTexture)" />
      <circle cx="1230" cy="330" r="340" fill="url(#sunGlow)" />
      <circle cx="1230" cy="330" r="42" fill="#FFFBEE" opacity="0.95" />

      {/* Birds, a few, far and small */}
      <g stroke="#8C7B55" strokeWidth="2.2" fill="none" opacity="0.4" strokeLinecap="round">
        <path d="M250 190 q9 -11 18 0 q9 -11 18 0" />
        <path d="M300 215 q7 -9 14 0 q7 -9 14 0" />
        <path d="M980 150 q8 -10 16 0 q8 -10 16 0" />
      </g>

      {/* Distant atmospheric haze band */}
      <rect x="0" y="330" width="1600" height="140" fill="url(#haze1)" filter="url(#blurLg)" />

      {/* Far ridge — hazy, low-contrast, well back */}
      <path
        d="M0 420 C 220 360 420 400 620 378 C 860 352 1040 392 1260 372 C 1380 362 1500 376 1600 360 L1600 480 L0 480 Z"
        fill="url(#ridgeFar)"
        opacity="0.55"
        filter="url(#blurLg)"
      />

      {/* Island with a small pale temple, soft and distant */}
      <g opacity="0.78" filter="url(#blurMd)">
        <ellipse cx="960" cy="430" rx="150" ry="22" fill="#A7AFA0" opacity="0.5" />
        <g transform="translate(905,372)">
          <polygon points="0,30 58,30 29,8" fill="#D8D0B9" />
          <rect x="4" y="30" width="6" height="22" fill="#D8D0B9" />
          <rect x="16" y="30" width="6" height="22" fill="#D8D0B9" />
          <rect x="28" y="30" width="6" height="22" fill="#D8D0B9" />
          <rect x="40" y="30" width="6" height="22" fill="#D8D0B9" />
          <rect x="52" y="30" width="6" height="22" fill="#D8D0B9" />
          <rect x="-2" y="50" width="62" height="5" fill="#C7BFA6" />
        </g>
      </g>

      {/* Mid ridge, warmer and closer, soft edge */}
      <path
        d="M0 470 C 260 410 480 452 720 432 C 940 414 1120 450 1340 432 C 1440 424 1540 438 1600 426 L1600 560 L0 560 Z"
        fill="url(#ridgeMid)"
        opacity="0.92"
        filter="url(#blurSm)"
      />

      {/* Sea */}
      <path d="M0 500 C 340 476 620 498 900 486 C 1160 475 1360 492 1600 480 L1600 600 L0 600 Z" fill="url(#seaGrad)" />
      <path d="M1030 486 L1600 480 L1600 600 L930 600 Z" fill="url(#sunPath)" opacity="0.55" />
      <g stroke="#F4F8F3" strokeOpacity="0.4" strokeWidth="2.2" fill="none" filter="url(#blurSm)">
        <path d="M140 540 q46 -9 92 0" />
        <path d="M560 555 q46 -9 92 0" />
        <path d="M1120 530 q46 -9 92 0" />
        <path d="M780 572 q38 -8 76 0" />
      </g>
      {/* Sailboat, small and quiet */}
      <g transform="translate(690,520)" opacity="0.92">
        <path d="M0 0 L0 -30 L18 -9 Z" fill="#FBF2DD" />
        <path d="M0 0 L-3 -24 L3 -24 Z" fill="#8A7349" />
        <path d="M0 2 L-20 5 L20 5 Z" fill="#6E5B3B" />
        <ellipse cx="0" cy="7" rx="16" ry="2.4" fill="#2E4A4C" opacity="0.25" />
      </g>

      {/* Left hillside, rolling into the frame */}
      <path
        d="M0 560 C 160 500 330 520 430 560 C 520 596 520 640 560 690 L0 900 Z"
        fill="url(#hillLeft)"
      />
      <path
        d="M0 560 C 160 500 330 520 430 560 C 480 580 500 605 520 630 L0 700 Z"
        fill="#9CB17E"
        opacity="0.35"
      />

      {/* Foreground meadow, calm and open so UI text stays legible */}
      <path d="M0 700 C 420 650 980 672 1600 640 L1600 900 L0 900 Z" fill="url(#groundFront)" />
      {/* soft light falling across the meadow — blurred only, no hard edges */}
      <ellipse cx="500" cy="760" rx="460" ry="110" fill="#B9CE93" opacity="0.16" filter="url(#blurLg)" />
      <ellipse cx="1250" cy="820" rx="420" ry="110" fill="#E9D8A2" opacity="0.14" filter="url(#blurLg)" />

      {/* Cliffside ruin, far right, tucked away from the text column */}
      <g transform="translate(1340,470)">
        <ellipse cx="60" cy="150" rx="150" ry="18" fill="#324423" opacity="0.3" />
        {/* column A */}
        <g>
          <rect x="-4" y="14" width="10" height="110" fill="url(#marbleShadow)" />
          <rect x="6" y="14" width="10" height="110" fill="url(#marbleLit)" />
          <rect x="-8" y="0" width="28" height="14" fill="url(#marbleLit)" />
          <rect x="-8" y="124" width="28" height="10" fill="url(#marbleShadow)" />
        </g>
        {/* column B, broken shorter */}
        <g transform="translate(58,34)">
          <rect x="-4" y="10" width="9" height="78" fill="url(#marbleShadow)" opacity="0.95" />
          <rect x="5" y="10" width="9" height="78" fill="url(#marbleLit)" opacity="0.95" />
          <rect x="-8" y="0" width="26" height="12" fill="url(#marbleLit)" opacity="0.95" />
          <polygon points="-10,88 24,88 18,100 -4,100" fill="url(#marbleShadow)" opacity="0.9" />
        </g>
        {/* fallen lintel */}
        <rect x="118" y="118" width="70" height="14" fill="url(#marbleShadow)" opacity="0.85" transform="rotate(-4 118 118)" />
        {/* far small stump */}
        <rect x="150" y="108" width="9" height="34" fill="url(#marbleShadow)" opacity="0.7" />
      </g>

      {/* Cypress trees — a few, irregular, grounded in the meadow */}
      {[
        [150, 690, 1],
        [205, 712, 0.78],
        [1230, 668, 0.92],
      ].map(([cx, cy, s], i) => (
        <g key={i} transform={`translate(${cx},${cy}) scale(${s})`}>
          <path
            d="M0 0 C -16 -22 -13 -56 0 -84 C 13 -56 16 -22 0 0 Z"
            fill="#324B22"
          />
          <path d="M0 -10 C -8 -30 -6 -58 0 -76" stroke="#435E2C" strokeWidth="3" fill="none" opacity="0.6" />
          <rect x="-2.5" y="0" width="5" height="10" fill="#4A3A22" />
        </g>
      ))}

      {/* Olive tree, left foreground, anchoring the composition */}
      <g transform="translate(100,790)">
        <path d="M0 50 C -8 14 -5 -34 0 -46" stroke="#4A3A22" strokeWidth="8" fill="none" strokeLinecap="round" />
        <path d="M0 10 C 10 -2 16 -18 14 -30" stroke="#4A3A22" strokeWidth="5" fill="none" strokeLinecap="round" />
        <circle cx="-26" cy="-56" r="30" fill="#8CA26E" opacity="0.95" />
        <circle cx="12" cy="-68" r="36" fill="#7E9A5C" />
        <circle cx="34" cy="-40" r="26" fill="#8CA26E" opacity="0.95" />
        <circle cx="-6" cy="-40" r="24" fill="#95AC78" opacity="0.9" />
      </g>

      {/* A quiet stone path, confined to the lower-right corner, well clear of the hero copy */}
      <path
        d="M1600 900 C 1480 840 1430 790 1380 740 C 1340 702 1320 672 1310 650"
        stroke="#D9CFB4"
        strokeWidth="46"
        fill="none"
        opacity="0.22"
        strokeLinecap="round"
        filter="url(#blurSm)"
      />

      {/* Full-canvas grain overlay for a painted, non-vector feel */}
      <rect x="0" y="0" width="1600" height="900" filter="url(#paperGrain)" opacity="0.5" />
    </svg>
  );
}
