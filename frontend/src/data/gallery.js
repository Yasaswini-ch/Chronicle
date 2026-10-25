// Real photographs of famous surviving Greek sculptures, temples, sanctuaries,
// theatres, tombs and palaces — public-domain / CC images via Wikimedia Commons.
//
// kind values that route an item to the PLACES section:
//   temple · sanctuary · fortification entrance · tholos tomb · tholos (beehive) tomb
//   theatre · palace · gateway · treasury (building)
// Everything else goes to ARTIFACTS.

export const GALLERY = [

  // ─── PLACES ──────────────────────────────────────────────────────────────

  {
    id: 'parthenon',
    image: '/images/gallery/parthenon.jpg',
    title: 'The Parthenon',
    greek: 'Parthenṓn',
    kind: 'Temple, completed 438 BC',
    location: 'Acropolis of Athens',
    date: '447–438 BC',
    architect: 'Iktinos & Kallikrates; sculpture programme by Pheidias',
    material: 'Pentelic marble, bronze fittings',
    blurb:
      'Commissioned by Perikles at the height of Athenian power, the Parthenon replaced an earlier temple destroyed by the Persians in 480 BC. Its Doric colonnade — eight columns across the façade instead of the usual six — sheltered a colossal gold-and-ivory cult statue of Athena Parthenos, nearly twelve metres tall, fashioned by the sculptor Pheidias. The 160-metre Ionic frieze running around the inner block depicted the Panathenaic procession, the great civic festival held every four years in the goddess\'s honour. Converted to a Christian church in the 5th century AD, then an Ottoman mosque, the building was gutted by a Venetian cannon-ball in 1687 that ignited stored gunpowder. The shell that survives is still the most influential building ever erected.',
    mythLink: 'Athena',
  },
  {
    id: 'lion-gate-mycenae',
    image: '/images/gallery/lion-gate-mycenae.jpg',
    title: 'The Lion Gate of Mycenae',
    greek: 'Mykḗnai',
    kind: 'Fortification entrance, c. 1250 BC',
    location: 'Mycenae, Peloponnese',
    date: 'c. 1250 BC',
    architect: 'Unknown Mycenaean builders',
    material: 'Limestone; lintel stone weighs approximately 20 tonnes',
    blurb:
      'The principal gate into Agamemnon\'s legendary citadel is the oldest monumental sculpture in Europe. Three massive limestone blocks form the threshold and jambs; a triangular corbelled slab above the lintel carries a relief of two lionesses (not lions — the manes are absent) rearing on either side of a central column, their forepaws resting on its base. The empty sockets show the heads were carved separately, probably in a harder stone or metal, and are long gone. The gate controlled the only road into a city whose cyclopean walls — up to seven metres thick — enclosed palaces, shaft graves, and storerooms that fed and armed the Aegean\'s greatest Bronze-Age power. Schliemann excavated the graves just inside the gate in 1876 and found the gold mask he immediately telegraphed to the king of Greece as the face of Agamemnon.',
    mythLink: 'Agamemnon',
  },
  {
    id: 'treasury-of-atreus',
    image: '/images/gallery/treasury-of-atreus.jpg',
    title: 'The Treasury of Atreus',
    greek: 'Thēsaurós toú Atréōs',
    kind: 'Tholos (beehive) tomb, c. 1250 BC',
    location: 'Mycenae, Peloponnese',
    date: 'c. 1250 BC',
    architect: 'Unknown Mycenaean builders',
    material: 'Conglomerate stone; corbelled without mortar',
    blurb:
      'Walk thirty-six metres down a stone-lined dromos (approach corridor) and the doorway opens into a perfectly circular chamber fourteen metres across and thirteen metres high — a corbelled dome assembled without a single drop of mortar, each ring of stone slightly overlapping the one below until the courses meet at the keystone. It stood as the largest unsupported span in the world for more than a thousand years, until the Pantheon surpassed it in Rome. Grave goods and human remains had been stripped by ancient looters before the tomb was rediscovered, but the engineering alone marks it as the work of a state commanding extraordinary wealth and labour. The name "Treasury of Atreus" and the alternative "Tomb of Agamemnon" are both romantic 19th-century inventions; its true occupant is unknown.',
    mythLink: 'Agamemnon',
  },
  {
    id: 'hephaisteion',
    image: '/images/gallery/hephaisteion.jpg',
    title: 'The Temple of Hephaestus',
    greek: 'Hephaisteîon',
    kind: 'Temple, c. 450–415 BC',
    location: 'Ancient Agora of Athens',
    date: '449–415 BC',
    architect: 'Possibly Iktinos',
    material: 'Pentelic marble',
    blurb:
      'Standing on a low hill at the western edge of the Athenian Agora, the Hephaisteion is the best-preserved ancient Greek temple in the world — its full colonnade of thirty-four Doric columns still standing, its cella roofed, its frieze metopes still largely intact. Dedicated to Hephaestus, god of the forge, and Athena Ergane, patron of crafts, it overlooked the potters\' and metalworkers\' quarters of the city below. The interior once held bronze cult statues of both gods by the sculptor Alkamenes, a pupil of Pheidias. The metopes on the east and south sides depict the Labours of Heracles and the exploits of Theseus, linking the building to Athens\'s founding myths. Converted into a Christian church of St George in the 7th century AD, which ironically saved it from spoliation.',
    mythLink: 'Hephaestus',
  },
  {
    id: 'temple-poseidon-sounion',
    image: '/images/gallery/temple-poseidon-sounion.jpg',
    title: 'Temple of Poseidon at Cape Sounion',
    greek: 'Naós toú Poseidṓnos',
    kind: 'Temple, c. 444–440 BC',
    location: 'Cape Sounion, Attica',
    date: '444–440 BC',
    architect: 'Unknown; possibly the architect of the Hephaisteion',
    material: 'Local Agrileza marble',
    blurb:
      'Perched sixty metres above the Aegean on the southernmost headland of Attica, this temple was the last landmark sailors saw when leaving Athens and the first they sighted returning home. It replaced an earlier temple destroyed by the Persians. Fifteen of the original thirty-four slender Doric columns survive, and their whiteness against the sea has made the cape one of the most painted and photographed ancient sites in Greece. Byron carved his name into one of the columns during his 1810 visit — a graffito visible to this day. The temple is inseparable from the myth of Aegeus: having told his son Theseus to hoist white sails if he returned victorious from Crete, Aegeus watched from this very headland and, seeing only black sails (Theseus forgot), threw himself into the sea that now bears his name.',
    mythLink: 'Theseus',
  },
  {
    id: 'erechtheion',
    image: '/images/gallery/erechtheion.jpg',
    title: 'The Erechtheion',
    greek: 'Erektheîon',
    kind: 'Temple, 421–406 BC',
    location: 'Acropolis of Athens',
    date: '421–406 BC',
    architect: 'Mnesikles (attributed)',
    material: 'Pentelic and Eleusinian marble',
    blurb:
      'The most sacred ground on the Acropolis — where Poseidon struck his trident to produce a saltwater spring and Athena planted the first olive tree — was enclosed by this deliberately irregular Ionic temple, forced into an asymmetrical plan by the holy landmarks it had to avoid disturbing. Its most recognisable feature is the south porch: six female figures in long Ionic drapery standing in place of columns, bearing the entablature on their heads. These Caryatids — five originals are now in the Acropolis Museum — gaze calmly outward, entirely unconcerned by the weight of stone above them. The building also housed the olive-wood statue of Athena Polias, the city\'s most ancient and sacred cult image, which was dressed in a new robe at each Panathenaic festival.',
    mythLink: 'Athena',
  },
  {
    id: 'theatre-epidaurus',
    image: '/images/gallery/theatre-epidaurus.jpg',
    title: 'Theatre of Epidaurus',
    greek: 'Théatron Epidaúrou',
    kind: 'Theatre, c. 340–330 BC',
    location: 'Sanctuary of Asklepios, Epidaurus, Peloponnese',
    date: 'c. 340–330 BC',
    architect: 'Polykleitos the Younger',
    material: 'Limestone',
    blurb:
      'Carved into the northern slope of a hill in the sanctuary of Asklepios, god of medicine, the theatre at Epidaurus is the most acoustically perfect ancient auditorium ever built. Fifty-five rows of limestone seats accommodate up to fourteen thousand spectators; a coin struck in the centre of the orchestra can be heard clearly in the topmost row, with no microphone and no amplification — a fact proved in modern experiments. Polykleitos the Younger calibrated the geometry so precisely that wind direction and the natural materials suppress low-frequency noise from the audience while carrying the human voice upward. Sick pilgrims came to Epidaurus to sleep in the sanctuary\'s abaton and receive healing dreams from the god; the theatre existed to restore their spirits alongside their bodies. The site is a UNESCO World Heritage monument still in active use for performances every summer.',
    mythLink: 'Apollo',
  },
  {
    id: 'palace-knossos',
    image: '/images/gallery/palace-knossos.jpg',
    title: 'Palace of Knossos',
    greek: 'Anáktoro tēs Knōsoú',
    kind: 'Palace, c. 1700–1380 BC',
    location: 'Knossos, Crete',
    date: 'Final palace period c. 1700–1380 BC',
    architect: 'Unknown Minoan builders',
    material: 'Limestone, gypsum, cedar timber',
    blurb:
      'The largest Bronze-Age palatial complex in the Aegean, Knossos was home to the Minoan civilisation that preceded and shaped Greek culture. Its multi-storey warren of over a thousand rooms — storerooms packed with olive oil and wine, lustral basins, throne rooms, light wells, a sophisticated drainage system — gave later Greeks the myth of the Labyrinth, the maze built by Daedalus to contain the Minotaur, half-man half-bull offspring of Pasiphaë and Poseidon\'s white bull. King Minos ruled here; Theseus came here to kill the monster and was guided out by Ariadne\'s thread. Arthur Evans excavated the site from 1900 and controversially restored it in reinforced concrete, repainting the vivid frescoes — a gesture that preserved the imagery for the world but has divided archaeologists ever since.',
    mythLink: 'Theseus',
  },
  {
    id: 'propylaea',
    image: '/images/gallery/propylaea.jpg',
    title: 'The Propylaea',
    greek: 'Propylaia',
    kind: 'Gateway, 437–432 BC',
    location: 'Acropolis of Athens',
    date: '437–432 BC',
    architect: 'Mnesikles',
    material: 'Pentelic marble and Eleusinian limestone',
    blurb:
      'The monumental gateway to the Acropolis is not simply a door but a building in its own right — a central hall flanked by two unequal wings, each with its own porch, merging Doric and Ionic orders in a single structure for the first time in Greek architecture. Construction was halted by the outbreak of the Peloponnesian War and the building was never entirely finished: mounting blocks for unset column drums are still visible on the floor. The northern wing housed the Pinakotheke, a picture gallery of panel paintings. Every procession to the Parthenon passed through here, climbing the Sacred Way worn smooth by generations of sandalled feet. It remains, even incomplete, one of the most sophisticated pieces of architecture left by antiquity.',
    mythLink: 'Athena',
  },
  {
    id: 'temple-apollo-delphi',
    image: '/images/gallery/temple-apollo-delphi.jpg',
    title: 'Temple of Apollo at Delphi',
    greek: 'Naós toú Apollṓnos',
    kind: 'Temple, rebuilt 330 BC',
    location: 'Sanctuary of Apollo, Delphi',
    date: 'Third temple rebuilt 330–320 BC',
    architect: 'Spintharus, Xenodoros, Agathon',
    material: 'Poros limestone (earlier phases); limestone and marble',
    blurb:
      'Three successive temples occupied this terrace on the south slope of Mount Parnassos; the remains standing today belong to the fourth-century reconstruction after an earthquake destroyed the previous building in 373 BC. Inside the adyton — the innermost forbidden chamber — sat the Pythia, the priestess of Apollo, who breathed vapours rising from a chasm in the rock and delivered oracles to enquirers from across the Greek world. Carved on the temple\'s entrance porch were the maxims "Know thyself" (gnōthi seautón) and "Nothing in excess" (mēdèn ágan). City-states sent delegations here before every major war; Croesus of Lydia was told that if he crossed the Halys River "a great empire would be destroyed" — it was his own. Seven enormous columns of the peristyle still stand at their full height.',
    mythLink: 'Apollo',
  },
  {
    id: 'sanctuary-olympia',
    image: '/images/gallery/sanctuary-olympia.jpg',
    title: 'Sanctuary of Zeus at Olympia',
    greek: 'Témenós toú Diós',
    kind: 'Sanctuary, active from c. 10th century BC',
    location: 'Olympia, Elis, Peloponnese',
    date: 'Olympic Games established traditionally 776 BC',
    architect: 'Multiple phases; Temple of Zeus by Libon of Elis, 470–457 BC',
    material: 'Shell limestone, Pentelic marble pediments',
    blurb:
      'For over a thousand years, every four years, the ancient world fell quiet: wars were paused, safe-conduct granted to all travellers, and athletes from every Greek city converged on the plain of the Alpheios River to compete in honour of Zeus. The Altis — the sacred enclosure — held the Temple of Zeus, which contained one of the Seven Wonders of the Ancient World: Pheidias\'s colossal chryselephantine statue of Zeus enthroned, forty-two feet high, his skin ivory, his robes and throne plated with gold. The statue is gone; the temple is a field of fallen drums, thrown down by earthquakes in the 6th century AD. But the stadium — still intact, its stone starting-block in place — holds 45,000 spectators and every four years its soil is disturbed for the lighting of the Olympic flame that travels to the modern Games.',
    mythLink: 'Zeus',
  },
  {
    id: 'tholos-delphi',
    image: '/images/gallery/tholos-delphi.jpg',
    title: 'The Tholos of Delphi',
    greek: 'Thólos Delphṓn',
    kind: 'Temple (circular), c. 380–360 BC',
    location: 'Sanctuary of Athena Pronaia, Delphi',
    date: 'c. 380–360 BC',
    architect: 'Theodoros of Phokaia',
    material: 'Pentelic marble and Eleusinian limestone',
    blurb:
      'Three Doric columns and their entablature — reconstructed in the 1930s from fragments found scattered across the precinct — are all that visibly survives of one of the most elegant buildings of the classical world. The Tholos was a circular peristyle temple, twenty-one columns ringing an inner chamber built of a contrasting dark Eleusinian limestone; inside that, a second ring of ten Corinthian half-columns decorated the wall. What religious function it served at the Sanctuary of Athena Pronaia is unknown; no ancient source explains its purpose. It stands a short walk below the main sanctuary and is often the first thing visitors photograph on the road to the main oracular precinct — a photogenic mystery from which the light is perfect in the early morning.',
    mythLink: 'Athena',
  },

  // ─── ARTIFACTS ──────────────────────────────────────────────────────────

  {
    id: 'nike-samothrace',
    image: '/images/gallery/nike-samothrace.jpg',
    title: 'Winged Victory of Samothrace',
    greek: 'Níkē',
    kind: 'Sculpture, c. 200–190 BC',
    location: 'Musée du Louvre, Paris',
    blurb:
      'A monumental marble figure of Nike, goddess of victory, caught mid-descent onto the prow of a ship, her drapery still rippling with the wind. Discovered on the island of Samothrace in 1863, she has no head and no arms, yet the sheer physical energy of the figure — the forward thrust, the billowing wings, the wet drapery pressed against her body — makes her one of the most arresting objects of antiquity.',
  },
  {
    id: 'venus-de-milo',
    image: '/images/gallery/venus-de-milo.jpg',
    title: 'Venus de Milo (Aphrodite of Melos)',
    greek: 'Aphroditē',
    kind: 'Sculpture, c. 150–125 BC',
    location: 'Musée du Louvre, Paris',
    blurb:
      'The most famous surviving likeness of Aphrodite, goddess of love and beauty — found on the island of Milos in 1820, already missing both arms. The subtle spiral twist of the body and the way the drapery clings while beginning to slip give the figure a sense of arrested motion that has fascinated viewers for two centuries.',
  },
  {
    id: 'zeus-artemision',
    image: '/images/gallery/zeus-artemision.jpg',
    title: 'The Artemision Bronze',
    greek: 'Zeús (or Poseidōn)',
    kind: 'Bronze, c. 460 BC',
    location: 'National Archaeological Museum, Athens',
    blurb:
      'Pulled from a shipwreck off Cape Artemision, this bronze god strides forward with arm drawn back — scholars still argue whether he once hurled a thunderbolt (Zeus) or a trident (Poseidon). The pose captures the exact moment before release with uncanny conviction; the eyes were originally inlaid with ivory and coloured stone.',
  },
  {
    id: 'charioteer-of-delphi',
    image: '/images/gallery/charioteer-of-delphi.jpg',
    title: 'The Charioteer of Delphi',
    greek: 'Hēníokhos',
    kind: 'Bronze, c. 470 BC',
    location: 'Delphi Archaeological Museum',
    blurb:
      'A life-size bronze of a victorious charioteer, offered to Apollo at his sanctuary in Delphi — one of the few ancient bronzes to survive with its inlaid glass eyes intact. The long pleated chiton, the carefully coiffed hair beneath the headband, and the faint smile all belong to the Early Classical style, just emerging from the rigid frontality of the Archaic period.',
  },
  {
    id: 'discobolus',
    image: '/images/gallery/discobolus.jpg',
    title: 'Discobolus (The Discus Thrower)',
    greek: 'Diskobólos',
    kind: 'Sculpture, Roman copy of a c. 460–450 BC bronze by Myron',
    location: 'Various museum collections',
    blurb:
      'Myron\'s study of the human body at the exact instant of coiled potential, frozen before release — one of the most copied sculptures from antiquity. The original bronze is lost; we know it only through Roman marble copies. The figure\'s calm expression contradicts the extreme physical tension of the pose, a deliberate choice by Myron that later critics debated at length.',
  },
  {
    id: 'laocoon',
    image: '/images/gallery/laocoon.jpg',
    title: 'Laocoön and His Sons',
    greek: 'Laokóōn',
    kind: 'Sculpture, 1st century BC/AD',
    location: 'Vatican Museums, Rome',
    blurb:
      'The Trojan priest Laocoön and his two sons locked in a death struggle with sea serpents — punishment, in one telling, for warning Troy against the wooden horse. Unearthed in Rome in 1506, it was immediately recognised from Pliny\'s description as a masterpiece made by three Rhodian sculptors. Michelangelo and every subsequent generation have studied it as the supreme depiction of human agony.',
  },
  {
    id: 'mask-of-agamemnon',
    image: '/images/gallery/mask-of-agamemnon.jpg',
    title: 'The Mask of Agamemnon',
    greek: 'Agamémnōn',
    kind: 'Gold funerary mask, c. 1550–1500 BC',
    location: 'National Archaeological Museum, Athens',
    blurb:
      'A gold death mask unearthed from a royal shaft grave at Mycenae in 1876 — predating the legendary Trojan War king Agamemnon by centuries, but named for him regardless. Schliemann\'s telegram to the Greek king announced he had "gazed upon the face of Agamemnon." The mask\'s features are individualised in a way unusual for the period: a narrow moustache, a pointed beard, eyelids closed over prominent brows.',
  },
];
