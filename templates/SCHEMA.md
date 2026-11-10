# Wiki Schema — <PROJECT_NAME> Knowledge Base

> LLM-maintained. Humans feed material and make decisions; LLM organizes, archives, and cross-references.
>
> Sections §1–§8 are the core — every project uses them from day one.
> Sections §9–§16 are **scale features** — adopt each one only when the trigger condition listed at its top is met.

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

## §13. Context budget & distillation (scale feature)

> **Adopt when**: an always-loaded doc (`CLAUDE.md`, system-prompt appendix, etc.) has grown past what the harness comfortably injects, or dated "lessons" entries accumulate faster than anyone re-reads them.

### 13.1 Injection tiers (orthogonal to L1/L2/L3)

Layering (§3) says *who may edit* a file. **Injection tier** says *what it costs to carry*: every token in an always-loaded doc is paid on every turn of every session. Classify content by tier, then put it where its tier belongs:

| Tier | Loaded | Belongs in | Example |
|---|---|---|---|
| T3 always-loaded | every turn | `CLAUDE.md` — rules, pointers, one-line lessons | "new entries = one line + pointer" |
| T2 scene-loaded | when a skill/topic activates | skill bodies, concepts pages | a methodology page read on demand |
| T1 atomic lookup | when explicitly queried | wiki pages, archives | a frozen experiment write-up |
| T0 raw truth | tool-queried only | ledgers, JSON artifacts | 10⁵-row ledgers |

The classic failure is **T1 content living at T3 price**: multi-KB war stories pasted into `CLAUDE.md` because that's where the author happened to be. The content isn't wrong — it's mis-tiered.

### 13.2 Budget lines + nightly check

