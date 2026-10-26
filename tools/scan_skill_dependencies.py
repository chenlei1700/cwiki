"""scan_skill_dependencies.py — bootstrap drafts for dependency frontmatter.

Purpose (see templates/SCHEMA.md §9):
- Legacy skills predate the frontmatter convention; nobody will hand-write
  declarations for a 20-skill backlog. This script scans each skill.md with
  regex heuristics and emits a DRAFT YAML block per skill for human review.
- It never modifies skill.md itself — drafts land in
  wiki/_dependency_drafts/<skill>.yaml (or stdout with --print).
- It is also enforcement layer B's engine: a PostToolUse hook can call
  `--skill <name> --print` the moment a skill file is created, so compliance
  costs one paste.

Extraction heuristics (tune the CONFIG block for your project):
- external table names (db.table with known prefixes)    -> consumes
- wiki/ paths in frontmatter or fenced code blocks       -> consumes (high confidence)
- wiki/ paths appearing >= 2 times in the body           -> consumes (inferred)
- "writes/outputs <path>" verb patterns                  -> produces
- code-module paths under known source dirs              -> consumes
- other skill names near call/consume verbs              -> upstream_skills
- load_bearing_for: NOT inferred here (the drift detector computes reverse
  views; see SCHEMA §9.2 one-way declaration)

Usage:
  python tools/scan_skill_dependencies.py                 # all skills -> drafts dir
  python tools/scan_skill_dependencies.py --skill X       # one skill
  python tools/scan_skill_dependencies.py --print         # stdout, write nothing
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path


def find_root() -> Path:
    p = Path.cwd()
    for cand in (p, *p.parents):
        if (cand / ".claude" / "skills").exists():
            return cand
    sys.exit("cannot locate project root (no .claude/skills found upward from cwd)")


ROOT = find_root()
SKILLS_DIR = ROOT / ".claude" / "skills"
DRAFT_DIR = ROOT / "wiki" / "_dependency_drafts"

# ---------------------------------------------------------------- CONFIG --
# CUSTOMIZE PER PROJECT: known database prefixes (db.table detection) and
# source directories whose paths count as code dependencies. Hand-written
# lists like these inevitably lag the project — revisit them whenever the
# drift detector reports surprising gaps.
DB_PREFIXES = ("analytics", "warehouse", "metrics")
CODE_DIRS = ("src", "scripts", "app", "lib")
# English + Chinese "produce" verbs; extend for your project's vocabulary.
PRODUCES_VERBS = r"(?:writes?|outputs?|generates?|produces?|updates?|输出|写入|落地|产出|生成|更新)"
# -------------------------------------------------------------------------

DB_TABLE_RE = re.compile(rf"\b({'|'.join(DB_PREFIXES)})\.([a-z_][a-z_0-9]+)\b")
WIKI_PATH_RE = re.compile(r"\bwiki/[\w/_{}\-]+(?:\.md|\.json|\.jsonl)\b")
CODE_PATH_RE = re.compile(
    rf"\b(?:{'|'.join(CODE_DIRS)})/[\w/_]+\.(?:py|ts|js|md|json|sql)\b")
FENCED_BLOCK_RE = re.compile(r"```[\s\S]*?```")
PRODUCES_HINT_RE = re.compile(
    rf"{PRODUCES_VERBS}\s*[:：]?\s*[`\"]?"
    rf"(wiki/[\w/_{{}}\-.]+|(?:{'|'.join(DB_PREFIXES)})\.[a-z_]+)")
UPSTREAM_HINT_RE = re.compile(
    r"(?:calls?|reads?|consumes?|depends on|调用|读|消费|依赖|基于|配合)\s*[`\"]?"
    r"([a-z][a-z\-]+(?:-[a-z]+)+)")


@dataclass
class SkillDeps:
    name: str
    consumes: set[str] = field(default_factory=set)
    produces: set[str] = field(default_factory=set)
    upstream_skills: set[str] = field(default_factory=set)
    downstream_skills: set[str] = field(default_factory=set)
    load_bearing_for: set[str] = field(default_factory=set)


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    end = text.find("\n---", 3)
    if end < 0:
        return "", text
    return text[3:end].strip(), text[end + 4:].lstrip()


def list_skill_names() -> list[str]:
    return sorted(p.parent.name for p in SKILLS_DIR.glob("*/skill.md"))


def scan_one(skill_path: Path, all_skill_names: list[str]) -> SkillDeps:
    text = skill_path.read_text(encoding="utf-8")
    front, body = split_frontmatter(text)
    self_name = skill_path.parent.name
    deps = SkillDeps(name=self_name)

    # paths inside fenced code blocks are commands the skill actually runs
    # -> strong consumes signal
    fenced_text = "\n".join(FENCED_BLOCK_RE.findall(body))

    for m in DB_TABLE_RE.finditer(text):
        deps.consumes.add(f"{m.group(1)}.{m.group(2)}")

    wiki_in_front = WIKI_PATH_RE.findall(front)
    wiki_in_fenced = WIKI_PATH_RE.findall(fenced_text)
    wiki_in_body = Counter(WIKI_PATH_RE.findall(body))

    for path in (*wiki_in_front, *wiki_in_fenced):   # high confidence
        deps.consumes.add(path)
    for path, count in wiki_in_body.items():          # inferred
        if count >= 2:
            deps.consumes.add(path)

    for m in PRODUCES_HINT_RE.finditer(text):
        target = m.group(1)
        deps.produces.add(target)
        deps.consumes.discard(target)  # a produced path is not also consumed

    for m in CODE_PATH_RE.finditer(text):
        deps.consumes.add(m.group(0))

    for m in UPSTREAM_HINT_RE.finditer(text):
        candidate = m.group(1)
        if candidate in all_skill_names and candidate != self_name:
            deps.upstream_skills.add(candidate)

    # heuristic: another skill's name followed by a consume-type verb
    for other in all_skill_names:
        if other == self_name:
            continue
        if re.search(rf"\b{re.escape(other)}\b.{{0,40}}(?:consumes?|reads?|calls?|消费|读|调用)", text):
            deps.downstream_skills.add(other)

    return deps


def render_draft(deps: SkillDeps) -> str:
    lines = [
        f"# Draft for: {deps.name}",
        "# Generated by scan_skill_dependencies.py — REVIEW, then paste into",
        f"# .claude/skills/{deps.name}/skill.md frontmatter (inside the --- block)",
        "#",
        "# Review notes (SCHEMA.md §9.1):",
        "# - delete anything that is not truly load-bearing (a casual link is not)",
        "# - leave load_bearing_for empty; the drift detector computes reverse views",
        "",
    ]

    def emit(field_name: str, items: set[str]) -> None:
        if not items:
            lines.append(f"{field_name}: []")
            return
        lines.append(f"{field_name}:")
        for x in sorted(items):
            lines.append(f"  - {x}")

    emit("consumes", deps.consumes)
    emit("produces", deps.produces)
    emit("upstream_skills", deps.upstream_skills)
    emit("downstream_skills", deps.downstream_skills)
    emit("load_bearing_for", deps.load_bearing_for)
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", help="scan one skill only (default: all)")
    ap.add_argument("--print", action="store_true", help="stdout, write nothing")
    args = ap.parse_args()

    all_names = list_skill_names()
    targets = [args.skill] if args.skill else all_names
    bad = [n for n in targets if n not in all_names]
    if bad:
        print(f"[error] unknown skill: {bad}", file=sys.stderr)
        print(f"[hint] available: {all_names}", file=sys.stderr)
        return 1

    if not args.print:
        DRAFT_DIR.mkdir(parents=True, exist_ok=True)

    summary: list[tuple[str, int, int, int]] = []
    for name in targets:
        deps = scan_one(SKILLS_DIR / name / "skill.md", all_names)
        draft = render_draft(deps)
        summary.append((name, len(deps.consumes), len(deps.produces),
                        len(deps.upstream_skills) + len(deps.downstream_skills)))
        if args.print:
            print(f"\n===== {name} =====")
            print(draft)
        else:
            (DRAFT_DIR / f"{name}.yaml").write_text(draft, encoding="utf-8")

    print(f"\n[scan_skill_dependencies] scanned {len(targets)} skill(s)")
    print(f"{'skill':<32} {'consumes':>8} {'produces':>8} {'cross':>5}")
    print("-" * 60)
    for name, nc, np_, nx in summary:
        print(f"{name:<32} {nc:>8} {np_:>8} {nx:>5}")
    if not args.print:
        print(f"\nDrafts -> {DRAFT_DIR.relative_to(ROOT)}/  "
              f"(review, then merge into each skill.md frontmatter)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
