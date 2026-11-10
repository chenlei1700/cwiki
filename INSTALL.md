# Installing cwiki (wiki-management skill)

Step-by-step install, verification, update and troubleshooting. The quick version
lives in [README § Install](README.md#install); this file is the detailed one.

## 0. Prerequisites

- **Claude Code** (CLI, desktop app, or IDE extension) with skills support —
  any recent version lists user and project skills automatically.
- **git** (for the clone-based installs; Mode C below works without it).
- Nothing to build or pip-install: the skill is plain markdown + optional
  stdlib-only Python tools.

Two facts that drive everything below:

1. **The folder name becomes the skill name.** Installing into
   `.../skills/wiki-management/` gives you a skill named `wiki-management`.
   Rename the folder if you want a different name — nothing inside cares.
2. **A skill is picked up at session start.** After installing or updating,
   start a **new** Claude Code session; a running session won't see it.

## 1. Choose an install mode

| Mode | Where it lives | Visible to | Choose when |
|---|---|---|---|
| A — user-global | `~/.claude/skills/wiki-management/` | every project on this machine | you want the methodology everywhere (most common) |
| B — per-project | `<project>/.claude/skills/wiki-management/` | that project only, **and everyone who clones it** | the wiki convention should travel with the repo / your team |
| C — copy without git | same paths as A or B | same | machines without git, or you want a frozen snapshot |

Modes A and B can coexist; a project-level skill of the same name shadows the
user-global one for that project, which is how you pin a project to a specific
version while keeping the global copy current.

### Mode A — user-global

```powershell
# Windows (PowerShell)
git clone https://github.com/chenlei1700/cwiki "$env:USERPROFILE\.claude\skills\wiki-management"
```

```bash
# macOS / Linux
git clone https://github.com/chenlei1700/cwiki ~/.claude/skills/wiki-management
```

### Mode B — per-project

```bash
cd <your-project>
git clone https://github.com/chenlei1700/cwiki .claude/skills/wiki-management
```

If your project is itself a git repo, decide how the skill rides along:

- **Vendored (recommended for teams)**: remove the skill's own git metadata and
  commit the files — everyone who clones the project gets the skill with zero steps:

  ```bash
  rm -rf .claude/skills/wiki-management/.git
  git add .claude/skills/wiki-management && git commit -m "vendor wiki-management skill"
  ```

- **Submodule**: `git submodule add https://github.com/chenlei1700/cwiki .claude/skills/wiki-management`
  — stays updatable via git, but every collaborator must remember
  `git submodule update --init`. Only worth it if you update often.

- Leaving it as a nested clone without either choice means collaborators get an
  empty directory — don't ship that.

### Mode C — copy without git

Download the repo archive (GitHub → Code → Download ZIP, or a release tarball),
extract, and place the folder at one of the Mode A/B paths. **Keep a note of
which commit/version you copied** (the README changelog states it) — a plain
folder copy cannot `git pull`, so updates are re-copy only (see §4).

## 2. Verify the install

1. Start a **new** Claude Code session in any project.
2. The skill should appear in the available-skills listing (name: `wiki-management`,
   or whatever you renamed the folder to). You can also just ask:
   *"do you see a wiki-management skill?"*
3. Functional check without touching a real project: in an empty scratch
   directory, say `bootstrap wiki` — you should get the one domain-category
   question and then a `wiki/` skeleton. Delete the scratch dir afterwards.

If the skill does not appear, see §5 Troubleshooting.

## 3. What is — and is not — installed

Installing the skill gives Claude the **methodology** (skill.md, templates,
docs). Two things are deliberately *not* active until you wire them:

- **The maintenance tools** (`tools/*.py`) are reference implementations, not
  auto-running services. To use one: copy it into your project (conventionally
  `scripts/maintenance/`), adjust the marked CONFIG block, run its `--selftest`,
  then wire it into pre-commit / hooks / your nightly job per
  [tools/README.md](tools/README.md). Start `wiki_lint_skeleton.py` in
  report-only mode for the first week before giving it exit codes.
- **Scale features** (SCHEMA §9–§16) stay dormant until their written adoption
  triggers are met. Installing everything on day one is the documented
  anti-pattern, not a shortcut.

Then say the first message for your scenario (README § Use): `bootstrap wiki`
for a fresh project, `adopt wiki` for a project that already has docs.

## 4. Updating

- **Clone installs (A/B)**: `git pull` inside the skill folder, then start a
  new session. Check the README changelog for schema additions worth adopting.
- **Vendored installs**: re-run the clone into a temp dir, copy over, commit.
  Diff `templates/SCHEMA.md` first if you have local customizations.
- **Mode C copies**: re-download and replace the folder. If you don't know
  which version a copy is, diff it against the repo before overwriting —
  local edits to a plain copy are otherwise silently lost.
- **Tools you copied into a project** do not update with the skill — they're
  yours now. When pulling a new tool version, re-apply your CONFIG block and
  re-run `--selftest`.
- Your project's `wiki/` content is **never touched by an update** — the skill
  ships rules and templates, not state.

## 5. Troubleshooting

| Symptom | Cause → fix |
|---|---|
| Skill not listed in a new session | Wrong path (must be exactly `.claude/skills/<name>/skill.md` under home or project root) → check with `ls`; or the folder landed one level deep (`.../wiki-management/cwiki/skill.md`) → move contents up |
| Skill listed but never triggers | Trigger phrases live in skill.md frontmatter `description:` — invoke explicitly ("use the wiki-management skill") to confirm it works, then check you're using a listed phrase |
| Two different versions behave inconsistently across projects | A project-level copy (Mode B) shadows the user-global one — `ls <project>/.claude/skills/` to see which copy that project resolves |
| `git pull` says "not a git repository" | The install is a plain copy (Mode C or a vendored copy) → update by re-copy, §4 |
| Collaborators see an empty skill folder | Nested clone committed as a gitlink → pick vendored or submodule, §1 Mode B |
| Tool exits 1 immediately after install | That's the point — it found violations. Read the evidence lines; run report-only for a week if adopting on a brownfield project |
| Line-ending noise in diffs on Windows | The repo ships `.gitattributes` (LF). If you vendored before 2026-10, re-copy it |

## 6. Uninstall

Delete the skill folder. Your `wiki/` and any tools you copied into
`scripts/maintenance/` are independent of the skill and keep working — the
skill is methodology, the wiki is yours.
