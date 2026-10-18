#!/usr/bin/env python
"""Fetch classical portraits for all remaining figures in the Chronicle knowledge graph."""

from __future__ import annotations

import html
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PORTRAITS_DIR = ROOT / "frontend" / "public" / "images" / "portraits"
DIST_PORTRAITS_DIR = ROOT / "frontend" / "dist" / "images" / "portraits"
PORTRAITS_JS = ROOT / "frontend" / "src" / "data" / "portraits.js"
MYTHS_FILE = ROOT / "data" / "processed" / "myths.json"

API = "https://commons.wikimedia.org/w/api.php"
UA = "ChronicleClassicalArt/1.0 (https://github.com/Yasaswini-ch/Chronicle; educational mythology platform)"

OK_LICENCE = re.compile(r"(public domain|^pd|cc0|cc[- ]by)", re.I)
BAD_WORDS = re.compile(r"(map|coin|stamp|logo|diagram|cover|poster|flag|portrait of (mr|mrs)|photograph of|statue of liberty|\.svg|chart|plan of|signature|bookplate|postcard)", re.I)

FIGURE_QUERIES: dict[str, list[str]] = {
    "Achelous": ["Achelous statue", "Hercules and Achelous sculpture", "Achelous river god"],
    "Acis": ["Acis and Galatea sculpture", "Acis statue", "Acis Galatea painting"],
    "Actaeon": ["Actaeon statue British Museum", "Diana and Actaeon sculpture", "Actaeon hunting sculpture"],
    "Admetus": ["Alcestis and Admetus painting", "Admetus classical", "Admetus Roman"],
    "Adonis": ["Adonis statue Canova", "Adonis sculpture Louvre", "Venus and Adonis statue"],
    "Aeacus": ["Aeacus statue", "Aeacus judge underworld", "Aeacus classical"],
    "Aeetes": ["King Aeetes Colchis painting", "Aeetes classical", "Jason and Aeetes"],
    "Aegeus": ["Aegeus statue", "King Aegeus painting", "Aegeus classical"],
    "Aegisthus": ["Death of Aegisthus painting", "Aegisthus classical", "Clytemnestra Aegisthus"],
    "Aeneas": ["Flight of Aeneas Barocci", "Aeneas Anchises statue Bernini", "Aeneas statue"],
    "Aeolus": ["Aeolus god of winds statue", "Aeolus relief", "Aeolus sculpture"],
    "Aeson": ["Medea and Aeson painting", "Aeson classical", "Jason and Aeson"],
    "Ajax": ["Ajax bust Vatican", "Ajax with body of Achilles statue", "Ajax sculpture Louvre"],
    "Alcestis": ["Alcestis statue", "Alcestis Kauffman painting", "Alcestis sculpture"],
    "Alcyone": ["Ceyx and Alcyone painting", "Alcyone halcyon", "Alcyone classical"],
    "Anchises": ["Aeneas and Anchises statue Bernini", "Anchises sculpture", "Aeneas carrying Anchises"],
    "Andromache": ["Andromache mourning Hector David", "Andromache statue", "Andromache classical"],
    "Antigone": ["Antigone and Oedipus painting", "Antigone sculpture", "Antigone classical"],
    "Arethusa": ["Arethusa nymph statue", "Fountain of Arethusa Syracuse", "Arethusa relief"],
    "Argus": ["Mercury and Argus Velazquez", "Argus Panoptes painting", "Argos Io classical"],
    "Aristaeus": ["Aristaeus statue Louvre", "Aristaeus sculpture", "Aristaeus bees"],
    "Asclepius": ["Asklepios statue Epidauros", "Asclepius bust Vatican", "Esculape statue Louvre"],
    "Atalanta": ["Atalanta statue Louvre", "Atalanta Hippomenes painting", "Atalanta sculpture"],
    "Athamas": ["Athamas Ino classical", "Athamas painting", "Athamas sculpture"],
    "Baucis": ["Philemon and Baucis Rubens", "Baucis and Philemon painting", "Baucis classical"],
    "Cadmus": ["Cadmus sowing dragon teeth painting", "Cadmus statue", "Cadmus Thebes"],
    "Callisto": ["Diana and Callisto Titian", "Callisto statue", "Callisto nymph painting"],
    "Calypso": ["Ulysses and Calypso painting", "Calypso nymph statue", "Calypso Ogygia"],
    "Camilla": ["Camilla warrior queen painting", "Camilla Volscian", "Camilla Virgil"],
    "Cassandra": ["Cassandra Evelyn De Morgan", "Cassandra Troy painting", "Cassandra prophetess"],
    "Cassiopeia": ["Cassiopeia Andromeda painting", "Cassiopeia constellation classical", "Cassiopeia Queen"],
    "Castor": ["Castor and Pollux statue Louvre", "Dioscuri Quirinale statue", "Castor sculpture"],
    "Cephalus": ["Cephalus and Procris painting", "Aurora and Cephalus painting", "Cephalus sculpture"],
    "Cepheus": ["Perseus and Andromeda Cepheus", "King Cepheus classical", "Cepheus Andromeda"],
    "Ceyx": ["Ceyx and Alcyone painting", "Ceyx classical", "Alcyone and Ceyx"],
    "Charybdis": ["Scylla and Charybdis classical", "Charybdis whirlpool", "Charybdis painting"],
    "Chimaera": ["Chimera of Arezzo statue", "Chimaera Etruscan bronze", "Chimera sculpture"],
    "Chimera": ["Chimera of Arezzo bronze", "Chimera statue", "Bellerophon and Chimera"],
    "Circe": ["Circe Invidiosa Waterhouse", "Circe Offering the Cup to Ulysses Waterhouse", "Circe painting"],
    "Clymene": ["Apollo and Clymene", "Clymene Phaethon", "Clymene oceanid"],
    "Creon": ["Creon and Oedipus painting", "Creon Thebes classical", "Creon statue"],
    "Cyclops": ["Polyphemus Cyclops statue", "Cyclops painting Redon", "Cyclops sculpture"],
    "Danae": ["Danae and the Shower of Gold Titian", "Danae painting Klimt", "Danae Rembrandt"],
    "Daphne": ["Apollo and Daphne Bernini statue", "Daphne statue Bernini", "Apollo Daphne sculpture"],
    "Dido": ["Death of Dido Guerin", "Dido and Aeneas painting", "Dido Queen of Carthage"],
    "Echo": ["Echo and Narcissus Waterhouse", "Echo nymph painting", "Echo statue"],
    "Eileithyia": ["Eileithyia relief", "Birth of Heracles relief", "Eileithyia goddess"],
    "Electra": ["Electra at the Tomb of Agamemnon Leighton", "Electra painting", "Electra classical"],
    "Endymion": ["Sleep of Endymion Girodet", "Selene and Endymion painting", "Endymion sculpture"],
    "Eos": ["Eos goddess of dawn painting", "Aurora painting Reni", "Eos chariot relief"],
    "Eris": ["Eris goddess of discord painting", "Apple of Discord classical", "Eris Strife"],
    "Europa": ["Rape of Europa Titian", "Europa and the Bull painting", "Europa sculpture"],
    "Euryalus": ["Nisus and Euryalus painting", "Euryalus Virgil", "Nisus Euryalus Roman"],
    "Evander": ["Aeneas and Evander painting", "King Evander Rome", "Evander classical"],
    "Furies": ["Orestes pursued by the Furies Bouguereau", "Erinyes painting", "Furies classical"],
    "Galatea": ["Triumph of Galatea Raphael", "Acis and Galatea painting", "Pygmalion Galatea statue"],
    "Galinthias": ["Galinthias weasel myth", "Birth of Hercules relief", "Galinthias classical"],
    "Glauce": ["Creusa Glauce Medea painting", "Glauce classical", "Medea Creusa"],
    "Glaucus": ["Glaucus and Scylla painting", "Glaucus sea god statue", "Glaucus sculpture"],
    "Gorgons": ["Medusa and the Gorgons painting", "Gorgon relief archaic", "Gorgons classical"],
    "Harmonia": ["Cadmus and Harmonia painting", "Harmonia goddess sculpture", "Harmonia classical"],
    "Harpies": ["Aeneas and the Harpies painting", "Harpy classical relief", "Harpies sculpture"],
    "Hecate": ["Hecate statue British Museum", "Triple Hecate relief", "Hecate goddess sculpture"],
    "Helios": ["Colossus of Rhodes engraving", "Helios sun chariot relief", "Helios bust classical"],
    "Hippolyta": ["Battle of the Amazons Rubens", "Hippolyta Queen of Amazons", "Hippolyta sculpture"],
    "Hippolytus": ["Phaedra and Hippolytus Guerin", "Hippolytus statue", "Hippolytus sarcophagus"],
    "Hippomenes": ["Atalanta and Hippomenes Guido Reni", "Hippomenes race painting", "Hippomenes statue"],
    "Hyacinthus": ["Death of Hyacinthus Tiepolo", "Hyacinthus statue", "Apollo and Hyacinthus"],
    "Hydra": ["Hercules and the Lernaean Hydra painting", "Lernaean Hydra sculpture", "Hercules Hydra Pollaiolo"],
    "Ibycus": ["The Cranes of Ibycus painting", "Ibycus poet", "Ibycus classical"],
    "Io": ["Jupiter and Io Correggio", "Io and Argus painting", "Io nymph classical"],
    "Iphigenia": ["Sacrifice of Iphigenia Tiepolo", "Iphigenia painting", "Iphigenia in Tauris statue"],
    "Iris": ["Iris goddess of the rainbow painting", "Iris statue Louvre", "Iris messenger of the gods"],
    "Laius": ["Oedipus and Laius painting", "King Laius Thebes", "Laius classical"],
    "Laocoon": ["Laocoon and His Sons statue Vatican", "Laocoon Vatican statue", "Laocoon sculpture"],
    "Latinus": ["King Latinus Aeneas painting", "Latinus Aeneid", "Latinus Roman"],
    "Lavinia": ["Lavinia Aeneas painting", "Lavinia Roman", "Lavinia Virgil"],
    "Leto": ["Leto and her children Apollo Artemis", "Latona statue", "Leto sculpture"],
    "Marsyas": ["Flaying of Marsyas Titian", "Marsyas statue Louvre", "Marsyas satyr sculpture"],
    "Meleager": ["Meleager statue Skopas", "Meleager and the Calydonian Boar", "Meleager sculpture Vatican"],
    "Menelaus": ["Menelaus supporting the body of Patroclus", "Menelaus bust Vatican", "Menelaus statue"],
    "Mezentius": ["Mezentius Aeneas painting", "Mezentius Etruscan", "Death of Mezentius"],
    "Narcissus": ["Narcissus painting Caravaggio", "Narcissus statue Louvre", "Echo and Narcissus"],
    "Nemesis": ["Nemesis statue Louvre", "Nemesis goddess sculpture", "Nemesis relief"],
    "Nestor": ["Nestor wise king painting", "Nestor Pylos classical", "Nestor Iliad"],
    "Nisus": ["Nisus and Euryalus painting", "King Nisus Scylla", "Nisus classical"],
    "Orestes": ["Orestes pursued by the Furies Bouguereau", "Orestes statue", "Orestes Electra sculpture"],
    "Orion": ["Blind Orion Searching for the Rising Sun Poussin", "Orion statue", "Orion hunter classical"],
    "Pallas": ["Pallas Athena statue", "Death of Pallas Aeneid painting", "Pallas statue"],
    "Patroclus": ["Death of Patroclus David", "Achilles and Patroclus painting", "Patroclus body statue"],
    "Pegasus": ["Pegasus statue Tuileries", "Bellerophon and Pegasus sculpture", "Pegasus winged horse statue"],
    "Pelias": ["Medea and Pelias daughters painting", "King Pelias Argonauts", "Pelias classical"],
    "Penelope": ["Penelope and the Suitors Waterhouse", "Penelope weaving painting", "Penelope statue Vatican"],
    "Phaedra": ["Phaedra painting Cabanel", "Phaedra and Hippolytus painting", "Phaedra classical"],
    "Philemon": ["Baucis and Philemon painting", "Philemon and Baucis Rembrandt", "Philemon classical"],
    "Phineus": ["Perseus and Phineus painting", "Phineus and the Harpies", "Phineus classical"],
    "Pollux": ["Castor and Pollux statue", "Pollux Dioscuri statue", "Dioscuri statue"],
    "Polydectes": ["Perseus turning Polydectes to stone", "Polydectes classical", "Perseus Polydectes"],
    "Polyphemus": ["Polyphemus Cyclops statue Sperlonga", "Ulysses deriding Polyphemus Turner", "Polyphemus painting"],
    "Pomona": ["Vertumnus and Pomona painting", "Pomona goddess statue", "Pomona sculpture"],
    "Procris": ["Death of Procris Piero di Cosimo", "Cephalus and Procris painting", "Procris classical"],
    "Proteus": ["Proteus sea god statue", "Proteus sculpture", "Aristaeus and Proteus"],
    "Pygmalion": ["Pygmalion and Galatea Gerome", "Pygmalion statue Burne-Jones", "Pygmalion sculpture"],
    "Pyrrha": ["Deucalion and Pyrrha painting", "Pyrrha and Deucalion", "Pyrrha classical"],
    "Scylla": ["Scylla sea monster statue", "Glaucus and Scylla painting", "Scylla sculpture"],
    "Semele": ["Jupiter and Semele Gustave Moreau", "Semele painting", "Death of Semele"],
    "Sibyl": ["Cumaean Sibyl Michelangelo", "Sibyl of Cumae painting Domenichino", "Sibyl painting"],
    "Sinon": ["Sinon Trojan horse painting", "Sinon before Priam", "Sinon Virgil"],
    "Sphinx": ["Oedipus and the Sphinx Ingres", "Sphinx statue classical", "Greek Sphinx sculpture"],
    "Telemachus": ["Telemachus and Mentor painting", "Telemachus statue", "Telemachus Odyssey"],
    "Thetis": ["Jupiter and Thetis Ingres", "Thetis bringing armor to Achilles", "Thetis Nereid statue"],
    "Thyestes": ["Atreus and Thyestes painting", "Banquet of Thyestes", "Thyestes classical"],
    "Tiresias": ["Tiresias and Odysseus painting", "Blind prophet Tiresias", "Tiresias seer"],
    "Tithonus": ["Aurora and Tithonus painting", "Tithonus classical", "Aurora Tithonus"],
    "Triptolemus": ["Triptolemus and Demeter relief", "Triptolemus winged chariot", "Triptolemus vase"],
    "Turnus": ["Aeneas defeating Turnus painting", "Turnus Virgil", "Death of Turnus"],
    "Vertumnus": ["Vertumnus and Pomona painting", "Vertumnus god statue", "Vertumnus sculpture"]
}


