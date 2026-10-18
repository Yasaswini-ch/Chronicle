#!/usr/bin/env python
"""Find and fetch public-domain artwork for myths from Wikimedia Commons.

Two steps, so a person approves every picture before it ships:

  python scripts/fetch_myth_art.py search
      For each myth without artwork, search Commons and save up to three candidate
      images (with licence and credit) plus labelled contact sheets in data/raw/art/.
      Look at the sheets and record your choices in data/annotations/myth_art_choices.json
      as {"myth_id": candidate_number or null}.

  python scripts/fetch_myth_art.py build
      Download the chosen images at display size into frontend/public/images/myths/ and write
      frontend/src/data/mythArt.json (file, credit, licence, source link for each).

Only images whose licence is public domain, CC0 or CC BY / CC BY-SA are considered, and the
credit is always shown next to the picture. A story with no good match simply gets no picture
(the interface draws a designed plate instead); a wrong picture is worse than none.
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

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
MYTHS = ROOT / "data" / "processed" / "myths.json"
CHOICES = ROOT / "data" / "annotations" / "myth_art_choices.json"
RAW = ROOT / "data" / "raw" / "art"
OUT_IMG = ROOT / "frontend" / "public" / "images" / "myths"
OUT_JSON = ROOT / "frontend" / "src" / "data" / "mythArt.json"
API = "https://commons.wikimedia.org/w/api.php"
UA = "ChronicleMythArt/1.0 (https://github.com/Yasaswini-ch/Chronicle; educational project)"

# Search phrases per story title (first that yields good candidates wins).
QUERIES: dict[str, list[str]] = {
    "Prometheus and Pandora (Part 1)": ["Pandora opening box painting", "Prometheus creating man painting"],
    "Prometheus and Pandora (Part 2)": ["Deucalion and Pyrrha painting", "Deucalion Pyrrha flood"],
    "Apollo and Daphne": ["Apollo and Daphne painting", "Apollo Daphne Tiepolo"],
    "Pyramus and Thisbe": ["Pyramus and Thisbe painting", "Thisbe Pyramus Waterhouse"],
    "Cephalus and Procris": ["Cephalus and Procris painting", "Death of Procris"],
    "Io and Callisto": ["Jupiter and Io Correggio", "Io Jupiter cloud painting"],
    "Callisto": ["Callisto Diana painting", "Callisto bear Juno painting"],
    "Diana and Actaeon": ["Diana and Actaeon painting", "Actaeon Titian"],
    "Latona and the Rustics": ["Latona Lycian peasants frogs painting"],
    "Midas": ["King Midas golden touch painting", "Midas Bacchus painting"],
    "Baucis and Philemon": ["Baucis and Philemon painting", "Philemon and Baucis Rubens"],
    "Proserpine (Part 1)": ["Rape of Proserpina painting", "Abduction of Persephone painting"],
    "Proserpine (Part 2)": ["Ceres searching Proserpine painting", "Persephone Rossetti Proserpine"],
    "Glaucus and Scylla": ["Glaucus and Scylla painting", "Scylla Circe painting"],
    "Pygmalion": ["Pygmalion and Galatea Gerome", "Pygmalion painting statue"],
    "Venus and Adonis": ["Venus and Adonis Titian", "Venus Adonis painting"],
    "Apollo and Hyacinthus": ["Death of Hyacinthus Tiepolo", "Apollo Hyacinth painting"],
    "Vertumnus and Pomona (Part 1)": ["Vertumnus and Pomona painting"],
    "Vertumnus and Pomona (Part 2)": ["Pomona painting", "Vertumnus Pomona fresco"],
    "Cupid and Psyche (Part 1)": ["Cupid and Psyche painting", "Psyche abandoned rock painting"],
    "Cupid and Psyche (Part 2)": ["Psyche lamp Cupid painting", "Cupid Psyche sleeping Gerard"],
    "Cupid and Psyche (Part 3)": ["Psyche Venus tasks painting", "Psyche sorting seeds ants"],
    "Cupid and Psyche (Part 4)": ["Psyche opening the golden box Waterhouse", "Psyche box Proserpine painting"],
    "Cadmus": ["Cadmus slaying the dragon painting", "Cadmus dragon teeth painting"],
    "The Myrmidons": ["Aeacus Myrmidons ants painting", "Jupiter Aegina painting"],
    "Nisus and Scylla": ["Scylla Nisus purple hair painting", "Scylla cutting hair of Nisus"],
    "Echo and Narcissus": ["Echo and Narcissus Waterhouse", "Narcissus painting Caravaggio"],
    "Minerva and Arachne": ["Minerva and Arachne painting", "Spinners Velazquez Arachne"],
    "Niobe": ["Niobe painting Wilson", "Niobe children killed painting"],
    "Perseus and Medusa": ["Perseus beheading Medusa painting", "Perseus Medusa Cellini"],
    "The Sea-Monster": ["Perseus and Andromeda painting", "Perseus rescues Andromeda"],
    "The Wedding Feast": ["Perseus Phineus wedding feast painting", "Perseus Phineus"],
    "Monsters of Myth": ["Chimera of Arezzo", "Griffin ancient Greek painting"],
    "The Sphinx": ["Oedipus and the Sphinx Ingres", "Oedipus Sphinx painting"],
    "Pegasus and the Chimaera": ["Bellerophon Pegasus Chimaera painting", "Bellerophon killing Chimera"],
    "The Centaurs": ["Centauromachy painting", "Chiron Achilles painting"],
    "Medea and Aeson": ["Medea rejuvenating Aeson", "Medea painting Delacroix"],
    "The Golden Fleece (Part 1)": ["Jason Golden Fleece painting", "Argonauts painting"],
    "The Golden Fleece (Part 2)": ["Jason Medea Colchis dragon painting", "Jason taking the Golden Fleece"],
    "Meleager and Atalanta": ["Meleager Atalanta Calydonian boar painting", "Death of Meleager"],
    "Atalanta": ["Atalanta Hippomenes Guido Reni", "Atalanta race golden apples painting"],
    "Hercules (Part 1)": ["Hercules Hydra painting", "Heracles labours painting"],
    "Hercules (Part 2)": ["Hercules Cerberus painting", "Heracles Cerberus Zurbaran"],
    "Hercules (Part 3)": ["Hercules Nessus Deianira painting", "Death of Hercules painting"],
    "Theseus (Part 1)": ["Theseus slaying the Minotaur painting", "Theseus Minotaur"],
    "Theseus (Part 2)": ["Theseus and Ariadne Naxos painting", "Theseus Amazons painting"],
    "Daedalus": ["Daedalus and Icarus painting", "Daedalus Icarus wings"],
    "Castor and Pollux": ["Castor and Pollux painting", "Dioscuri painting"],
    "Bacchus (Part 1)": ["Bacchus painting Titian", "Birth of Bacchus painting"],
    "Erysichthon": ["Erysichthon Ceres painting"],
    "Achelous and Hercules": ["Hercules and Achelous painting Benton", "Heracles Achelous"],
    "Admetus and Alcestis": ["Alcestis Hercules Death painting", "Alcestis painting Kauffman"],
    "Antigone": ["Antigone Oedipus Colonus painting", "Antigone painting"],
    "Penelope": ["Penelope weaving Waterhouse", "Penelope and her suitors Waterhouse"],
    "Orpheus and Eurydice": ["Orpheus and Eurydice painting", "Orpheus Eurydice Corot"],
    "Aristaeus, the Bee-Keeper": ["Aristaeus painting bees", "Aristaeus Proteus"],
    "Ibycus": ["Ibycus cranes painting"],
    "Simonides": ["Simonides Scopas banquet painting", "Castor Pollux banquet Scopas"],
    "Orion": ["Orion painting Poussin", "Orion blind Diana painting"],
    "Aurora and Tithonus": ["Aurora and Tithonus painting", "Aurora Tithonus"],
    "Acis and Galatea": ["Acis and Galatea Poussin", "Polyphemus Galatea painting"],
    "The Trojan War (Part 1)": ["Judgement of Paris painting", "Judgment of Paris Rubens"],
    "The Trojan War (Part 2)": ["Sacrifice of Iphigenia painting", "Achilles Agamemnon quarrel Tiepolo"],
    "The Trojan War (Part 3)": ["Achilles Patroclus painting", "Briseis Achilles painting"],
    "The Trojan War (Part 4)": ["Death of Patroclus painting", "Patroclus body painting David"],
    "The Trojan War (Part 5)": ["Achilles Hector duel painting", "Hector Achilles combat"],
    "The Trojan War (Part 6)": ["Priam Achilles Hector body painting", "Achilles dragging Hector body"],
    "The Fall of Troy (Part 1)": ["Trojan Horse Tiepolo", "Wooden horse Troy painting"],
    "The Fall of Troy (Part 2)": ["Sack of Troy painting", "Priam death painting"],
    "Menelaus and Helen": ["Helen of Troy painting", "Menelaus Helen painting"],
    "Agamemnon, Orestes, and Electra": ["Orestes pursued by the Furies Bouguereau", "Orestes Electra painting"],
    "Return of Ulysses (Part 1)": ["Ulysses Polyphemus Turner", "Odysseus Polyphemus painting"],
    "Return of Ulysses (Part 2)": ["Circe offering cup to Ulysses Waterhouse", "Ulysses Circe painting"],
    "The Laestrygonians": ["Laestrygonians Odyssey painting"],
    "Scylla and Charybdis": ["Ulysses Scylla Charybdis painting", "Scylla Charybdis painting"],
    "The Phaeacians (Part 1)": ["Ulysses Nausicaa painting", "Nausicaa Odysseus"],
    "The Phaeacians (Part 2)": ["Ulysses at the court of Alcinous painting", "Odysseus Alcinous"],
    "Fate of the Suitors": ["Odysseus slaying the suitors painting", "Ulysses Penelope suitors painting"],
    "Adventures of Aeneas (Part 1)": ["Flight of Aeneas from Troy Barocci", "Aeneas Anchises Ascanius painting"],
    "Adventures of Aeneas (Part 2)": ["Aeneas Harpies painting", "Aeneas Dido painting"],
    "Adventures of Aeneas (Part 3)": ["Dido and Aeneas painting Guerin", "Death of Dido painting"],
    "Palinurus": ["Palinurus painting", "Aeneas Palinurus"],
    "The Infernal Regions (Part 1)": ["Aeneas Sibyl underworld painting", "Charon ferry Styx painting"],
    "The Infernal Regions (Part 2)": ["Aeneas Cerberus Sibyl", "Aeneas Golden Bough Turner"],
    "The Infernal Regions (Part 3)": ["Aeneas Anchises Elysium painting", "Elysian fields painting"],
    "Camilla (Part 1)": ["Aeneas Latinus painting", "Aeneas landing Latium painting"],
    "Camilla (Part 2)": ["Camilla Volscian painting", "Camilla warrior painting"],
    "Evander": ["Aeneas Evander painting", "Aeneas Pallas Evander"],
    "Infant Rome": ["Romulus Remus she-wolf painting", "Aeneas Tiber painting"],
    "Nisus and Euryalus": ["Nisus and Euryalus painting", "Nisus Euryalus Aeneid"],
    "Mezentius": ["Mezentius Aeneas painting", "Aeneas Turnus Mezentius"],
    "Pallas, Camilla, Turnus": ["Turnus Aeneas duel painting", "Death of Turnus painting"],
}

OK_LICENCE = re.compile(r"(public domain|^pd|cc0|cc[- ]by)", re.I)
BAD_WORDS = re.compile(r"(map|coin|stamp|logo|diagram|cover|poster|flag|portrait of (mr|mrs)|photograph of|statue of liberty|\.svg|"
                       r"chart|plan of|signature|bookplate|postcard)", re.I)


def get(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode(params | {"format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def strip(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def candidates_for(queries: list[str], need: int = 3) -> list[dict]:
    seen, out = set(), []
    for q in queries:
        data = get({"action": "query", "generator": "search", "gsrsearch": f"{q} filetype:bitmap", "gsrnamespace": 6,
                    "gsrlimit": 12, "prop": "imageinfo", "iiprop": "url|size|extmetadata|mime",
                    "iiurlwidth": 1100, "iiextmetadatafilter": "LicenseShortName|Artist|Credit|ObjectName|ImageDescription|DateTimeOriginal"})
        pages = sorted((data.get("query", {}).get("pages", {})).values(), key=lambda p: p.get("index", 99))
        for p in pages:
            info = (p.get("imageinfo") or [{}])[0]
            title = p.get("title", "")
            meta = info.get("extmetadata", {})
            lic = strip(meta.get("LicenseShortName", {}).get("value", ""))
            if title in seen or not info or not OK_LICENCE.search(lic) or BAD_WORDS.search(title):
                continue
            if info.get("mime") not in ("image/jpeg", "image/png"):
                continue
            w, h = info.get("width", 0), info.get("height", 0)
            if w < 700 or h < 500 or not (0.45 < w / h < 2.3):
                continue
            seen.add(title)
            out.append({
                "title": title, "thumb": info.get("thumburl"), "page": info.get("descriptionurl"), "license": lic,
                "artist": strip(meta.get("Artist", {}).get("value", ""))[:90],
                "name": strip(meta.get("ObjectName", {}).get("value", ""))[:100],
                "date": strip(meta.get("DateTimeOriginal", {}).get("value", ""))[:30],
                "width": w, "height": h,
            })
            if len(out) >= need:
                return out
        time.sleep(0.4)
    return out


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"could not download {url}")


def search() -> None:
    myths = json.loads(MYTHS.read_text(encoding="utf-8"))
    have = {p.stem for p in OUT_IMG.glob("*.jpg")}
    todo = [m for m in myths if m["title"] in QUERIES and m["id"] not in have]
    RAW.mkdir(parents=True, exist_ok=True)
    cache_file = RAW / "candidates.json"
    cache = json.loads(cache_file.read_text(encoding="utf-8")) if cache_file.exists() else {}
    for i, m in enumerate(todo, 1):
        if m["id"] in cache:
            continue
        try:
            cache[m["id"]] = {"title": m["title"], "candidates": candidates_for(QUERIES[m["title"]])}
        except Exception as exc:  # network hiccup: leave for a re-run
            print("  skip", m["title"], exc)
            continue
        print(f"[{i}/{len(todo)}] {m['title']}: {len(cache[m['id']]['candidates'])} candidates", flush=True)
        cache_file.write_text(json.dumps(cache, indent=1, ensure_ascii=False), encoding="utf-8")
        time.sleep(0.3)
    contact_sheets(cache)


def contact_sheets(cache: dict, per_sheet: int = 10) -> None:
    font = ImageFont.load_default()
    ids = list(cache)
    for s in range(0, len(ids), per_sheet):
        chunk = ids[s : s + per_sheet]
        cell_w, cell_h, label_h = 330, 250, 38
        sheet = Image.new("RGB", (cell_w * 3 + 150, (cell_h + label_h) * len(chunk)), "white")
        d = ImageDraw.Draw(sheet)
        for row, mid in enumerate(chunk):
            y = row * (cell_h + label_h)
            d.text((6, y + 6), f"{s + row + 1}. {cache[mid]['title']}", fill="black", font=font)
            d.text((6, y + 22), mid, fill="gray", font=font)
            for col, c in enumerate(cache[mid]["candidates"]):
                f = RAW / f"{mid}_{col + 1}.jpg"
                try:
                    if not f.exists():
                        f.write_bytes(fetch_bytes(c["thumb"]))
                    im = Image.open(f).convert("RGB")
                    im.thumbnail((cell_w - 10, cell_h - 10))
                    x = 150 + col * cell_w
                    sheet.paste(im, (x, y + label_h))
                    d.text((x, y + 4), f"#{col + 1} {c['name'][:42] or c['title'][5:47]}", fill="navy", font=font)
                    d.text((x, y + 18), f"{c['artist'][:30]} | {c['license'][:16]}", fill="gray", font=font)
                except Exception as exc:
                    d.text((150 + col * cell_w, y + label_h + 10), f"(failed: {exc})", fill="red", font=font)
        out = RAW / f"sheet_{s // per_sheet + 1:02d}.jpg"
        sheet.save(out, quality=82)
        print("wrote", out.name, f"({len(chunk)} stories)")


def build() -> None:
    choices = json.loads(CHOICES.read_text(encoding="utf-8"))
    cache = json.loads((RAW / "candidates.json").read_text(encoding="utf-8"))
    OUT_IMG.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(OUT_JSON.read_text(encoding="utf-8")) if OUT_JSON.exists() else {}
    for mid, pick in choices.items():
        if not pick:
            continue
        c = cache[mid]["candidates"][int(pick) - 1]
        data = fetch_bytes(c["thumb"])  # already 1100px wide
        im = Image.open(io.BytesIO(data)).convert("RGB")
        im.thumbnail((1100, 1100))
        im.save(OUT_IMG / f"{mid}.jpg", "JPEG", quality=82, optimize=True, progressive=True)
        artist = c["artist"] or "Unknown artist"
        name = c["name"] or re.sub(r"\.\w+$", "", c["title"].replace("File:", ""))
        manifest[mid] = {"file": f"/images/myths/{mid}.jpg", "credit": f"{artist}, {name}".strip(", ")[:150],
                         "license": c["license"], "source": c["page"]}
        print("saved", mid, "<-", c["title"][:60])
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    {"search": search, "build": build}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
