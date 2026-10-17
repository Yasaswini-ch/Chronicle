import React, { useState, useEffect, useMemo } from 'react';
import Reveal from '../components/Reveal';
import SectionIcon from '../components/SectionIcon';
import FamilyTree from '../components/FamilyTree';
import ClusterTree from '../components/ClusterTree';
import FigureProfileCard from '../components/FigureProfileCard';
import { typeColor } from '../utils/colors';
import { buildUnifiedTree } from '../utils/forest';

export default function PantheonView({ onSelectMyth }) {
  const [graphData, setGraphData] = useState({ nodes: [], edges: [], stats: {} });
  const [selectedFigure, setSelectedFigure] = useState(null);
  const [sourceFigure, setSourceFigure] = useState('');
  const [targetFigure, setTargetFigure] = useState('');
  const [tracedPath, setTracedPath] = useState(null);
  const [pathSearched, setPathSearched] = useState(false);
  const [pathSearching, setPathSearching] = useState(false);
  const [filterType, setFilterType] = useState('all');

  useEffect(() => {
    fetch('/api/graph')
      .then(res => res.json())
      .then(data => {
        setGraphData(data);
        if (data.nodes && data.nodes.length > 0) {
          const mostConnected = [...data.nodes].sort((a, b) => (b.degree || 0) - (a.degree || 0))[0];
          setSelectedFigure(mostConnected);

          // Default the path tracer to a pair that's actually linked, so the
          // first thing a visitor sees is a working example, not a dead end.
          const firstEdge = (data.edges || [])[0];
          if (firstEdge) {
            setSourceFigure(firstEdge.source);
            setTargetFigure(firstEdge.target);
          } else {
            setSourceFigure(data.nodes[0].id);
            if (data.nodes.length > 1) setTargetFigure(data.nodes[1].id);
          }
        }
      })
      .catch(err => console.error('Failed to load graph:', err));
  }, []);

  const handleTracePath = () => {
    if (!sourceFigure || !targetFigure) return;
    setPathSearching(true);
    setPathSearched(false);
    fetch(`/api/graph/path?source=${encodeURIComponent(sourceFigure)}&target=${encodeURIComponent(targetFigure)}`)
      .then(res => res.json())
      .then(data => {
        setTracedPath(data.path || null);
        setPathSearched(true);
        setPathSearching(false);
      })
      .catch(() => {
        setTracedPath(null);
        setPathSearched(true);
        setPathSearching(false);
      });
  };

  const figureTypes = Array.from(new Set(graphData.nodes.map(n => n.type).filter(Boolean))).sort();

  const filteredNodes = graphData.nodes.filter(n => {
    if (filterType === 'all') return true;
    return n.type?.toLowerCase() === filterType.toLowerCase();
  });

  // Calculate direct ties for selected figure
  const relatedEdges = graphData.edges.filter(
    e => selectedFigure && (e.source === selectedFigure.id || e.target === selectedFigure.id)
  );

  const nodeById = (id) => graphData.nodes.find(n => n.id === id);

  const edgeBetween = (a, b) =>
    graphData.edges.find(e => (e.source === a && e.target === b) || (e.source === b && e.target === a));

  const forest = useMemo(() => buildUnifiedTree(graphData.nodes, graphData.edges), [graphData]);

  const selectFromForest = (node) => setSelectedFigure(node);

  const openDossier = (node) => {
    setSelectedFigure(node);
    document.getElementById('pantheon-dossier')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <div>
      <Reveal style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '4px' }}>
          <SectionIcon name="tree" />
          <h2 style={{ fontSize: '1.6rem', margin: 0 }}>The Family Tree of the Gods</h2>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Every parent, lover, rival, and monster-slayer the data connects, drawn as one forest of family
          trees below — the pantheon doesn&apos;t form a single tree (the myths never explicitly link every
          figure to every other), so it&apos;s shown as the separate clusters the stories actually describe.
          Click any name for a quick profile, right here.
        </p>
      </Reveal>

      {/* The complete pantheon, every cluster rendered as its own tree,
          with a sticky profile card beside it for whoever you click */}
      <div className="pantheon-forest-layout" style={{ marginBottom: '32px' }}>
        <Reveal className="panel" style={{ padding: '12px 16px 24px 16px' }}>
          <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1.5px', color: 'var(--accent-gold)', marginBottom: '4px' }}>
            The Complete Pantheon ({forest.tree.size} Connected Figures, {forest.clusterCount} Family Groups)
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
            The dashed "Pantheon" node isn&apos;t a god — it just gathers the {forest.clusterCount} family
            groups the myths actually describe into one diagram, since the stories never explicitly link
            every figure to every other.
          </div>
          <ClusterTree cluster={forest.tree} onSelect={selectFromForest} />

          {forest.isolated.length > 0 && (
            <div style={{ marginTop: '24px', paddingTop: '18px', borderTop: '1px dashed var(--border-subtle)' }}>
              <div style={{ fontSize: '0.72rem', letterSpacing: '1px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '10px', textAlign: 'center' }}>
                Standalone Figures — No Recorded Ties
              </div>
              <div className="forest-isolated-chips" style={{ justifyContent: 'center' }}>
                {forest.isolated.map((n) => (
                  <button key={n.id} className="forest-isolated-chip" onClick={() => selectFromForest(n)}>
                    {n.label}
                  </button>
                ))}
              </div>
            </div>
          )}
        </Reveal>

        <FigureProfileCard
          figure={selectedFigure}
          edges={graphData.edges}
          onSelectMyth={onSelectMyth}
          onOpenDossier={openDossier}
        />
      </div>

      {/* Telemetry bar (2 columns, no three-in-a-row) */}
      <div className="grid-2" style={{ marginBottom: '24px' }}>
        <Reveal className="card">
          <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1.5px', color: 'var(--text-muted)' }}>
            Figures in the Pantheon
          </div>
          <div style={{ fontSize: '1.4rem', color: 'var(--text-primary)', marginTop: '4px', fontWeight: 600 }}>
            {graphData.nodes.length} Figures
          </div>
        </Reveal>
        <Reveal delay={80} className="card">
          <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1.5px', color: 'var(--text-muted)' }}>
            Connections Between Them
          </div>
          <div style={{ fontSize: '1.4rem', color: 'var(--text-primary)', marginTop: '4px', fontWeight: 600 }}>
            {graphData.edges.length} Ties <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 400 }}>(Density: {graphData.stats?.density ? graphData.stats.density.toFixed(3) : '0.042'})</span>
          </div>
        </Reveal>
      </div>

      <div className="split-320">
        {/* Figures Directory */}
        <Reveal className="card" style={{ padding: '16px' }}>
          <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1.5px', color: 'var(--accent-gold)', marginBottom: '12px' }}>
            Browse Every Figure
          </div>

          <select
            value={filterType}
            onChange={e => setFilterType(e.target.value)}
            style={{ width: '100%', marginBottom: '12px' }}
          >
            <option value="all">Gods, Mortals & Creatures</option>
            {figureTypes.map(t => (
              <option key={t} value={t}>{t.toUpperCase()}</option>
            ))}
          </select>

          <div style={{ maxHeight: '540px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {filteredNodes.map(node => {
              const isSelected = selectedFigure && selectedFigure.id === node.id;
              return (
                <div
                  key={node.id}
                  className="myth-row"
                  onClick={() => setSelectedFigure(node)}
                  style={{
                    padding: '8px 12px',
                    cursor: 'pointer',
                    background: isSelected ? 'var(--bg-surface-elevated)' : 'transparent',
                    borderLeft: `3px solid ${isSelected ? typeColor(node.type) : 'transparent'}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <span style={{ color: isSelected ? 'var(--text-primary)' : 'var(--text-secondary)', fontWeight: isSelected ? 600 : 400 }}>
                    {node.label}
                  </span>
                  <span style={{ fontSize: '0.7rem', color: typeColor(node.type), textTransform: 'uppercase', fontWeight: 600 }}>
                    {node.type}
                  </span>
                </div>
              );
            })}
          </div>
        </Reveal>

        {/* Selected Figure Dossier & Path Tracer */}
        <div id="pantheon-dossier" style={{ scrollMarginTop: '24px' }}>
          {selectedFigure && (
            <div
              key={selectedFigure.id}
              className="card story-panel"
              style={{ marginBottom: '24px', padding: '24px', borderTop: `4px solid ${typeColor(selectedFigure.type)}` }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '12px', marginBottom: '16px' }}>
                <div>
                  <h3 style={{ fontSize: '1.5rem', marginBottom: '4px' }}>{selectedFigure.label}</h3>
                  <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1px', color: typeColor(selectedFigure.type), fontWeight: 700 }}>
                    {selectedFigure.type?.toUpperCase()} &bull; Network Degree {selectedFigure.degree}
                  </span>
                </div>
              </div>

              {/* Narratives Featured */}
              <div style={{ marginBottom: '16px' }}>
                <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Associated Narratives
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {(selectedFigure.myths || []).length > 0 ? (
                    selectedFigure.myths.map((m, i) => (
                      <span
                        key={i}
                        onClick={() => onSelectMyth && onSelectMyth(m)}
                        style={{
                          background: 'var(--bg-surface-elevated)',
                          border: '1px solid var(--border-subtle)',
                          padding: '4px 10px',
                          fontSize: '0.85rem',
                          cursor: onSelectMyth ? 'pointer' : 'default',
                        }}
                      >
                        {m}
                      </span>
                    ))
                  ) : (
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No direct myths cataloged</span>
                  )}
                </div>
              </div>

              {/* Direct Connections, as an actual branching family tree */}
              <div>
                <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                  Family Tree ({relatedEdges.length} {relatedEdges.length === 1 ? 'Tie' : 'Ties'})
                </div>
                <FamilyTree
                  selectedFigure={selectedFigure}
                  edges={relatedEdges}
                  nodeById={nodeById}
                  onSelect={setSelectedFigure}
                />
              </div>
            </div>
          )}

          {/* Shortest Path Finder */}
          <Reveal className="card" style={{ padding: '24px' }}>
            <h4 style={{ fontSize: '1.1rem', marginBottom: '8px' }}>How Is X Connected To Y?</h4>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '16px' }}>
              Pick any two figures and see the shortest chain of relationships that links them.
            </p>

            <div className="grid-form-3">
              <div>
                <label style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                  Origin Figure
                </label>
                <select
                  value={sourceFigure}
                  onChange={e => setSourceFigure(e.target.value)}
                  style={{ width: '100%' }}
                >
                  {graphData.nodes.map(n => (
                    <option key={n.id} value={n.id}>{n.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                  Destination Figure
                </label>
                <select
                  value={targetFigure}
                  onChange={e => setTargetFigure(e.target.value)}
                  style={{ width: '100%' }}
                >
                  {graphData.nodes.map(n => (
                    <option key={n.id} value={n.id}>{n.label}</option>
                  ))}
                </select>
              </div>

              <button onClick={handleTracePath} className="btn-primary" disabled={pathSearching} style={{ height: '42px' }}>
                Trace Path
              </button>
            </div>

            {pathSearching && (
              <div style={{ marginTop: '16px', fontSize: '0.85rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                Searching the pantheon…
              </div>
            )}

            {!pathSearching && pathSearched && tracedPath && (
              <div className="story-panel" style={{ marginTop: '16px', padding: '18px 20px', background: 'var(--bg-surface-elevated)', borderLeft: '3px solid var(--accent-gold)' }}>
                <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--accent-gold)', marginBottom: '14px' }}>
                  Connection Path &mdash; {tracedPath.length - 1} {tracedPath.length - 1 === 1 ? 'Relationship' : 'Relationships'} Apart
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '6px' }}>
                  {tracedPath.map((name, i) => {
                    const node = nodeById(name);
                    return (
                      <React.Fragment key={name}>
                        <div
                          style={{
                            background: 'var(--bg-surface)',
                            border: '1px solid var(--border-strong)',
                            borderBottom: `3px solid ${typeColor(node?.type)}`,
                            padding: '8px 14px',
                          }}
                        >
                          <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1rem', color: 'var(--text-primary)' }}>
                            {name}
                          </div>
                          {node?.type && (
                            <div style={{ fontSize: '0.68rem', letterSpacing: '1px', textTransform: 'uppercase', color: typeColor(node.type), fontWeight: 700 }}>
                              {node.type}
                            </div>
                          )}
                        </div>
                        {i < tracedPath.length - 1 && (
                          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '0 4px' }}>
                            <span style={{ fontSize: '0.7rem', fontStyle: 'italic', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>
                              {edgeBetween(tracedPath[i], tracedPath[i + 1])?.relation?.replace(/_/g, ' ') || 'connected to'}
                            </span>
                            <span style={{ color: 'var(--text-muted)' }}>&rarr;</span>
                          </div>
                        )}
                      </React.Fragment>
                    );
                  })}
                </div>

                {/* Where each link in the chain actually comes from */}
                <div style={{ marginTop: '16px', paddingTop: '14px', borderTop: '1px solid var(--border-subtle)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {tracedPath.slice(0, -1).map((name, i) => {
                    const next = tracedPath[i + 1];
                    const edge = edgeBetween(name, next);
                    if (!edge?.myth) return null;
                    return (
                      <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
                        <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                          <strong style={{ color: 'var(--text-primary)' }}>{name}</strong>
                          {' '}&amp;{' '}
                          <strong style={{ color: 'var(--text-primary)' }}>{next}</strong> appear together in{' '}
                          <em>&ldquo;{edge.myth}&rdquo;</em>
                        </span>
                        {onSelectMyth && (
                          <button onClick={() => onSelectMyth(edge.myth)} className="btn-secondary" style={{ fontSize: '0.7rem', padding: '4px 10px' }}>
                            Read This Myth &rarr;
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {!pathSearching && pathSearched && !tracedPath && (
              <div className="story-panel" style={{ marginTop: '16px', padding: '12px 16px', background: 'var(--bg-surface-elevated)', borderLeft: '3px solid var(--accent-garnet)' }}>
                <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--accent-garnet)', marginBottom: '4px' }}>
                  No Path Found
                </div>
                <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                  <strong style={{ color: 'var(--text-primary)' }}>{sourceFigure}</strong> and{' '}
                  <strong style={{ color: 'var(--text-primary)' }}>{targetFigure}</strong> aren&apos;t linked
                  through any relationship recorded in this collection. Try two figures who appear in the
                  same myth.
                </div>
              </div>
            )}
          </Reveal>
        </div>
      </div>
    </div>
  );
}
