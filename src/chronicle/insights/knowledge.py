"""Knowledge layer over the myth corpus: names, profiles, comparisons, motifs, quizzes.

``MythKnowledge`` is dependency-free (standard library only) so that it runs
unchanged on a serverless host. It combines four data sources:

* the myth records (``data/processed/myths.json``)
* the alias table (``data/annotations/character_aliases.json``) - Roman and
  epithet names resolve to one canonical Greek name
* the curated genealogy (``data/annotations/genealogy.json``)
* an optional :class:`~chronicle.ner.knowledge_graph.KnowledgeGraph`
"""

from __future__ import annotations

import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from chronicle.ner.kinship import FamilyTree
from chronicle.text.bm25 import BM25

ROOT = Path(__file__).resolve().parents[3]
ALIASES_PATH = ROOT / "data" / "annotations" / "character_aliases.json"
GENEALOGY_PATH = ROOT / "data" / "annotations" / "genealogy.json"

# Surface forms that are ordinary words, so only a Capitalised match counts.
_CASE_SENSITIVE = {"Hero", "Echo", "Pan", "Io", "Iris", "Sol", "Luna", "Ge", "Dis", "Pallas", "Amor", "Aurora", "Sibyl"}

# Olympian Greek <-> Roman equivalents used by the quiz and glossary.
ROMAN_NAMES = {
    "Zeus": "Jupiter", "Hera": "Juno", "Poseidon": "Neptune", "Hades": "Pluto", "Demeter": "Ceres",
    "Hestia": "Vesta", "Athena": "Minerva", "Apollo": "Apollo", "Artemis": "Diana", "Ares": "Mars",
    "Aphrodite": "Venus", "Hephaestus": "Vulcan", "Hermes": "Mercury", "Dionysus": "Bacchus",
    "Persephone": "Proserpine", "Eros": "Cupid", "Cronus": "Saturn", "Heracles": "Hercules",
    "Odysseus": "Ulysses",
}

# name -> (label, description, regex, optional constraints)
MOTIFS: dict[str, dict[str, Any]] = {
    "transformation": {
        "label": "Transformation",
        "description": "A character is changed into a tree, animal, stone, flower or constellation.",
        "pattern": r"\b(changed|turned|transformed|metamorphosed)\b[^.]{0,50}?\b(into|to)\s+(a\s+|an\s+|the\s+)?"
                   r"(tree|flower|stone|rock|bird|spider|stag|heifer|swan|laurel|reed|fountain|spring|stream|river|wolf|bear|"
                   r"star|constellation|statue|cow|mountain|lizard|serpent|dove|owl|hawk|lark|kingfisher|halcyon|insect|ant|"
                   r"beast|bull|cypress|myrtle|vine|tortoise|woman|maiden|rock)\b",
        "min": 1,
    },
    "underworld": {
        "label": "Journey to the Underworld",
        "description": "A mortal or god enters the realm of the dead.",
        "pattern": r"\b(Tartarus|Elysium|Styx|Acheron|Lethe|Cerberus|infernal regions|lower world|nether world|underworld|realm of (Pluto|Hades|Dis))\b",
        "min": 2,
    },
    "mortal_vs_god": {
        "label": "Mortal Defies a God",
        "description": "A human challenges, insults or rivals a deity and pays for it.",
        "pattern": r"\b(challenged|boast\w*|presum\w*|defied|insult\w*|contend\w*|vied|rival\w*|dared)\b",
        "min": 2,
        "types": {"mortal", "god"},
        "themes_any": {"hubris", "jealousy"},
    },
    "disguise": {
        "label": "Divine Disguise",
        "description": "A god hides in mortal or animal form to test or deceive.",
        "pattern": r"\b(disguis\w+|in the guise of|assum(ed|ing) the (form|shape)|took the (form|shape)|taking the (form|shape))\b",
        "min": 1,
    },
    "prophecy": {
        "label": "Prophecy and Oracles",
        "description": "A foretold fate shapes the story.",
        "pattern": r"\b(oracle\w*|prophe\w+|foretold|predicted|soothsayer|seer|augur\w*|destined|decreed by fate)\b",
        "min": 2,
    },
    "forbidden": {
        "label": "The Forbidden Act",
        "description": "A command or warning is broken, with fatal results.",
        "pattern": r"\b(forbade|forbidden|warned (him|her|them)|charged (him|her) not|on no account|look(ed)? back|disobey\w*)\b",
        "min": 1,
    },
    "monster": {
        "label": "Monster Slaying",
        "description": "A hero overcomes a monstrous creature.",
        "pattern": r"\b(slew|slain|killed|destroyed|overcame|conquered)\b[^.]{0,120}\b(monster|serpent|dragon|Hydra|Chimaera|Minotaur|Medusa|Gorgon|Sphinx|giant|Python|lion|boar|Cyclops|Cerberus|Geryon|Antaeus|Cacus|Harpies|stag|bull)\b",
        "min": 1,
    },
    "voyage": {
        "label": "Voyage and Wandering",
        "description": "A long sea-journey or exile drives the plot.",
        "pattern": r"\b(set sail|voyage\w*|sailed|wanderings?|wandered|shipwreck\w*)\b",
        "min": 2,
    },
    "hospitality": {
        "label": "Test of Hospitality",
        "description": "Gods visit as strangers; kindness is rewarded, cruelty punished.",
        "pattern": r"\b(hospitality|hospitable|strangers?|entertain\w*|guests?)\b",
        "min": 3,
    },
    "doomed_love": {
        "label": "Love Ends in Death",
        "description": "Lovers are parted or destroyed.",
        "pattern": r"\b(died|killed (himself|herself)|stabbed (himself|herself)|slew (himself|herself)|perished|mourn\w*|lament\w*)\b",
        "min": 2,
        "themes_any": {"love"},
    },
    "contest": {
        "label": "The Contest",
        "description": "A competition of skill or strength decides the outcome.",
        "pattern": r"\b(contest|competition|match(ed)? (his|her)|footrace|trial of skill|challenged (him|her))\b",
        "min": 2,
    },
}


