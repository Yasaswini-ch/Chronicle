import json
import os

myths = [
    {
        "id": "myth_icarus",
        "title": "The Fall of Icarus",
        "text": "Daedalus, a brilliant Athenian inventor, and his son Icarus were imprisoned in the Labyrinth of Crete by King Minos. Desperate to escape, Daedalus crafted two pairs of wings out of feathers and wax. Before they took flight, Daedalus warned his son not to fly too close to the sea, lest the dampness clog his wings, nor too close to the sun, lest the heat melt the wax. However, upon experiencing the sheer thrill of flight, Icarus was overcome with hubris. He soared higher and higher, ignoring his father's frantic warnings. The blazing sun melted the wax holding the feathers together, and Icarus plummeted into the sea and drowned. The heartbroken Daedalus named the sea the Icarian Sea in his memory. This tragedy stands as a timeless warning against reckless ambition and the failure to heed wise counsel.",
        "theme": "hubris",
        "characters": [
            {"name": "Icarus", "type": "mortal"},
            {"name": "Daedalus", "type": "mortal"},
            {"name": "King Minos", "type": "mortal"}
        ],
        "relationships": [
            {"source": "Daedalus", "target": "Icarus", "relation": "parent_of"},
            {"source": "Icarus", "target": "Daedalus", "relation": "child_of"}
        ],
        "locations": ["Crete", "Labyrinth", "Icarian Sea"],
        "artifacts": ["Wings of wax and feathers"],
        "moral": "Do not let hubris and reckless ambition overcome wisdom and caution.",
        "source": "Ovid's Metamorphoses"
    },
    {
        "id": "myth_arachne",
        "title": "Athena and Arachne",
        "text": "Arachne was a mortal woman possessing extraordinary skill in weaving, yet she was deeply flawed by her immense arrogance. She dared to boast that her weaving was superior even to that of Athena, the goddess of crafts and wisdom. Offended by this hubris, Athena disguised herself as an old woman and warned Arachne not to offend the gods. Unrepentant, Arachne challenged the goddess to a contest. Athena wove a magnificent tapestry depicting the glory of the Olympian gods and the tragic fates of mortals who defied them. Arachne, however, wove a flawless but disrespectful tapestry highlighting the gods' infidelities and flaws. Though Arachne's work was technically perfect, Athena was enraged by the mortal's disrespect. She tore the tapestry to shreds and struck Arachne. In despair, Arachne hung herself, but Athena transformed the rope into a web and Arachne into a spider, condemning her and her descendants to weave for eternity.",
        "theme": "hubris",
        "characters": [
            {"name": "Arachne", "type": "mortal"},
            {"name": "Athena", "type": "god"}
        ],
        "relationships": [
            {"source": "Athena", "target": "Arachne", "relation": "enemy_of"}
        ],
        "locations": ["Lydia"],
        "artifacts": ["Tapestry", "Loom"],
        "moral": "Never boast of surpassing the gods, for mortal pride leads to divine punishment.",
        "source": "Ovid's Metamorphoses"
    },
    {
        "id": "myth_niobe",
        "title": "The Tears of Niobe",
        "text": "Niobe, the Queen of Thebes, was blessed with fourteen beautiful children: seven sons and seven daughters. Consumed by pride, she foolishly mocked Leto, the mother of only two gods, Apollo and Artemis. Niobe demanded that the people of Thebes worship her instead of Leto, claiming her fertility made her superior. Enraged by this sacrilege, Leto dispatched her twin children to punish the queen's hubris. Apollo descended and shot down all seven of Niobe's sons with his golden arrows, while Artemis struck down her seven daughters with her silver arrows. Devastated and inconsolable, Niobe fled to Mount Sipylus in Asia Minor, where she wept endlessly for her lost children. Taking pity on her eternal sorrow, the gods transformed her into a stone. Yet, even as a rock, she continued to weep, the water trickling down the stone serving as a perpetual reminder of the cost of divine retribution.",
        "theme": "hubris",
        "characters": [
            {"name": "Niobe", "type": "mortal"},
            {"name": "Leto", "type": "god"},
            {"name": "Apollo", "type": "god"},
            {"name": "Artemis", "type": "god"}
        ],
        "relationships": [
            {"source": "Niobe", "target": "Apollo", "relation": "enemy_of"},
            {"source": "Apollo", "target": "Niobe", "relation": "killed_by"}
        ],
        "locations": ["Thebes", "Mount Sipylus"],
        "artifacts": ["Golden arrows", "Silver arrows"],
        "moral": "Pride and boasting against the divine will inevitably bring total ruin.",
        "source": "Ovid's Metamorphoses"
    },
    {
        "id": "myth_bellerophon",
        "title": "Bellerophon and Pegasus",
        "text": "Bellerophon was a great hero of Corinth who managed to capture the legendary winged horse, Pegasus, using a golden bridle given to him by Athena. Riding Pegasus, Bellerophon accomplished incredible feats, most notably slaying the monstrous Chimera—a terrifying beast with the head of a lion, the body of a goat, and the tail of a serpent. With Pegasus by his side, Bellerophon defeated the fierce Amazons and thwarted numerous assassins. However, his unprecedented successes swelled his ego to dangerous proportions. Believing himself worthy of dwelling among the gods, he mounted Pegasus and attempted to fly to Mount Olympus. Zeus, angered by the hero's immense hubris, sent a gadfly to sting Pegasus. The winged horse bucked in pain, throwing Bellerophon back down to Earth. Bellerophon survived the fall but was blinded and crippled, spending the rest of his life wandering alone in misery.",
        "theme": "hubris",
        "characters": [
            {"name": "Bellerophon", "type": "mortal"},
            {"name": "Pegasus", "type": "creature"},
            {"name": "Zeus", "type": "god"},
            {"name": "Chimera", "type": "creature"}
        ],
        "relationships": [
            {"source": "Bellerophon", "target": "Chimera", "relation": "killed_by"}
        ],
        "locations": ["Corinth", "Mount Olympus", "Lycia"],
        "artifacts": ["Golden Bridle"],
        "moral": "Do not attempt to elevate yourself to the status of gods, for mortals must know their place.",
        "source": "Pindar's Olympian Odes"
    },
    {
        "id": "myth_phaethon",
        "title": "The Ride of Phaethon",
        "text": "Phaethon, a proud young mortal, sought out his father, Helios the sun god, to prove his divine lineage. Helios swore an oath by the River Styx to grant the boy any wish. To Helios's horror, Phaethon demanded to drive the sun chariot for a single day. Bound by his solemn vow, Helios reluctantly agreed but warned his son of the immense danger, for the immortal horses were powerful and the path perilous. Phaethon took the reins, but the fiery horses quickly sensed his weak grip and lack of authority. They veered off course, soaring too high and freezing the earth, then plunging too low, scorching the land and creating vast deserts. As the world faced utter destruction, Zeus had no choice but to intervene. He struck Phaethon down with a thunderbolt. The boy plunged from the sky like a falling star into the River Eridanos, dead due to his own foolish ambition.",
        "theme": "hubris",
        "characters": [
            {"name": "Phaethon", "type": "mortal"},
            {"name": "Helios", "type": "god"},
            {"name": "Zeus", "type": "god"}
        ],
        "relationships": [
            {"source": "Helios", "target": "Phaethon", "relation": "parent_of"}
        ],
        "locations": ["River Eridanos", "The Sky"],
        "artifacts": ["Sun Chariot"],
        "moral": "Reckless ambition without the necessary skill leads to catastrophic failure.",
        "source": "Ovid's Metamorphoses"
    },
    {
        "id": "myth_orpheus_eurydice",
        "title": "Orpheus and Eurydice",
        "text": "Orpheus, the greatest musician in the world, fell deeply in love with a beautiful nymph named Eurydice. Their happiness was abruptly shattered on their wedding day when Eurydice was fatally bitten by a venomous snake. Overwhelmed by grief, Orpheus descended into the Underworld, armed only with his lyre. He played a melody so heartbreakingly beautiful that it softened the cold hearts of Hades and Persephone. They agreed to let Eurydice return to the land of the living on one condition: Orpheus must walk ahead of her and never look back until they both reached the surface. The journey was long and silent. Just as Orpheus stepped into the sunlight, a wave of doubt washed over him. Desperate to know if she was truly there, he turned around. He saw Eurydice for a fleeting moment before she was pulled back into the shadows forever, lost to him due to his tragic lack of trust.",
        "theme": "love",
        "characters": [
            {"name": "Orpheus", "type": "mortal"},
            {"name": "Eurydice", "type": "mortal"},
            {"name": "Hades", "type": "god"},
            {"name": "Persephone", "type": "god"}
        ],
        "relationships": [
            {"source": "Orpheus", "target": "Eurydice", "relation": "married_to"},
            {"source": "Eurydice", "target": "Orpheus", "relation": "married_to"}
        ],
        "locations": ["Underworld", "Thrace"],
        "artifacts": ["Lyre"],
        "moral": "Love requires absolute trust and patience to overcome the darkest trials.",
        "source": "Virgil's Georgics"
    },
    {
        "id": "myth_pygmalion",
        "title": "Pygmalion and Galatea",
        "text": "Pygmalion was a talented sculptor in Cyprus who had grown utterly disgusted by the flaws and vices of mortal women. Resolving to live a celibate life, he devoted all his passion to his art. He spent months carving a magnificent statue of a woman out of pure, flawless ivory. The sculpture was so exquisitely beautiful and lifelike that Pygmalion inevitably fell deeply in love with his own creation. He named her Galatea, dressing her in fine silks and bringing her gifts, treating her as if she were a living bride. During the festival of Aphrodite, Pygmalion offered a fervent prayer at the altar, begging the goddess of love for a bride just like his ivory statue. Moved by the sincerity of his devotion, Aphrodite granted his wish. When Pygmalion returned home and kissed the statue's cold lips, he felt warmth radiating from the ivory. Galatea came to life, and the two were happily married.",
        "theme": "love",
        "characters": [
            {"name": "Pygmalion", "type": "mortal"},
            {"name": "Galatea", "type": "mortal"},
            {"name": "Aphrodite", "type": "god"}
        ],
        "relationships": [
            {"source": "Pygmalion", "target": "Galatea", "relation": "married_to"}
        ],
        "locations": ["Cyprus"],
        "artifacts": ["Ivory Statue"],
        "moral": "True devotion and pure love can bring even the most impossible dreams to life.",
        "source": "Ovid's Metamorphoses"
    },
    {
        "id": "myth_cupid_psyche",
        "title": "Cupid and Psyche",
        "text": "Psyche was a mortal princess whose beauty was so astounding that mortals began worshipping her instead of Aphrodite. Infuriated by this jealousy, Aphrodite ordered her son, Cupid (Eros), to make Psyche fall in love with a hideous monster. However, upon seeing her, Cupid accidentally pricked himself with his own arrow and fell madly in love. Psyche was taken to a magnificent hidden palace where her mysterious husband visited her only under the cover of darkness, forbidding her from ever seeing his face. Manipulated by her envious sisters, Psyche lit an oil lamp one night to see him. She discovered the beautiful god of love but accidentally spilled hot oil on his shoulder, awakening him. Betrayed by her lack of trust, Cupid fled. Desperate, Psyche underwent seemingly impossible, grueling trials set by a vindictive Aphrodite. Her unwavering perseverance ultimately moved the gods. Zeus granted her immortality, and Psyche and Cupid were joyously reunited forever.",
        "theme": "love",
        "characters": [
            {"name": "Psyche", "type": "mortal"},
            {"name": "Cupid", "type": "god"},
            {"name": "Aphrodite", "type": "god"}
        ],
        "relationships": [
            {"source": "Cupid", "target": "Psyche", "relation": "married_to"},
            {"source": "Psyche", "target": "Cupid", "relation": "married_to"},
            {"source": "Aphrodite", "target": "Cupid", "relation": "parent_of"}
        ],
        "locations": ["Mount Olympus", "Underworld", "Cupid's Palace"],
        "artifacts": ["Golden Arrows", "Oil Lamp"],
        "moral": "True love can only flourish where there is unwavering trust.",
        "source": "Apuleius' The Golden Ass"
    },
    {
        "id": "myth_echo_narcissus",
        "title": "Echo and Narcissus",
        "text": "Echo was a beautiful but exceedingly talkative wood nymph. Because she constantly distracted Hera with her endless chatter to cover up Zeus's affairs, the furious queen of the gods cursed Echo to only repeat the last words spoken to her. Sometime later, Echo fell deeply in love with a breathtakingly handsome young hunter named Narcissus. Tragically, she could not express her feelings, and the cruel Narcissus brutally rejected her. Heartbroken, Echo faded away until nothing was left but her voice. To punish Narcissus for his overwhelming arrogance and cruelty, the goddess Nemesis lured him to a pristine pool. There, Narcissus saw his own reflection in the water and immediately fell desperately in love with it. Unable to pull himself away from his own image, he eventually withered away and died of starvation beside the water. In his place, a beautiful flower sprang up, bearing his name.",
        "theme": "love",
        "characters": [
            {"name": "Echo", "type": "mortal"},
            {"name": "Narcissus", "type": "mortal"},
            {"name": "Hera", "type": "god"},
            {"name": "Nemesis", "type": "god"}
        ],
        "relationships": [
            {"source": "Echo", "target": "Narcissus", "relation": "lover_of"},
            {"source": "Nemesis", "target": "Narcissus", "relation": "enemy_of"}
        ],
        "locations": ["Mount Helicon", "A clear pool"],
        "artifacts": [],
        "moral": "Vanity and self-obsession destroy the soul, while unrequited love can consume it.",
        "source": "Ovid's Metamorphoses"
    },
    {
        "id": "myth_ceyx_alcyone",
        "title": "Ceyx and Alcyone",
        "text": "Ceyx, the king of Trachis, and his beloved wife Alcyone shared a profound and unbreakable bond. Despite Alcyone's desperate pleas and terrifying premonitions, Ceyx insisted on making a perilous sea voyage to consult an oracle. Tragically, a violent storm shattered his ship, and Ceyx drowned, praying for Alcyone with his final breath. Meanwhile, unaware of his death, Alcyone continually prayed to Hera for his safe return. Pitying her devotion, Hera sent a dream to reveal the tragic truth. The next morning, a devastated Alcyone found Ceyx's lifeless body washing ashore. Overcome with immense grief, she threw herself into the pounding waves to join him in death. Moved by their immense and undying love, the gods mercifully transformed both husband and wife into halcyon birds (kingfishers). It is said that every winter, Aeolus, the god of winds, calms the turbulent seas for seven days so Alcyone can safely lay her eggs.",
        "theme": "love",
        "characters": [
            {"name": "Ceyx", "type": "mortal"},
            {"name": "Alcyone", "type": "mortal"},
            {"name": "Hera", "type": "god"}
        ],
        "relationships": [
            {"source": "Ceyx", "target": "Alcyone", "relation": "married_to"},
            {"source": "Alcyone", "target": "Ceyx", "relation": "married_to"}
        ],
        "locations": ["Trachis", "The Aegean Sea"],
        "artifacts": [],
        "moral": "True love transcends even the boundaries of death.",
        "source": "Ovid's Metamorphoses"
    },
    {
        "id": "myth_theseus_ariadne",
        "title": "Theseus and Ariadne",
        "text": "When the heroic Theseus arrived in Crete as a sacrificial tribute to the fearsome Minotaur, Princess Ariadne instantly fell in love with him. Desperate to save him from a gruesome death in the Labyrinth, she betrayed her father, King Minos, and gave Theseus a ball of magical thread to trace his path back. Following his victory over the beast, Theseus fled Crete, taking Ariadne with him. However, when they stopped at the island of Naxos to rest, Theseus abandoned the sleeping princess on the shore. Some say he did so out of divine command, while others claim he simply tired of her. When Ariadne awoke, she found herself utterly betrayed and alone, weeping bitterly at the horizon. Fortunately, the god Dionysus soon discovered the heartbroken princess, fell deeply in love with her, and made her his divine wife, placing her wedding crown among the stars as the constellation Corona Borealis.",
        "theme": "betrayal",
        "characters": [
            {"name": "Theseus", "type": "mortal"},
            {"name": "Ariadne", "type": "mortal"},
            {"name": "Minotaur", "type": "creature"},
            {"name": "Dionysus", "type": "god"}
        ],
        "relationships": [
            {"source": "Ariadne", "target": "Theseus", "relation": "lover_of"},
            {"source": "Theseus", "target": "Ariadne", "relation": "enemy_of"},
            {"source": "Dionysus", "target": "Ariadne", "relation": "married_to"}
        ],
        "locations": ["Crete", "Labyrinth", "Naxos"],
        "artifacts": ["Ball of thread", "Corona Borealis"],
        "moral": "Those who break vows of love and loyalty will face their own reckoning.",
        "source": "Plutarch's Life of Theseus"
    },
    {
        "id": "myth_medea_jason",
        "title": "Medea and Jason",
        "text": "To win the fabled Golden Fleece, the Greek hero Jason required the dark magic of Medea, a powerful sorceress and princess of Colchis. Medea fell deeply in love with him, betraying her father and murdering her own brother to secure Jason's escape. They lived as exiles in Corinth, raising two sons. However, Jason's ambitions led him to ruthlessly betray Medea; he arranged to marry Glauce, the daughter of the Corinthian king, to secure political power. Enraged by this ultimate betrayal, Medea exacted a horrifying revenge. She sent a poisoned golden dress to the young bride, which consumed Glauce and her father in magical flames. To completely destroy Jason's lineage and inflict maximum pain, Medea then murdered her own beloved sons. As Jason watched in horror, Medea escaped on a chariot drawn by winged dragons, leaving the hero to die alone and disgraced.",
        "theme": "betrayal",
        "characters": [
            {"name": "Medea", "type": "mortal"},
            {"name": "Jason", "type": "mortal"},
            {"name": "Glauce", "type": "mortal"}
        ],
        "relationships": [
            {"source": "Medea", "target": "Jason", "relation": "married_to"},
            {"source": "Jason", "target": "Medea", "relation": "enemy_of"}
        ],
        "locations": ["Colchis", "Corinth"],
        "artifacts": ["Golden Fleece", "Poisoned Dress", "Dragon Chariot"],
        "moral": "The breaking of sacred oaths invites terrifying and devastating retribution.",
        "source": "Euripides' Medea"
    },
    {
        "id": "myth_clytemnestra",
        "title": "The Murder of Agamemnon",
        "text": "Before sailing for Troy, King Agamemnon sacrificed his own daughter, Iphigenia, to appease the goddess Artemis and secure favorable winds for his massive fleet. His wife, Queen Clytemnestra, never forgave him for this horrific betrayal of their family. While Agamemnon fought the ten-year Trojan War, Clytemnestra took a lover, Aegisthus, and plotted her dark revenge. When the victorious king finally returned to Mycenae, bearing the prophetess Cassandra as his captive prize, Clytemnestra welcomed him with false warmth, laying down a purple tapestry for him to walk upon. As Agamemnon bathed, relaxing after a decade of brutal war, Clytemnestra threw a heavy net over him and brutally hacked him to death with an axe, while Aegisthus murdered Cassandra. Clytemnestra claimed the throne, arguing her act was a justified execution, thus continuing the bloody curse upon the House of Atreus.",
        "theme": "betrayal",
        "characters": [
            {"name": "Clytemnestra", "type": "mortal"},
            {"name": "Agamemnon", "type": "mortal"},
            {"name": "Aegisthus", "type": "mortal"},
            {"name": "Cassandra", "type": "mortal"}
        ],
        "relationships": [
            {"source": "Clytemnestra", "target": "Agamemnon", "relation": "married_to"},
            {"source": "Clytemnestra", "target": "Agamemnon", "relation": "killed_by"}
        ],
        "locations": ["Mycenae", "Aulis"],
        "artifacts": ["Purple Tapestry", "Axe", "Net"],
        "moral": "Violence begets violence, and familial betrayal leaves an indelible stain.",
        "source": "Aeschylus' Agamemnon"
    },
    {
        "id": "myth_prometheus_fire",
        "title": "The Theft of Fire",
        "text": "Prometheus, a brilliant and forward-thinking Titan, deeply pitied the helpless state of humanity, who shivered in the cold and darkness. Zeus had strictly forbidden mortals from possessing fire, intending to keep them weak and dependent on the gods. Betraying the King of Olympus, Prometheus snuck up to the sun and stole a spark of divine fire, hiding it within a hollow fennel stalk. He brought this tremendous gift down to mankind, teaching them civilization, metalworking, and the arts of survival. When Zeus saw the earth illuminated by fires, his fury was boundless. To punish this ultimate betrayal of divine law, Zeus chained Prometheus to a jagged crag in the Caucasus Mountains. Every day, a giant eagle would descend and tear out the Titan's liver, which would magically regenerate each night, subjecting Prometheus to eternal agony for his love of humanity.",
        "theme": "betrayal",
        "characters": [
            {"name": "Prometheus", "type": "titan"},
            {"name": "Zeus", "type": "god"}
        ],
        "relationships": [
            {"source": "Prometheus", "target": "Zeus", "relation": "enemy_of"}
        ],
        "locations": ["Mount Olympus", "Caucasus Mountains"],
        "artifacts": ["Fennel stalk", "Divine Fire", "Chains"],
        "moral": "Sacrifice and suffering are often the price for challenging tyranny and advancing civilization.",
        "source": "Hesiod's Theogony"
    },
    {
        "id": "myth_paris_apple",
        "title": "The Judgment of Paris",
        "text": "At the wedding of Peleus and Thetis, Eris, the goddess of discord, threw a golden apple inscribed 'For the Fairest' into the crowd, seeking to cause chaos because she wasn't invited. Hera, Athena, and Aphrodite all fiercely claimed the prize. To avoid making the choice himself, Zeus appointed Paris, a Trojan prince, to act as the judge. The three goddesses appeared before the young mortal, each offering him a magnificent bribe. Hera offered dominion over all of Asia; Athena offered unparalleled wisdom and absolute victory in war; but Aphrodite offered the love of the most beautiful woman in the world, Helen of Sparta. Paris foolishly chose Aphrodite's bribe, betraying the trust placed in him to judge fairly. However, Helen was already married to King Menelaus. Paris's selfish choice and subsequent abduction of Helen constituted a grave betrayal of guest-friendship, sparking the devastating ten-year Trojan War.",
        "theme": "betrayal",
        "characters": [
            {"name": "Paris", "type": "mortal"},
            {"name": "Aphrodite", "type": "god"},
            {"name": "Hera", "type": "god"},
            {"name": "Athena", "type": "god"},
            {"name": "Helen", "type": "mortal"}
        ],
        "relationships": [
            {"source": "Paris", "target": "Helen", "relation": "lover_of"}
        ],
        "locations": ["Mount Ida", "Troy", "Sparta"],
        "artifacts": ["Golden Apple of Discord"],
        "moral": "Lust and superficial desires will ultimately lead to ruin and devastating conflict.",
        "source": "Homer's Iliad"
    },
    {
        "id": "myth_hera_io",
        "title": "Hera and Io",
        "text": "Zeus became infatuated with Io, a beautiful mortal priestess of Hera. When Hera grew suspicious of a sudden thick cloud covering the earth, Zeus attempted to hide his infidelity by quickly transforming Io into a pure white heifer. The sharp-sighted Hera saw through the deception immediately and cunningly asked for the beautiful cow as a gift. Unable to refuse without arousing further suspicion, Zeus handed over the disguised Io. Hera placed the heifer under the guard of Argus Panoptes, a fearsome giant with a hundred eyes, ensuring Io could never escape. Zeus, taking pity on the suffering maiden, sent Hermes to slay the giant. Hermes lulled all hundred of Argus's eyes to sleep with a magical story and cut off his head. In a fit of revenge, Hera sent a vicious gadfly to sting Io endlessly, driving the tormented heifer to wander the entire earth in madness.",
        "theme": "revenge",
        "characters": [
            {"name": "Io", "type": "mortal"},
            {"name": "Hera", "type": "god"},
            {"name": "Zeus", "type": "god"},
            {"name": "Argus", "type": "creature"},
            {"name": "Hermes", "type": "god"}
        ],
        "relationships": [
            {"source": "Hera", "target": "Io", "relation": "enemy_of"},
            {"source": "Zeus", "target": "Io", "relation": "lover_of"}
        ],
        "locations": ["Argos", "Egypt", "Ionian Sea"],
        "artifacts": ["Peacock feathers"],
        "moral": "The innocent often suffer the most in conflicts between the powerful.",
        "source": "Ovid's Metamorphoses"
    },
    {
        "id": "myth_athena_medusa",
        "title": "The Curse of Medusa",
        "text": "Medusa was originally a mortal woman of exquisite beauty, serving as a devoted priestess in the sacred temple of Athena. Her beauty caught the attention of Poseidon, the god of the sea, who aggressively pursued her and violated her within Athena's holy sanctuary. Instead of punishing Poseidon, the furious Athena turned her wrath upon the victim. Disgusted by the desecration of her temple, the goddess transformed Medusa into a horrifying monster. Her magnificent hair was turned into a writhing nest of venomous snakes, and her face was made so terrifying that any living creature who met her gaze was instantly turned to solid stone. Banished to live in isolation, Medusa became a target for countless heroes seeking glory, ultimately facing her doom at the hands of Perseus, who used a mirrored shield to decapitate her while she slept.",
        "theme": "revenge",
        "characters": [
            {"name": "Medusa", "type": "mortal"},
            {"name": "Athena", "type": "god"},
            {"name": "Poseidon", "type": "god"},
            {"name": "Perseus", "type": "mortal"}
        ],
        "relationships": [
            {"source": "Athena", "target": "Medusa", "relation": "enemy_of"},
            {"source": "Poseidon", "target": "Medusa", "relation": "lover_of"},
            {"source": "Perseus", "target": "Medusa", "relation": "killed_by"}
        ],
        "locations": ["Athena's Temple", "Gorgon's Lair"],
        "artifacts": ["Mirrored Shield", "Aegis"],
        "moral": "Injustice is often dealt by those in power to protect their own pride.",
        "source": "Ovid's Metamorphoses"
    },
    {
        "id": "myth_poseidon_odysseus",
        "title": "Poseidon's Wrath",
        "text": "During his long journey home from the Trojan War, Odysseus and his crew found themselves trapped in the cave of Polyphemus, a savage and gigantic Cyclops. To escape, Odysseus cleverly blinded the giant with a sharpened stake and sneaked out tied beneath the bellies of sheep. As he sailed away, Odysseus foolishly revealed his true name to the monster, boasting of his victory. Polyphemus, who was the son of Poseidon, prayed to his father for vengeance. Enraged that a mere mortal had mutilated his child, the god of the sea swore a terrible revenge. For ten agonizing years, Poseidon relentlessly tormented Odysseus, sending violent storms, destroying his ships, and repeatedly blowing him off course, ensuring that the hero would lose all his men and arrive home alone and in rags.",
        "theme": "revenge",
        "characters": [
            {"name": "Odysseus", "type": "mortal"},
            {"name": "Poseidon", "type": "god"},
            {"name": "Polyphemus", "type": "creature"}
        ],
        "relationships": [
            {"source": "Poseidon", "target": "Odysseus", "relation": "enemy_of"},
            {"source": "Odysseus", "target": "Polyphemus", "relation": "enemy_of"}
        ],
        "locations": ["Cyclops' Cave", "The Mediterranean Sea", "Ithaca"],
        "artifacts": ["Sharpened Olive Stake"],
        "moral": "Boasting of one's victories can easily invite the wrath of powerful enemies.",
        "source": "Homer's Odyssey"
    },
    {
        "id": "myth_achilles_hector",
        "title": "The Vengeance of Achilles",
        "text": "During the brutal siege of Troy, the great Greek warrior Achilles withdrew from battle due to a petty dispute with King Agamemnon over a captured maiden. Without Achilles, the Greeks suffered heavy losses. Desperate, Achilles' beloved companion Patroclus borrowed his armor to frighten the Trojans, but he was ultimately slain by Hector, Troy's greatest champion. The news of Patroclus's death shattered Achilles. Consumed by an uncontrollable, raging thirst for revenge, Achilles set aside his anger at Agamemnon and returned to the battlefield like a demon. He slaughtered Trojans mercilessly, clogging the river Scamander with corpses, until he finally cornered Hector outside the city walls. After a brief chase, Achilles easily killed Hector. Denying the Trojan hero funeral rites, a vengeful Achilles tied Hector's mangled corpse to his chariot and brutally dragged it around the city walls for days, defiling the body in a shocking display of relentless fury.",
        "theme": "revenge",
        "characters": [
            {"name": "Achilles", "type": "mortal"},
            {"name": "Hector", "type": "mortal"},
            {"name": "Patroclus", "type": "mortal"}
        ],
        "relationships": [
            {"source": "Achilles", "target": "Hector", "relation": "enemy_of"},
            {"source": "Achilles", "target": "Patroclus", "relation": "lover_of"}
        ],
        "locations": ["Troy", "River Scamander"],
        "artifacts": ["Armor of Achilles", "Chariot"],
        "moral": "Unchecked grief and rage can drive even a hero to commit horrific atrocities.",
        "source": "Homer's Iliad"
    },
    {
        "id": "myth_atreus_thyestes",
        "title": "The Banquet of Atreus",
        "text": "The brothers Atreus and Thyestes were locked in a bitter struggle for the throne of Mycenae. Thyestes secretly seduced Atreus's wife and stole a magical golden fleece to usurp the kingdom. After Atreus reclaimed his rightful throne with the help of Zeus, he plotted a revenge so monstrous it cursed his family for generations. Pretending to seek reconciliation, Atreus invited Thyestes back to Mycenae for a grand feast. Secretly, Atreus murdered Thyestes's young sons, chopped them into pieces, and cooked their flesh in a rich stew. He served this horrific meal to the unsuspecting Thyestes. After his brother had eaten his fill, Atreus cruelly revealed the severed heads and hands of the children. Sickened and horrified, Thyestes cursed the House of Atreus and fled. The sun itself was said to have reversed its course in the sky, unable to look upon such an abominable act of revenge.",
        "theme": "revenge",
        "characters": [
            {"name": "Atreus", "type": "mortal"},
            {"name": "Thyestes", "type": "mortal"}
        ],
        "relationships": [
            {"source": "Atreus", "target": "Thyestes", "relation": "enemy_of"},
            {"source": "Atreus", "target": "Thyestes", "relation": "sibling_of"}
        ],
        "locations": ["Mycenae"],
        "artifacts": ["Golden Fleece"],
        "moral": "Vengeance that crosses the bounds of humanity taints the soul and curses descendants.",
        "source": "Seneca's Thyestes"
    },
    {
        "id": "myth_odysseus_cyclops",
        "title": "Outwitting the Cyclops",
        "text": "Trapped in the cave of the monstrous, man-eating Cyclops Polyphemus, Odysseus knew that relying on brute strength would lead to certain death, for only the giant could move the massive boulder blocking the exit. Relying instead on his legendary wisdom and cunning, Odysseus formulated a daring plan. He offered the Cyclops strong, unwatered wine until the beast fell into a drunken stupor. When asked his name, Odysseus cleverly replied, 'My name is Nobody.' While the giant slept, Odysseus and his men drove a flaming, sharpened stake into Polyphemus's single eye. Awakening in agonizing pain, the blinded Cyclops roared for help, shouting to his brethren outside, 'Nobody is killing me!' Thinking Polyphemus was afflicted by a disease sent by the gods, the other Cyclopes ignored his cries and left. The next morning, Odysseus and his surviving men escaped by clinging to the undersides of the giant's massive sheep.",
        "theme": "wisdom",
        "characters": [
            {"name": "Odysseus", "type": "mortal"},
            {"name": "Polyphemus", "type": "creature"}
        ],
        "relationships": [
            {"source": "Odysseus", "target": "Polyphemus", "relation": "enemy_of"}
        ],
        "locations": ["Cyclops' Cave"],
        "artifacts": ["Olive Wood Stake", "Skin of Wine"],
        "moral": "Intellect and clever planning can overcome seemingly insurmountable physical strength.",
        "source": "Homer's Odyssey"
    },
    {
        "id": "myth_sphinx",
        "title": "Oedipus and the Sphinx",
        "text": "The city of Thebes was under siege by a terrifying monster known as the Sphinx—a creature with the head of a woman, the body of a lion, and the wings of an eagle. She guarded the road to the city, halting all travelers and challenging them with a complex riddle. Those who failed to answer correctly were immediately devoured. For months, no one could outsmart the beast. Finally, a wandering traveler named Oedipus approached her. The Sphinx demanded: 'What walks on four legs in the morning, two legs at noon, and three legs in the evening?' Using profound wisdom and insight into human nature, Oedipus confidently answered, 'Man. As an infant he crawls on all fours, as an adult he walks on two legs, and in old age he relies on a walking stick.' Defeated by a mortal's intellect, the Sphinx threw herself off a high cliff to her death, and Oedipus was hailed as a hero.",
        "theme": "wisdom",
        "characters": [
            {"name": "Oedipus", "type": "mortal"},
            {"name": "Sphinx", "type": "creature"}
        ],
        "relationships": [
            {"source": "Oedipus", "target": "Sphinx", "relation": "enemy_of"}
        ],
        "locations": ["Thebes", "Mount Phikion"],
        "artifacts": [],
        "moral": "True strength lies not in the sword, but in the power of an observant and analytical mind.",
        "source": "Sophocles' Oedipus Rex"
    },
    {
        "id": "myth_midas",
        "title": "The Golden Touch",
        "text": "King Midas of Phrygia was granted a single wish by the god Dionysus as a reward for his hospitality. Driven by foolish greed rather than wisdom, Midas wished that everything he touched would turn to solid gold. Initially overjoyed, Midas transformed rocks, twigs, and statues into priceless treasures. However, his excitement quickly turned to absolute horror when he sat down to eat. His bread, meat, and wine turned to solid gold the moment they touched his lips. Starving and terrified, the true tragedy struck when he absentmindedly hugged his beloved daughter; she instantly transformed into a lifeless, golden statue. Realizing the profound foolishness of his greed, Midas begged Dionysus to take back the cursed gift. The god instructed him to wash in the River Pactolus. Midas did so, losing the golden touch and finally gaining true wisdom: realizing that some things are far more precious than wealth.",
        "theme": "wisdom",
        "characters": [
            {"name": "Midas", "type": "mortal"},
            {"name": "Dionysus", "type": "god"}
        ],
        "relationships": [
            {"source": "Dionysus", "target": "Midas", "relation": "mentor_of"}
        ],
        "locations": ["Phrygia", "River Pactolus"],
        "artifacts": ["Golden Touch"],
        "moral": "Greed blinds us to the true value of life, love, and sustenance.",
        "source": "Ovid's Metamorphoses"
    },
    {
        "id": "myth_daedalus",
        "title": "The Labyrinth of Daedalus",
        "text": "Daedalus was universally recognized as the most brilliant inventor, architect, and craftsman of his age. His unmatched intellect led King Minos of Crete to commission him to build the ultimate prison: the Labyrinth. It was a complex, sprawling maze of twisting, turning corridors designed to hold the ferocious Minotaur and ensure that no one who entered could ever find their way out. The design was a masterpiece of architectural wisdom, so complex that even Daedalus himself barely managed to escape after finishing it. Later, when Daedalus aided the hero Theseus in navigating the maze, Minos imprisoned Daedalus in a high tower. Relying once again on his unparalleled ingenuity, Daedalus closely observed the flight of birds and engineered wings of feathers and wax, proving that true wisdom and inventiveness cannot be contained by stone walls or tyrants.",
        "theme": "wisdom",
        "characters": [
            {"name": "Daedalus", "type": "mortal"},
            {"name": "King Minos", "type": "mortal"},
            {"name": "Minotaur", "type": "creature"}
        ],
        "relationships": [
            {"source": "Minos", "target": "Daedalus", "relation": "enemy_of"}
        ],
        "locations": ["Crete", "The Labyrinth"],
        "artifacts": ["The Labyrinth", "Wax Wings"],
        "moral": "Human ingenuity and intellect can construct the greatest marvels and overcome the most daunting traps.",
        "source": "Ovid's Metamorphoses"
    },
    {
        "id": "myth_athena_poseidon",
        "title": "The Contest for Athens",
        "text": "When a beautiful new city was founded in Attica, both Athena, goddess of wisdom, and Poseidon, god of the sea, claimed it as their own. To prevent a war between the gods, Zeus decreed that they must each offer a gift to the citizens, who would then choose their patron. Poseidon struck the Acropolis with his mighty trident, and a spring of water gushed forth. However, the water was salty like the sea and entirely useless for drinking or agriculture. Athena stepped forward and gently planted a seed in the ground. It rapidly grew into a flourishing olive tree. She explained that the tree would provide the city with wood for building, food to eat, and oil for cooking and lamps. Recognizing the deep practical wisdom and enduring value of Athena's gift over Poseidon's flashy but useless display, the citizens chose Athena, naming their great city Athens in her honor.",
        "theme": "wisdom",
        "characters": [
            {"name": "Athena", "type": "god"},
            {"name": "Poseidon", "type": "god"},
            {"name": "Zeus", "type": "god"}
        ],
        "relationships": [
            {"source": "Athena", "target": "Poseidon", "relation": "enemy_of"}
        ],
        "locations": ["Athens", "The Acropolis"],
        "artifacts": ["Trident", "Olive Tree"],
        "moral": "Practical wisdom and sustainable gifts are vastly superior to mere displays of raw power.",
        "source": "Apollodorus' Bibliotheca"
    },
    {
        "id": "myth_hera_callisto",
        "title": "The Bear Callisto",
        "text": "Callisto was a devoted follower of Artemis, having taken a strict vow of chastity to run with the hunting goddess in the wild. However, Zeus, captivated by her extraordinary beauty, disguised himself as Artemis to get close to her and forcefully took advantage of the nymph. When Callisto's subsequent pregnancy was discovered, a furious Artemis banished her from the hunt. Callisto gave birth to a son named Arcas. When Hera, the fiercely jealous queen of the gods, discovered her husband's latest indiscretion, she unleashed her wrath upon the innocent victim rather than her unfaithful husband. Hera cursed Callisto, transforming the beautiful nymph into a clumsy, terrifying brown bear, forcing her to flee into the mountains in terror of the hunters she once ran with. Years later, Arcas nearly killed his own mother on a hunt, prompting Zeus to finally intervene and place them both in the stars as Ursa Major and Ursa Minor.",
        "theme": "jealousy",
        "characters": [
            {"name": "Callisto", "type": "mortal"},
            {"name": "Hera", "type": "god"},
            {"name": "Zeus", "type": "god"},
            {"name": "Artemis", "type": "god"}
        ],
        "relationships": [
            {"source": "Hera", "target": "Callisto", "relation": "enemy_of"},
            {"source": "Zeus", "target": "Callisto", "relation": "lover_of"}
        ],
        "locations": ["Arcadia", "The Night Sky"],
        "artifacts": ["Constellations"],
        "moral": "Jealousy is often blind, unfairly punishing the victims rather than the true perpetrators.",
        "source": "Ovid's Metamorphoses"
    },
    {
        "id": "myth_apollo_marsyas",
        "title": "The Flaying of Marsyas",
        "text": "The satyr Marsyas stumbled upon a magnificent double-flute that had been invented and then discarded by Athena because playing it contorted her face. Marsyas mastered the instrument, creating music so enchanting that he foolishly boasted he could play better than Apollo, the god of music. Apollo, deeply insulted and jealous of his own supremacy, challenged the satyr to a musical contest, with the winner allowed to do whatever they wished to the loser. The Muses judged the contest. Marsyas played beautifully on his flute, and Apollo played brilliantly on his lyre. The contest was tied until Apollo demanded they play their instruments upside down. Apollo easily flipped his lyre and sang, while Marsyas could neither play a flute upside down nor sing while blowing into it. Declared the winner, a cruel and vindictive Apollo tied Marsyas to a pine tree and flayed him alive for daring to challenge a god.",
        "theme": "jealousy",
        "characters": [
            {"name": "Marsyas", "type": "creature"},
            {"name": "Apollo", "type": "god"},
            {"name": "Athena", "type": "god"}
        ],
        "relationships": [
            {"source": "Apollo", "target": "Marsyas", "relation": "enemy_of"},
            {"source": "Apollo", "target": "Marsyas", "relation": "killed_by"}
        ],
        "locations": ["Phrygia"],
        "artifacts": ["Aulos (Double-Flute)", "Lyre"],
        "moral": "Divine vanity is ruthless, and challenging those with absolute power is deeply perilous.",
        "source": "Ovid's Metamorphoses"
    },
    {
        "id": "myth_apple_discord",
        "title": "Eris and the Golden Apple",
        "text": "When King Peleus and the sea-nymph Thetis were married, all the gods and goddesses of Olympus were invited to the grand feast—except for Eris, the goddess of strife. Insulted and burning with spiteful jealousy at being excluded from the joyous occasion, Eris devised a cruel plan to ruin the celebration. She forged a brilliant golden apple and inscribed it with a single, provocative phrase: 'Kallistoi'—To the Fairest. Eris crashed the wedding and tossed the apple into the center of the banqueting hall. Immediately, the three most powerful goddesses—Hera, Athena, and Aphrodite—each claimed the prize, their vanity and jealousy blinding them to Eris's obvious trap. Their bitter dispute over the apple shattered the peace of the wedding and ultimately forced a mortal, Paris of Troy, to judge them, setting off a chain of events that resulted in the catastrophic Trojan War.",
        "theme": "jealousy",
        "characters": [
            {"name": "Eris", "type": "god"},
            {"name": "Hera", "type": "god"},
            {"name": "Athena", "type": "god"},
            {"name": "Aphrodite", "type": "god"}
        ],
        "relationships": [
            {"source": "Eris", "target": "Hera", "relation": "enemy_of"}
        ],
        "locations": ["Mount Pelion"],
        "artifacts": ["Golden Apple of Discord"],
        "moral": "Spite and petty jealousy can spark conflicts that consume entire nations.",
        "source": "Stasinus' Cypria"
    },
    {
        "id": "myth_aphrodite_psyche",
        "title": "The Wrath of Aphrodite",
        "text": "Aphrodite, the goddess of love and beauty, grew intensely jealous when a mere mortal woman named Psyche began receiving the adoration and sacrifices that rightfully belonged to her. Temples to Aphrodite were abandoned as people flocked to see Psyche's extraordinary beauty. Unable to tolerate this insult, Aphrodite ordered her son Cupid to ruin the girl's life. When Cupid instead married Psyche and hid her away, Aphrodite's fury only grew. After Psyche was separated from Cupid, she wandered the earth looking for him, eventually surrendering herself to her vindictive mother-in-law. Aphrodite subjected the exhausted pregnant girl to horrific, seemingly impossible tasks: sorting a massive mountain of mixed seeds in a single evening, gathering golden wool from fierce, man-killing sheep, and retrieving a box of beauty from the Queen of the Underworld. Only through the secret assistance of sympathetic gods and creatures did Psyche survive the goddess's jealous wrath.",
        "theme": "jealousy",
        "characters": [
            {"name": "Aphrodite", "type": "god"},
            {"name": "Psyche", "type": "mortal"},
            {"name": "Cupid", "type": "god"}
        ],
        "relationships": [
            {"source": "Aphrodite", "target": "Psyche", "relation": "enemy_of"}
        ],
        "locations": ["Aphrodite's Temple", "Underworld"],
        "artifacts": ["Box of Beauty", "Golden Wool"],
        "moral": "Envy can turn even the goddess of love into a ruthless tormentor.",
        "source": "Apuleius' The Golden Ass"
    },
    {
        "id": "myth_galinthias",
        "title": "The Jealousy of Eileithyia",
        "text": "When Alcmene was in agonizing labor, ready to give birth to the great hero Heracles (the son of Zeus), the jealous goddess Hera intervened. She sent Eileithyia, the goddess of childbirth, to sit outside Alcmene's chamber with her arms and legs tightly crossed. This magical gesture trapped the baby in the womb, causing Alcmene excruciating pain for seven days and nights, as Hera hoped the mortal woman would die in labor. A clever servant girl named Galinthias noticed the strange woman holding the spell. Realizing what was happening, Galinthias sprinted out of the room, joyously shouting that the baby had been born despite Eileithyia's efforts. Startled by the news, the goddess leaped to her feet, uncrossing her limbs and breaking the magical block. Heracles was instantly born. Enraged at being tricked by a mere servant, the spiteful goddess transformed the clever Galinthias into a weasel.",
        "theme": "jealousy",
        "characters": [
            {"name": "Hera", "type": "god"},
            {"name": "Eileithyia", "type": "god"},
            {"name": "Alcmene", "type": "mortal"},
            {"name": "Galinthias", "type": "mortal"}
        ],
        "relationships": [
            {"source": "Hera", "target": "Alcmene", "relation": "enemy_of"},
            {"source": "Eileithyia", "target": "Galinthias", "relation": "enemy_of"}
        ],
        "locations": ["Thebes"],
        "artifacts": [],
        "moral": "Divine spite is relentless, but human cleverness can sometimes outwit it.",
        "source": "Ovid's Metamorphoses"
    }
]

