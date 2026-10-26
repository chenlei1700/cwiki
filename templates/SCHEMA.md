# Wiki Schema — <PROJECT_NAME> Knowledge Base

> LLM-maintained. Humans feed material and make decisions; LLM organizes, archives, and cross-references.
>
> Sections §1–§8 are the core — every project uses them from day one.
> Sections §9–§12 are **scale features** — adopt each one only when the trigger condition listed at its top is met.

## §1. Purpose

This `wiki/` is a knowledge base maintained by LLM agents over the lifetime of the project. The human's role is to feed material (notes, papers, post-mortems, design discussions) and to make decisions. The LLM's role is to organize that material into a consistent, cross-linked structure that future sessions (and future humans) can navigate.

## §2. Directory layout

```
wiki/
├── SCHEMA.md                  # this file — operating rules
├── index.md                   # table of contents
├── log.md                     # operations log (newest first)
├── MAINTENANCE_ROUTING.md     # event → file list routing
├── ONBOARDING.md              # (optional) new-session loading guide — see §12
├── concepts/                  # methodology, definitions, lessons
├── experiments/               # date-stamped events (each one frozen)
├── sources/                   # external material summaries
├── architecture/              # how the system is built
└── <domain>/                  # project-specific (optional: e.g. strategies/, models/, apis/)
```

## §3. Data layering (the most important rule)

Every file belongs to exactly one of three layers. **The layer dictates who is allowed to edit it.**

| Layer | Definition | Who edits | Examples |
|---|---|---|---|
| **L1 SSOT** | Machine-generated original truth. One source. | Scripts / external systems. **No human edits.** | JSON ledgers, append-only event logs, config files |
| **L2 Derived** | A view computed from L1 by a sync script. | Sync script. **No human edits.** | Markdown summaries of "current state" generated from JSON |
| **L3 Narrative** | Hand-written stories, lessons, methodology. | Humans + LLM. **Scripts must NOT overwrite.** | `experiments/*.md`, `concepts/*.md`, `log.md` |

**The cardinal rule**: any fact exists in **one place only**, in L1. L2 and L3 *reference* L1 via links; they never *copy* the content. If you find yourself writing a metric into a narrative that already exists in an L1 ledger, replace with a link.

This rule also applies to files *outside* `wiki/`: a project-level `CLAUDE.md` or `README.md` that mentions "current version / current state" is itself an L2 consumer — it should link to the derived view, never copy its numbers. (Copied numbers are guaranteed to go stale; a link cannot.)