# Phrases in a user question that point at a motif.
MOTIF_KEYWORDS = {
    "underworld": ["underworld", "afterlife", "land of the dead", "realm of the dead", "descent to"],
    "disguise": ["disguise", "disguised", "in disguise"],
    "prophecy": ["prophecy", "prophecies", "oracle", "foretold", "fated"],
    "monster": ["monster", "slay", "slaying", "slain", "dragon"],
    "mortal_vs_god": ["defy the gods", "defies the gods", "defying the gods", "challenge the gods", "challenges a god",
                      "mortal challenge", "mortals who", "mortal defies"],
    "forbidden": ["forbidden", "disobey", "disobedience", "broke a command", "looked back"],
    "voyage": ["voyage", "sea journey", "shipwreck", "sailing"],
    "hospitality": ["hospitality", "strangers", "guests"],
    "doomed_love": ["tragic love", "doomed love", "lovers die", "lovers parted"],
    "contest": ["contest", "competition", "competed", "rivalry of skill"],
    "transformation": ["turned into", "changed into", "turn into", "transformed into"],
}


def _sentence_at(text: str, pos: int) -> str:
    """The sentence of *text* that contains character offset *pos*."""
    marks = (". ", "? ", "! ", "\n")
    start = max(text.rfind(m, 0, pos) for m in marks)
    start = 0 if start < 0 else start + 1
    ends = [e for e in (text.find(m, pos) for m in marks) if e >= 0]
    end = min(ends) + 1 if ends else len(text)
    return text[start:end].strip()