aliases = {
    "Zeus": ["Jupiter", "Jove", "Cloud-gatherer", "Thunderer"],
    "Hera": ["Juno", "Ox-eyed", "Queen of the Gods"],
    "Poseidon": ["Neptune", "Earth-shaker", "God of the Sea"],
    "Demeter": ["Ceres", "Deo", "Bringer of Seasons"],
    "Athena": ["Minerva", "Pallas", "Pallas Athena", "Grey-eyed"],
    "Apollo": ["Phoebus", "Far-shooter", "Loxias", "Pythian Apollo"],
    "Artemis": ["Diana", "Cynthia", "Phoebe", "Lady of the Beasts"],
    "Ares": ["Mars", "Enyalius", "Bane of Mortals"],
    "Aphrodite": ["Venus", "Cytherea", "Cypris", "Lady of Cyprus"],
    "Hephaestus": ["Vulcan", "Mulciber", "The Lame God"],
    "Hermes": ["Mercury", "Argeiphontes", "The Wayfinder"],
    "Dionysus": ["Bacchus", "Liber", "Bromios", "Iacchus"],
    "Hades": ["Pluto", "Dis", "Orcus", "Lord of the Dead"],
    "Persephone": ["Proserpina", "Kore", "The Maiden"],
    "Heracles": ["Hercules", "Alcides"],
    "Odysseus": ["Ulysses", "Man of Many Wiles"],
    "Achilles": ["Pelides", "Swift-footed"],
    "Agamemnon": ["Atrides", "Lord of Men"],
    "Menelaus": ["Atrides", "Red-haired"],
    "Helen": ["Helen of Troy", "Helen of Sparta"],
    "Paris": ["Alexander"],
    "Hector": ["Tamer of Horses"],
    "Aeneas": ["Aeneas"],
    "Jason": ["Son of Aeson"],
    "Medea": ["Colchian Princess"],
    "Theseus": ["Son of Aegeus"],
    "Minotaur": ["Asterion", "Asterius"],
    "Perseus": ["Son of Danae"],
    "Medusa": ["The Gorgon", "Snake-haired"],
    "Orpheus": ["The Thracian Singer"],
    "Eurydice": ["Oak Nymph"],
    "Prometheus": ["The Titan", "Forethought"],
    "Epimetheus": ["Afterthought"],
    "Pandora": ["The First Woman", "All-Gifts"],
    "Icarus": ["Son of Daedalus"],
    "Daedalus": ["The Artificer", "The Inventor"],
    "Arachne": ["The Weaver"],
    "Narcissus": ["The Vain Youth"],
    "Echo": ["The Oread"],
    "Pygmalion": ["The Sculptor"],
    "Galatea": ["The Statue"],
    "Psyche": ["The Soul"],
    "Eros": ["Cupid", "Amor"],
    "Cronus": ["Saturn"],
    "Rhea": ["Ops", "Cybele"],
    "Uranus": ["Caelus", "Father Sky"],
    "Gaia": ["Terra", "Mother Earth"],
    "Leto": ["Latona"]
}

with open(r"c:\Opensource\chronicle\data\processed\myths.json", "w", encoding="utf-8") as f:
    json.dump(myths, f, indent=4)

with open(r"c:\Opensource\chronicle\data\annotations\character_aliases.json", "w", encoding="utf-8") as f:
    json.dump(aliases, f, indent=4)

print("Files generated successfully.")
