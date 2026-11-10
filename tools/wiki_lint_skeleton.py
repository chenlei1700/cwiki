#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""wiki_lint_skeleton.py — starter nightly lint for a cwiki-style knowledge base.

A deliberately small, stdlib-only skeleton of the mechanized lint described in
docs/maintenance-mechanisms.md ("discipline becomes gates" + "guard the guards").
Copy into your project (e.g. scripts/maintenance/), adjust the CONFIG block, wire
into your nightly job, and grow your own checks onto the same pattern. The source
project this generalizes from runs 15+ checks grown from exactly this shape.

Ships five checks (specs: templates/SCHEMA.md §13 / §15 / §16):
  budget        — always-loaded docs over their byte budget
  entry_form    — new dated lesson entries must be "one line + pointer" (non-retroactive)
  supersedes    — pages declared superseded must carry a tombstone banner;
                  tombstoned paths must not resurrect
  big_untracked — untracked files > N MB under wiki/ (they will ram your pre-commit gate)
  topics        — _topics.json shape: broken JSON / empty anchors / dead page anchors /
                  alias collisions

Design rules baked in (each paid for in incidents upstream):
  * Judgments are pure functions over injectable inputs — `--selftest` fault-injects
    every check without touching a real repo. Run the selftest from your test suite.
  * Report evidence (which file, what fix), never bare booleans.
  * Violations exit 1; informational findings don't. Mixing severities trains
    people to ignore the report.
  * Thresholds/budgets are judgment calls — the CONFIG comments say so. Don't dress
    pinned numbers up as derived.

Usage: python wiki_lint_skeleton.py [--root .] [--selftest]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

# ---------------- CONFIG (judgment calls — tune per project, say so) ----------
BUDGETS = {                      # always-loaded docs: whole-file byte budgets
    "CLAUDE.md": 140_000,        # pinned: safe margin under the harness warning line
}
CUTOFF_DATE = "2026-11-09"       # entry-form gate applies to entries strictly after this
ENTRY_MAX_BYTES = 800            # pinned from observed healthy pointer-entry sizes
ENTRY_POINTER_MIN = 500          # above this, an entry must carry some link
BIG_FILE_MB = 20                 # keep in sync with your pre-commit large-file gate
TOMBSTONE_WORD = "DEPRECATED"    # banner word a superseded page must carry

_ENTRY_RE = re.compile(r"^- \[(\d{4}-\d{2}-\d{2})", re.M)
_POINTER_RE = re.compile(r"\]\(|\[\[")
_SUPERSEDES_RE = re.compile(r"^supersedes:\s*\[(.*?)\]", re.M)


@dataclass
class Report:
    findings: list = field(default_factory=list)

    def add(self, check: str, severity: str, msg: str) -> None:
        self.findings.append((check, severity, msg))

    @property
    def violations(self):
        return [f for f in self.findings if f[1] == "violation"]


# ---------------- pure judgments (selftest targets these directly) ------------

def judge_budget(name: str, size: int, budget: int) -> str | None:
    if size > budget:
        return (f"{name} is {size:,}B > budget {budget:,}B — run the distillation "
                f"SOP (SCHEMA §13.3)")
    return None


def split_entries(text: str) -> list[tuple[str, str]]:
    """Dated bullets `- [YYYY-MM-DD] ...` → [(date, full entry text)]."""
    ms = list(_ENTRY_RE.finditer(text))
    return [(m.group(1),
             text[m.start(): ms[i + 1].start() if i + 1 < len(ms) else len(text)].strip())
            for i, m in enumerate(ms)]


def judge_entry_form(date: str, entry: str) -> str | None:
    """New entries = one line + pointer. Entries at/before CUTOFF are exempt
    (they belong to the distillation backlog — non-retroactive, SCHEMA §13.4)."""
    if date <= CUTOFF_DATE:
        return None
    b = len(entry.encode("utf-8"))
    if b > ENTRY_MAX_BYTES:
        return f"{b:,}B > {ENTRY_MAX_BYTES}B — long content belongs in a wiki page; keep one line + pointer here"
    if b > ENTRY_POINTER_MIN and not _POINTER_RE.search(entry):
        return f"{b:,}B with no link — unique facts would live only in this file; add a pointer or migrate"
    return None


