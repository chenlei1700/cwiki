"""check_new_skills_registered.py — Stop-hook gate (enforcement layer C).

Purpose (see templates/SCHEMA.md §9 and docs/maintenance-mechanisms.md):
- New skills must declare dependency frontmatter (consumes / produces /
  upstream_skills / downstream_skills / load_bearing_for).
- This script runs as a Claude Code Stop hook: it checks ONLY skills newly
  created in the current session (= git untracked / newly added), so the
  legacy backlog never blocks anyone — legacy files are covered by the
  nightly drift detector (layer D).

Exit codes:
  0 = no new skills, or all new skills registered
  1 = a newly created skill lacks the frontmatter (blocks agent stop)

Wire-up (.claude/settings.json):
  "Stop": [{"hooks": [{"type": "command",
            "command": "python tools/check_new_skills_registered.py"}]}]
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


def find_root() -> Path:
    p = Path.cwd()
    for cand in (p, *p.parents):
        if (cand / ".claude" / "skills").exists():
            return cand
    return p  # no skills dir at all — checks below will no-op


ROOT = find_root()
SKILL_PATH_RE = re.compile(r"^\.claude/skills/([\w\-]+)/skill\.md$")
DECL_FIELD_RE = re.compile(
    r"^(consumes|produces|upstream_skills|downstream_skills|load_bearing_for):",
    re.MULTILINE,
)


def list_new_skill_paths() -> list[Path]:
    """Find skill.md files that are new in this session (?? untracked / A added)."""
    try:
        # -uall expands untracked directories into individual files —
        # without it, git shows only the directory and skill.md is missed.
        result = subprocess.run(
            ["git", "status", "--porcelain", "-uall", ".claude/skills/"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    paths: list[Path] = []
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        # porcelain format: XY <path>  (X = staged, Y = unstaged)
        flags, path = line[:2], line[3:].strip().replace("\\", "/")
        if flags.strip() not in ("??", "A", "AM", "AD", "AC"):
            continue
        if SKILL_PATH_RE.match(path):
            paths.append(ROOT / path)
    return paths


def is_registered(skill_path: Path) -> bool:
    if not skill_path.exists():
        return True  # deleted in-session — don't block
    try:
        text = skill_path.read_text(encoding="utf-8")
    except OSError:
        return True
    if not text.startswith("---"):
        return False
    end = text.find("\n---", 3)
    if end < 0:
        return False
    return bool(DECL_FIELD_RE.search(text[3:end]))


def main() -> int:
    new_paths = list_new_skill_paths()
    if not new_paths:
        return 0

    unregistered = [p for p in new_paths if not is_registered(p)]
    if not unregistered:
        return 0

    print("=" * 64, file=sys.stderr)
    print("  Stop blocked: skill(s) created this session lack dependency", file=sys.stderr)
    print("  frontmatter (SCHEMA.md §9)", file=sys.stderr)
    print("=" * 64, file=sys.stderr)
    for p in unregistered:
        rel = p.relative_to(ROOT).as_posix()
        skill_name = p.parent.name
        print(f"  x {rel}", file=sys.stderr)
        print(f"    Fix: python tools/scan_skill_dependencies.py "
              f"--skill {skill_name} --print", file=sys.stderr)
        print("    then paste the YAML into the frontmatter (inside the --- block)",
              file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
