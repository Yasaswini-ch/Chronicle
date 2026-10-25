// src/data/figureLore.js
// Short reference text for the figure dossier page, keyed by the figure name used in the app.
// Written as plain summaries of the standard ancient sources (Hesiod, Homer, the Homeric Hymns,
// Apollodorus). Parentage, siblings and partners are deliberately left out: the dossier reads
// those from the family data so the two never disagree.

export const FIGURE_LORE = {
  Zeus: {
    epithet: "King of the Gods, Lord of the Sky",
    realm: "Sky, thunder and Mount Olympus",
    symbol: "Thunderbolt, eagle, oak",
    overview:
      "Zeus is the ruler of the Olympian gods and the power behind sky, weather and thunder. In Hesiod he leads the Olympians to victory over the Titans and takes the sky as his domain. He also watches over oaths, justice and the duty to treat guests and strangers well.",
    symbols: [
      { name: "Thunderbolt", note: "His weapon and the sign of his power" },
      { name: "Eagle", note: "The bird that carries his thunderbolt" },
      { name: "Oak", note: "His sacred tree, linked to the oracle at Dodona" },
    ],
  },
  Hera: {
    epithet: "Queen of the Gods",
    realm: "Marriage and the family",
    symbol: "Crown, peacock, pomegranate",
    overview:
      "Hera is the queen of the Olympians and the goddess of marriage. Her cult was strongest at Argos and Samos. In many myths she appears as a fierce defender of her status, pursuing the lovers and children of her husband with long grudges.",
    symbols: [
      { name: "Crown", note: "Marks her as queen of the gods" },
      { name: "Peacock", note: "A bird linked to her in later tradition" },
      { name: "Pomegranate", note: "Carried by her cult statue at Argos" },
    ],
  },
  Poseidon: {
    epithet: "Lord of the Sea",
    realm: "The sea, earthquakes and horses",
    symbol: "Trident, horse, dolphin",
    overview:
      "Poseidon rules the sea and is also the god who shakes the earth. Sailors prayed to him for safe voyages, and he was honored as the creator of the horse. In the Odyssey his anger at Odysseus drives much of the hero's long journey home.",
    symbols: [
      { name: "Trident", note: "A three-pronged spear that stirs the sea" },
      { name: "Horse", note: "An animal closely tied to his cult" },
      { name: "Dolphin", note: "A sea creature often shown beside him" },
    ],
  },
  Demeter: {
    epithet: "Goddess of the Harvest",
    realm: "Grain, harvest and the seasons of farming",
    symbol: "Ears of grain, torch, poppy",
    overview:
      "Demeter is the goddess of grain and the harvest. In the Homeric Hymn to Demeter she searches the world for her lost daughter Persephone and lets the earth go barren until her daughter returns. Her cult at Eleusis became one of the most important mystery rites of the Greek world.",
    symbols: [
      { name: "Ears of grain", note: "The crop she gave to humankind" },
      { name: "Torch", note: "Carried on her search for Persephone" },
      { name: "Poppy", note: "A flower often shown in her hand in art" },
    ],
  },
  Athena: {
    epithet: "Goddess of Wisdom and Craft",
    realm: "Wisdom, craft and strategic warfare",
    symbol: "Owl, olive tree, aegis",
    overview:
      "Athena is the goddess of wisdom, skilled work and clever warfare, and the patron of Athens. She backs heroes who rely on intelligence, such as Odysseus and Perseus. Her contest with Poseidon over Athens ended when the city chose her gift of the olive tree.",
    symbols: [
      { name: "Owl", note: "A bird of wisdom, stamped on Athenian coins" },
      { name: "Olive tree", note: "Her gift to the city of Athens" },
      { name: "Aegis", note: "A protective goatskin cloak worn on her chest" },
    ],
  },
  Apollo: {
    epithet: "God of Light, Music and Prophecy",
    realm: "Light, music, prophecy and healing",
    symbol: "Lyre, laurel, bow",
    overview:
      "Apollo is the god of music, prophecy, healing and archery. His oracle at Delphi was the most consulted in the Greek world. Myths about him often show the limits of his gifts, such as his failed love for Daphne, who became a laurel tree.",
    symbols: [
      { name: "Lyre", note: "The instrument he plays and teaches" },
      { name: "Laurel", note: "His sacred plant, from the story of Daphne" },
      { name: "Bow", note: "The weapon of the far-shooting god" },
    ],
  },
  Artemis: {
    epithet: "Goddess of the Wild",
    realm: "The hunt, wild animals and wild places",
    symbol: "Bow, deer, crescent moon",
    overview:
      "Artemis is the goddess of the hunt and of wild places and animals. She is a maiden goddess who guards her independence and punishes those who intrude on her, as in the story of Actaeon. Later tradition links her with the moon.",
    symbols: [
      { name: "Bow and arrows", note: "Her hunting weapons" },
      { name: "Deer", note: "An animal sacred to her" },
      { name: "Crescent moon", note: "A sign added in later tradition" },
    ],
  },
  Ares: {
    epithet: "God of War",
    realm: "War and battle",
    symbol: "Spear, helmet, shield",
    overview:
      "Ares is the god of war, shown in Homer as violent and unpopular, even among the other gods. He stands for the raw fury of battle, while Athena stands for strategy. His affair with Aphrodite is one of the best-known stories about him.",
    symbols: [
      { name: "Spear", note: "His main weapon" },
      { name: "Helmet", note: "Part of the armor that marks him as a warrior" },
      { name: "Shield", note: "A sign of the battlefield" },
    ],
  },
  Aphrodite: {
    epithet: "Goddess of Love and Beauty",
    realm: "Love, desire and beauty",
    symbol: "Dove, myrtle, scallop shell",
    overview:
      "Aphrodite is the goddess of love, beauty and desire. In Hesiod she rises from the sea foam, and her power over desire affects gods and mortals alike. She plays a central part in the story of the Trojan War, where the promise of Helen sets events in motion.",
    symbols: [
      { name: "Dove", note: "A bird closely tied to her cult" },
      { name: "Myrtle", note: "A plant sacred to her" },
      { name: "Scallop shell", note: "Recalls her birth from the sea" },
    ],
  },
  Hephaestus: {
    epithet: "God of Fire and the Forge",
    realm: "Fire, metalwork and craftsmen",
    symbol: "Hammer, anvil, tongs",
    overview:
      "Hephaestus is the god of fire and the forge, and the craftsman of the gods. In the Iliad he makes new armor for Achilles, including the famous shield. He is usually shown as lame, and in the Odyssey he traps his wife Aphrodite and Ares in a fine net.",
    symbols: [
      { name: "Hammer", note: "His main tool at the forge" },
      { name: "Anvil", note: "Where he shapes metal for gods and heroes" },
      { name: "Tongs", note: "Used to handle the burning metal" },
    ],
  },
  Hermes: {
    epithet: "Messenger of the Gods",
    realm: "Messages, travelers, trade and the road",
    symbol: "Caduceus, winged sandals, traveler's hat",
    overview:
      "Hermes is the messenger of the gods and the patron of travelers, traders and thieves. He also guides the souls of the dead to the underworld. Stories about him stress speed and cunning, from his theft of Apollo's cattle as a baby to his help for heroes such as Perseus and Odysseus.",
    symbols: [
      { name: "Caduceus", note: "A herald's staff with two entwined snakes" },
      { name: "Winged sandals", note: "They carry him between the worlds" },
      { name: "Traveler's hat", note: "A wide-brimmed hat for the road" },
    ],
  },
  Dionysus: {
    epithet: "God of Wine and Festival",
    realm: "Wine, festivity and theater",
    symbol: "Grapevine, thyrsus, ivy",
    overview:
      "Dionysus is the god of wine, festivals and ecstatic ritual, and the patron of Greek theater. His cult breaks the usual limits of everyday life, which is why his stories often show both joy and danger. He is one of the few gods in myth who is born from a mortal mother.",
    symbols: [
      { name: "Grapevine", note: "The plant that gives wine" },
      { name: "Thyrsus", note: "A staff topped with a pine cone and wrapped in ivy" },
      { name: "Ivy", note: "A plant worn in his wreaths" },
    ],
  },
  Hades: {
    epithet: "Lord of the Underworld",
    realm: "The underworld and the dead",
    symbol: "Helm of invisibility, Cerberus, bident",
    overview:
      "Hades rules the underworld, the realm of the dead, and the name belongs both to the god and to his kingdom. He seldom leaves it. His best-known story is the abduction of Persephone, which ties him to the seasons through her yearly return to the earth.",
    symbols: [
      { name: "Helm of invisibility", note: "A cap that hides its wearer" },
      { name: "Cerberus", note: "The hound that guards the entrance to his realm" },
      { name: "Bident", note: "A two-pronged staff shown in art" },
    ],
  },
  Hestia: {
    epithet: "Goddess of the Hearth",
    realm: "The hearth, home and household",
    symbol: "Hearth fire, sacred flame",
    overview:
      "Hestia is the goddess of the hearth and the home. She plays almost no part in the stories, but she held a central place in daily worship. A Homeric Hymn to Hestia says she receives the first offering at every sacrifice.",
    symbols: [
      { name: "Hearth fire", note: "The center of every Greek household" },
      { name: "Sacred flame", note: "Kept burning in the public hearth of a city" },
    ],
  },
};
