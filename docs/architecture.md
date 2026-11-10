# cwiki — architecture & methodology

What the system is, why it is shaped this way, and how the pieces relate.
This is the *reader's* document. The operator's manual is [skill.md](../skill.md)
(what the LLM does), the rulebook is [templates/SCHEMA.md](../templates/SCHEMA.md)
(the rules a wiki lives under), and the machine room is
[maintenance-mechanisms.md](maintenance-mechanisms.md) (the moving parts that
keep the rules true). Install steps: [INSTALL.md](../INSTALL.md).

---

## 1. The problem

An LLM-maintained knowledge base fails in characteristic ways, and none of them
look like failure on the day they happen:

- **Copy drift** — the same fact hand-written in three places; two go stale,
  readers can't tell which one is current.
- **Context-cost creep** — every session appends its lesson to the always-loaded
  doc; eighteen months later the doc costs more per turn than the work it guides.
- **Last-writer-wins** — a correction silently overwrites history; the information
  that a disagreement ever existed is destroyed.
- **Prose status** — "this direction is dead" written as a paragraph no tool can
  read; the direction gets expensively re-explored.
- **Discipline decay** — every one of the above has a written rule against it,
  and written rules alone decay. (This is the meta-failure that makes the others
  recurring instead of one-off.)

cwiki is the generalization of a system that hit all five in a multi-year
production project and grew a countermeasure for each.

## 2. Core model: two orthogonal dimensions

Every piece of content is classified on two independent axes. Most confusion in
doc systems comes from conflating them.

### 2.1 Modification rights — who may edit (L1 / L2 / L3)

| Layer | What | Who writes |
|---|---|---|
| **L1 SSOT** | machine-generated raw truth (ledgers, JSON artifacts) | scripts only |
| **L2 Derived** | views computed from L1 (`_current_*` summaries) | sync scripts only |
| **L3 Narrative** | stories, lessons, methodology | humans + LLM only |

The cardinal rule: **a fact lives in exactly one place, in L1**; everything else
links. L2 is regenerated, never merged; L3 is never clobbered by a script. This
single rule removes the copy-drift failure class (full spec: SCHEMA §3).

### 2.2 Injection tiers — what it costs to carry (T0–T3)

| Tier | Loaded | Belongs in |
|---|---|---|
| T3 | every turn of every session | `CLAUDE.md`: rules, pointers, one-liners |
| T2 | when a skill/topic activates | skill bodies, concepts pages |
| T1 | when explicitly queried | wiki pages, archives |
| T0 | tool-queried only | raw ledgers |

The classic failure is T1 content at T3 price — war stories pasted into
`CLAUDE.md`. The distillation loop (SCHEMA §13) continuously re-tiers content
downward; budgets and a per-entry form gate catch mis-tiered writes early.

These axes are orthogonal: a narrative lesson (L3) can be mis-tiered at T3; a
derived view (L2) is deliberately T3-adjacent because it is small and current.

## 3. Anatomy of a cwiki-managed project

```
project/
├── CLAUDE.md               # T3: rules + pointers (budgeted, entry-form gated)
├── wiki/
│   ├── SCHEMA.md           # the rules this wiki runs under
│   ├── index.md            # entry point for every query
│   ├── log.md              # one line per event, newest first
│   ├── MAINTENANCE_ROUTING.md  # event → files-to-update table
│   ├── concepts/ experiments/ sources/ architecture/ <domain>/   # L3 pages
│   ├── _topics.json        # topic registry (stitching keys)        [§16]
│   ├── _tombstones.json    # deleted-page registry                  [§15]
│   └── <topic>_ledger/     # L1 machine data living inside the wiki [§10]
└── scripts/maintenance/    # copied tools: lint, sync, drift detector
```

Information flows in a loop:

```
   humans / LLM sessions ──write──► L3 narrative ──link──► L1 truth
   automated producers  ──append─► L1 ledgers ──sync────► L2 views
   nightly jobs ──regenerate L2, run lint + drift detectors, append daily L1
   gates (pre-commit / hooks / nightly exit codes) ──block or name violations
```

Four forces keep it consistent: sync scripts, write-time gates, nightly jobs,
and periodic LLM lint for what mechanical checks can't see.

## 4. The methodology, as seven commitments