Reference allowed directions:
- L3 can reference L1 and L2
- L2 can reference L1
- L1 references nothing (atomic truths)
- L2 **must not** reference L3 (derived views can't depend on stories)

Two sub-kinds of L1 worth distinguishing once they appear:

- **Append-only ledgers** (`*.jsonl`): history is immutable. A wrong row is never edited — append a superseding row, or attach a correction in a separate *overlay* file that consumers explicitly honor (see §10). Rationale: once N tools read the ledger, silent in-place edits desynchronize every one of them.
- **Derived observability data** (rebuildable JSON/JSONL produced from logs or ledgers): mark as gitignored. It can always be regenerated, so it must never become something other files link to as truth.

## §4. Page templates

See `templates/page_types/` in the wiki-management skill folder for the full templates. Summary:

### Concept page (`concepts/<name>.md`)
```markdown
# <Concept name>

## Definition

## Where it applies in this project

## Related concepts
- [[other-concept]]

## Open questions
```

### Experiment page (`experiments/<topic>_YYYYMMDD.md`)
```markdown
# <Experiment title>

**Date**: YYYY-MM-DD
**Type**: <experiment / refactor / incident / spike>
**Status**: in-progress | done | abandoned
**Conclusion (one line)**: ...

## Background & hypothesis
## Setup
## Result
## Analysis & lessons
## Next steps
```

### Source page (`sources/<short-name>.md`)
```markdown
# <Material title>

**Type**: article | paper | book | video | discussion
**URL / origin**: ...
**Ingested**: YYYY-MM-DD

## Key takeaways
1.
2.

## Relevance to this project

## Referenced by
- [[page-that-cites-this]]
```

### Architecture page (`architecture/<component>.md`)
```markdown
# <Component>

**Status**: current | deprecated

## Overview

## Components
- [[sub-component-a]]
- [[sub-component-b]]

## Data flow

## Known issues / TODOs
```

### Domain entity page (`<domain>/<entity>.md`)
For domain-specific items (strategies, models, APIs, etc.) — see `templates/page_types/domain_entity.md` for a flexible template.

## §5. Cross-references

- Use `[[page-name]]` (Obsidian-compatible) — the slug is filename without `.md`
- Link **liberally**. Dangling links (target doesn't exist yet) are TODO markers, not errors.
- Cross-reference is **bi-directional**: when you add `[[X]]` in page A, also add a back-reference in page X (under a `## Referenced by` section).

## §6. File-naming rules

| Directory | Rule | Reason |
|---|---|---|
| Stable domain pages | **No version suffix** — use stable name, track version in a field | Avoids stale links each version bump |
| `experiments/` | **Must** include date or version tag (e.g. `auth_refactor_20260520.md`) | Each is a frozen historical event |
| `concepts/` | Descriptive English name, no version | Methodology outlives versions |
| `_<name>.md` prefix | Convention for "L2 view that points to current state" — filename stable, contents updated by sync | Marks L2 visually |

## §7. Operating procedures (summary)

### Ingest (new material)
1. Classify (concept / experiment / source / architecture / domain)
2. Locate or create host page
3. Add `[[cross-references]]`
4. Update neighbors with back-references
5. Add to `index.md` + append one line to `log.md`

### Query (answer a question)
1. Read `index.md` first — always
2. Read 2-4 candidate pages
3. Cite sources in your answer
4. If a new insight emerges, propose ingesting it (don't ingest unilaterally)

### Lint (health check)
Periodically scan for: orphan pages, dangling links, stale `Status: tentative` (>60 days), L1/L2/L3 violations, duplicate facts, missing index entries, missing log entries. Report; don't auto-fix.

## §8. Operating principles

1. **LLM-maintained** — humans give material, LLM produces structure
2. **Every ingest touches multiple pages** — update neighbors, not just the host
3. **Record more, not less** — losing experiments are as valuable as winning ones
4. **Mark uncertainty** — `Status: tentative` is honest; assertive false claims are damaging
5. **Preserve evolution history** — the *changes* in a strategy/model/design are themselves knowledge
6. **Status lives in structured fields, not prose.** A natural-language note inside a registry, docstring, or page ("this direction was abandoned", "this is deprecated") is an *assertion nobody re-checks* — it goes stale silently and later readers act on it. Anything a tool or future session must act on (closed / deprecated / superseded / invalid) must be a structured marker (frontmatter field, ledger column, overlay key) that consumers actually read.

---

## §9. Dependency declarations in frontmatter (scale feature)

> **Adopt when**: the project has 10+ skills/scripts that read or write wiki content, and "changed X, forgot to update Y" has bitten at least twice.

Skills (and other executable docs) declare their load-bearing inputs/outputs in YAML frontmatter:

```yaml
---
name: my-skill
description: ...
consumes:                       # what I read (changes to these affect me)
  - wiki/architecture/data-flow.md
  - analytics.daily_summary     # external table, db.table format
  - src/pipeline/runner.py      # code module, project-root-relative
produces:                       # what I write (downstream can sense my changes)
  - wiki/experiments/scorecard_*.md    # globs allowed
upstream_skills:
  - data-collector
downstream_skills:              # optional — drift detector can infer the reverse
  - daily-report
load_bearing_for:               # if I change, these must be reviewed in lockstep
  - wiki/MAINTENANCE_ROUTING.md
---
```

Three conventions that keep this system cheap:

1. **Declare load-bearing only.** A casual markdown link is not a dependency. Test: *"If X changes and Y is not updated, does something silently fail or mislead?"* — yes → declare; no → don't.
2. **One-way declaration.** A declares `load_bearing_for: [B]`; B does not have to declare the reverse. The drift detector computes reverse views mechanically — humans never maintain symmetry by hand.
3. **Frontmatter is the SSOT.** Reverse tables and dependency graphs are *derived* (DO-NOT-EDIT, script-generated). Never hand-write them.

**Enforcement is four-layered** (each layer backstops the previous — see `docs/maintenance-mechanisms.md` in the skill repo):

| Layer | Mechanism | When it fires |
|---|---|---|
| A | Written rule (CLAUDE.md / this section) | read at session start |
| B | PostToolUse hook prints a draft frontmatter to stderr | the instant a new skill file is created |
| C | Stop hook blocks session end if a newly created skill lacks the fields | session end |
| D | Nightly drift detector: unregistered files, dead references, asymmetric declarations | daily |

Reference implementations: `tools/check_new_skills_registered.py` (layer C), `tools/check_dependency_drift.py` (layer D), `tools/scan_skill_dependencies.py` (bootstrap drafts for legacy files).

**Scope note**: this section covers executable docs (skills/scripts). Plain wiki pages do *not* declare anything — they are the referenced side; the drift detector infers "which wiki pages are load-bearing" from the skills' `consumes:` lists. Making wiki pages self-declare would just be a second, hand-maintained copy of that information.

## §10. Machine ledgers inside the wiki (scale feature)

> **Adopt when**: automated processes (search loops, experiment runners, monitors) produce thousands of structured records that humans will never read row-by-row, but tools must query.

Keep a `wiki/<topic>_ledger/` (or similar) directory holding append-only machine data: `*.jsonl` ledgers, state DBs, overlay files. Rules learned the hard way:

1. **Division of labor**: *the ledger answers "how did this specific item do"; a wiki page answers "is this direction still worth pursuing"*. Don't dump ledger rows into pages; don't make tools parse narrative pages. When a conclusion exists only in the machine ledger, humans can't find it — generate a summary page (see §11) so both audiences are served.
2. **Append-only + overlays for corrections**: a recorded verdict cannot be edited in place. To invalidate it, write an overlay record with a *new* key (e.g. `invalidated_by: <reason-id>`), and make consumers explicitly honor that key. Record *why* it was invalidated — "wrong reason, coincidentally right conclusion" misleads the next reader into "tried that, doesn't work" when the truth was "that couldn't be measured".
3. **Structured retirement markers**: when a whole direction is closed, write a machine-readable `action: close` (or equivalent) record — not just a prose note. Coverage/summary tools can only count what is structured; prose conclusions are invisible to them, and "invisible to the tool" eventually becomes "reported as never tried".
4. **Derived data is gitignored**: anything rebuildable from the ledger (timelines, health reports, action streams) must be regenerable and never committed as truth.

## §11. Auto-generated wiki pages (scale feature)

> **Adopt when**: machine ledgers (§10) exist and humans keep missing conclusions that live only in them.

Generated pages are L2 with special rules:

1. **Derive the format from this SCHEMA's existing page types** — do not invent a new format per generator. A generated experiment summary should look like an experiment page.
2. **Regenerate-without-clobber**: if a generated page hosts hand-written sections (e.g. a human "verdict" paragraph), the generator must preserve those sections across re-runs. A generator that wipes human input on its second run will simply stop being used.
3. **Self-disclosure of limits**: a generated page must state what its emptiness means. "No decision records found" must say *"empty ≠ nobody tried — records may predate structured markers; check <source>"*. Otherwise an empty section reads as an authoritative "nothing happened", which is exactly the misreading that caused duplicated work before the page existed.
4. Mark the generated region with an explicit banner:
   ```markdown
   <!-- AUTO-GENERATED by <script> from <source> — edits outside HUMAN sections will be overwritten -->
   ```

## §12. Navigation layer (scale feature)

> **Adopt when**: new sessions keep re-deriving project context, or nobody can remember which doc/skill handles what.

Three optional top-level docs, all L3, all small:

| File | Purpose | Key pattern |
|---|---|---|
| `ONBOARDING.md` | What a *new session* must load before doing real work | Starts with a copy-paste block: *"Paste this as your first message: ..."*. Carries a header warning that any versions/numbers in its body are historical snapshots — current state lives in the L2 derived view. |
| `USAGE_MANUAL.md` | Scenario → command manual ("I want to X → run Y, output lands in Z") | One section per recurring scenario; commands verbatim |
| `SKILL_ROUTING.md` | Trigger phrase → skill mapping + disambiguation rules | Needed once skills > ~10 and their scopes overlap |

Bootstrap includes an `ONBOARDING.md` template; the other two emerge when the pain appears.
