# cwiki — LLM-maintained project knowledge base skill

A [Claude Code skill](https://docs.claude.com/en/docs/claude-code) that gives any project a clean, LLM-maintained `wiki/` knowledge base.

The methodology is distilled from running a multi-year quant research wiki, then generalized to be project-agnostic. Works for code projects, research labs, post-mortem archives, personal lab notebooks — anything where you want the LLM to organize and cross-reference knowledge instead of you doing it by hand.

## What you get

- **3-layer data model** — SSOT (machine truth) / Derived (auto views) / Narrative (hand-written stories). Prevents the "same fact updated in three places, contradicting itself" failure mode.
- **5 generic page categories** — `concepts/`, `experiments/`, `sources/`, `architecture/`, plus your own domain dirs. Each has a template.
- **`[[name]]` cross-references** — Obsidian-compatible. Bi-directional back-references are enforced by the Ingest flow.
- **Event-routing table** — `MAINTENANCE_ROUTING.md` maps "this kind of change" → "exactly these files must be updated". Stops drift between code and wiki.
- **Ingest / Query / Lint** as three named operations the skill drives end-to-end.

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
| `建立 wiki` / `bootstrap wiki` / `set up project wiki` | §2 Bootstrap — creates `wiki/SCHEMA.md`, `index.md`, `log.md`, `MAINTENANCE_ROUTING.md` and 4 starter category dirs |
| `ingest this: <material>` / `把这个加进 wiki` | §3 Ingest — classifies, creates/updates the host page, adds `[[]]` cross-refs, updates `index.md` + `log.md` |
| `wiki 里有没有 X` / `query wiki` / `之前对 X 的结论是?` | §4 Query — reads `index.md`, walks to candidate pages, answers with citations |
| `lint wiki` / `wiki 体检` | §5 Lint — orphan-page check, dangling-link check, stale-status scan, L1/L2/L3 violation check |

The skill is **opt-in** — it only activates on those trigger phrases. It will not touch your repo when you're doing normal work.

## What's inside this repo

```
.
├── skill.md                       # main instructions (§0–§9)
├── templates/
│   ├── SCHEMA.md                  # the rule book — gets copied to wiki/ at bootstrap
│   ├── index.md                   # starter table of contents
│   ├── log.md                     # ops log format
│   ├── MAINTENANCE_ROUTING.md     # event → file list table (extend per project)
│   └── page_types/
│       ├── concept.md
│       ├── experiment.md
│       ├── source.md
│       ├── architecture.md
│       └── domain_entity.md       # flexible template for project-specific entities
└── README.md
```

## Design notes

A few non-obvious decisions worth knowing about:

- **Templates are kept short on purpose** — under 30 lines each. Long templates get treated like mandatory forms; short templates leave room for the actual content.
- **The dependency-declaration system (§6 of skill.md)** is marked *optional advanced*. Heavy mechanical drift detection only pays off once a project has >10 scripts producing wiki content. New projects should skip it.
- **The `[[]]` cross-reference convention is bi-directional**: every `[[X]]` you add in page A must also produce a back-reference in page X. The Ingest flow enforces this — it's the single biggest reason orphan pages don't accumulate.
- **L1 (machine truth) and L3 (narratives) never touch the same fact.** If a number lives in a JSON ledger, the narrative page links to the ledger rather than copying. This is the rule that prevents the worst kind of drift.

## License

MIT — use it however you like. If you extend the methodology in interesting ways, PRs welcome.