def judge_supersedes(declaring_page: str, old_rel: str, old_text: str | None) -> tuple[str, str] | None:
    """old_text=None means the old page is gone (info, lineage still documented)."""
    if old_text is None:
        return ("info", f"{declaring_page} supersedes {old_rel}, which no longer exists (ok — lineage note)")
    head = "\n".join(old_text.splitlines()[:5])
    if TOMBSTONE_WORD not in head:
        return ("violation",
                f"{old_rel} is superseded by {declaring_page} but carries no tombstone banner "
                f"(add `> **{TOMBSTONE_WORD}** -> see [[...]]` at the top)")
    return None


def scan_big_untracked(porcelain: str, root: Path) -> list[str]:
    """`??` rows of `git status --porcelain -uall wiki/` that are files > BIG_FILE_MB."""
    big = []
    for ln in porcelain.splitlines():
        if not ln.startswith("??"):
            continue
        rel = ln[3:].strip().strip('"')
        p = root / rel
        try:
            if p.is_file() and p.stat().st_size > BIG_FILE_MB * 1024 * 1024:
                big.append(f"{p.stat().st_size / 1e6:.0f}MB {rel}")
        except OSError:
            continue
    return big


def judge_topics(raw: str | None, page_exists) -> list[tuple[str, str]]:
    """Registry shape checks. `page_exists(rel)->bool` is injected for testability."""
    if raw is None:
        return []
    try:
        topics = json.loads(raw)
        assert isinstance(topics, list)
    except Exception:
        # Never degrade a broken registry to "empty" — that silently disables every gate.
        return [("violation", "_topics.json is broken JSON — fix it; it must not be read as an empty registry")]
    out: list[tuple[str, str]] = []
    seen_alias: dict[str, str] = {}
    for t in topics:
        name = t.get("name", "?")
        anchors = t.get("anchors") or {}
        if not any(anchors.get(k) for k in anchors):
            out.append(("violation", f"topic {name}: anchors all empty — a topic must point somewhere"))
        for p in anchors.get("pages", []):
            if not page_exists(p):
                out.append(("violation", f"topic {name}: dead page anchor {p}"))
        for a in [name] + list(t.get("aliases", [])):
            if a in seen_alias and seen_alias[a] != name:
                out.append(("violation", f"alias '{a}' collides: {seen_alias[a]} vs {name}"))
            seen_alias[a] = name
    return out


# ---------------- collectors (thin I/O shells over the judgments) -------------

def run_all(root: Path) -> Report:
    rep = Report()
    for name, budget in BUDGETS.items():
        p = root / name
        if not p.exists():
            rep.add("budget", "info", f"{name} not found (cannot check — this is not 'within budget')")
            continue
        why = judge_budget(name, p.stat().st_size, budget)
        if why:
            rep.add("budget", "violation", why)
        for date, entry in split_entries(p.read_text(encoding="utf-8", errors="replace")):
            w = judge_entry_form(date, entry)
            if w:
                rep.add("entry_form", "violation", f"[{date}] {entry.splitlines()[0][:50]}… — {w}")
    wiki = root / "wiki"
    if wiki.exists():
        for page in wiki.rglob("*.md"):
            text = page.read_text(encoding="utf-8", errors="replace")
            m = _SUPERSEDES_RE.search(text[:2000])
            if m:
                for old_rel in [s.strip().strip("'\"") for s in m.group(1).split(",") if s.strip()]:
                    old = root / old_rel
                    verdict = judge_supersedes(str(page.relative_to(root)), old_rel,
                                               old.read_text(encoding="utf-8", errors="replace")
                                               if old.exists() else None)
                    if verdict:
                        rep.add("supersedes", *verdict)
        tomb = wiki / "_tombstones.json"
        if tomb.exists():
            try:
                for t in json.loads(tomb.read_text(encoding="utf-8")):
                    if (root / t["path"]).exists():
                        rep.add("supersedes", "violation",
                                f"tombstoned path resurrected: {t['path']} (reason it died: {t.get('reason', '?')})")
            except Exception:
                rep.add("supersedes", "violation", "_tombstones.json is broken JSON")
        try:
            out = subprocess.run(["git", "status", "--porcelain", "-uall", "wiki/"],
                                 cwd=root, capture_output=True, text=True,
                                 encoding="utf-8", errors="replace", timeout=60).stdout
            big = scan_big_untracked(out, root)
            if big:
                rep.add("big_untracked", "violation",
                        f"{len(big)} untracked file(s) > {BIG_FILE_MB}MB under wiki/ — gitignore "
                        f"(if rebuildable) or split: " + " | ".join(big[:5]))
        except (OSError, subprocess.TimeoutExpired):
            rep.add("big_untracked", "info", "git unavailable — big-file check skipped (not 'clean')")
        treg = wiki / "_topics.json"
        for sev, msg in judge_topics(treg.read_text(encoding="utf-8") if treg.exists() else None,
                                     lambda rel: (root / rel).exists()):
            rep.add("topics", sev, msg)
    return rep


