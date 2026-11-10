# tools/ — reference implementations

Generic, sanitized versions of the maintenance machinery described in
[`docs/maintenance-mechanisms.md`](../docs/maintenance-mechanisms.md). They are
**reference implementations**: copy into your project (conventionally
`scripts/maintenance/`), then customize the marked CONFIG blocks.

| Tool | Mechanism | Role |
|---|---|---|
| [`sync_views_example.py`](sync_views_example.py) | 1 — L1→L2 sync | Regenerates derived views from an append-only ledger. `--check` for pre-commit, `--dry-run`, DO-NOT-EDIT marker, refuses to clobber unmarked files |
| [`scan_skill_dependencies.py`](scan_skill_dependencies.py) | 3B — bootstrap / nudge | Emits draft dependency frontmatter per skill from regex heuristics. Never edits skill.md; drafts go to `wiki/_dependency_drafts/` or stdout |
| [`check_new_skills_registered.py`](check_new_skills_registered.py) | 3C — Stop hook | Blocks session end if a skill *created this session* lacks dependency frontmatter. Legacy files never block |
| [`check_dependency_drift.py`](check_dependency_drift.py) | 3D — nightly detector | Unregistered files (grace period) / dead declarations (hard error, exit 1) / reverse asymmetry (info) |
| [`wiki_lint_skeleton.py`](wiki_lint_skeleton.py) | 7 + §13/§15/§16 — nightly lint | Starter mechanized lint: budgets, entry-form gate, supersedes/tombstones + resurrection, big untracked files, topic-registry shape. Pure-function judgments + `--selftest` with 18 fault injections — grow your own checks onto this pattern |

## Wiring

Pre-commit (Mechanism 1):

```bash
# .git/hooks/pre-commit (or your hook framework)
python scripts/maintenance/sync_views_example.py --check || exit 1
```

Claude Code hooks (`.claude/settings.json`), Mechanism 3:

```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{ "type": "command",
        "command": "python scripts/maintenance/check_new_skills_registered.py" }]
    }]
  }
}
```

Nightly (cron / end-of-day pipeline):

```bash
python scripts/maintenance/sync_views_example.py          # self-heal L2
python scripts/maintenance/check_dependency_drift.py      # drift report (exit 1 on hard errors)
python scripts/maintenance/wiki_lint_skeleton.py          # mechanized wiki lint (exit 1 on violations)
```

Guard the guards: wire each tool's `--selftest` into your normal test suite, e.g.

```python
@pytest.mark.parametrize("tool", ["scripts/maintenance/wiki_lint_skeleton.py", ...])
def test_selftest_green(tool):
    r = subprocess.run([sys.executable, tool, "--selftest"], capture_output=True, text=True)
    assert r.returncode == 0 and "OK" in r.stdout   # content assert defeats an empty selftest
```

## Two rules before trusting any of these gates

1. **Fault-inject once**: re-introduce the bug the gate exists to catch and confirm it turns red. A gate that has never fired is indistinguishable from a broken one.
2. The CONFIG blocks (db prefixes, source dirs, verb lists) are hand-written allow-lists — they *will* lag your project. When the drift report looks suspiciously clean, check the config before celebrating.
