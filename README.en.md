# cwiki — LLM-maintained project knowledge base skill

> [中文（默认）](README.md) | English - kept in sync; English is canonical where wording differs.

A [Claude Code skill](https://docs.claude.com/en/docs/claude-code) that gives any project a clean, LLM-maintained `wiki/` knowledge base — plus the **maintenance machinery** (sync scripts, hooks, drift detectors) that keeps it truthful over months.

The methodology is distilled from running a multi-year quant research wiki in production (40+ skills, nightly pipelines, append-only ledgers), then generalized to be project-agnostic. Works for code projects, research labs, post-mortem archives, personal lab notebooks — anything where you want the LLM to organize and cross-reference knowledge instead of you doing it by hand.

## What you get

**The methodology** (skill.md + templates/):

- **3-layer data model** — SSOT (machine truth) / Derived (auto views) / Narrative (hand-written stories). Prevents the "same fact updated in three places, contradicting itself" failure mode.
- **5 generic page categories** — `concepts/`, `experiments/`, `sources/`, `architecture/`, plus your own domain dirs. Each has a template.
- **`[[name]]` cross-references** — Obsidian-compatible. Bi-directional back-references are enforced by the Ingest flow.
- **Event-routing table** — `MAINTENANCE_ROUTING.md` maps "this kind of change" → "exactly these files must be updated", with **symptom-if-skipped** and **backstop** columns that turn it into a reverse diagnostic index.
- **Ingest / Query / Lint** as three named operations the skill drives end-to-end.
- **Scale features (opt-in, each with an explicit adoption trigger)** — dependency frontmatter with 4-layer enforcement, append-only ledgers with query-before-explore, auto-generated pages with no-clobber + self-disclosure rules, a navigation layer (`ONBOARDING.md` etc.), context budgets + a distillation SOP for always-loaded docs, contradiction structure (evolution trail / open contradictions), freshness arbitration (sources fingerprints, supersedes + tombstones, a fixed newest-truth ordering), and a topic layer that stitches pages/ledgers/log/code behind one lookup key.

**The machinery** (docs/ + tools/):

- [`docs/architecture.md`](docs/architecture.md) — the reader's overview: the problem, the two orthogonal dimensions (modification rights x injection tiers), the seven methodology commitments, component map, project lifecycle, and stated limits. Start here to understand the system; the files below are for operating it.
- [`docs/maintenance-mechanisms.md`](docs/maintenance-mechanisms.md) — the full operating picture: L1→L2 sync contract, append-only ledgers, hook-based enforcement (PostToolUse / Stop / pre-commit / nightly), freshness tiers, generated-page rules, "discipline becomes gates", an operations calendar, and a symptom→cause failure index.
- [`tools/`](tools/README.md) — generic reference implementations: `sync_views_example.py` (L1→L2 sync with `--check` for pre-commit), `scan_skill_dependencies.py` (frontmatter draft generator), `check_new_skills_registered.py` (Stop-hook gate), `check_dependency_drift.py` (nightly drift detector).

## Install

Quick version below — **[INSTALL.md](INSTALL.md) has the detailed guide**:
mode trade-offs (global vs per-project vs no-git copy, shadowing rules),
post-install verification, vendoring vs submodule for team repos, what is and
isn't auto-active (tools need wiring), updating each install mode, a
troubleshooting table, and uninstall.

### Mode A — user-global (available in every project)

```bash
# Clone into your user-global skills directory.
# Windows:
git clone https://github.com/chenlei1700/cwiki "$env:USERPROFILE\.claude\skills\wiki-management"

# macOS / Linux:
git clone https://github.com/chenlei1700/cwiki ~/.claude/skills/wiki-management
```

The folder name (`wiki-management`) becomes the skill name. Rename if you prefer a different invocation name.

### Mode B — per-project

```bash
git clone https://github.com/chenlei1700/cwiki .claude/skills/wiki-management
```

Then vendor it (remove its `.git`, commit the files) so anyone cloning your project gets the skill too — details and the submodule alternative in [INSTALL.md §1](INSTALL.md).

After installing, **start a new session** (skills are picked up at session start) and verify per [INSTALL.md §2](INSTALL.md).

## Use — two starting scenarios

The install is identical either way; what differs is the first thing you say.

### Scenario 1 — brand-new project (greenfield)

Say `bootstrap wiki` / `建立 wiki`. The skill creates `wiki/SCHEMA.md`, `index.md`, `log.md`, `MAINTENANCE_ROUTING.md`, `ONBOARDING.md` and the starter category dirs in ~5 minutes (skill.md §2), asks one question about domain categories, and you start ingesting from day one. No machinery beyond the skeleton — scale features wait for their adoption triggers.

### Scenario 2 — existing project (brownfield)

Say `adopt wiki` / `把 wiki 方法论用到现有项目`. The skill runs the **Adoption flow** (skill.md §2B) instead of bare Bootstrap:

1. **Read-only inventory** of what you already have — grown README/docs, a `CLAUDE.md` fat with accumulated lessons, machine artifacts/ledgers — classified into layers; you confirm a one-page adoption map.
2. **Skeleton stands up alongside** — nothing existing moves; machine artifacts are declared L1 *where they live* (moving them breaks producers); the adoption date becomes the cutoff for all non-retroactive gates.
3. **Incremental migration, two lanes** — migrate-on-touch for docs real work revisits, plus a small queue for the backlog (automatable for small files via the Mechanism-8 headless driver with mechanical acceptance + rollback).
4. **Gates only as triggered** — typically just the always-loaded-doc budget + entry-form gate on day one, lint in report-only mode for the first week. Legacy content is never gated retroactively.

The anti-pattern Adoption exists to prevent: a big-bang rewrite of all existing docs into wiki format — it loses fidelity, stalls halfway, and leaves you with two half-truths instead of one messy truth.

### Daily operations (both scenarios, once the wiki exists)

| You say | What happens |
|---|---|
| `ingest this: <material>` / `把这个加进 wiki` | §3 Ingest — classifies, creates/updates the host page, adds `[[]]` cross-refs, updates `index.md` + `log.md` |
| `wiki 里有没有 X` / `query wiki` / `之前对 X 的结论是?` | §4 Query — reads `index.md`, walks to candidate pages, answers with citations |
| `lint wiki` / `wiki 体检` | §5 Lint — orphan-page check, dangling-link check, stale-status scan, L1/L2/L3 violation check |

The skill is **opt-in** — it only activates on those trigger phrases. It will not touch your repo when you're doing normal work.

## What's inside this repo

```
.
├── skill.md                       # main instructions (§0–§9)
├── INSTALL.md                     # detailed install / verify / update / troubleshoot
├── templates/
│   ├── SCHEMA.md                  # the rule book — core §1–§8 + scale features §9–§16
│   ├── index.md                   # starter table of contents
│   ├── log.md                     # ops log format
│   ├── MAINTENANCE_ROUTING.md     # event → file list table (+ symptom/backstop columns,
│   │                              #   ordered-checklist pattern, forbidden actions, who-reads-what)
│   ├── ONBOARDING.md              # new-session loading guide template
│   └── page_types/
│       ├── concept.md
│       ├── experiment.md
│       ├── source.md
│       ├── architecture.md
│       └── domain_entity.md       # flexible template for project-specific entities
├── docs/
│   ├── architecture.md            # the why and the map — read this first
│   └── maintenance-mechanisms.md  # how the wiki stays alive: sync, hooks, ledgers,
│                                  #   drift detection, generated pages, gates
├── tools/                         # reference implementations (copy + customize CONFIG blocks)
│   ├── README.md                  # wiring instructions (pre-commit / hooks / nightly)
│   ├── sync_views_example.py
│   ├── scan_skill_dependencies.py
│   ├── check_new_skills_registered.py
│   ├── check_dependency_drift.py
│   └── wiki_lint_skeleton.py      # starter mechanized nightly lint (5 checks + selftest)
└── README.md
```

## Design notes

A few non-obvious decisions worth knowing about:

- **Templates are kept short on purpose** — long templates get treated like mandatory forms; short templates leave room for the actual content.
- **Every scale feature states its adoption trigger.** Heavy machinery (frontmatter enforcement, ledgers, generated pages) only pays off past a certain project size; adopting it early just adds ceremony. Each section in SCHEMA §9–§12 opens with "Adopt when: ...".
- **The `[[]]` cross-reference convention is bi-directional**: every `[[X]]` you add in page A must also produce a back-reference in page X. The Ingest flow enforces this — it's the single biggest reason orphan pages don't accumulate.
- **L1 (machine truth) and L3 (narratives) never touch the same fact.** If a number lives in a JSON ledger, the narrative page links to the ledger rather than copying. This is the rule that prevents the worst kind of drift — and it applies to `CLAUDE.md`/`README.md` too.
- **A rule written as prose decays; the same rule wired as a failing check doesn't.** That observation (paid for repeatedly in the source project) is why the dependency convention ships with four enforcement layers and why `docs/maintenance-mechanisms.md` ends every mechanism with its gates. Corollary: fault-inject every gate once — a gate that has never fired is indistinguishable from a broken one.
- **Status lives in structured fields, not prose.** A "this is deprecated" paragraph is invisible to tools; the direction it closed gets re-explored months later. Closures/deprecations get machine-readable markers.

## Changelog

- **v3 (2026-11)** — memory-governance sync from the source project (informed by studying TencentDB-Agent-Memory and NVIDIA auto-ontology, then battle-testing in production): SCHEMA §13 context budgets + distillation SOP (injection tiers, two-mode retirement, distill ledger, spot-check read-back, entry-form gate); §14 contradiction structure (evolution trail / open contradictions, no last-writer-wins, correction back-marks); §15 freshness arbitration (`sources:` fingerprints with 3-state nightly check, `supersedes:` + tombstone registry with resurrection detection, fixed newest-truth ordering); §16 topic layer (small registry + derived five-column view + near-miss gate); Mechanisms 7 (distillation loop) and 8 (external assistant-memory sovereignty — facts live in the wiki, memory holds pointers; headless migration driver pattern with mechanical acceptance, fidelity floor, path whitelist and write-surface delta gate); `tools/wiki_lint_skeleton.py` (starter mechanized lint, 5 checks, pure-function judgments, 18-injection `--selftest`); "guard the guards" wiring notes.
- **v2 (2026-10)** — synced from the source project's evolved design: SCHEMA scale features §9–§12 (dependency frontmatter + 4-layer enforcement; machine ledgers + overlay corrections; generated pages with no-clobber + self-disclosure; navigation layer), routing-table v2 patterns (symptom/backstop columns, ordered checklists + safety nets, forbidden actions, who-reads-what appendix), `ONBOARDING.md` template, `docs/maintenance-mechanisms.md`, `tools/` reference implementations, `.gitattributes` (LF normalization).
- **v1 (2026-05)** — initial release: 3-layer model, 5 categories, routing table, Ingest/Query/Lint.

## License

MIT — use it however you like. If you extend the methodology in interesting ways, PRs welcome.
