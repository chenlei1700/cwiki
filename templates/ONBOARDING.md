# New-Session Onboarding — <PROJECT_NAME>

> ⚠️ **SSOT notice**: any version numbers, metrics, or "current state" mentioned in this file's body are **historical snapshots** frozen at writing time. Current state lives in the L2 derived view (`wiki/_current_state.md` or equivalent) — always trust that over this page.

> Purpose: let a brand-new LLM session load this project's accumulated knowledge **before** doing real work, instead of re-deriving (or contradicting) it.

## The most important thing — copy this into your first message

When starting a session that will explore, design, or change anything non-trivial, paste:

```
Read wiki/ONBOARDING.md first to load project state and prior knowledge, then start my task: [your task]
```

## Before any new exploration — query the ledgers

If the project keeps an exploration/hypothesis ledger (SCHEMA §10), query it **before** writing any experiment plan:

```bash
# has this been tried before? why did it fail?
<your query command> --topic <target>
<your query command> --result fail
```

Re-running a failed path because nobody checked is the most expensive recurring mistake this file exists to prevent.

## Reading order

1. `wiki/_current_state.md` — what is live right now (L2, auto-synced)
2. `wiki/index.md` — map of everything
3. The 2–4 concept/architecture pages relevant to your task (find via index)
4. `wiki/MAINTENANCE_ROUTING.md` — before you *write* anything, know which files your change must touch

## House rules in 5 lines

- Same fact lives in one place (L1); link, never copy — [SCHEMA §3](SCHEMA.md)
- Never hand-edit L2 (generated) files; never let scripts clobber L3 (narrative) files
- Every ingest updates neighbors + index + log, not just the host page
- Mark tentative conclusions as tentative
- Record failures as carefully as wins

## Known traps (append as they are discovered)

- <trap 1 — one line + link to the experiment/concept page with the full story>
- <trap 2>
