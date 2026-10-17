// Maps a handful of figures to one of the real photographs already in the
// Gallery of Antiquity, where the match is genuinely apt (the actual subject
// of that artifact). Everyone else gets a generated medallion placeholder
// instead of a fabricated or mismatched "portrait."
export const PORTRAITS = {
  zeus: '/images/gallery/zeus-artemision.jpg',
  poseidon: '/images/gallery/zeus-artemision.jpg', // the bronze's identity is debated between the two
  aphrodite: '/images/gallery/venus-de-milo.jpg',
  agamemnon: '/images/gallery/mask-of-agamemnon.jpg',
};

export function portraitFor(name) {
  return PORTRAITS[String(name || '').trim().toLowerCase()] || null;
}
