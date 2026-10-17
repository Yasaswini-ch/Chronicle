import React from 'react';
import useReveal from '../hooks/useReveal';

/**
 * Wraps any block of content and animates it in (fade + rise) the moment it
 * scrolls into view. `delay` (ms) staggers siblings; `as` picks the wrapper tag.
 */
export default function Reveal({ children, delay = 0, as: Tag = 'div', className = '', style = {}, ...rest }) {
  const [ref, visible] = useReveal();
  return (
    <Tag
      ref={ref}
      className={`reveal ${visible ? 'reveal-visible' : ''} ${className}`.trim()}
      style={{ transitionDelay: visible ? `${delay}ms` : '0ms', ...style }}
      {...rest}
    >
      {children}
    </Tag>
  );
}
