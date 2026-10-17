#!/usr/bin/env python
"""Build the expanded Chronicle corpus from public-domain sources.

Downloads Bulfinch's *The Age of Fable* (Project Gutenberg #4928, 1855, public
domain), splits it into one record per myth, annotates every record, and merges
the result with the 30 hand-written myths already in ``data/processed/myths.json``.

Annotation is automatic and therefore *silver* quality:

* **characters** - dictionary match against ``data/annotations/character_aliases.json``
  (Roman names such as Jupiter/Minerva resolve to their Greek canonical names).
* **locations**  - gazetteer match.
* **themes**     - a lexicon score per theme, standardised across the corpus.
* **relationships** - taken from the curated ``data/annotations/genealogy.json``
  when both people appear in the myth.

The hand-checked evaluation set in ``data/eval/`` is what accuracy claims
should be measured against, not these labels.

Usage:
    python scripts/build_corpus.py            # download (cached) + rebuild
    python scripts/build_corpus.py --offline  # use data/raw/bulfinch.txt only
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "bulfinch.txt"
MYTHS = ROOT / "data" / "processed" / "myths.json"
ALIASES = ROOT / "data" / "annotations" / "character_aliases.json"
GENEALOGY = ROOT / "data" / "annotations" / "genealogy.json"
TYPES = ROOT / "data" / "annotations" / "character_types.json"
URL = "https://www.gutenberg.org/cache/epub/4928/pg4928.txt"
SOURCE = "Bulfinch, The Age of Fable (1855)"
SOURCE_URL = "https://www.gutenberg.org/ebooks/4928"

MIN_CHARS = 1500          # drop stubs shorter than this
CHUNK_TARGET = 5500       # split long myths into parts of roughly this size
CHUNK_MAX = 8000

# canonical name -> (type, extra aliases).  Existing alias-file entries are kept.
EXTRA: dict[str, tuple[str, list[str]]] = {
    "Zeus": ("god", ["Jupiter", "Jove"]), "Hera": ("god", ["Juno"]),
    "Poseidon": ("god", ["Neptune"]), "Hades": ("god", ["Pluto", "Dis", "Orcus"]),
    "Demeter": ("god", ["Ceres"]), "Hestia": ("god", ["Vesta"]),
    "Athena": ("god", ["Minerva", "Pallas Athena"]), "Apollo": ("god", ["Phoebus", "Phoebus Apollo"]),
    "Artemis": ("god", ["Diana", "Cynthia"]), "Ares": ("god", ["Mars"]),
    "Aphrodite": ("god", ["Venus", "Cytherea"]), "Hephaestus": ("god", ["Vulcan"]),
    "Hermes": ("god", ["Mercury"]), "Dionysus": ("god", ["Bacchus"]),
    "Persephone": ("god", ["Proserpine", "Proserpina"]), "Eros": ("god", ["Cupid", "Amor"]),
    "Cronus": ("titan", ["Saturn", "Kronos"]), "Rhea": ("titan", []), "Uranus": ("titan", ["Ouranos"]),
    "Gaia": ("titan", ["Ge", "Tellus"]), "Atlas": ("titan", []), "Iapetus": ("titan", []),
    "Helios": ("god", ["Sol"]), "Selene": ("god", ["Luna"]), "Eos": ("god", ["Aurora"]),
    "Hebe": ("god", []), "Pan": ("god", []), "Nemesis": ("god", []), "Eris": ("god", []),
    "Hecate": ("god", []), "Amphitrite": ("god", []), "Thetis": ("god", []), "Nereus": ("god", []),
    "Triton": ("god", []), "Proteus": ("god", []), "Aeolus": ("god", []), "Morpheus": ("god", []),
    "Iris": ("god", []), "Leto": ("god", ["Latona"]), "Maia": ("god", []), "Calliope": ("god", []),
    "Heracles": ("mortal", ["Hercules"]), "Odysseus": ("mortal", ["Ulysses"]),
    "Phaethon": ("mortal", ["Phaeton"]), "Perseus": ("mortal", []), "Theseus": ("mortal", []),
    "Jason": ("mortal", []), "Medea": ("mortal", []), "Achilles": ("mortal", []),
    "Agamemnon": ("mortal", []), "Menelaus": ("mortal", []), "Helen": ("mortal", []),
    "Paris": ("mortal", []), "Hector": ("mortal", []), "Priam": ("mortal", []), "Hecuba": ("mortal", []),
    "Cassandra": ("mortal", []), "Andromache": ("mortal", []), "Ajax": ("mortal", []),
    "Patroclus": ("mortal", []), "Diomedes": ("mortal", []), "Nestor": ("mortal", []),
    "Penelope": ("mortal", []), "Telemachus": ("mortal", []), "Circe": ("god", []),
    "Calypso": ("god", []), "Aeneas": ("mortal", []), "Dido": ("mortal", []), "Ascanius": ("mortal", []),
    "Anchises": ("mortal", []), "Turnus": ("mortal", []), "Evander": ("mortal", []),
    "Orpheus": ("mortal", []), "Eurydice": ("mortal", []), "Narcissus": ("mortal", []),
    "Echo": ("god", []), "Pygmalion": ("mortal", []), "Galatea": ("mortal", []),
    "Psyche": ("mortal", []), "Daphne": ("god", []), "Pyramus": ("mortal", []),
    "Thisbe": ("mortal", []), "Cephalus": ("mortal", []), "Procris": ("mortal", []),
    "Io": ("mortal", []), "Callisto": ("mortal", []), "Actaeon": ("mortal", []),
    "Midas": ("mortal", []), "Baucis": ("mortal", []), "Philemon": ("mortal", []),
    "Glaucus": ("god", []), "Scylla": ("creature", []), "Charybdis": ("creature", []),
    "Adonis": ("mortal", []), "Hyacinthus": ("mortal", []), "Vertumnus": ("god", []),
    "Pomona": ("god", []), "Cadmus": ("mortal", []), "Harmonia": ("mortal", []), "Semele": ("mortal", []),
    "Arachne": ("mortal", []), "Niobe": ("mortal", []), "Medusa": ("creature", []),
    "Pegasus": ("creature", []), "Chimaera": ("creature", ["Chimera"]), "Bellerophon": ("mortal", []),
    "Andromeda": ("mortal", []), "Cepheus": ("mortal", []), "Cassiopeia": ("mortal", []),
    "Sphinx": ("creature", []), "Oedipus": ("mortal", []), "Antigone": ("mortal", []),
    "Jocasta": ("mortal", []), "Creon": ("mortal", []), "Minotaur": ("creature", []),
    "Ariadne": ("mortal", []), "Minos": ("mortal", ["King Minos"]), "Daedalus": ("mortal", []),
    "Icarus": ("mortal", []), "Aegeus": ("mortal", []), "Pasiphae": ("mortal", []),
    "Meleager": ("mortal", []), "Atalanta": ("mortal", []), "Admetus": ("mortal", []),
    "Alcestis": ("mortal", []), "Castor": ("mortal", []), "Pollux": ("mortal", ["Polydeuces"]),
    "Leda": ("mortal", []), "Danae": ("mortal", []), "Alcmene": ("mortal", []), "Deianira": ("mortal", []),
    "Clytemnestra": ("mortal", []), "Orestes": ("mortal", []), "Electra": ("mortal", []),
    "Iphigenia": ("mortal", []), "Aegisthus": ("mortal", []), "Laertes": ("mortal", []),
    "Polyphemus": ("creature", []), "Cyclops": ("creature", ["Cyclopes"]), "Argus": ("creature", []),
    "Prometheus": ("titan", []), "Epimetheus": ("titan", []), "Pandora": ("mortal", []),
    "Tantalus": ("mortal", []), "Pelops": ("mortal", []), "Atreus": ("mortal", []),
    "Aeetes": ("mortal", []), "Aeson": ("mortal", []), "Pelias": ("mortal", []), "Glauce": ("mortal", []),
    "Ceyx": ("mortal", []), "Alcyone": ("mortal", []), "Endymion": ("mortal", []),
    "Tithonus": ("mortal", []), "Acis": ("mortal", []), "Marsyas": ("mortal", []),
    "Cerberus": ("creature", []), "Hydra": ("creature", []), "Harpies": ("creature", ["Harpy"]),
    "Furies": ("creature", ["Erinyes", "Eumenides"]), "Sibyl": ("mortal", []),
    "Charon": ("god", []), "Tiresias": ("mortal", []), "Camilla": ("mortal", []),
    "Euryalus": ("mortal", []), "Nisus": ("mortal", []), "Lavinia": ("mortal", []),
    "Sisyphus": ("mortal", []), "Ixion": ("mortal", []), "Tityus": ("mortal", []),
    "Latinus": ("mortal", []), "Mezentius": ("mortal", []), "Pallas": ("mortal", []),
    "Aristaeus": ("mortal", []), "Aeacus": ("mortal", []), "Chiron": ("creature", []),
    "Asclepius": ("god", ["Aesculapius"]), "Orion": ("mortal", []), "Phineus": ("mortal", []),
    "Phaedra": ("mortal", []), "Hippolytus": ("mortal", []), "Deucalion": ("mortal", []),
    "Pyrrha": ("mortal", []), "Python": ("creature", []), "Achelous": ("god", []),
    "Arethusa": ("god", []), "Triptolemus": ("mortal", []), "Hippomenes": ("mortal", []),
    "Sinon": ("mortal", []), "Laocoon": ("mortal", []), "Ino": ("mortal", []), "Athamas": ("mortal", []),
    "Acrisius": ("mortal", []), "Polydectes": ("mortal", []), "Lycaon": ("mortal", []),
    "Hippolyta": ("mortal", []), "Gorgons": ("creature", ["Gorgon"]), "Graeae": ("creature", []),
    "Epaphus": ("mortal", []), "Electryon": ("mortal", []), "Tyndareus": ("mortal", []),
    "Laius": ("mortal", []), "Oeneus": ("mortal", []), "Peleus": ("mortal", []),
    "Europa": ("mortal", []), "Aerope": ("mortal", []), "Ismene": ("mortal", []), "Lavinia": ("mortal", []),
    "Metis": ("titan", []), "Clymene": ("titan", []), "Perse": ("titan", []), "Amphitrite": ("god", []),
    "Hero": ("mortal", []), "Leander": ("mortal", []), "Clytie": ("mortal", []), "Dryope": ("mortal", []),
    "Erysichthon": ("mortal", []), "Arion": ("mortal", []), "Ibycus": ("mortal", []),
}
# surface forms that are ordinary words/places when lowercase or ambiguous in prose
AMBIGUOUS_TITLECASE_ONLY = {"Hero", "Echo", "Pan", "Io", "Iris", "Sol", "Luna", "Ge", "Dis", "Pallas",
                            "Paris", "Amor", "Aurora", "Latona", "Sibyl", "Furies", "Harpies", "Cyclops"}
# names whose bare form is too ambiguous to count unless they appear in the title
TITLE_ONLY = {"Hero"}

PLACES = [
    "Olympus", "Parnassus", "Helicon", "Delphi", "Delos", "Thebes", "Athens", "Sparta", "Troy",
    "Crete", "Labyrinth", "Colchis", "Argos", "Mycenae", "Corinth", "Ithaca", "Thessaly", "Attica",
    "Arcadia", "Sicily", "Libya", "Egypt", "Ethiopia", "Phrygia", "Lydia", "Cyprus", "Rhodes",
    "Naxos", "Lemnos", "Aulis", "Mount Ida", "Mount Etna", "Etna", "Tartarus", "Elysium", "Styx",
    "Underworld", "Hades", "Lethe", "Cumae", "Carthage", "Latium", "Rome", "Italy", "Sicily",
    "Calydon", "Pelion", "Ossa", "Eleusis", "Boeotia", "Phocis", "Pylos", "Tyre", "Sidon",
    "Babylon", "Scythia", "Hellespont", "Aegean", "Ionian Sea", "Mount Cithaeron", "Cithaeron",
    "Mount Olympus", "Elis", "Euboea", "Salamis", "Marathon", "Epirus", "Thrace", "Macedonia",
    "Mount Sipylus", "Pisa", "Tiber", "Nile", "Eridanus", "Phasis", "Aeaea", "Ogygia", "Scheria",
]

THEMES = ["hubris", "love", "betrayal", "revenge", "wisdom", "jealousy", "transformation", "quest", "loss"]
LEX = {
    "hubris": r"\b(proud|pride|prid\w*|boast\w*|presum\w*|arrogan\w*|vain|vanity|insolen\w*|scorn\w*|defied|defy|defiance|contemptuous|haughty|overween\w*|impiety|impious|sacrilege\w*)\b",
    "love": r"\b(love|loved|loves|loving|lover|lovers|beloved|passion\w*|bride|marry|married|marriage|wedding|nuptial\w*|wooed|woo|suitor|suitors|betrothed|affection\w*|devoted|devotion|tender\w*|kiss\w*)\b",
    "betrayal": r"\b(betray\w*|treacher\w*|deceiv\w*|deceit\w*|deceiving|trick\w*|traitor\w*|perfid\w*|faithless|treason\w*|perjur\w*|guile|fraud|false)\b",
    "revenge": r"\b(reveng\w*|vengeance|avenge\w*|punish\w*|wrath|retribution|fury|furies|slew|slay|slain|anger\w*|enraged|incensed)\b",
    "wisdom": r"\b(wise|wisdom|counsel\w*|cunning|prudent|prudence|sage|advice|advised|shrewd|oracle\w*|prophe\w*|foresight|sagacity|learned)\b",
    "jealousy": r"\b(jealous\w*|envy|envied|envious|rival|rivals|rivalry|resent\w*|spite|spiteful)\b",
    "transformation": r"\b(metamorphos\w*|transform\w*)\b|\b(changed|turned|converted)\b[^.]{0,40}\b(into|to a|to an)\b|\b(was|were|is|are) (changed|turned)\b",
    "quest": r"\b(journey\w*|voyage\w*|quest|sought|seek\w*|adventure\w*|labors?|labours?|monster\w*|hero|heroes|set sail|fleece|task|tasks|expedition|wander\w*|slay\w*)\b",
    "loss": r"\b(death|died|dying|dead|grief|mourn\w*|weep\w*|wept|tears|sorrow\w*|lament\w*|funeral\w*|shade|shades|ghost\w*|perish\w*|bereft)\b",
}
LEX_RE = {k: re.compile(v, re.I) for k, v in LEX.items()}

THEME_MORAL = {
    "hubris": "Pride and boasting before the gods bring ruin.",
    "love": "Love can ennoble and destroy in equal measure.",
    "betrayal": "Broken trust is repaid in kind.",
    "revenge": "Vengeance spreads suffering beyond its first target.",
    "wisdom": "Foresight and restraint prevail where force fails.",
    "jealousy": "Envy poisons the one who feeds it.",
    "transformation": "Those who offend nature or the gods may be remade by them.",
    "quest": "Great ends demand courage and endurance.",
    "loss": "Mortals must bear grief and the finality of death.",
}


# ---------------------------------------------------------------------------
# Download + segmentation
# ---------------------------------------------------------------------------

def download(offline: bool) -> str:
    if RAW.exists():
        return RAW.read_text(encoding="utf8")
    if offline:
        sys.exit(f"--offline given but {RAW} does not exist")
    print("Downloading", URL)
    RAW.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(URL, timeout=60) as r:
        data = r.read().decode("utf8")
    RAW.write_text(data, encoding="utf8")
    return data


def clean(text: str) -> str:
    text = text.replace("\r", "")
    text = re.sub(r"\[Footnote[^\]]*\]", "", text, flags=re.S)
    text = re.sub(r"\[Illustration[^\]]*\]", "", text, flags=re.S)
    text = re.sub(r"\[\d+\]", "", text)
    lines = [ln for ln in text.split("\n") if not re.match(r"^\s{2,}\S", ln)]  # drop quoted verse
    text = "\n".join(lines).replace("_", "")
    paras = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", text)]
    return "\n\n".join(p for p in paras if p)


TITLE_FIX = {
    "Giants, Sphinx, Pegasus and Chimaera, Centaurs, Griffin, and Pygmies": "Monsters of Myth",
    "Juno and Her Rivals, Io and Callisto": "Io and Callisto",
    "Minerva": "Minerva and Arachne",
    "Erisichthon": "Erysichthon",
}

HEAD_RE = re.compile(r"^([A-Z][A-Z ,'’.-]{4,70})$", re.M)


def segments(book: str) -> list[tuple[str, str]]:
    start = book.index("*** START")
    body = book[start : book.index("*** END")].replace("\r", "")
    lo = body.index("PROMETHEUS AND PANDORA", body.index("CHAPTER II"))
    hi = body.index("PYTHAGORAS", body.index("CHAPTER XXXIV"))
    body = body[lo:hi]
    marks: list[tuple[int, int, str]] = []
    for m in HEAD_RE.finditer(body):
        if marks and body[marks[-1][1] : m.start()] == "\n":  # heading wrapped onto a second line
            prev = marks.pop()
            marks.append((prev[0], m.end(), prev[2] + " " + m.group(1).strip()))
        else:
            marks.append((m.start(), m.end(), m.group(1).strip()))
    out: list[tuple[str, str]] = []
    for i, (_, end, head) in enumerate(marks):
        nxt = marks[i + 1][0] if i + 1 < len(marks) else len(body)
        if head.startswith("CHAPTER"):
            continue
        txt = clean(body[end:nxt])
        title = head
        if "--" in head:  # combined chapter heading: the text under it is its first story
            title = head.split("--")[0]
        title = title.title().replace("'S", "'s").replace(" And ", " and ").replace(" Of ", " of ").replace(" The ", " the ")
        title = TITLE_FIX.get(title, title)
        if len(txt) >= MIN_CHARS:
            out.append((title, txt))
    return out


def chunk(title: str, text: str) -> list[tuple[str, str]]:
    if len(text) <= CHUNK_MAX:
        return [(title, text)]
    paras, parts, cur = text.split("\n\n"), [], ""
    for p in paras:
        if cur and len(cur) + len(p) > CHUNK_TARGET:
            parts.append(cur)
            cur = ""
        cur += ("\n\n" if cur else "") + p
    if cur:
        if parts and len(cur) < 1200:
            parts[-1] += "\n\n" + cur
        else:
            parts.append(cur)
    return [(title, p) for p in parts]


# ---------------------------------------------------------------------------
# Annotation
# ---------------------------------------------------------------------------

def build_aliases() -> tuple[dict[str, list[str]], dict[str, str]]:
    aliases = json.loads(ALIASES.read_text(encoding="utf8"))
    types = {}
    for name, (typ, extra) in EXTRA.items():
        types[name] = typ
        cur = aliases.setdefault(name, [])
        for a in extra:
            if a not in cur:
                cur.append(a)
    for name in aliases:
        types.setdefault(name, "mortal")
    return aliases, types


def compile_names(aliases: dict[str, list[str]]):
    pats = {}
    for canon, alts in aliases.items():
        forms = sorted({canon, *alts}, key=len, reverse=True)
        # case-sensitive: myth names are capitalised; this avoids "echo", "hero", "pan"
        pats[canon] = re.compile(r"\b(?:" + "|".join(re.escape(f) for f in forms) + r")\b")
    return pats


def find_characters(title: str, text: str, pats, types) -> list[dict[str, str]]:
    counts = {}
    for canon, pat in pats.items():
        n = len(pat.findall(text))
        in_title = bool(pat.search(title))
        if canon in TITLE_ONLY and not in_title:
            continue
        if n >= 2 or (in_title and n >= 1):
            counts[canon] = n + (5 if in_title else 0)
    ranked = sorted(counts, key=counts.get, reverse=True)[:12]
    return [{"name": n, "type": types.get(n, "mortal")} for n in ranked]


def find_places(text: str) -> list[str]:
    found = Counter()
    for p in PLACES:
        n = len(re.findall(rf"\b{re.escape(p)}\b", text))
        if n:
            found[p] += n
    return [p for p, _ in found.most_common(8)]


def theme_scores(text: str) -> dict[str, float]:
    words = max(1, len(text.split()))
    return {t: 1000.0 * len(LEX_RE[t].findall(text)) / words for t in THEMES}


def assign_themes(records: list[dict]) -> None:
    raw = [theme_scores(r["text"]) for r in records]
    mu = {t: statistics.mean(s[t] for s in raw) for t in THEMES}
    sd = {t: (statistics.pstdev(s[t] for s in raw) or 1.0) for t in THEMES}
    for rec, s in zip(records, raw):
        z = {t: (s[t] - mu[t]) / sd[t] for t in THEMES}
        ranked = sorted(THEMES, key=lambda t: z[t], reverse=True)
        rec["theme"] = ranked[0]
        rec["themes"] = [t for t in ranked[:3] if z[t] >= 0.5] or [ranked[0]]
        rec["moral"] = THEME_MORAL[rec["theme"]]
        rec["moral_source"] = "theme_template"


def relationships_for(chars: list[dict], genealogy: list[list[str]]) -> list[dict[str, str]]:
    names = {c["name"] for c in chars}
    return [{"source": s, "target": o, "relation": r} for s, r, o in genealogy if s in names and o in names]


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def build(offline: bool) -> None:
    aliases, types = build_aliases()
    pats = compile_names(aliases)
    genealogy = json.loads(GENEALOGY.read_text(encoding="utf8"))["relations"]

    originals = json.loads(MYTHS.read_text(encoding="utf8"))
    originals = [m for m in originals if m.get("corpus", "curated") == "curated"]
    rename = {"Cupid": "Eros", "King Minos": "Minos"}
    for m in originals:
        m["corpus"] = "curated"
        for c in m["characters"]:
            c["name"] = rename.get(c["name"], c["name"])
        for r in m.get("relationships", []):
            r["source"] = rename.get(r["source"], r["source"])
            r["target"] = rename.get(r["target"], r["target"])
        m["themes"] = [m["theme"]]
        m["word_count"] = len(m["text"].split())

    book = download(offline)
    new, seen = [], Counter()
    kept: list[tuple[str, str, list[dict]]] = []
    for title, text in segments(book):
        for _, ptext in chunk(title, text):
            chars = find_characters(title, ptext, pats, types)
            if len(chars) >= 2:
                kept.append((title, ptext, chars))
    totals = Counter(t for t, _, _ in kept)
    for title, ptext, chars in kept:
        seen[title] += 1
        ptitle = f"{title} (Part {seen[title]})" if totals[title] > 1 else title
        if True:
            new.append({
                "id": f"myth_b_{slug(ptitle)}",
                "title": ptitle,
                "text": ptext,
                "characters": chars,
                "relationships": relationships_for(chars, genealogy),
                "locations": find_places(ptext),
                "artifacts": [],
                "source": SOURCE,
                "source_url": SOURCE_URL,
                "corpus": "bulfinch",
                "word_count": len(ptext.split()),
            })
    assign_themes(new)
    ALIASES.write_text(json.dumps(aliases, indent=2, ensure_ascii=False), encoding="utf8")
    TYPES.write_text(json.dumps(dict(sorted(types.items())), indent=1, ensure_ascii=False), encoding="utf8")
    MYTHS.write_text(json.dumps(originals + new, indent=2, ensure_ascii=False), encoding="utf8")

    print(f"{len(originals)} curated + {len(new)} Bulfinch myths = {len(originals) + len(new)}")
    print("themes:", dict(Counter(m["theme"] for m in originals + new)))
    print("avg words:", round(statistics.mean(m["word_count"] for m in new)),
          "| characters/myth:", round(statistics.mean(len(m["characters"]) for m in new), 1),
          "| with relationships:", sum(1 for m in new if m["relationships"]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="never touch the network")
    build(ap.parse_args().offline)
