import React from 'react';
import { THEME } from '../data/theme';
import './PageHeader.css';

export default function PageHeader({
  label,
  title,
  intro,
  image,
  light = false,
  children,
}) {
  const bgImage = image || THEME.heroBg;

  return (
    <header
      className={`page-header ${light ? 'page-header--light' : ''}`}
      style={{ backgroundImage: `url(${bgImage})` }}
    >
      {/* Gradient overlay: rgba(20,16,12,0.65) bottom, rgba(20,16,12,0.25) top */}
      <div className="page-header-overlay" aria-hidden="true" />

      {/* Decorative vine at right edge at 35% opacity, never overlapping text */}
      <img
        src={THEME.vineRight}
        alt=""
        aria-hidden="true"
        className="page-header-vine-right"
        loading="lazy"
      />

      <div className="page-header-container">
        {label && <div className="label page-header-label">{label}</div>}
        {title && <h1 className="page-header-title">{title}</h1>}
        {intro && <p className="page-header-intro">{intro}</p>}
        {children && <div className="page-header-extras">{children}</div>}
      </div>
    </header>
  );
}