class MythKnowledge:
    """Query interface over characters, families, themes and motifs."""

    def __init__(
        self,
        myths: list[dict[str, Any]],
        aliases: dict[str, list[str]] | None = None,
        family: FamilyTree | None = None,
    ) -> None:
        self.myths = myths
        self.by_id = {m["id"]: m for m in myths}
        if aliases is None:
            aliases = json.loads(ALIASES_PATH.read_text(encoding="utf-8")) if ALIASES_PATH.exists() else {}
        self.aliases = aliases
        types_path = ROOT / "data" / "annotations" / "character_types.json"
        self._types: dict[str, str] = json.loads(types_path.read_text(encoding="utf-8")) if types_path.exists() else {}
        if family is None:
            family = FamilyTree.from_file(GENEALOGY_PATH) if GENEALOGY_PATH.exists() else FamilyTree()
        self.family = family

        self._form_to_canon: dict[str, str] = {}
        for canon, alts in aliases.items():
            for form in (canon, *alts):
                self._form_to_canon.setdefault(form.lower(), canon)
        self._name_re = self._compile_names()

        self._characters: dict[str, dict[str, Any]] = {}
        self._index_characters()
        self._bm25: BM25 | None = None
        self._motif_cache: dict[str, list[dict[str, Any]]] | None = None

    # ------------------------------------------------------------------ names
    def _compile_names(self) -> re.Pattern[str]:
        forms = sorted(self._form_to_canon, key=len, reverse=True)
        return re.compile(r"\b(" + "|".join(re.escape(f) for f in forms) + r")\b", re.I) if forms else re.compile(r"(?!x)x")

    def resolve(self, name: str) -> str | None:
        """Canonical Greek name for any known form ("Minerva" -> "Athena")."""
        name = name.strip()
        return self._form_to_canon.get(name.lower()) or (name if name in self._characters or name in self.family else None)

    def find_characters(self, text: str) -> list[str]:
        """Canonical characters mentioned in *text*, in order of appearance."""
        found: list[str] = []
        for m in self._name_re.finditer(text):
            surface = m.group(1)
            canon = self._form_to_canon[surface.lower()]
            if (canon in _CASE_SENSITIVE or surface.title() in _CASE_SENSITIVE) and not surface[:1].isupper():
                continue
            if canon not in found:
                found.append(canon)
        return found

    @property
    def character_names(self) -> list[str]:
        return sorted(self._characters)

    def match_motif(self, query: str) -> str | None:
        """Motif id a question is asking about, if any."""
        q = query.lower()
        for mid, phrases in MOTIF_KEYWORDS.items():
            if any(p in q for p in phrases):
                return mid
        return None

    # ------------------------------------------------------------- characters
    def _index_characters(self) -> None:
        for m in self.myths:
            for rank, c in enumerate(m.get("characters", [])):
                name = c["name"] if isinstance(c, dict) else str(c)
                typ = c.get("type", "mortal") if isinstance(c, dict) else "mortal"
                info = self._characters.setdefault(name, {"types": Counter(), "myths": []})
                info["types"][typ] += 1
                info["myths"].append((m["id"], rank))

    def has_character(self, name: str) -> bool:
        return name in self._characters or name in self.family

    def characters(self) -> list[dict[str, Any]]:
        """All characters with myth counts, most prominent first."""
        rows = [
            {
                "name": n,
                "type": info["types"].most_common(1)[0][0],
                "myth_count": len(info["myths"]),
                "roman_name": ROMAN_NAMES.get(n),
            }
            for n, info in self._characters.items()
        ]
        return sorted(rows, key=lambda r: (-r["myth_count"], r["name"]))

    def profile(self, name: str) -> dict[str, Any] | None:
        """Everything the corpus knows about one character."""
        canon = self.resolve(name)
        if canon is None or not self.has_character(canon):
            return None
        info = self._characters.get(canon, {"types": Counter({self._types.get(canon, "mortal"): 1}), "myths": []})

        myth_rows, theme_counts, companions, places = [], Counter(), Counter(), Counter()
        relations: dict[tuple[str, str], str] = {}
        for mid, rank in sorted(info["myths"], key=lambda t: t[1]):
            m = self.by_id[mid]
            myth_rows.append({"id": mid, "title": m["title"], "theme": m.get("theme"), "themes": m.get("themes", [m.get("theme")]),
                              "source": m.get("source", "")})
            theme_counts.update(m.get("themes") or [m.get("theme")])
            places.update(m.get("locations", []))
            for c in m.get("characters", []):
                other = c["name"] if isinstance(c, dict) else str(c)
                if other != canon:
                    companions[other] += 1
            for r in m.get("relationships", []):
                if r["source"] == canon:
                    relations[(r["relation"], r["target"])] = m["title"]
                elif r["target"] == canon:
                    relations[(r["relation"] + "_by", r["source"])] = m["title"]
        return {
            "name": canon,
            "type": info["types"].most_common(1)[0][0],
            "aliases": [a for a in self.aliases.get(canon, []) if a != canon],
            "roman_name": ROMAN_NAMES.get(canon),
            "myths": myth_rows,
            "themes": [{"theme": t, "count": c} for t, c in theme_counts.most_common()],
            "companions": [{"name": n, "shared_myths": c} for n, c in companions.most_common(8)],
            "family": self.family.family_of(canon),
            "story_relations": [{"relation": r, "other": o, "myth": t} for (r, o), t in sorted(relations.items())],
            "locations": [p for p, _ in places.most_common(6)],
        }

    def family_members(self, name: str, relation: str) -> list[str] | None:
        """Relatives of *name* for a plural/singular kin word ("sons", "wife", ...)."""
        canon = self.resolve(name)
        if canon is None or canon not in self.family:
            return None
        fam, rel = self.family, relation.lower().rstrip("s") if relation != "children" else "children"
        female = fam.female
        parents, kids = sorted(fam.parents.get(canon, ())), sorted(fam.children.get(canon, ()))
        sibs = sorted(s for s, full in fam.siblings(canon).items() if full)  # full siblings; see half_siblings()
        spouses = sorted(fam.spouses.get(canon, ()))
        if relation in ("wives", "wife"):
            rel = "wife"
        table = {
            "father": [p for p in parents if p not in female], "mother": [p for p in parents if p in female],
            "parent": parents,
            "son": [k for k in kids if k not in female], "daughter": [k for k in kids if k in female],
            "child": kids, "children": kids,
            "brother": [s for s in sibs if s not in female], "sister": [s for s in sibs if s in female],
            "sibling": sibs,
            "wife": [s for s in spouses if s in female], "husband": [s for s in spouses if s not in female],
            "spouse": spouses,
        }
        return table.get(rel)

    def half_siblings(self, name: str, relation: str) -> list[str]:
        """Half-brothers / half-sisters of *name* matching a sibling kin word."""
        canon = self.resolve(name)
        if canon is None or canon not in self.family or relation.lower().rstrip("s") not in ("brother", "sister", "sibling"):
            return []
        want = relation.lower().rstrip("s")
        female = self.family.female
        out = [s for s, full in self.family.siblings(canon).items() if not full]
        if want == "brother":
            out = [s for s in out if s not in female]
        elif want == "sister":
            out = [s for s in out if s in female]
        return sorted(out)

    def compare(self, a: str, b: str) -> dict[str, Any] | None:
        """Side-by-side comparison of two characters."""
        pa, pb = self.profile(a), self.profile(b)
        if pa is None or pb is None:
            return None
        ids_a = {m["id"] for m in pa["myths"]}
        ids_b = {m["id"] for m in pb["myths"]}
        shared = [self.by_id[i]["title"] for i in sorted(ids_a & ids_b)]
        themes_a = {t["theme"] for t in pa["themes"]}
        themes_b = {t["theme"] for t in pb["themes"]}
        relation = self.family.describe(pa["name"], pb["name"]) or self.family.path_description(pa["name"], pb["name"])
        return {
            "a": pa, "b": pb,
            "shared_myths": shared,
            "shared_themes": sorted(themes_a & themes_b),
            "only_a_themes": sorted(themes_a - themes_b),
            "only_b_themes": sorted(themes_b - themes_a),
            "relationship": relation,
        }

    # ---------------------------------------------------------------- search
    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """BM25 search over titles, characters and text (dependency-free)."""
        if self._bm25 is None:
            self._bm25 = BM25([self._doc(m) for m in self.myths])
        return [self.myths[i] for i, _ in self._bm25.top(query, top_k)]

    @staticmethod
    def _doc(m: dict[str, Any]) -> str:
        names = " ".join(c["name"] if isinstance(c, dict) else str(c) for c in m.get("characters", []))
        return f"{m.get('title', '')} {m.get('title', '')} {names} {names} {m.get('text', '')}"

    # ---------------------------------------------------------------- motifs
    def _compute_motifs(self) -> dict[str, list[dict[str, Any]]]:
        out: dict[str, list[dict[str, Any]]] = {}
        for mid, spec in MOTIFS.items():
            rx = re.compile(spec["pattern"], re.I)
            rows = []
            for m in self.myths:
                text = m.get("text", "")
                hits = list(rx.finditer(text))
                if len(hits) < spec.get("min", 1):
                    continue
                types = {c.get("type") for c in m.get("characters", []) if isinstance(c, dict)}
                if "types" in spec and not spec["types"] <= types:
                    continue
                if "themes_any" in spec and not spec["themes_any"] & set(m.get("themes") or [m.get("theme")]):
                    continue
                snippet = _sentence_at(text, hits[0].start())
                rows.append({"id": m["id"], "title": m["title"], "theme": m.get("theme"), "strength": len(hits),
                             "snippet": snippet[:300]})
            out[mid] = sorted(rows, key=lambda r: -r["strength"])
        return out

    def motifs(self) -> list[dict[str, Any]]:
        if self._motif_cache is None:
            self._motif_cache = self._compute_motifs()
        return [{"id": k, "label": MOTIFS[k]["label"], "description": MOTIFS[k]["description"], "count": len(v)}
                for k, v in self._motif_cache.items()]

    def motif_myths(self, motif_id: str) -> list[dict[str, Any]] | None:
        if self._motif_cache is None:
            self._motif_cache = self._compute_motifs()
        return self._motif_cache.get(motif_id)

    # ------------------------------------------------------------------ quiz
    def quiz(self, n: int = 8, seed: int | None = None) -> list[dict[str, Any]]:
        """Multiple-choice questions built from the curated data (family, Roman names, myth casts)."""
        rng = random.Random(seed)
        pool: list[dict[str, Any]] = []
        fam = self.family

        def make(question: str, answer: str, distractors: list[str], kind: str, fact: str = "") -> None:
            wrong = [d for d in dict.fromkeys(distractors) if d != answer]
            if len(wrong) < 3:
                return
            opts = rng.sample(wrong, 3) + [answer]
            rng.shuffle(opts)
            pool.append({"kind": kind, "question": question, "options": opts, "answer": opts.index(answer), "fact": fact})

        people = sorted(fam.names)
        for child, parents in fam.parents.items():
            for p in parents:
                role = "mother" if p in fam.female else "father"
                far = [x for x in people if x not in fam.ancestors(child) and x != child and (x in fam.female) == (p in fam.female)]
                make(f"Who was the {role} of {child}?", p, far, "family", fam.describe(p, child) or "")
        for a, spouses in fam.spouses.items():
            for s in spouses:
                role = "wife" if s in fam.female else "husband"
                far = [x for x in people if x not in spouses and x != a and (x in fam.female) == (s in fam.female)]
                make(f"Who was the {role} of {a}?", s, far, "family", fam.describe(s, a) or "")
        greeks = list(ROMAN_NAMES)
        for g, r in ROMAN_NAMES.items():
            if g != r:
                make(f"What did the Romans call {g}?", r, [v for k, v in ROMAN_NAMES.items() if v != r and k != g], "roman",
                     f"{g} was known to the Romans as {r}.")
                make(f"Which Greek god or hero did the Romans call {r}?", g, [x for x in greeks if x != g], "roman",
                     f"{r} is the Roman name for {g}.")
        curated = [m for m in self.myths if m.get("corpus") == "curated"]
        all_names = self.character_names
        for m in curated:
            cast = [c["name"] for c in m.get("characters", []) if isinstance(c, dict)]
            if cast:
                a = rng.choice(cast)
                make(f"Which of these characters appears in \"{m['title']}\"?", a, [x for x in all_names if x not in cast], "myth",
                     f"{a} appears in {m['title']}.")
            if m.get("theme") in {"hubris", "love", "betrayal", "revenge", "wisdom", "jealousy"}:
                make(f"Which theme does \"{m['title']}\" most illustrate?", m["theme"],
                     ["hubris", "love", "betrayal", "revenge", "wisdom", "jealousy"], "theme", m.get("moral", ""))

        rng.shuffle(pool)
        seen, out = set(), []
        for q in pool:  # at most one question per kind-and-subject keeps the quiz varied
            key = q["question"]
            if key not in seen:
                seen.add(key)
                out.append(q)
            if len(out) >= n:
                break
        return out
