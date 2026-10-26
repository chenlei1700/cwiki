# cwiki — LLM-maintained project knowledge base skill

A [Claude Code skill](https://docs.claude.com/en/docs/claude-code) that gives any project a clean, LLM-maintained `wiki/` knowledge base — plus the **maintenance machinery** (sync scripts, hooks, drift detectors) that keeps it truthful over months.

The methodology is distilled from running a multi-year quant research wiki in production (40+ skills, nightly pipelines, append-only ledgers), then generalized to be project-agnostic. Works for code projects, research labs, post-mortem archives, personal lab notebooks — anything where you want the LLM to organize and cross-reference knowledge instead of you doing it by hand.

## What you get

**The methodology** (skill.md + templates/):

- **3-layer data model** — SSOT (machine truth) / Derived (auto views) / Narrative (hand-written stories). Prevents the "same fact updated in three places, contradicting itself" failure mode.
- **5 generic page categories** — `concepts/`, `experiments/`, `sources/`, `architecture/`, plus your own domain dirs. Each has a template.
- **`[[name]]` cross-references** — Obsidian-compatible. Bi-directional back-references are enforced by the Ingest flow.
- **Event-routing table** — `MAINTENANCE_ROUTING.md` maps "this kind of change" → "exactly these files must be updated", with **symptom-if-skipped** and **backstop** columns that turn it into a reverse diagnostic index.
- **Ingest / Query / Lint** as three named operations the skill drives end-to-end.
- **Scale features (opt-in, each with an explicit adoption trigger)** — dependency frontmatter with 4-layer enforcement, append-only ledgers with query-before-explore, auto-generated pages with no-clobber + self-disclosure rules, and a navigation layer (`ONBOARDING.md` etc.).

**The machinery** (docs/ + tools/):

- [`docs/maintenance-mechanisms.md`](docs/maintenance-mechanisms.md) — the full operating picture: L1→L2 sync contract, append-only ledgers, hook-based enforcement (PostToolUse / Stop / pre-commit / nightly), freshness tiers, generated-page rules, "discipline becomes gates", an operations calendar, and a symptom→cause failure index.
- [`tools/`](tools/README.md) — generic reference implementations: `sync_views_example.py` (L1→L2 sync with `--check` for pre-commit), `scan_skill_dependencies.py` (frontmatter draft generator), `check_new_skills_registered.py` (Stop-hook gate), `check_dependency_drift.py` (nightly drift detector).

## Install

Pick one of the two install modes.

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

Then commit the `.claude/skills/wiki-management/` directory along with your project, so anyone cloning your project gets the skill too.

## Use

In any Claude Code session, just say one of:

| You say | What happens |
|---|---|
| `建立 wiki` / `bootstrap wiki` / `set up project wiki` | §2 Bootstrap — creates `wiki/SCHEMA.md`, `index.md`, `log.md`, `MAINTENANCE_ROUTING.md`, `ONBOARDING.md` and 4 starter category dirs |
| `ingest this: <material>` / `把这个加进 wiki` | §3 Ingest — classifies, creates/updates the host page, adds `[[]]` cross-refs, updates `index.md` + `log.md` |
| `wiki 里有没有 X` / `query wiki` / `之前对 X 的结论是?` | §4 Query — reads `index.md`, walks to candidate pages, answers with citations |
| `lint wiki` / `wiki 体检` | §5 Lint — orphan-page check, dangling-link check, stale-status scan, L1/L2/L3 violation check |

The skill is **opt-in** — it only activates on those trigger phrases. It will not touch your repo when you're doing normal work.

## What's inside this repo

```
.
├── skill.md                       # main instructions (§0–§9)
├── templates/
│   ├── SCHEMA.md                  # the rule book — core §1–§8 + scale features §9–§12
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
│   └── maintenance-mechanisms.md  # how the wiki stays alive: sync, hooks, ledgers,
│                                  #   drift detection, generated pages, gates
├── tools/                         # reference implementations (copy + customize CONFIG blocks)
│   ├── README.md                  # wiring instructions (pre-commit / hooks / nightly)
│   ├── sync_views_example.py
│   ├── scan_skill_dependencies.py
│   ├── check_new_skills_registered.py
│   └── check_dependency_drift.py
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

- **v2 (2026-10)** — synced from the source project's evolved design: SCHEMA scale features §9–§12 (dependency frontmatter + 4-layer enforcement; machine ledgers + overlay corrections; generated pages with no-clobber + self-disclosure; navigation layer), routing-table v2 patterns (symptom/backstop columns, ordered checklists + safety nets, forbidden actions, who-reads-what appendix), `ONBOARDING.md` template, `docs/maintenance-mechanisms.md`, `tools/` reference implementations, `.gitattributes` (LF normalization).
- **v1 (2026-05)** — initial release: 3-layer model, 5 categories, routing table, Ingest/Query/Lint.

## License

MIT — use it however you like. If you extend the methodology in interesting ways, PRs welcome.
