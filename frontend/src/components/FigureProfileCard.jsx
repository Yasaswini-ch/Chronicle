import React from 'react';
import { typeColor } from '../utils/colors';
import { portraitFor } from '../data/portraits';
import { lookupTerm } from '../data/glossary';
import './FigureProfileCard.css';

/**
 * A compact profile panel for whichever figure was last clicked in the
 * pantheon tree — cream card with the portrait on top.
 */
export default function FigureProfileCard({ figure, edges, onSelectMyth, onOpenDossier }) {
  if (!figure) {
    return (
      <div className="card figure-profile-card figure-profile-empty">
        <div className="figure-profile-empty-text">
          Click any figure in the tree to explore their lineage.
        </div>
      </div>
    );
  }

  const portrait = portraitFor(figure.label || figure.id);
  const typeInfo = lookupTerm(figure.type);
  const ties = edges.filter((e) => e.source === figure.id || e.target === figure.id);
  const color = typeColor(figure.type);

  return (
    <div
      className="card figure-profile-card"
      style={{ borderTopColor: color, borderTopWidth: '4px', borderTopStyle: 'solid' }}
    >
      {/* Portrait on Top */}
      <div className="figure-profile-media">
        {portrait ? (
          <img
            src={portrait}
            alt={figure.label}
            className="figure-profile-img"
            loading="lazy"
          />
        ) : (
          <div
            className="figure-profile-medallion"
            style={{ borderColor: color, color }}
          >
            {(figure.label || '?').charAt(0).toUpperCase()}
          </div>
        )}
      </div>

      <div className="figure-profile-content">
        <h3 className="figure-profile-name">{figure.label}</h3>

        <div className="figure-profile-type-badge">
          <span
            className="figure-profile-type-text"
            style={{ color }}
          >
            {figure.type}
          </span>
        </div>

        {typeInfo && (
          <p className="figure-profile-definition">
            {typeInfo.definition}
          </p>
        )}

        {/* Stats Row */}
        <div className="figure-profile-stats">
          <div className="figure-profile-stat-box">
            <div className="figure-profile-stat-val">
              {figure.degree ?? ties.length}
            </div>
            <div className="figure-profile-stat-label">Ties</div>
          </div>
          <div className="figure-profile-stat-divider" />
          <div className="figure-profile-stat-box">
            <div className="figure-profile-stat-val">
              {(figure.myths || []).length}
            </div>
            <div className="figure-profile-stat-label">Myths</div>
          </div>
        </div>

        {/* Narratives featured in */}
        {figure.myths && figure.myths.length > 0 && (
          <div className="figure-profile-myths-wrap">
            <div className="figure-profile-subheading">Appears In</div>
            <div className="figure-profile-myths-list">
              {figure.myths.slice(0, 4).map((m) => (
                <button
                  key={m}
                  type="button"
                  className="figure-profile-myth-btn"
                  onClick={() => onSelectMyth && onSelectMyth(m)}
                >
                  <span>{m}</span>
                  <span className="figure-profile-myth-arrow">→</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {onOpenDossier && (
          <button
            type="button"
            className="btn-ghost figure-profile-dossier-btn"
            onClick={() => onOpenDossier(figure)}
          >
            Full Dossier &amp; Path Tracer →
          </button>
        )}
      </div>
    </div>
  );
}
