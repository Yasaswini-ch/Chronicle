// Real classical artwork for each myth — ancient vase paintings, museum
// statue photography, and public-domain 19th-century paintings sourced from
// Wikimedia Commons, one per myth where a genuinely fitting depiction exists.
// (The Fall of Icarus uses its own bespoke illustration instead — see
// StorybookView — since that one was a gift, not a Commons lookup.)
export const MYTH_IMAGES = {
  myth_arachne: { file: '/images/myths/myth_arachne.jpg', credit: 'René-Antoine Houasse, "Minerve et Arachne"' },
  myth_niobe: { file: '/images/myths/myth_niobe.jpg', credit: 'Roman sculpture, Niobe Group' },
  myth_bellerophon: { file: '/images/myths/myth_bellerophon.jpg', credit: 'Relief of Bellerophon, Aphrodisias' },
  myth_phaethon: { file: '/images/myths/myth_phaethon.jpg', credit: 'Classical depiction of Phaethon' },
  myth_orpheus_eurydice: { file: '/images/myths/myth_orpheus_eurydice.jpg', credit: 'Ancient textile fragment, Orpheus and Eurydice' },
  myth_pygmalion: { file: '/images/myths/myth_pygmalion.jpg', credit: 'Jean Raoux, "Pygmalion"' },
  myth_cupid_psyche: { file: '/images/myths/myth_cupid_psyche.jpg', credit: 'Fresco, Pompeii' },
  myth_echo_narcissus: { file: '/images/myths/myth_echo_narcissus.jpg', credit: 'Pompeian fresco, Narcissus' },
  myth_ceyx_alcyone: { file: '/images/myths/myth_ceyx_alcyone.jpg', credit: 'Alcyone and Ceyx transformed into halcyons' },
  myth_theseus_ariadne: { file: '/images/myths/myth_theseus_ariadne.jpg', credit: 'Fresco, House of the Coloured Capitals, Pompeii' },
  myth_medea_jason: { file: '/images/myths/myth_medea_jason.jpg', credit: 'Relief of Medea and the Peliades' },
  myth_clytemnestra: { file: '/images/myths/myth_clytemnestra.jpg', credit: 'John Collier, "Clytemnestra" (1882)' },
  myth_prometheus_fire: { file: '/images/myths/myth_prometheus_fire.jpg', credit: 'Laconian black-figure kylix, Prometheus and Atlas' },
  myth_paris_apple: { file: '/images/myths/myth_paris_apple.jpg', credit: 'Fresco fragment, The Judgement of Paris' },
  myth_hera_io: { file: '/images/myths/myth_hera_io.jpg', credit: 'Io and Argos, Naples Archaeological Museum' },
  myth_athena_medusa: { file: '/images/myths/myth_athena_medusa.jpg', credit: 'Classical Gorgon depiction' },
  myth_poseidon_odysseus: { file: '/images/myths/myth_poseidon_odysseus.jpg', credit: 'Statue of Poseidon, National Archaeological Museum, Athens' },
  myth_achilles_hector: { file: '/images/myths/myth_achilles_hector.jpg', credit: 'Achilles fighting Memnon, Rijksmuseum van Oudheden' },
  myth_atreus_thyestes: { file: '/images/myths/myth_atreus_thyestes.jpg', credit: 'Classical depiction of the House of Atreus' },
  myth_odysseus_cyclops: { file: '/images/myths/myth_odysseus_cyclops.jpg', credit: 'Greek vase painting, Polyphemus and Odysseus' },
  myth_sphinx: { file: '/images/myths/myth_sphinx.jpg', credit: 'Attic red-figure pelike, Oedipus and the Sphinx' },
  myth_midas: { file: '/images/myths/myth_midas.jpg', credit: 'Red-figure stamnos, Silenus and Midas' },
  myth_athena_poseidon: { file: '/images/myths/myth_athena_poseidon.jpg', credit: 'Mattei Athena, Musée du Louvre' },
  myth_aphrodite_psyche: { file: '/images/myths/myth_aphrodite_psyche.jpg', credit: 'Cnidus Aphrodite, Palazzo Altemps' },
};

export function mythImageFor(mythId) {
  return MYTH_IMAGES[mythId] || null;
}
