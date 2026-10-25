import React, { useEffect, useRef } from 'react';

/**
 * CursorSparkles — Subtle, dreamy celestial golden stardust and diamond sparkles
 * that trail gently behind cursor movement across the page.
 * Uses an efficient canvas with an auto-sleeping requestAnimationFrame loop.
 */
export default function CursorSparkles() {
  const canvasRef = useRef(null);

  useEffect(() => {
    // Respect user's motion preferences
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return;
    }

    // Skip on touch-only devices without a pointer
    if (window.matchMedia('(hover: none)').matches) {
      return;
    }

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId = null;
    let isRunning = false;
    let lastX = -100;
    let lastY = -100;

    const particles = [];

    const COLORS = [
      '#FFFFFF',       // Diamond white core
      '#FFF3D1',       // Pale starlight
      '#FFD98A',       // Radiant theme glow
      '#E8BE65',       // Warm Grecian gold
      '#D9A441',       // Antique gold
    ];

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = window.innerWidth * dpr;
      canvas.height = window.innerHeight * dpr;
      ctx.scale(dpr, dpr);
    };

    resize();
    window.addEventListener('resize', resize);

    // Draw an authentic 4-pointed diamond star sparkle
    const drawStar = (x, y, size, alpha, color, rotation) => {
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(rotation);
      ctx.globalAlpha = Math.max(0, Math.min(1, alpha));
      ctx.fillStyle = color;

      // Soft glow backing
      ctx.shadowColor = color;
      ctx.shadowBlur = 6;

      ctx.beginPath();
      // Draw 4-point concave star
      const inner = size * 0.22;
      ctx.moveTo(0, -size);
      ctx.quadraticCurveTo(0, -inner, inner, 0);
      ctx.quadraticCurveTo(0, inner, 0, size);
      ctx.quadraticCurveTo(0, inner, -inner, 0);
      ctx.quadraticCurveTo(0, -inner, 0, -size);
      ctx.closePath();
      ctx.fill();

      // Tiny white radiant center
      ctx.fillStyle = '#FFFFFF';
      ctx.beginPath();
      ctx.arc(0, 0, Math.max(0.7, size * 0.2), 0, Math.PI * 2);
      ctx.fill();

      ctx.restore();
    };

    // Draw a circular glowing stardust mote
    const drawMote = (x, y, radius, alpha, color) => {
      ctx.save();
      ctx.globalAlpha = Math.max(0, Math.min(1, alpha));
      ctx.fillStyle = color;
      ctx.shadowColor = color;
      ctx.shadowBlur = 4;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    };

    const spawnSparkles = (x, y) => {
      // Spawn 2 to 4 varied micro-sparkles
      const count = 2 + Math.floor(Math.random() * 2);
      for (let i = 0; i < count; i++) {
        const isStar = Math.random() > 0.45;
        const color = COLORS[Math.floor(Math.random() * COLORS.length)];
        const angle = Math.random() * Math.PI * 2;
        const speed = 0.3 + Math.random() * 1.2;

        particles.push({
          x: x + (Math.random() - 0.5) * 8,
          y: y + (Math.random() - 0.5) * 8,
          vx: Math.cos(angle) * speed,
          vy: Math.sin(angle) * speed - 0.2, // Subtle upward float
          size: isStar ? 3.5 + Math.random() * 4 : 1.2 + Math.random() * 2,
          alpha: 0.9 + Math.random() * 0.1,
          decay: 0.022 + Math.random() * 0.025,
          color,
          isStar,
          rotation: Math.random() * Math.PI,
          vRot: (Math.random() - 0.5) * 0.08,
        });
      }

      if (!isRunning) {
        isRunning = true;
        animId = requestAnimationFrame(render);
      }
    };

    const handlePointerMove = (e) => {
      const x = e.clientX;
      const y = e.clientY;

      // Distance threshold: spawn when moving smoothly
      const dx = x - lastX;
      const dy = y - lastY;
      const dist = Math.hypot(dx, dy);

      if (dist > 5) {
        spawnSparkles(x, y);
        lastX = x;
        lastY = y;
      }
    };

    const render = () => {
      ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);

      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        p.x += p.vx;
        p.y += p.vy;
        p.vx *= 0.96; // Air drag
        p.vy *= 0.96;
        p.rotation += p.vRot;
        p.alpha -= p.decay;

        if (p.alpha <= 0) {
          particles.splice(i, 1);
          continue;
        }

        if (p.isStar) {
          drawStar(p.x, p.y, p.size * (p.alpha * 0.4 + 0.6), p.alpha, p.color, p.rotation);
        } else {
          drawMote(p.x, p.y, p.size * (p.alpha * 0.3 + 0.7), p.alpha, p.color);
        }
      }

      if (particles.length > 0) {
        animId = requestAnimationFrame(render);
      } else {
        isRunning = false;
        ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
      }
    };

    window.addEventListener('pointermove', handlePointerMove, { passive: true });

    return () => {
      window.removeEventListener('pointermove', handlePointerMove);
      window.removeEventListener('resize', resize);
      if (animId) cancelAnimationFrame(animId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        inset: 0,
        width: '100vw',
        height: '100vh',
        pointerEvents: 'none',
        zIndex: 9999,
      }}
      aria-hidden="true"
    />
  );
}
