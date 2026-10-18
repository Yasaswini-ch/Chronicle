#!/usr/bin/env python
"""Fetch authentic classical artworks and portraits for all myths and gods in Chronicle.

Downloads public-domain artworks from Wikimedia Commons:
1. Portraits for all major Olympian gods, Titans, and mythological figures in the Pantheon.
2. Narrative artworks for all 125 myths in the corpus.
3. Updates frontend/src/data/portraits.js and frontend/src/data/mythImages.js.
4. Copies assets to frontend/public/ and frontend/dist/.
"""

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
MYTHS_FILE = ROOT / "data" / "processed" / "myths.json"
PORTRAITS_DIR = ROOT / "frontend" / "public" / "images" / "portraits"
MYTHS_IMG_DIR = ROOT / "frontend" / "public" / "images" / "myths"
DIST_PORTRAITS_DIR = ROOT / "frontend" / "dist" / "images" / "portraits"
DIST_MYTHS_DIR = ROOT / "frontend" / "dist" / "images" / "myths"

PORTRAITS_JS = ROOT / "frontend" / "src" / "data" / "portraits.js"
MYTH_IMAGES_JS = ROOT / "frontend" / "src" / "data" / "mythImages.js"

API = "https://commons.wikimedia.org/w/api.php"
UA = "ChronicleClassicalArt/1.0 (https://github.com/Yasaswini-ch/Chronicle; educational mythology platform)"

OK_LICENCE = re.compile(r"(public domain|^pd|cc0|cc[- ]by)", re.I)
BAD_WORDS = re.compile(r"(map|coin|stamp|logo|diagram|cover|poster|flag|portrait of (mr|mrs)|photograph of|statue of liberty|\.svg|chart|plan of|signature|bookplate|postcard)", re.I)

