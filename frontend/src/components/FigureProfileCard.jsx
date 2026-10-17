import React from 'react';
import { typeColor } from '../utils/colors';
import { portraitFor } from '../data/portraits';
import { lookupTerm } from '../data/glossary';

/**
 * A compact "profile" panel for whichever figure was last clicked in the
 * pantheon tree — a portrait (real artifact photo where one genuinely
 * matches, otherwise a generated medallion), their type, how many ties and
 * myths the data actually records for them, and quick links into the rest
 * of the app.
 */
export default function FigureProfileCard({ figure, edges, onSelectMyth, onOpenDossier }) {
  if (!figure) {
    return (
      <div className="panel figure-card figure-card-empty">
        <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', textAlign: 'center', padding: '20px 14px' }}>
          Click any name in the tree to see who they are.
        </div>
      </div>
    );
  }

  const portrait = portraitFor(figure.label || figure.id);
  const typeInfo = lookupTerm(figure.type);
  const ties = edges.filter((e) => e.source === figure.id || e.target === figure.id);

  return (
    <div className="panel figure-card" style={{ borderTop: `4px solid ${typeColor(figure.type)}` }}>
      <div className="figure-card-portrait">
        {portrait ? (
          <>
            <img src={portrait} alt={figure.label} />
            <img src="/images/decor/greek-key-frame.png" alt="" aria-hidden="true" className="figure-card-frame-overlay" />
          </>
        ) : (
          <div className="figure-card-medallion" style={{ borderColor: typeColor(figure.type), color: typeColor(figure.type) }}>
            {(figure.label || '?').charAt(0)}
          </div>
        )}
      </div>

      <div style={{ padding: '14px 16px 18px 16px' }}>
        <h3 style={{ fontSize: '1.2rem', marginBottom: '2px', textAlign: 'center' }}>{figure.label}</h3>
        <div style={{ textAlign: 'center', marginBottom: '10px' }}>
          <span style={{ fontSize: '0.72rem', letterSpacing: '1px', textTransform: 'uppercase', color: typeColor(figure.type), fontWeight: 700 }}>
            {figure.type}
          </span>
        </div>

        {typeInfo && (
          <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: 1.55, marginBottom: '12px' }}>
            {typeInfo.definition}
          </p>
        )}

        <div style={{ display: 'flex', justifyContent: 'space-around', borderTop: '1px solid var(--border-subtle)', borderBottom: '1px solid var(--border-subtle)', padding: '8px 0', marginBottom: '12px' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1.1rem', color: 'var(--text-primary)' }}>{figure.degree ?? ties.length}</div>
            <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Ties</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1.1rem', color: 'var(--text-primary)' }}>{(figure.myths || []).length}</div>
            <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Myths</div>
          </div>
        </div>

        {figure.myths && figure.myths.length > 0 && (
          <div style={{ marginBottom: '12px' }}>
            <div style={{ fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--text-muted)', marginBottom: '6px' }}>
              Appears In
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {figure.myths.slice(0, 4).map((m) => (
                <button key={m} className="figure-card-myth-link" onClick={() => onSelectMyth && onSelectMyth(m)}>
                  {m}
                </button>
              ))}
            </div>
          </div>
        )}

        {onOpenDossier && (
          <button className="btn-secondary" style={{ width: '100%', fontSize: '0.72rem' }} onClick={() => onOpenDossier(figure)}>
            Full Dossier &amp; Path Tracer &rarr;
          </button>
        )}
      </div>
    </div>
  );
}