1. **Single source of truth, enforced by links.** Facts live once; everything
   else points. Applies beyond the wiki — `CLAUDE.md`/`README` link to derived
   views rather than carry their numbers.
2. **Discipline becomes gates.** Any "next time remember to…" from a
   post-mortem is translated into a failing check (pre-commit, hook, nightly
   exit code, test). A rule written as prose decays; the same rule as a red
   check doesn't. Three sub-rules, each paid for in incidents: fault-inject
   every gate once; derive allow-lists from the consumer rather than
   hand-writing them; report evidence, never bare booleans.
3. **Guard the guards.** The lint's own result goes into the nightly report;
   every check ships a `--selftest` with fault injections that runs in the
   project's normal test suite. A silently crashed gate is worse than no gate.
4. **History is append-only; status is structured.** Corrections are
   superseding rows/overlays, never in-place edits. Deprecation/closure is a
   machine-readable marker (frontmatter, ledger column, tombstone), never only
   prose. Contradictions land in a dedicated section *before* the body changes.
5. **Non-retroactive adoption.** Every gate keys off a cutoff date; legacy
   content is exempt and migrates incrementally (on-touch + a queued backlog).
   Gating history on day one kills adoption — grace beats purity.
6. **Pay-as-you-grow.** The core (§1–§8: layers, pages, cross-refs,
   Ingest/Query/Lint) is day-one. Every scale feature (§9–§16) states the pain
   that justifies it and stays dormant until that pain appears. Installing
   everything upfront is the documented anti-pattern.
7. **The LLM curates; mechanisms verify.** Humans feed material and decide;
   the LLM organizes and cross-links; but anywhere an LLM's *claim* matters
   (a migration "succeeded", a page "exists"), a mechanical check verifies it —
   trust is not part of the safety model, even for the LLM's own output.

## 5. Component map — who reads what

| Artifact | Audience | Role |
|---|---|---|
| [skill.md](../skill.md) | the LLM, at trigger time | operator manual: Bootstrap / Adoption / Ingest / Query / Lint flows |
| [templates/SCHEMA.md](../templates/SCHEMA.md) | copied into each project; read by LLM + humans | the rulebook the project's wiki runs under (core §1–§8, scale §9–§16) |
| [templates/](../templates/) others | copied at bootstrap | starters: index, log, routing table, onboarding, page types |
| [maintenance-mechanisms.md](maintenance-mechanisms.md) | humans wiring automation | the 8 mechanisms, operations calendar, failure-mode index |
| [tools/](../tools/README.md) | copied into `scripts/maintenance/` | reference gates: sync `--check`, drift detector, Stop-hook, lint skeleton |
| this file | humans evaluating or learning the system | the why and the map |

## 6. Lifecycle of a cwiki-managed project

1. **Day 0 — Bootstrap or Adoption.** Fresh project: skeleton in 5 minutes
   (skill.md §2). Existing project: read-only inventory → confirmed adoption
   map → skeleton coexists → incremental migration, adoption date = cutoff
   (skill.md §2B).
2. **Daily — Ingest / Query / Lint.** Material routes to pages with
   bi-directional cross-refs; queries start at `index.md`; lint reports, never
   auto-fixes.
3. **As pain appears — scale features.** Routing table when multi-file events
   get half-done; frontmatter enforcement at 10+ producers; ledgers when
   "didn't we try this?" has no answer; generated pages when ledger conclusions
   go unseen; budgets/distillation when the always-loaded doc swells;
   fingerprints/tombstones when concurrent sessions blur freshness; topics when
   "where is everything about X" has no entry point.
4. **Nightly — self-healing.** L2 regenerates, lint and drift detectors run
   with exit codes, migration batches advance, and the pipeline's report
   records whether the guards themselves ran.

## 7. Provenance and limits

The methodology is distilled from a multi-year quant research project (40+
skills, nightly pipelines, ledgers at 10⁵–10⁶ rows) and from studying
TencentDB-Agent-Memory and NVIDIA auto-ontology; everything here survived
production contact, and several rules exist *because* their absence caused a
named incident upstream.

Known limits, stated rather than papered over: semantic duplication (a copied
*claim* rather than a copied number) is not machine-detectable — it is caught,
if at all, at distillation spot-check; correction back-marks are lint-*hinted*
only; the write side ultimately runs on LLM discipline, which is why every
write-side rule has a next-morning detection gate rather than a promise.