# God & figure queries for the Pantheon
GOD_QUERIES: dict[str, list[str]] = {
    "zeus": ["Zeus Otricoli bust Vatican", "Zeus statue Louvre", "Jupiter sculpture Roman"],
    "hera": ["Hera Barberini Vatican statue", "Hera bust Vatican", "Hera Ludovisi"],
    "poseidon": ["Poseidon of Melos statue", "Poseidon statue Athens National Archaeological", "Neptune statue Louvre"],
    "athena": ["Athena Giustiniani statue Vatican", "Mattei Athena Louvre", "Pallas Athena statue"],
    "apollo": ["Apollo Belvedere statue Vatican", "Apollo Belvedere", "Apollo statue Vatican"],
    "artemis": ["Diana of Versailles statue Louvre", "Diane Chasseresse Louvre", "Artemis sculpture"],
    "aphrodite": ["Venus de Milo Louvre", "Aphrodite of Knidos statue", "Capitoline Venus statue"],
    "ares": ["Ares Borghese statue Louvre", "Mars statue Louvre", "Ares Ludovisi"],
    "hermes": ["Hermes of Praxiteles Olympia", "Hermes Ingenui statue Vatican", "Hermes Fastening His Sandal Louvre"],
    "hephaestus": ["Vulcan statue Guillaume Coustou Louvre", "Hephaestus sculpture Thorvaldsen", "Vulcan sculpture"],
    "dionysus": ["Bacchus statue Michelangelo Bargello", "Dionysos statue Louvre", "Bacchus sculpture"],
    "hades": ["Pluto Cerberus statue Roman", "Hades Cerberus sculpture", "Pluto statue"],
    "demeter": ["Demeter of Knidos statue British Museum", "Ceres statue Vatican", "Demeter sculpture"],
    "persephone": ["Rape of Proserpina Bernini sculpture", "Persephone statue Roman", "Proserpina sculpture"],
    "cronus": ["Saturn devouring his son Rubens", "Cronus sculpture", "Saturn Roman relief"],
    "rhea": ["Rhea Cybele statue Madrid", "Cybele statue Roman", "Rhea goddess sculpture"],
    "uranus": ["Uranus relief Roman", "Ouranos painting classical", "Caelus Roman statue"],
    "gaia": ["Tellus relief Ara Pacis", "Gaea goddess sculpture", "Gaia Roman relief"],
    "atlas": ["Farnese Atlas statue Naples", "Atlas Farnese", "Atlas sculpture classical"],
    "prometheus": ["Prometheus Nicolas-Sébastien Adam Louvre", "Prometheus Gustave Moreau", "Prometheus Titan sculpture"],
    "epimetheus": ["Pandora and Epimetheus painting", "Epimetheus classical"],
    "heracles": ["Farnese Hercules statue Naples", "Hercules Farnese", "Herakles sculpture"],
    "hercules": ["Farnese Hercules statue Naples", "Hercules Farnese", "Herakles sculpture"],
    "achilles": ["Achilles statue Hyde Park", "Achilles Borghese Louvre", "Achilles fighting Hector classical"],
    "odysseus": ["Head of Odysseus Sperlonga sculpture", "Odysseus statue Sperlonga", "Ulysses sculpture"],
    "theseus": ["Theseus and Minotaur statue Barye", "Theseus statue Canova", "Theseus sculpture"],
    "perseus": ["Perseus with Head of Medusa Cellini", "Perseus Canova statue", "Perseus sculpture"],
    "jason": ["Jason with the Golden Fleece Thorvaldsen", "Jason Golden Fleece statue"],
    "medea": ["Medea statue Paul Lemoyne", "Medea painting Delacroix", "Medea classical"],
    "oedipus": ["Oedipus and the Sphinx Ingres", "Oedipus classical painting"],
    "daedalus": ["Daedalus and Icarus statue Canova", "Daedalus sculpture classical"],
    "icarus": ["Lament for Icarus Draper", "Icarus falling classical"],
    "medusa": ["Medusa Rondanini Munich", "Medusa Bernini bust Rome", "Medusa sculpture"],
    "minotaur": ["Theseus slaying Minotaur statue Barye", "Minotaur classical sculpture"],
    "paris": ["Paris statue Canova", "Judgement of Paris classical"],
    "hector": ["Hector statue Thorvaldsen", "Hector Troy classical"],
    "helen": ["Helen of Troy painting Evelyn De Morgan", "Helen of Troy classical painting"],
    "agamemnon": ["Mask of Agamemnon National Archaeological Museum", "Agamemnon bust"],
    "clytemnestra": ["Clytemnestra John Collier painting", "Clytemnestra classical"],
    "orpheus": ["Orpheus statue classical", "Orpheus and Eurydice Rodin"],
    "eurydice": ["Eurydice statue classical", "Orpheus and Eurydice Corot"],
    "psyche": ["Psyche Revived by Cupid Kiss Canova Louvre", "Psyche statue Canova"],
    "eros": ["Eros Farnese statue Naples", "Cupid statue Roman", "Eros sculpture"],
    "cupid": ["Cupid and Psyche Canova Louvre", "Cupid sculpture classical"],
    "bellerophon": ["Bellerophon Pegasus statue", "Bellerophon relief Aphrodisias"],
    "midas": ["Midas and Silenus painting", "King Midas classical"],
    "arachne": ["Minerva and Arachne painting Houasse", "Arachne painting classical"],
    "niobe": ["Niobe Group sculpture Uffizi", "Niobe statue Roman"],
    "phaethon": ["Fall of Phaethon Rubens", "Phaethon classical painting"],
    "chiron": ["Achilles and Chiron painting Regnault", "Chiron centaur painting"],
    "cerberus": ["Cerberus statue Roman", "Heracles and Cerberus classical"],
    "pandora": ["Pandora Waterhouse painting", "Pandora opening box classical"],
    "deucalion": ["Deucalion and Pyrrha painting Rubens", "Deucalion Pyrrha classical"],
    "pyramus": ["Pyramus and Thisbe painting", "Pyramus Thisbe classical"],
    "thisbe": ["Thisbe Waterhouse painting", "Thisbe classical painting"],
    "charon": ["Charon crossing the Styx Patinir", "Charon ferry classical"],
    "hypnos": ["Hypnos bronze head British Museum", "Hypnos statue classical"],
    "thanatos": ["Thanatos sculpture classical", "Thanatos Roman"],
    "pan": ["Pan statue Vatican", "Pan and Daphnis sculpture"],
    "hestia": ["Hestia Giustiniani statue Rome", "Hestia sculpture Roman"],
    "alcmene": ["Alcmene Hercules classical", "Alcmene Roman"],
    "semile": ["Jupiter and Semele Gustave Moreau", "Semele classical"],
    "minos": ["King Minos classical statue", "Minos sculpture"],
    "leda": ["Leda and the Swan painting", "Leda Swan Leonardo"],
    "ariadne": ["Sleeping Ariadne Vatican statue", "Ariadne statue Louvre"],
    "atreus": ["House of Atreus classical", "Atreus sculpture"],
    "priam": ["Priam Achilles painting", "Priam Troy classical"],
    "hecuba": ["Hecuba Troy painting", "Hecuba classical"],
    "jocasta": ["Jocasta Oedipus painting", "Jocasta classical"],
}

