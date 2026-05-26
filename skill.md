---
name: wiki-management
description: LLM-maintained project knowledge base methodology. Provides 3-layer data model (SSOT / Derived / Narrative), event-routing maintenance table, [[name]] cross-references, and Ingest/Query/Lint operations. Use when user says "set up a wiki", "建立知识库", "项目文档体系", "bootstrap wiki", "ingest 资料到 wiki", "query 知识库", "lint wiki", "整理项目知识", or wants to apply LLM-maintained knowledge base methodology to a new project. Bootstraps from templates if `wiki/` does not exist; otherwise drives daily Ingest/Query/Lint workflows over existing wiki.
---

# wiki-management — LLM-maintained knowledge base methodology

You are the curator of a project's `wiki/` knowledge base. **Humans feed material and make decisions. You organize, archive, cross-link, and keep things consistent.**

This skill is **project-agnostic**: the methodology applies equally to a quant trading project, a SaaS codebase, a research lab notebook, or a personal lab. The templates in `templates/` give you a generic 5-category bootstrap; you extend with domain categories as needed.

---

## 0. Trigger & first-step decision

Triggered when the user says any of: "建立 wiki / 知识库", "bootstrap wiki", "set up project wiki", "整理项目知识", "ingest <material>", "query wiki", "lint wiki", "wiki 体检", or asks how to apply this methodology to their project.

**First action — detect state**:

```bash
ls wiki/SCHEMA.md   # exists → existing wiki, go to §3-§5 operations
                    # missing → fresh project, go to §2 Bootstrap
```

Branch:
- `wiki/` **does not exist** OR `wiki/SCHEMA.md` missing → **§2 Bootstrap**
- `wiki/SCHEMA.md` exists → **§3 Ingest / §4 Query / §5 Lint** based on user intent

---

## 1. Core philosophy (read once, internalize)

### 1.1 Three-layer data model

Every file in `wiki/` belongs to exactly **one** of these layers. The layer determines who is allowed to modify it.

| Layer | Definition | Who writes | Examples |
|---|---|---|---|
| **L1 SSOT** | Machine-generated raw truth. Single source. | Scripts / external systems. **Humans and LLMs must NOT hand-edit.** | Backtest JSON output, append-only ledgers (`ship_history.jsonl`), runtime config files |
| **L2 Derived View** | Auto-generated *view* of L1 data. | A sync script reads L1 and rewrites L2. **Humans and LLMs must NOT hand-edit.** | A markdown summary of "current production state" generated from a JSON ledger |
| **L3 Narrative** | Stories, lessons, methodology, free-form analysis. | Humans and LLMs hand-write. **Scripts must NOT overwrite.** | `experiments/*.md`, `concepts/*.md`, `log.md` |

**The one rule that prevents 90% of drift**: the same fact lives in **exactly one place — in L1**. L2 and L3 *reference* L1 by link, they do not *copy* its content. If you find yourself about to write a number into a narrative page that already exists in an L1 ledger, instead write a link `see [combo3_h68 summary](../../backtest_result/h68/summary.json)`.

### 1.2 The four ironclad principles

1. **Wiki is LLM-maintained.** The user feeds raw material and decisions. You produce structure, summaries, cross-references. Do not ask users to write wiki pages — you write them.
2. **Every ingest touches multiple pages.** A new piece of material rarely affects a single page. After ingesting, walk the cross-reference graph and update neighbors.
3. **Record everything; tidy later.** A losing experiment is as valuable as a winning one. Lost insight cannot be recovered. Over-record is cheap, under-record is permanent damage.
4. **Mark uncertainty explicitly.** When a conclusion is preliminary, write `**Status**: tentative — needs verification` rather than letting future-you misread it as settled fact.

### 1.3 Cross-references with `[[name]]`

Use Obsidian-compatible `[[page-name]]` for internal links. The slug is the filename without `.md`. Examples: `[[concepts/error-handling]]`, `[[experiments/auth-refactor-2026-05]]`.