Set explicit byte budgets for each always-loaded doc (two lines: the lessons/section budget, and a whole-file budget a safe margin under the harness's own warning threshold). A nightly check reports current size and flags over-budget as a violation. **The numbers are judgment calls — say so in the config comment** rather than dressing them up as derived.

### 13.3 Distillation SOP (run interactively, never headless)

When over budget:

1. Cluster same-theme entries/fragments (theme candidates come from existing concepts pages and skill section titles);
2. Synthesize into T2/T1 pages — **UPDATE > MERGE > CREATE** (prefer enriching an existing page over creating a near-duplicate);
3. **Retire in two modes**: a self-contained fragment → replace in place with a one-line pointer `→ [[concepts/xxx]]`, move the full original into `wiki/lessons/archive/YYYYMM.md`; a fragment deeply embedded in a composite narrative → synthesize only, leave the original untouched (absorbed when the whole entry retires);
4. Append to a distill ledger (`wiki/lessons/distill_ledger.jsonl`): source fingerprint, destination page, date, bytes saved;
5. When absorbing a "correction" entry, the synthesis keeps only the corrected conclusion plus one evolution-trail line;
6. **Spot-check read-back**: after distilling, randomly pick 2 originals and compare against the synthesized page section by section — a synthesis that drops a caveat is a *silent* failure (the archive has it, but nobody reads archives). Record `spot_checked: true` in the ledger. This step cannot be mechanized; it is the human gate of the SOP.

### 13.4 Entry-form gate (write-side shaping)

Budgets only catch *accumulated* drift; a single 3KB narrative entry hides below the total line for months. Add a per-entry check: dated entries added **after a cutoff date** must be "one line + pointer" — over ~800B, or over ~500B with no link at all, is a violation named the next night. Three design points, each earned:

- **Non-retroactive**: entries at or before the cutoff are exempt (they belong to the distillation backlog). Gating history on day one kills adoption — same grace-period logic as §9's enforcement.
- **No write-time hook**: write-side blocking via hooks disturbs concurrent sessions and has its own failure modes; next-morning naming is enough, because the budget line still backstops it.
- Thresholds are judgment calls pinned from the observed size of healthy pointer entries; write that in the comment.

## §14. Contradiction structure (scale feature)

> **Adopt when**: corrections have started silently overwriting history, or two sessions have reached conflicting conclusions and the page only shows whichever wrote last.

### 14.1 Fixed sections on synthesis pages

Concepts pages produced by distillation (or any synthesis) carry a fixed skeleton so tools and future sessions know where to look: `## Scenario` / `## SOP` / `## Decision logic` / `## Anti-patterns` / `## Key evidence` (pointing back to concrete dates / artifacts / ledger rows) / `## Evolution trail` / `## Open contradictions` (write "(none)" explicitly — an absent section is ambiguous, an empty one is information).

### 14.2 Three rules

1. **A contradiction never overwrites the body.** New evidence conflicting with the current conclusion lands first in *Open contradictions* with pointers to both sides' evidence; only after adjudication does the body change, and the entry moves to *Evolution trail*.
2. **Keep both claims.** When merging conflicting conclusions, preserve both with the disagreement stated explicitly. "Last writer wins" is forbidden — it silently destroys the information that a disagreement ever existed.
3. **Corrections back-mark.** When a conclusion is corrected, go back to the original text and add a `⛔ superseded → see [date]` marker. (A lint can only *hint* at missing back-marks — semantic detection is unreliable; be honest about that limit rather than pretending the check is strong.)

## §15. Freshness arbitration: fingerprints, supersedes, tombstones (scale feature)

> **Adopt when**: multiple concurrent sessions write the wiki and a reader can no longer tell which of two overlapping pages reflects the latest state.

### 15.1 `sources:` fingerprints in frontmatter (new pages mandatory, legacy gradual)

A page declares the evidence its conclusions **load-bearing** depend on (same test as §9: would a silent change mislead the reader?):

```yaml
sources:
  - path: build/v3/report.json     # artifact: existence + optional sha256
    sha256: ab12...
  - commit: 7868099c               # code state: narrative-grade pointer
```

Nightly check reports three states per entry: **intact / changed / missing** (verify commits with `git cat-file -e`). Report only — scripts never edit L3 pages. The two grades don't mix: `commit` is narrative-level ("around this change"); byte-accurate reconciliation goes through artifact hashes.

### 15.2 `supersedes:` + tombstones

- A page replacing another declares `supersedes: [wiki/old_page.md]` in frontmatter; the superseded page **must** carry a tombstone banner at the top (`> **DEPRECATED** → see [[new_page]]`). Lint: declared-but-unmarked = violation; old page deleted entirely = info (the declaration still documents lineage).
- **Deleted pages go in a tombstone registry** (`wiki/_tombstones.json`: path, date, reason, successor). Generators consult it before re-emitting a page — and the registry has teeth even for generators that never integrated it, because the nightly check detects **resurrections** (a tombstoned path existing again) after the fact.

### 15.3 Newest-truth ordering

When several artifacts describe the same thing, resolve "which is current" in this order — do not improvise per case:

1. a **derived view** (`_current_*` L2 file) if one exists — that is its whole job;
2. **filename semantics** (`_current_*` vs date-stamped history);
3. **tombstone / supersedes** declarations;
4. last resort: `git log -1 --format=%ci -- <path>` on each candidate.

mtime is not on the list — sync scripts and checkouts rewrite it meaninglessly.

## §16. Topic layer (scale feature)

> **Adopt when**: "when I mention topic X, locate the content, current progress, change history, related sessions, related code" has no single entry point — the answer is smeared across pages, ledgers, log entries and commits.

A **topic** is a stitching key, not a new content layer. Design constraints that keep it cheap:

1. **The registry is small L1 truth** (`wiki/_topics.json`): per topic only `name / aliases / status (active|paused|done) / anchors` — where anchors point into existing artifacts (pages, ledger paths, code roots, log-title keywords). **No narrative lives here**; narrative already has homes.
2. **The five-column view is derived, never stored**: a resolver tool answers "topic → ① content pages ② progress (from anchored ledgers/derived views) ③ change history (log entries matching the topic) ④ related sessions ⑤ related code" by walking anchors at query time. Storing the view would create a second copy that drifts.
3. **`check-new` gate**: before registering a new topic, search existing names/aliases (substring + a fuzzy pass, e.g. character-bigram overlap **aggregated at topic level across aliases** — per-alias matching misses near-duplicates split across aliases). Near-miss → propose merging instead of creating.
4. **Orphan prompts, not orphan blocks**: plans/pages with no registered topic are listed as info by the nightly check — pressure to register, no blocking.
5. Lint guards the registry shape: dead anchors = violation; alias collisions = violation; empty anchors = violation; broken JSON = violation (never silently treated as an empty registry).