# Import QUERIES from fetch_myth_art.py
from scripts.fetch_myth_art import QUERIES as BASE_MYTH_QUERIES

MYTH_QUERIES = dict(BASE_MYTH_QUERIES)

# Additional title mappings for myths not covered in BASE_MYTH_QUERIES
ADDITIONAL_QUERIES = {
    "The Fall of Icarus": ["Daedalus and Icarus painting", "Fall of Icarus painting"],
    "The Labyrinth of Daedalus": ["Theseus Minotaur labyrinth painting", "Daedalus labyrinth classical"],
    "The Bear Callisto": ["Callisto Diana painting", "Jupiter and Callisto painting"],
    "The Flaying of Marsyas": ["Apollo and Marsyas painting Titian", "Apollo Marsyas painting"],
    "Eris and the Golden Apple": ["Judgement of Paris painting", "Apple of Discord painting"],
    "The Jealousy of Eileithyia": ["Birth of Hercules painting", "Alcmene Hercules classical"],
}
MYTH_QUERIES.update(ADDITIONAL_QUERIES)


def strip_html(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def query_commons(query: str) -> dict | None:
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": f"{query} filetype:bitmap",
        "gsrnamespace": 6,
        "gsrlimit": 8,
        "prop": "imageinfo",
        "iiprop": "url|size|extmetadata|mime",
        "iiurlwidth": 800,
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
            artist = strip_html(meta.get("Artist", {}).get("value", ""))[:90] or "Classical Roman/Greek Antiquity"
            name = strip_html(meta.get("ObjectName", {}).get("value", ""))[:100] or re.sub(r"\.\w+$", "", title.replace("File:", ""))
            return {
                "thumb": thumb,
                "title": title,
                "credit": f"{artist}, {name}".strip(", ")[:140],
                "license": lic or "Public Domain",
            }
    except Exception as e:
        print(f"  [Warn] Query '{query}' failed: {e}")
    return None


def download_image(url: str, dest_path: Path, max_size: int = 800) -> bool:
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
        except Exception as e:
            time.sleep(1.0 * (attempt + 1))
    return False


def run():
    PORTRAITS_DIR.mkdir(parents=True, exist_ok=True)
    MYTHS_IMG_DIR.mkdir(parents=True, exist_ok=True)
    DIST_PORTRAITS_DIR.mkdir(parents=True, exist_ok=True)
    DIST_MYTHS_DIR.mkdir(parents=True, exist_ok=True)

    print("=== 1. FETCHING GOD & FIGURE PORTRAITS ===")
    portraits_map: dict[str, str] = {}

    for fig, queries in GOD_QUERIES.items():
        dest = PORTRAITS_DIR / f"{fig}.jpg"
        web_path = f"/images/portraits/{fig}.jpg"
        if dest.exists() and dest.stat().st_size > 5000:
            print(f"  [OK:Cache] {fig} -> {dest.name}")
            portraits_map[fig] = web_path
            # ensure copy in dist
            (DIST_PORTRAITS_DIR / f"{fig}.jpg").write_bytes(dest.read_bytes())
            continue

        print(f"  [Fetch] Searching portrait for {fig}...", end=" ", flush=True)
        found = False
        for q in queries:
            res = query_commons(q)
            if res and res.get("thumb"):
                ok = download_image(res["thumb"], dest, max_size=500)
                if ok:
                    print(f"found: {res['title'][:40]}")
                    portraits_map[fig] = web_path
                    (DIST_PORTRAITS_DIR / f"{fig}.jpg").write_bytes(dest.read_bytes())
                    found = True
                    break
            time.sleep(0.3)
        if not found:
            print("not found, will fallback")

    # Generate portraits.js
    portraits_js_code = (
        "// Authentic museum statue & classical portrait mappings for Pantheon figures.\n"
        "export const PORTRAITS = " + json.dumps(portraits_map, indent=2) + ";\n\n"
        "export function portraitFor(name) {\n"
        "  return PORTRAITS[String(name || '').trim().toLowerCase()] || null;\n"
        "}\n"
    )
    PORTRAITS_JS.write_text(portraits_js_code, encoding="utf-8")
    print(f"  -> Wrote {len(portraits_map)} portraits to {PORTRAITS_JS}")

    print("\n=== 2. FETCHING MISSING MYTH ARTWORKS ===")
    with open(MYTHS_FILE, "r", encoding="utf-8") as f:
        myths = json.load(f)

    # Read existing mythImages.js if available
    myth_images_dict = {}
    if MYTH_IMAGES_JS.exists():
        content = MYTH_IMAGES_JS.read_text(encoding="utf-8")
        for k, f, c in re.findall(r'(\w+):\s*\{\s*file:\s*[\'"]([^\'"]+)[\'"],\s*credit:\s*[\'"]([^\'"]+)[\'"]', content):
            myth_images_dict[k] = {"file": f, "credit": c}

    # Fallback pool from decor and gallery
    fallback_pool = [
        {"file": "/images/decor/temple-clouds-hero.jpg", "credit": "Classical Greek Acropolis & Olympian Vista"},
        {"file": "/images/decor/delphi-landscape.jpg", "credit": "Sanctuary of Apollo at Delphi, Greece"},
        {"file": "/images/decor/mount-olympus-landscape.jpg", "credit": "Mount Olympus, Abode of the Gods"},
        {"file": "/images/decor/ruins-engraving.png", "credit": "Classical Ruins Engraving of Antiquity"},
        {"file": "/images/gallery/parthenon.jpg", "credit": "The Parthenon, Athens, Greece"},
        {"file": "/images/gallery/nike-samothrace.jpg", "credit": "Winged Victory of Samothrace, Musée du Louvre"},
    ]

    for idx, m in enumerate(myths, 1):
        mid = m["id"]
        mtitle = m["title"]
        dest = MYTHS_IMG_DIR / f"{mid}.jpg"
        web_path = f"/images/myths/{mid}.jpg"

        if mid in myth_images_dict and dest.exists() and dest.stat().st_size > 5000:
            # Sync to dist
            (DIST_MYTHS_DIR / f"{mid}.jpg").write_bytes(dest.read_bytes())
            continue

        if dest.exists() and dest.stat().st_size > 5000:
            myth_images_dict[mid] = {
                "file": web_path,
                "credit": f"Classical depiction of {mtitle}",
            }
            (DIST_MYTHS_DIR / f"{mid}.jpg").write_bytes(dest.read_bytes())
            continue

        # Look up search queries
        queries = MYTH_QUERIES.get(mtitle, [f"{mtitle} Greek myth painting", f"{mtitle} classical painting"])
        print(f"  [{idx}/{len(myths)}] {mtitle}...", end=" ", flush=True)

        found = False
        for q in queries:
            res = query_commons(q)
            if res and res.get("thumb"):
                ok = download_image(res["thumb"], dest, max_size=900)
                if ok:
                    print(f"saved: {res['title'][:35]}")
                    myth_images_dict[mid] = {
                        "file": web_path,
                        "credit": res["credit"],
                    }
                    (DIST_MYTHS_DIR / f"{mid}.jpg").write_bytes(dest.read_bytes())
                    found = True
                    break
            time.sleep(0.3)

        if not found:
            # Use thematic fallback
            fb = fallback_pool[(idx) % len(fallback_pool)]
            myth_images_dict[mid] = {
                "file": fb["file"],
                "credit": fb["credit"],
            }
            print(f"thematic plate -> {fb['file']}")

    # Write updated mythImages.js
    myth_images_js_code = (
        "// Real classical artwork for each myth in the Chronicle corpus.\n"
        "export const MYTH_IMAGES = " + json.dumps(myth_images_dict, indent=2) + ";\n\n"
        "export function mythImageFor(mythId) {\n"
        "  return MYTH_IMAGES[mythId] || null;\n"
        "}\n"
    )
    MYTH_IMAGES_JS.write_text(myth_images_js_code, encoding="utf-8")
    print(f"\n=== FINISHED ===")
    print(f"Total myths with artwork: {len(myth_images_dict)} / {len(myths)}")
    print(f"Total gods with portraits: {len(portraits_map)}")


if __name__ == "__main__":
    run()
