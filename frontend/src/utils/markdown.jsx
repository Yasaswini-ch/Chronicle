import React from 'react';

// Renders the small subset of markdown the Oracle's response generator
// actually produces (**bold**, *italic*, ### headings, "- " bullet lists)
// as real React elements instead of showing literal asterisks/hashes.
function renderInline(line, keyPrefix) {
  const parts = [];
  const re = /\*\*(.+?)\*\*|\*(.+?)\*/g;
  let lastIndex = 0;
  let match;
  let i = 0;
  while ((match = re.exec(line))) {
    if (match.index > lastIndex) parts.push(line.slice(lastIndex, match.index));
    if (match[1] !== undefined) {
      parts.push(<strong key={`${keyPrefix}-${i++}`}>{match[1]}</strong>);
    } else {
      parts.push(<em key={`${keyPrefix}-${i++}`}>{match[2]}</em>);
    }
    lastIndex = re.lastIndex;
  }
  if (lastIndex < line.length) parts.push(line.slice(lastIndex));
  return parts;
}

export default function renderMarkdownLite(text) {
  if (!text) return null;
  const blocks = String(text).split(/\n\n+/);

  return blocks.map((block, bi) => {
    const trimmed = block.trim();

    const headingMatch = /^#{2,3}\s+(.*)$/.exec(trimmed);
    if (headingMatch) {
      return (
        <div
          key={bi}
          style={{ fontFamily: 'var(--font-heading)', fontSize: '1.05rem', color: 'var(--accent-gold)', marginTop: bi === 0 ? 0 : '12px', marginBottom: '6px' }}
        >
          {renderInline(headingMatch[1], `h${bi}`)}
        </div>
      );
    }

    const lines = trimmed.split('\n').filter(Boolean);
    if (lines.length > 0 && lines.every((l) => /^[-*]\s+/.test(l.trim()))) {
      return (
        <ul key={bi} style={{ margin: `${bi === 0 ? 0 : 10}px 0 0 18px`, padding: 0 }}>
          {lines.map((l, li) => (
            <li key={li}>{renderInline(l.trim().replace(/^[-*]\s+/, ''), `li${bi}-${li}`)}</li>
          ))}
        </ul>
      );
    }

    return (
      <p key={bi} style={{ margin: bi === 0 ? 0 : '10px 0 0 0' }}>
        {renderInline(trimmed, `p${bi}`)}
      </p>
    );
  });
}