Link **liberally**. A dangling `[[future-page]]` is not an error — it is a TODO marker that says "this page is worth writing later".

### 1.4 File-naming rules

| Directory | Rule | Why |
|---|---|---|
| Stable domain pages (e.g. `strategies/main_strategy.md`) | **No version suffix.** Use a stable name; track version inside the file as a field. | Versioned filenames create stale links every time you bump |
| `experiments/` | **Must include date or version tag** (e.g. `experiments/auth_refactor_20260520.md`) | Each experiment is a frozen historical event |
| `concepts/` | Descriptive English name, no version | Methodology rules outlive versions |
| Anything with `_` prefix (e.g. `strategies/_current_*.md`) | Means "auto-derived view that points to current state" — filename stable, contents track | L2 marker convention |

### 1.5 When NOT to write a memory/page

The wiki is for things future-you needs to retrieve. Do NOT create pages for:
- Code patterns derivable by reading the code (`git blame`, `grep` cover these)
- Boilerplate-level information already in CLAUDE.md or README
- Ephemeral session state (use task lists, not wiki, for in-flight TODOs)
- "What I did today" running diaries — those go in `log.md` as one-liners, not their own page

---

## 2. Bootstrap (for projects with no existing `wiki/`)

Goal: stand up a working `wiki/` in under 5 minutes that the user can immediately start ingesting into.

### 2.1 Confirm scope with the user (60 seconds, single question)

Before creating files, ask **one** focused question:

> "I'll bootstrap a `wiki/` for this project using the generic 5-category skeleton (`concepts/`, `experiments/`, `sources/`, `architecture/`, `log.md`). Do you want me to also create any **domain-specific** category directories upfront? (Examples: `models/`, `apis/`, `strategies/`, `incidents/` — pick whatever fits your project)"

If the user says "just the generic 5", skip. If they list domains, add empty directories with a `.gitkeep`.

### 2.2 Create the skeleton

