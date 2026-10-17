"""Family relations for Greek myth characters.

``FamilyTree`` loads the curated genealogy (``data/annotations/genealogy.json``)
and answers kinship questions in plain language, e.g. "Hera is Zeus's sister
and wife." Beyond the directly recorded relations it *derives* siblings (shared
parent), grandparents, aunts/uncles, nieces/nephews and cousins.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

# (neutral, male, female) wording for a relation of ``a`` *to* ``b``
_WORDS = {
    "parent": ("parent", "father", "mother"),
    "child": ("child", "son", "daughter"),
    "sibling": ("sibling", "brother", "sister"),
    "half_sibling": ("half-sibling", "half-brother", "half-sister"),
    "spouse": ("spouse", "husband", "wife"),
    "lover": ("lover", "lover", "lover"),
    "grandparent": ("grandparent", "grandfather", "grandmother"),
    "grandchild": ("grandchild", "grandson", "granddaughter"),
    "uncle_aunt": ("aunt or uncle", "uncle", "aunt"),
    "nibling": ("niece or nephew", "nephew", "niece"),
    "cousin": ("cousin", "cousin", "cousin"),
    "ancestor": ("ancestor", "ancestor", "ancestor"),
    "descendant": ("descendant", "descendant", "descendant"),
}


class FamilyTree:
    """Directed parent graph plus spouse / lover / explicit-sibling sets."""

    def __init__(self) -> None:
        self.parents: dict[str, set[str]] = defaultdict(set)
        self.children: dict[str, set[str]] = defaultdict(set)
        self.spouses: dict[str, set[str]] = defaultdict(set)
        self.lovers: dict[str, set[str]] = defaultdict(set)
        self.explicit_siblings: dict[str, set[str]] = defaultdict(set)
        self.female: set[str] = set()
        self.names: set[str] = set()

    # ------------------------------------------------------------------ load
    @classmethod
    def from_file(cls, path: str | Path) -> "FamilyTree":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_relations(data.get("relations", []), data.get("female", []))

    @classmethod
    def from_relations(cls, relations: list[list[str]], female: list[str] | None = None) -> "FamilyTree":
        tree = cls()
        tree.female = set(female or [])
        for s, rel, o in relations:
            tree.names.update((s, o))
            if rel == "parent_of":
                tree.parents[o].add(s)
                tree.children[s].add(o)
            elif rel == "married_to":
                tree.spouses[s].add(o)
                tree.spouses[o].add(s)
            elif rel == "lover_of":
                tree.lovers[s].add(o)
                tree.lovers[o].add(s)
            elif rel == "sibling_of":
                tree.explicit_siblings[s].add(o)
                tree.explicit_siblings[o].add(s)
        return tree

    def __contains__(self, name: str) -> bool:
        return name in self.names

    # --------------------------------------------------------------- derived
    def ancestors(self, name: str) -> set[str]:
        """All known ancestors of *name* (parents, grandparents, ...)."""
        seen: set[str] = set()
        stack = list(self.parents.get(name, ()))
        while stack:
            node = stack.pop()
            if node not in seen:
                seen.add(node)
                stack.extend(self.parents.get(node, ()))
        return seen

    def siblings(self, name: str) -> dict[str, bool]:
        """Return ``{sibling: is_full}``; full if they share every known parent."""
        result: dict[str, bool] = {s: True for s in self.explicit_siblings.get(name, ())}
        mine = self.parents.get(name, set())
        for parent in mine:
            for other in self.children.get(parent, ()):
                if other == name:
                    continue
                if other in self.ancestors(name) or name in self.ancestors(other):
                    continue  # a descendant of a sibling is not a sibling
                theirs = self.parents.get(other, set())
                # Full siblings need two known parents on both sides; one shared parent is only a half-sibling.
                full = len(mine) >= 2 and mine == theirs
                result[other] = result.get(other, False) or full
        return result

    def _word(self, kind: str, person: str) -> str:
        neutral, male, female = _WORDS[kind]
        if person in self.female:
            return female
        if person in self.names:
            return male
        return neutral

    # ------------------------------------------------------------- relations
    def relations(self, a: str, b: str) -> list[str]:
        """Roles *a* plays toward *b* (e.g. ``["spouse", "sibling"]``), best first."""
        kinds: list[str] = []
        if b in self.spouses.get(a, ()):
            kinds.append("spouse")
        if b in self.children.get(a, ()):
            kinds.append("parent")
        if b in self.parents.get(a, ()):
            kinds.append("child")
        sibs = self.siblings(a)
        if b in sibs:
            kinds.append("sibling" if sibs[b] or b in self.explicit_siblings.get(a, ()) else "half_sibling")
        if b in self.lovers.get(a, ()) and "spouse" not in kinds:
            kinds.append("lover")
        if kinds:
            return kinds

        grandparents = {g for p in self.parents.get(a, ()) for g in self.parents.get(p, ())}
        if b in grandparents:
            return ["grandchild"]
        if a in {g for p in self.parents.get(b, ()) for g in self.parents.get(p, ())}:
            return ["grandparent"]
        if any(b in self.siblings(p) for p in self.parents.get(a, ())):
            return ["nibling"]
        if any(a in self.siblings(p) for p in self.parents.get(b, ())):
            return ["uncle_aunt"]
        for pa in self.parents.get(a, ()):
            for pb in self.parents.get(b, ()):
                if pb in self.siblings(pa):
                    return ["cousin"]
        if a in self.ancestors(b):
            return ["ancestor"]
        if b in self.ancestors(a):
            return ["descendant"]
        return []

    def describe(self, a: str, b: str) -> str | None:
        """Plain-English statement of how *a* and *b* are related, or ``None``."""
        kinds = self.relations(a, b)
        if not kinds:
            return None
        # each kind is a's role toward b, read as "a is b's <word>"
        words = [self._word(k, a) for k in kinds]
        return f"{a} is {b}'s {' and '.join(words)}."

    def path_description(self, a: str, b: str, max_hops: int = 4) -> str | None:
        """Shortest chain of family links (BFS), e.g. for in-laws and distant kin."""
        from collections import deque

        def hops(n: str):
            for p in self.parents.get(n, ()):
                yield p, f"child of {p}"
            for c in self.children.get(n, ()):
                yield c, f"parent of {c}"
            for s in self.spouses.get(n, ()):
                yield s, f"spouse of {s}"
            for s in self.explicit_siblings.get(n, ()):
                yield s, f"sibling of {s}"

        seen = {a: None}
        queue = deque([(a, 0)])
        while queue:
            node, depth = queue.popleft()
            if node == b:
                break
            if depth >= max_hops:
                continue
            for nxt, label in hops(node):
                if nxt not in seen:
                    seen[nxt] = (node, label)
                    queue.append((nxt, depth + 1))
        if b not in seen:
            return None
        steps: list[str] = []
        cur = b
        while seen[cur] is not None:
            prev, label = seen[cur]
            steps.append(f"{prev} is {label}")
            cur = prev
        return "; ".join(reversed(steps)) + "."

    def family_of(self, name: str) -> dict[str, Any]:
        """Structured family summary for a character profile."""
        sibs = self.siblings(name)
        return {
            "parents": sorted(self.parents.get(name, ())),
            "children": sorted(self.children.get(name, ())),
            "spouses": sorted(self.spouses.get(name, ())),
            "lovers": sorted(self.lovers.get(name, ())),
            "siblings": sorted(s for s, full in sibs.items() if full),
            "half_siblings": sorted(s for s, full in sibs.items() if not full),
        }

