import React, { useLayoutEffect, useRef, useState } from 'react';
import { typeColor } from '../utils/colors';
import { portraitFor } from '../data/portraits';

/**
 * Renders one full connected cluster of the pantheon as a multi-generation
 * tree: every member visible at once, positioned in rows by BFS depth from
 * the cluster's most-connected figure, with real branch lines drawn between
 * measured node positions (so it's correct no matter how many children or
 * levels a cluster has — not a fixed 3-row layout).
 */
export default function ClusterTree({ cluster, onSelect }) {
  const containerRef = useRef(null);
  const nodeRefs = useRef({});
  const [lines, setLines] = useState([]);
  const [box, setBox] = useState({ width: 0, height: 0 });

  const measure = () => {
    const container = containerRef.current;
    if (!container) return;
    const containerRect = container.getBoundingClientRect();
    const nextLines = cluster.edges
      .map(({ parentId, childId, relation }) => {
        const p = nodeRefs.current[parentId]?.getBoundingClientRect();
        const c = nodeRefs.current[childId]?.getBoundingClientRect();
        if (!p || !c) return null;
        return {
          x1: p.left + p.width / 2 - containerRect.left,
          y1: p.bottom - containerRect.top,
          x2: c.left + c.width / 2 - containerRect.left,
          y2: c.top - containerRect.top,
          relation,
        };
      })
      .filter(Boolean);
    setLines(nextLines);
    setBox({ width: containerRect.width, height: containerRect.height });
  };

  useLayoutEffect(() => {
    measure();
    const onResize = () => measure();
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cluster]);

  return (
    <div ref={containerRef} className="forest-cluster">
      <svg className="forest-lines" width={box.width} height={box.height}>
        {lines.map((l, i) => {
          const midY = (l.y1 + l.y2) / 2;
          return (
            <path
              key={i}
              d={`M ${l.x1} ${l.y1} C ${l.x1} ${midY}, ${l.x2} ${midY}, ${l.x2} ${l.y2}`}
              fill="none"
              stroke="var(--border-strong)"
              strokeWidth="1.4"
            />
          );
        })}
      </svg>

      {cluster.levels.map((level, li) => (
        <div key={li} className="forest-level">
          {level.map((node) => {
            const isRoot = node.type === 'root';
            const portrait = !isRoot ? portraitFor(node.label || node.id) : null;
            return (
              <button
                key={node.id}
                ref={(el) => { nodeRefs.current[node.id] = el; }}
                className={isRoot ? 'tree-node forest-node forest-root-node' : 'tree-node forest-node'}
                style={{ borderTopColor: isRoot ? 'var(--accent-garnet)' : typeColor(node.type) }}
                onClick={() => !isRoot && onSelect && onSelect(node)}
                disabled={isRoot}
                title={isRoot ? 'An organizing node — not a mythological figure' : undefined}
              >
                {portrait && (
                  <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '4px' }}>
                    <img
                      src={portrait}
                      alt=""
                      aria-hidden="true"
                      style={{
                        width: '28px',
                        height: '28px',
                        borderRadius: '50%',
                        objectFit: 'cover',
                        border: `1.5px solid ${typeColor(node.type)}`,
                      }}
                    />
                  </div>
                )}
                <div className="tree-node-name">{node.label}</div>
                {node.type && !isRoot && (
                  <div className="tree-node-type" style={{ color: typeColor(node.type) }}>{node.type}</div>
                )}
                {isRoot && <div className="tree-node-type" style={{ color: 'var(--accent-garnet)' }}>{node.degree} family groups</div>}
              </button>
            );
          })}
        </div>
      ))}
    </div>
  );
}
