// Plain-language glossary for visitors with zero prior knowledge of Greek mythology.
// Keys are matched case-insensitively against badge labels, character types, and in-text terms.
export const GLOSSARY = {
  titan: {
    term: 'Titan',
    definition:
      'One of the elder gods who ruled the universe before the Olympians. The Titans were the children of Gaia (Earth) and Ouranos (Sky). Zeus and his siblings overthrew them in a great war and took their place as rulers of the cosmos.',
  },
  god: {
    term: 'God / Goddess (Olympian)',
    definition:
      'An immortal, all-powerful being who presides over one or more of the twelve thrones of Mount Olympus — the mountain-top home of the gods. Each Olympian governs a domain of life: Zeus rules the sky, Poseidon the sea, Athena wisdom and war-craft, and so on.',
  },
  mortal: {
    term: 'Mortal',
    definition:
      'A human being — king, queen, inventor, or ordinary person — who can die, unlike the gods. Many of the most memorable Greek myths are really about mortals testing, defying, or being tested by the immortals.',
  },
  creature: {
    term: 'Creature',
    definition:
      'A mythical being that is neither a full god nor an ordinary human — monsters, hybrid beasts, and enchanted animals such as the Sphinx, the Cyclops, or Pegasus the winged horse.',
  },
  pantheon: {
    term: 'Pantheon',
    definition:
      'The complete family of gods worshipped by a culture. "The Greek pantheon" means all of the Greek gods considered together, usually pictured living together on Mount Olympus.',
  },
  olympian: {
    term: 'Olympian',
    definition:
      'One of the ruling gods who lives on Mount Olympus, the highest mountain in Greece. The Olympians won their power by defeating the older Titans.',
  },
  chthonic: {
    term: 'Chthonic',
    definition:
      '(pronounced "THON-ic") Belonging to the underworld or the depths of the earth, rather than the sky. Hades and the spirits of the dead are chthonic.',
  },
  hubris: {
    term: 'Hubris',
    definition:
      'Dangerous, excessive pride — the belief that you can defy fate or the gods and get away with it. Hubris is the single most common reason a Greek hero falls; it is almost always punished.',
  },
  nemesis: {
    term: 'Nemesis',
    definition:
      'Originally the goddess of retribution, who made sure hubris never went unpunished. Today the word means "the downfall someone brings upon themselves."',
  },
  fate: {
    term: 'Fate',
    definition:
      'In Greek belief, the thread of a person’s life, spun, measured, and cut by the three Fates (Moirai). Even the gods could not undo what Fate decreed — only delay it.',
  },
  oracle: {
    term: 'Oracle',
    definition:
      'A priest or priestess believed to speak prophecy on behalf of a god — most famously the Oracle of Delphi, who spoke for Apollo. People traveled great distances to ask an oracle about their future.',
  },
  nymph: {
    term: 'Nymph',
    definition:
      'A minor nature spirit, almost always female, tied to a particular place — a spring, a tree, a mountain, or the sea. Nymphs are immortal-ish (very long-lived) but not true gods.',
  },
  muse: {
    term: 'Muse',
    definition:
      'One of nine goddesses, daughters of Zeus, who inspire poetry, music, dance, and the arts. We still say someone is "my muse" when they inspire our creative work.',
  },
  labyrinth: {
    term: 'Labyrinth',
    definition:
      'A vast maze built by the inventor Daedalus on Crete to contain the Minotaur. The word now means any confusing, winding structure.',
  },
  underworld: {
    term: 'The Underworld',
    definition:
      'The realm of the dead, ruled by Hades. Not a place of punishment for everyone (that is only for the wicked) — simply where every soul goes after death.',
  },
  apotheosis: {
    term: 'Apotheosis',
    definition: 'The moment a mortal is raised up and made into a god — the ultimate reward in Greek myth.',
  },
  epithet: {
    term: 'Epithet',
    definition:
      'A descriptive nickname attached to a god’s name, like "Zeus, Father of Gods and Men" or "Athena of the Flashing Eyes." Epithets highlight one part of a god’s identity.',
  },
};

// Themes that appear in the Chronicle corpus — explained for a first-time reader.
export const THEME_GUIDE = {
  hubris: 'A character becomes too proud or ambitious, defies a warning or a god, and pays for it.',
  love: 'Devotion, longing, or romance — between gods, mortals, or impossible pairs of both.',
  betrayal: 'Trust is broken — by a lover, a friend, a family member, or a god.',
  revenge: 'A wrong is repaid, often generations later and often worse than the original offense.',
  wisdom: 'A character gains (or lacks) insight, cunning, or self-knowledge, usually through hardship.',
  jealousy: 'Envy — of beauty, power, or love — drives a god or mortal to act.',
  transformation: 'Someone is changed into a tree, an animal, a stone or a star — usually as punishment, rescue, or reward.',
  quest: 'A journey, voyage or set of labours that tests a hero against monsters, gods and the sea.',
  loss: 'Death, mourning and the underworld: what mortals must give up, and what they try to win back.',
};

export function lookupTerm(raw) {
  if (!raw) return null;
  const key = String(raw).trim().toLowerCase();
  if (GLOSSARY[key]) return GLOSSARY[key];
  if (THEME_GUIDE[key]) return { term: `Theme: ${key}`, definition: THEME_GUIDE[key] };
  return null;
}