def strip_html(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def query_commons(query: str) -> dict | None:
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": f"{query} filetype:bitmap",
        "gsrnamespace": 6,
        "gsrlimit": 6,
        "prop": "imageinfo",
        "iiprop": "url|size|extmetadata|mime",
        "iiurlwidth": 600,
        "iiextmetadatafilter": "LicenseShortName|Artist|ObjectName|DateTimeOriginal",
        "format": "json",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            data = json.load(r)
        pages = data.get("query", {}).get("pages", {})
        for p in pages.values():
            info = (p.get("imageinfo") or [{}])[0]
            title = p.get("title", "")
            meta = info.get("extmetadata", {})
            lic = strip_html(meta.get("LicenseShortName", {}).get("value", ""))
            if not info or not OK_LICENCE.search(lic) or BAD_WORDS.search(title):
                continue
            if info.get("mime") not in ("image/jpeg", "image/png"):
                continue
            thumb = info.get("thumburl")
            if not thumb:
                continue
            return {
                "thumb": thumb,
                "title": title,
            }
    except Exception as e:
        print(f"  [Warn] Query '{query}' failed: {e}")
    return None


def download_image(url: str, dest_path: Path, max_size: int = 500) -> bool:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            im = Image.open(io.BytesIO(data)).convert("RGB")
            im.thumbnail((max_size, max_size))
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            im.save(dest_path, "JPEG", quality=85, optimize=True)
            return True
        except Exception:
            time.sleep(1.0 * (attempt + 1))
    return False


def run():
    PORTRAITS_DIR.mkdir(parents=True, exist_ok=True)
    DIST_PORTRAITS_DIR.mkdir(parents=True, exist_ok=True)

    # Read existing portraits
    portraits_map: dict[str, str] = {}
    if PORTRAITS_JS.exists():
        content = PORTRAITS_JS.read_text(encoding="utf-8")
        m = re.search(r"export\s+const\s+PORTRAITS\s*=\s*(\{.*?\});", content, re.DOTALL)
        if m:
            try:
                portraits_map = json.loads(m.group(1))
            except Exception:
                pass

    print(f"Loaded {len(portraits_map)} existing portraits.")
    missing_figs = [f for f in FIGURE_QUERIES if f.lower() not in portraits_map]
    print(f"Fetching portraits for {len(missing_figs)} additional figures...")

    # Classical statue fallback bank
    fallback_bank = [
        "/images/gallery/discobolus.jpg",
        "/images/gallery/zeus-artemision.jpg",
        "/images/gallery/charioteer-of-delphi.jpg",
        "/images/gallery/venus-de-milo.jpg",
        "/images/gallery/nike-samothrace.jpg",
        "/images/gallery/laocoon.jpg",
    ]

    for idx, fig in enumerate(missing_figs, 1):
        clean_key = fig.lower()
        file_name = f"{clean_key}.jpg"
        dest = PORTRAITS_DIR / file_name
        web_path = f"/images/portraits/{file_name}"

        if dest.exists() and dest.stat().st_size > 3000:
            portraits_map[clean_key] = web_path
            (DIST_PORTRAITS_DIR / file_name).write_bytes(dest.read_bytes())
            print(f"  [{idx}/{len(missing_figs)}] [Cached] {fig}")
            continue

        queries = FIGURE_QUERIES[fig]
        print(f"  [{idx}/{len(missing_figs)}] Searching {fig}...", end=" ", flush=True)

        found = False
        for q in queries:
            res = query_commons(q)
            if res and res.get("thumb"):
                ok = download_image(res["thumb"], dest, max_size=500)
                if ok:
                    print(f"saved: {res['title'][:35]}")
                    portraits_map[clean_key] = web_path
                    (DIST_PORTRAITS_DIR / file_name).write_bytes(dest.read_bytes())
                    found = True
                    break
            time.sleep(0.25)

        if not found:
            fb = fallback_bank[idx % len(fallback_bank)]
            portraits_map[clean_key] = fb
            print(f"thematic fallback -> {fb}")

    # Write updated portraits.js
    portraits_js_code = (
        "// Authentic museum statue & classical portrait mappings for Pantheon figures.\n"
        "export const PORTRAITS = " + json.dumps(portraits_map, indent=2) + ";\n\n"
        "export function portraitFor(name) {\n"
        "  return PORTRAITS[String(name || '').trim().toLowerCase()] || null;\n"
        "}\n"
    )
    PORTRAITS_JS.write_text(portraits_js_code, encoding="utf-8")
    print(f"\n=== FINISHED ===")
    print(f"Total portraits in Pantheon registry: {len(portraits_map)}")


if __name__ == "__main__":
    run()
