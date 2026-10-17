import React from 'react';

/**
 * Previously wrapped a word in a hover/tap popover with a glossary
 * definition. Removed after the popover's position repeatedly broke across
 * different parts of the page in ways that weren't pinned down — rather
 * than keep shipping a broken interaction, this now just renders the word
 * as plain text. Every call site (`<Term word="...">text</Term>`) still
 * works unchanged; it just no longer does anything special.
 */
export default function Term({ children }) {
  return <>{children}</>;
}
