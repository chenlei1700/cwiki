"""check_dependency_drift.py — nightly drift detector (enforcement layer D).

Purpose (see templates/SCHEMA.md §9 and docs/maintenance-mechanisms.md):
- Skills declare consumes/produces/load_bearing_for in frontmatter.
- Over time, declarations drift from reality. This script scans three kinds
  of inconsistency; run it nightly (cron / end-of-day pipeline).

Checks:
  (1) unregistered skills: .claude/skills/<X>/skill.md without the frontmatter
      (grace period: recently modified files warn, older ones are listed as
       legacy with a bootstrap hint)
  (2) dead declarations: a consumes/produces path or table that no longer
      resolves  -> HARD ERROR (exit 1)
  (3) reverse asymmetry: A consumes B's produces, but B doesn't list A as a
      downstream_skill  -> info only (self-heals as declarations accrue)

Severity separation is deliberate: mixing hard errors with info noise trains
people to ignore the report.

Usage:
  python tools/check_dependency_drift.py
  python tools/check_dependency_drift.py --quiet     # exit code only
  python tools/check_dependency_drift.py --fix-hint  # print repair guidance
"""
from __future__ import annotations

import argparse
import re
import sys
import time
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

REGISTRATION_GRACE_DAYS = 7

# Minimal YAML handling: we only need list-style frontmatter fields.
DECL_FIELDS = (
    "consumes",
    "produces",
    "upstream_skills",
    "downstream_skills",
    "load_bearing_for",
)


@dataclass
class SkillDecl:
    name: str
    path: Path
    has_frontmatter: bool
    declared: dict[str, list[str]] = field(default_factory=dict)
    mtime: float = 0.0


def parse_frontmatter(path: Path) -> SkillDecl:
    """Read only the frontmatter; extract the declaration list fields."""
    name = path.parent.name
    decl = SkillDecl(name=name, path=path, has_frontmatter=False,
                     mtime=path.stat().st_mtime)
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return decl
    end = text.find("\n---", 3)
    if end < 0:
        return decl
    front = text[3:end]
    decl.has_frontmatter = True

    current_field: str | None = None
    for raw_line in front.splitlines():
        line = raw_line.rstrip()
        m = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if m:
            field_name, val = m.group(1), m.group(2).strip()
            if field_name in DECL_FIELDS:
                current_field = field_name
                if val and val != "[]":
                    inline = re.findall(r"[\"']?([\w./\-{}*]+)[\"']?", val)
                    decl.declared[current_field] = [x for x in inline if x]
                else:
                    decl.declared[current_field] = []
            else:
                current_field = None
            continue
        m = re.match(r"^\s+-\s*(.+)$", line)
        if m and current_field:
            item = m.group(1).strip().strip("\"'")
            item = re.split(r"\s+#", item, maxsplit=1)[0].strip()  # drop comments
            if item:
                decl.declared.setdefault(current_field, []).append(item)
    return decl


def list_skills() -> list[Path]:
    return sorted(SKILLS_DIR.glob("*/skill.md"))


# ---------- (1) unregistered ----------
def check_unregistered(decls: list[SkillDecl]) -> list[str]:
    issues: list[str] = []
    now = time.time()
    cutoff = now - REGISTRATION_GRACE_DAYS * 86400
    for d in decls:
        if d.declared:
            continue  # any declaration field present counts as registered
        age_days = (now - d.mtime) / 86400
        rel = d.path.relative_to(ROOT)
        if d.mtime > cutoff:
            issues.append(f"  !  {rel} (modified {age_days:.1f}d ago, missing frontmatter)")
        else:
            issues.append(f"  .  {rel} (legacy, modified {age_days:.0f}d ago; "
                          f"run scan_skill_dependencies.py for a draft)")
    return issues


# ---------- (2) dead declarations ----------
def ref_resolves(ref: str, all_skill_names: set[str]) -> bool:
    """Decide whether a consumes/produces string still matches reality."""
    # external table in db.table format — format check only (don't hit the DB
    # on every run; a dedicated weekly check can verify tables exist)
    if re.match(r"^[a-z][a-z_]*\.[a-z][a-z_0-9]+$", ref):
        return True
    if ref in all_skill_names:
        return True
    # template paths: globs / {placeholder} / date patterns -> glob the repo
    if ("*" in ref or "{" in ref
            or "YYYYMMDD" in ref or "YYYY-MM-DD" in ref or "DATE" in ref):
        glob_ref = (ref.replace("YYYYMMDD", "*")
                       .replace("YYYY-MM-DD", "*")
                       .replace("DATE", "*"))
        glob_ref = re.sub(r"\{[^}]+\}", "*", glob_ref)
        try:
            return any(ROOT.glob(glob_ref))
        except (ValueError, OSError):
            return True  # tolerate exotic templates
    return (ROOT / ref).exists()


def check_broken_refs(decls: list[SkillDecl], all_skill_names: set[str]) -> list[str]:
    issues: list[str] = []
    for d in decls:
        for field_name in ("consumes", "produces"):
            for ref in d.declared.get(field_name, []):
                if not ref_resolves(ref, all_skill_names):
                    issues.append(f"  x  {d.name} {field_name}: {ref!r} does not resolve")
    return issues


# ---------- (3) reverse asymmetry ----------
def check_asymmetry(decls: list[SkillDecl]) -> list[str]:
    issues: list[str] = []
    by_name = {d.name: d for d in decls}
    produces_index: dict[str, list[str]] = {}
    for d in decls:
        for ref in d.declared.get("produces", []):
            produces_index.setdefault(ref, []).append(d.name)
    for a in decls:
        for ref in a.declared.get("consumes", []):
            for producer in produces_index.get(ref, []):
                if producer == a.name:
                    continue
                downstream = by_name[producer].declared.get("downstream_skills", [])
                if a.name not in downstream:
                    issues.append(
                        f"  ~  {a.name} consumes {ref!r} (produced by {producer}), "
                        f"but {producer} doesn't list {a.name} as downstream")
    return issues


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--fix-hint", action="store_true", help="print repair guidance")
    args = ap.parse_args()

    decls = [parse_frontmatter(p) for p in list_skills()]
    all_names = {d.name for d in decls}

    unreg = check_unregistered(decls)
    broken = check_broken_refs(decls, all_names)
    asym = check_asymmetry(decls)

    has_hard_error = bool(broken)

    if args.quiet:
        return 1 if has_hard_error else 0

    print("=" * 64)
    print("  Dependency Drift Report (SCHEMA.md §9)")
    print("=" * 64)

    print(f"\n(1) unregistered / missing frontmatter  ({len(unreg)})")
    print("\n".join(unreg) if unreg else "  ok: all skills registered")

    print(f"\n(2) dead declarations (HARD ERROR)  ({len(broken)})")
    print("\n".join(broken) if broken else "  ok: all declared references resolve")

    print(f"\n(3) reverse asymmetry (info only)  ({len(asym)})")
    if asym:
        print("\n".join(asym[:20]))
        if len(asym) > 20:
            print(f"  ... {len(asym) - 20} more omitted")
    else:
        print("  ok: reverse declarations symmetric")

    print("\n" + "=" * 64)
    if has_hard_error:
        print(f"  EXIT 1 ({len(broken)} hard errors)")
        if args.fix_hint:
            print("\nRepair guidance:")
            print("  - delete declarations whose target no longer exists")
            print("  - on table/path renames, update frontmatter in the same change")
            print("  - after a path rename, grep all skills for the old path and batch-fix")
    else:
        print("  EXIT 0 (no hard errors)")
    return 1 if has_hard_error else 0


if __name__ == "__main__":
    sys.exit(main())
