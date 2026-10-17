import React from 'react';
import { typeColor } from '../utils/colors';

// Which relation labels mean "the other person is beside me" (siblings, spouses, lovers)
const PEER_RELATIONS = ['sibling_of', 'married_to', 'lover_of', 'spouse_of'];

function classify(edge, selfId) {
  const isSelfSource = edge.source === selfId;
  const relation = edge.relation || 'connected_to';

  if (relation === 'parent_of') return isSelfSource ? 'child' : 'parent';
  if (relation === 'child_of') return isSelfSource ? 'parent' : 'child';
  if (relation === 'mentor_of') return isSelfSource ? 'child' : 'parent';
  if (PEER_RELATIONS.includes(relation)) return 'peer';
  return 'other';
}

function Node({ name, node, relation, onSelect, small }) {
  return (
    <button
      onClick={() => onSelect && node && onSelect(node)}
      className="tree-node"
      style={{ borderTopColor: typeColor(node?.type) }}
      title={relation ? relation.replace(/_/g, ' ') : undefined}
    >
      <div className="tree-node-name" style={{ fontSize: small ? '0.82rem' : '0.92rem' }}>{name}</div>
      {node?.type && <div className="tree-node-type" style={{ color: typeColor(node.type) }}>{node.type}</div>}
    </button>
  );
}

/**
 * Renders the selected figure's direct ties as an actual branching family
 * tree — parents/mentors above, children below, siblings & spouses beside —
 * instead of a flat list of names.
 */
export default function FamilyTree({ selectedFigure, edges, nodeById, onSelect }) {
  const groups = { parent: [], child: [], peer: [], other: [] };
  const seen = new Set();

  edges.forEach((e) => {
    const other = e.source === selectedFigure.id ? e.target : e.source;
    const bucket = classify(e, selectedFigure.id);
    // The underlying data often records both parent_of and its inverse
    // child_of for the same pair — only show each relative once per bucket.
    const dedupeKey = `${bucket}:${other}`;
    if (seen.has(dedupeKey)) return;
    seen.add(dedupeKey);
    groups[bucket].push({ name: other, node: nodeById(other), relation: e.relation });
  });

  const hasAncestors = groups.parent.length > 0;
  const hasDescendants = groups.child.length > 0;

  if (edges.length === 0) {
    return <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No direct ties recorded.</div>;
  }

  return (
    <div className="family-tree">
      {hasAncestors && (
        <div className="tree-tier tree-tier-ancestors">
          {groups.parent.map((p, i) => (
            <Node key={i} {...p} onSelect={onSelect} small />
          ))}
        </div>
      )}

      <div className="tree-tier tree-tier-self">
        {groups.peer.slice(0, Math.ceil(groups.peer.length / 2)).map((p, i) => (
          <Node key={`pl${i}`} {...p} onSelect={onSelect} small />
        ))}
        <div className="tree-node tree-node-self" style={{ borderTopColor: typeColor(selectedFigure.type) }}>
          <div className="tree-node-name" style={{ fontWeight: 700 }}>{selectedFigure.label}</div>
          {selectedFigure.type && <div className="tree-node-type" style={{ color: typeColor(selectedFigure.type) }}>{selectedFigure.type}</div>}
        </div>
        {groups.peer.slice(Math.ceil(groups.peer.length / 2)).map((p, i) => (
          <Node key={`pr${i}`} {...p} onSelect={onSelect} small />
        ))}
      </div>

      {hasDescendants && (
        <div className="tree-tier tree-tier-descendants">
          {groups.child.map((c, i) => (
            <Node key={i} {...c} onSelect={onSelect} small />
          ))}
        </div>
      )}

      {groups.other.length > 0 && (
        <div className="tree-other-ties">
          <div className="tree-other-label">Other Ties</div>
          <div className="tree-other-chips">
            {groups.other.map((o, i) => (
              <button key={i} className="tree-other-chip" onClick={() => onSelect && o.node && onSelect(o.node)}>
                {o.name} <em>{o.relation?.replace(/_/g, ' ')}</em>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
