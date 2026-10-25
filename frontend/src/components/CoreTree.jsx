import React, { useLayoutEffect, useRef, useState } from 'react';
import { portraitFor } from '../data/portraits';
import { typeColor } from '../utils/colors';
import './CoreTree.css';

function relationLabel(relation) {
  return relation ? relation.replace(/_/g, ' ') : 'connected to';
}

function CoreNode({ node, selectedId, onSelect, onNodeClick, relation, nodeRef }) {
  const isSelected = node.id === selectedId;
  const portrait = portraitFor(node.label || node.id);
  return (
    <button
      type="button"
      ref={nodeRef}
      className={`core-tree-node ${isSelected ? 'is-selected' : ''}`}
      onClick={() => (onNodeClick ? onNodeClick(node) : onSelect(node))}
      style={{ borderTopColor: typeColor(node.type) }}
    >
      <span className="core-tree-node-ring" style={{ borderColor: typeColor(node.type) }}>
        {portrait ? <img src={portrait} alt="" aria-hidden="true" /> : (node.label || '?').charAt(0)}
      </span>
      <span className="core-tree-node-name">{node.label || node.id}</span>
      {relation && <span className="core-tree-node-relation">{relationLabel(relation)}</span>}
      {node.type && <span className="core-tree-node-type">{node.type}</span>}
    </button>
  );
}

export default function CoreTree({ nodes = [], edges = [], selectedId, onSelect, onNodeClick }) {
  if (!nodes.length) {
    return <div className="core-tree-empty">The family tree is still being gathered.</div>;
  }

  const selected = nodes.find((node) => node.id === selectedId);
  const treeRef = useRef(null);
  const nodeRefs = useRef({});
  const [drawnEdges, setDrawnEdges] = useState([]);

  const allNodes = nodes.slice().sort((a, b) => (a.label || a.id).localeCompare(b.label || b.id));

  const directEdges = selected
    ? edges.filter((edge) => edge.source === selected.id || edge.target === selected.id)
    : [];

  const nodeFor = (id) => nodes.find((node) => node.id === id);
  const parents = directEdges
    .filter((edge) => edge.relation === 'parent_of' && edge.target === selected?.id)
    .map((edge) => ({ node: nodeFor(edge.source), relation: edge.relation, edge }));
  const children = directEdges
    .filter((edge) => edge.relation === 'parent_of' && edge.source === selected?.id)
    .map((edge) => ({ node: nodeFor(edge.target), relation: edge.relation, edge }));
  const lateral = directEdges
    .filter((edge) => edge.relation !== 'parent_of')
    .map((edge) => ({
      node: nodeFor(edge.source === selected?.id ? edge.target : edge.source),
      relation: edge.relation,
      edge,
    }));

  useLayoutEffect(() => {
    if (!selected || !treeRef.current) return undefined;
    const measure = () => {
      const bounds = treeRef.current.getBoundingClientRect();
      setDrawnEdges(directEdges.map((edge) => {
        const from = nodeRefs.current[edge.source]?.getBoundingClientRect();
        const to = nodeRefs.current[edge.target]?.getBoundingClientRect();
        if (!from || !to) return null;
        const start = edge.source === selected.id ? from : to;
        const end = edge.source === selected.id ? to : from;
        return {
          ...edge,
          x1: start.left + start.width / 2 - bounds.left,
          y1: start.top + start.height / 2 - bounds.top,
          x2: end.left + end.width / 2 - bounds.left,
          y2: end.top + end.height / 2 - bounds.top,
        };
      }).filter(Boolean));
    };
    measure();
    window.addEventListener('resize', measure);
    return () => window.removeEventListener('resize', measure);
  }, [selected, directEdges.length]);

  if (!selected) {
    return (
      <div className="core-tree-picker" aria-label="Choose a figure">
        {allNodes.map((node) => (
          <CoreNode key={node.id} node={node} selectedId={selectedId} onSelect={onSelect} />
        ))}
      </div>
    );
  }

  const renderNode = ({ node, relation }) => node && (
    <CoreNode
      key={node.id}
      node={node}
      selectedId={selectedId}
      onSelect={onSelect}
      onNodeClick={onNodeClick}
      relation={relation}
      nodeRef={(element) => { nodeRefs.current[node.id] = element; }}
    />
  );

  return (
    <div className="core-tree core-tree-focused" ref={treeRef}>
      <svg className="core-tree-edges" aria-hidden="true" viewBox={`0 0 ${treeRef.current?.offsetWidth || 1} ${treeRef.current?.offsetHeight || 1}`} preserveAspectRatio="none">
        {drawnEdges.map((edge, index) => (
          <line
            key={`${edge.source}-${edge.target}-${index}`}
            x1={edge.x1}
            y1={edge.y1}
            x2={edge.x2}
            y2={edge.y2}
            className={`core-tree-edge core-tree-edge--${edge.relation || 'connected'}`}
          />
        ))}
      </svg>

      {parents.length > 0 && <div className="core-tree-band core-tree-band--parents">{parents.map(renderNode)}</div>}
      {lateral.length > 0 && <div className="core-tree-band core-tree-band--lateral">{lateral.map(renderNode)}</div>}
      <div className="core-tree-band core-tree-band--selected">{renderNode({ node: selected, relation: null })}</div>
      {children.length > 0 && <div className="core-tree-band core-tree-band--children">{children.map(renderNode)}</div>}

      {directEdges.length === 0 && <p className="core-tree-empty">No direct family relationships are recorded for this figure.</p>}
    </div>
  );
}