# ---------------- selftest: fault injection per check -------------------------

def _selftest() -> int:
    fails: list[str] = []

    def expect(cond: bool, name: str) -> None:
        print(("  OK  " if cond else "  FAIL ") + name)
        if not cond:
            fails.append(name)

    expect(judge_budget("x.md", 200, 100) is not None, "over budget -> red")
    expect(judge_budget("x.md", 50, 100) is None, "within budget -> green")

    old_long = "- [2026-01-01] " + "x" * 2000
    new_long = "- [2026-12-01] " + "x" * 2000
    new_mid = "- [2026-12-01] " + "x" * 600
    expect(judge_entry_form(*split_entries(old_long)[0]) is None, "old long entry -> exempt (non-retroactive)")
    expect("belongs in a wiki page" in (judge_entry_form(*split_entries(new_long)[0]) or ""),
           "new oversized entry -> red")
    expect("no link" in (judge_entry_form(*split_entries(new_mid)[0]) or ""),
           "new mid entry without pointer -> red")
    expect(judge_entry_form(*split_entries(new_mid + " [p](a.md)")[0]) is None,
           "new mid entry with pointer -> green")
    ents = split_entries(old_long + "\n\n" + new_long)
    expect(len(ents) == 2 and ents[1][0] == "2026-12-01", "entry splitting keeps date with body")

    expect(judge_supersedes("new.md", "old.md", "no banner here")[0] == "violation",
           "superseded page without tombstone -> red")
    expect(judge_supersedes("new.md", "old.md", f"> **{TOMBSTONE_WORD}** -> see [[new]]\n# old") is None,
           "tombstone in place -> green")
    expect(judge_supersedes("new.md", "old.md", None)[0] == "info", "old page gone -> info only")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td); (root / "wiki").mkdir()
        bigf = root / "wiki" / "big.bin"; bigf.write_bytes(b"\0" * ((BIG_FILE_MB + 1) << 20))
        (root / "wiki" / "small.bin").write_bytes(b"\0" * 10)
        porcelain = "?? wiki/big.bin\n?? wiki/small.bin\n?? wiki/gone.bin\n M wiki/tracked.md\n"
        got = scan_big_untracked(porcelain, root)
        expect(len(got) == 1 and "big.bin" in got[0], f"big-file scan: only the >20MB ?? file (got {got})")
        bigf.write_bytes(b"\0" * 10)
        expect(scan_big_untracked(porcelain, root) == [], "after shrinking -> clean (injection removed)")

    exists = {"wiki/a.md"}.__contains__
    good = json.dumps([{"name": "t1", "aliases": ["alpha"], "anchors": {"pages": ["wiki/a.md"]}}])
    expect(judge_topics(good, exists) == [], "well-formed registry -> green")
    expect(any("dead page anchor" in m for _, m in judge_topics(
        json.dumps([{"name": "t1", "anchors": {"pages": ["wiki/nope.md"]}}]), exists)),
        "dead anchor -> red")
    expect(any("anchors all empty" in m for _, m in judge_topics(
        json.dumps([{"name": "t1", "anchors": {}}]), exists)), "empty anchors -> red")
    expect(any("collides" in m for _, m in judge_topics(
        json.dumps([{"name": "t1", "aliases": ["x"], "anchors": {"pages": ["wiki/a.md"]}},
                    {"name": "t2", "aliases": ["x"], "anchors": {"pages": ["wiki/a.md"]}}]), exists)),
        "alias collision -> red")
    expect(any("broken JSON" in m for _, m in judge_topics("{oops", exists)),
           "broken registry -> red, never read as empty")
    expect(judge_topics(None, exists) == [], "no registry file -> no findings (feature not adopted)")

    print(("\nselftest: all passed" if not fails else f"\nselftest: {len(fails)} FAILED: {fails}"))
    return 0 if not fails else 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    rep = run_all(Path(a.root).resolve())
    for check, sev, msg in rep.findings:
        print(f" {'!!' if sev == 'violation' else 'i '} [{check}] {msg}")
    print(f"--- {len(rep.violations)} violation(s) (report-only: this tool never edits pages)")
    return 1 if rep.violations else 0


if __name__ == "__main__":
    sys.exit(main())