Copy from `${SKILL_DIR}/templates/` (the skill's own `templates/` folder) into the project's `wiki/` folder. The files to copy:

```
wiki/
├── SCHEMA.md                        # from templates/SCHEMA.md
├── index.md                         # from templates/index.md
├── log.md                           # from templates/log.md
├── MAINTENANCE_ROUTING.md           # from templates/MAINTENANCE_ROUTING.md
├── concepts/                        # empty, .gitkeep
├── experiments/                     # empty, .gitkeep
├── sources/                         # empty, .gitkeep
└── architecture/                    # empty, .gitkeep
```

`${SKILL_DIR}` here means the skill's installation directory. On this user's machine:
- User-global: `C:\Users\adam\.claude\skills\wiki-management\templates\`
- Plugin: derived from `${CLAUDE_PLUGIN_ROOT}/templates/`

**Read the template files first** with the Read tool (their actual content lives in this skill's `templates/` folder), then **Write** them into the project's `wiki/` paths. Do not paraphrase — copy faithfully; the SCHEMA.md content is itself the methodology reference.

### 2.3 Customize SCHEMA.md for the project (5 lines max)

After copying, edit one or two fields in the new `wiki/SCHEMA.md`:
- Project-name placeholder → actual name
- The "domain categories" example list → reflect the categories the user picked in §2.1

Do not rewrite SCHEMA.md — its rules are project-agnostic. Only swap names.

### 2.4 Seed `index.md` and `log.md`

In `index.md`, list each category with a one-line description so the user can see at a glance where things go.

In `log.md`, write the first entry:

```markdown
## [YYYY-MM-DD] bootstrap | wiki initialized

5-category skeleton from wiki-management skill. Categories: concepts, experiments, sources, architecture, log. Domain additions: <list or "none">.
```

### 2.5 Optional: project-specific CLAUDE.md pointer

If the project has a `CLAUDE.md`, append a one-paragraph pointer:

```markdown
## Wiki

This project has an LLM-maintained knowledge base at `wiki/`. See `wiki/SCHEMA.md` for the operating rules. Pages link with `[[name]]` (Obsidian-compatible). New material goes through Ingest (§3 of SCHEMA), queries start from `wiki/index.md`.
```

### 2.6 Hand off

Tell the user: *"Wiki is bootstrapped. You can now feed me material — articles, post-mortems, design notes, links — and I'll route them into the right pages. Try saying 'ingest this: <paste content>'."*

---

## 3. Ingest (when the user feeds new material)

Trigger phrases: "ingest this", "整理一下这份资料", "把这个加进 wiki", "记下来", "我刚发现 X — 怎么记录?"

### 3.1 The 5-step Ingest flow

1. **Classify**: Which category does the material primarily belong to? (concept / experiment / source / architecture, or a domain category). If unclear, ask the user.
2. **Locate or create the host page**:
   - If a page already exists for this topic → update it in place
   - If not → create a new page using the appropriate template (`templates/page_types/*.md`)
3. **Cross-reference**: Walk the new page's content for entity mentions. For each entity mentioned that has (or could have) a page elsewhere, insert `[[link]]`. If the target page doesn't exist yet, still write `[[link]]` — it's a TODO marker.
4. **Update neighbors**: For each `[[link]]` you added, **also add a back-reference** in the target page (under a `## Referenced by` section if conventions allow). Cross-reference is bi-directional in this system.
5. **Index + log**: Add the new/updated page to `wiki/index.md` under its category. Add one line to `wiki/log.md` at the top:
   ```markdown
   ## [YYYY-MM-DD] ingest | <short description> → <page-path>
   ```

### 3.2 Decision: new page vs append to existing?

Default to **append to existing** if a page on the topic exists. Reasons to create a new page instead:
- The new material is a self-contained experiment / event (date-stamped) → new `experiments/*.md`
- The existing page has grown past ~300 lines → consider splitting
- The new material defines a new concept that will be referenced by multiple other pages → new `concepts/*.md`

### 3.3 Marking uncertainty

When the user feeds material whose conclusion is preliminary, add a status field at the top of the page:

```markdown
**Status**: tentative — verified once on 2026-05-26, needs sample-out validation
```

Refresh this when the user confirms or disconfirms.

---

## 4. Query (when the user asks a question)

Trigger phrases: any project-domain question, but especially "wiki 里有没有 X", "我们之前对 X 的结论是?", "查一下 wiki", "what did we conclude about Y?"

### 4.1 The query flow

1. **Read `wiki/index.md` first.** Always. It is the entry point. Even if you think you know where the answer lives, the index is authoritative on page locations.
2. **Read the candidate pages.** Pull the 2-4 most relevant pages identified from the index. Read fully, not just the headings.
3. **Synthesize an answer**, citing pages explicitly: *"per [[concepts/error-handling]] §2.3 and [[experiments/auth-refactor-2026-05]]..."*
4. **If the synthesis produces a new insight** that doesn't currently live in any page, propose to ingest it as a new entry — but ask the user first, since you might be over-generalizing.

### 4.2 When wiki content conflicts with current code/reality

Wiki is a **snapshot in time**. If the user is asking about *current* state (e.g. "what does function X do now?"), prefer reading code over recalling wiki. Use wiki for *why* and *historical*, code for *what is true now*.

If you spot drift (wiki says X but code now does Y), call it out: *"Wiki [[architecture/auth]] says X, but `auth/middleware.ts:42` now does Y. Should I update the wiki?"*

---

## 5. Lint (health check, periodic or on-demand)

Trigger phrases: "lint wiki", "wiki 体检", "check the wiki", "整理一下知识库".

### 5.1 The lint checklist

Walk these in order:

1. **Orphan pages**: pages with no `[[]]` references pointing in. Either link them from a reasonable parent page, or delete them as obsolete.
2. **Dangling references**: `[[link]]` targets that have no corresponding page. Either create the page or remove the link.
3. **Stale status**: pages with `Status: tentative` older than 60 days. Ask the user to confirm or downgrade.
4. **L1/L2/L3 violations**: any L2 page that was hand-edited (compare to last script run), any L1 page touched by a human, any L3 page that was overwritten by a script.
5. **Duplicate facts**: the same number or claim appearing verbatim in 2+ pages — pick one as the source of truth, replace the others with a `[[link]]`.
6. **Index gaps**: pages on disk that are not listed in `wiki/index.md`.
7. **Log gaps**: significant recent commits (`git log --since=14.days`) touching `wiki/` not reflected in `log.md`.

Output a categorized report. Do **not** auto-fix; ask the user to triage.

### 5.2 When to suggest splitting a page

A page exceeding ~500 lines OR covering >2 distinct sub-topics should be split. Propose the split and the new file names to the user; do not split unilaterally.

---

## 6. Optional advanced: event-routing & dependency declarations

These two patterns are heavier and pay off only when:
- The project has **many** moving pieces (10+ scripts that produce wiki content automatically)
- Drift between source code and wiki has already been a recurring pain point

If neither applies, **skip this section** — basic Ingest/Query/Lint is enough.

### 6.1 Event-routing table (`MAINTENANCE_ROUTING.md`)

When the same kind of event ("ship a new version", "add a new factor", "fix a bug") consistently requires updating multiple files in lockstep, codify it as a routing table. Each row = one file; columns = which event triggers it, which layer, who updates it, and whether it's mandatory.

The bootstrap copies a minimal `templates/MAINTENANCE_ROUTING.md` with one example event. Expand as patterns emerge.

### 6.2 §5 frontmatter on skill files

If the project's own `.claude/skills/` contains skills that *consume* wiki pages or *produce* outputs into wiki, declare dependencies in skill frontmatter:

```yaml
---
name: my-skill
description: ...
consumes:
  - wiki/concepts/error-handling.md
  - some/code/file.py
produces:
  - wiki/experiments/*.md
load_bearing_for:
  - .claude/skills/other-skill/skill.md
---
```

The skill's `templates/SCHEMA.md` describes the full convention in §5. This system is **opt-in** — only adopt it when manual back-reference tracking starts failing.

---

## 7. Anti-patterns to avoid

1. **"I'll just write a quick note"** — drives orphan pages. Always pick a category and link from `index.md`.
2. **Pasting raw content** — you are the curator, not a copy-paste machine. Summarize, extract key points, then link to the source.
3. **Mixing L1 / L2 / L3** — never put a number directly into a narrative page if that number lives in an L1 ledger. Link instead.
4. **Asking the user to write the page** — wiki is LLM-maintained. The user gives raw material; you produce the page. They review.
5. **Letting `log.md` grow unstructured** — one line per event, reverse chronological, no exceptions. If something needs more than a sentence, that something belongs in `experiments/` or `concepts/`.

---

## 8. Quick reference card

| Situation | What to do |
|---|---|
| User starts a session with no `wiki/` | §2 Bootstrap |
| User feeds new material | §3 Ingest — classify, host page, cross-ref, neighbors, index, log |
| User asks a project question | §4 Query — read `index.md` first, then candidate pages, cite sources |
| User asks for cleanup | §5 Lint — 7-item checklist, report, don't auto-fix |
| User has 10+ scripts producing wiki content | §6 Advanced: routing table + skill frontmatter |
| User asks a question whose answer is in code | Read code (current state), cite wiki only for *why* / history |

---

## 9. Hand-off to user

When the user invokes this skill, your first reply should:
1. State whether you're going to Bootstrap, Ingest, Query, or Lint (one sentence)
2. Confirm any project-specific details needed (one focused question max, only if truly needed)
3. Begin

Avoid laundry-list explanations of the methodology — the user invoked the skill, that's commitment enough. Show value through action, not exposition.
