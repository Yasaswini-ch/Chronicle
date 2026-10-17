// Maps a character "type" or myth "theme" to its dedicated accent color
// variable, so Gods, Titans, Mortals, and Creatures (and each theme) read
// as visually distinct rather than everything sharing one gold accent.
export function typeColor(type) {
  const key = String(type || '').trim().toLowerCase();
  const map = {
    god: 'var(--type-god)',
    titan: 'var(--type-titan)',
    mortal: 'var(--type-mortal)',
    creature: 'var(--type-creature)',
    location: 'var(--type-location)',
    artifact: 'var(--type-artifact)',
  };
  return map[key] || 'var(--accent-gold)';
}

export function themeColor(theme) {
  const key = String(theme || '').trim().toLowerCase();
  const map = {
    hubris: 'var(--theme-hubris)',
    love: 'var(--theme-love)',
    betrayal: 'var(--theme-betrayal)',
    revenge: 'var(--theme-revenge)',
    wisdom: 'var(--theme-wisdom)',
    jealousy: 'var(--theme-jealousy)',
    transformation: 'var(--theme-transformation)',
    quest: 'var(--theme-quest)',
    loss: 'var(--theme-loss)',
  };
  return map[key] || 'var(--accent-gold)';
}
