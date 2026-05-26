# Wiki Schema — <PROJECT_NAME> Knowledge Base

> LLM-maintained. Humans feed material and make decisions; LLM organizes, archives, and cross-references.

## §1. Purpose

This `wiki/` is a knowledge base maintained by LLM agents over the lifetime of the project. The human's role is to feed material (notes, papers, post-mortems, design discussions) and to make decisions. The LLM's role is to organize that material into a consistent, cross-linked structure that future sessions (and future humans) can navigate.

## §2. Directory layout

```
wiki/
├── SCHEMA.md                  # this file — operating rules
├── index.md                   # table of contents
├── log.md                     # operations log (newest first)
├── MAINTENANCE_ROUTING.md     # event → file list routing
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

Reference allowed directions:
- L3 can reference L1 and L2
- L2 can reference L1
- L1 references nothing (atomic truths)
- L2 **must not** reference L3 (derived views can't depend on stories)

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
