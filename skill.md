---
name: wiki-management
description: LLM-maintained project knowledge base methodology. Provides 3-layer data model (SSOT / Derived / Narrative), event-routing maintenance table, [[name]] cross-references, Ingest/Query/Lint operations, and the sync/drift/enforcement mechanisms that keep the wiki alive at scale. Use when user says "set up a wiki", "建立知识库", "项目文档体系", "bootstrap wiki", "adopt wiki", "把 wiki 方法论用到现有项目", "整理现有文档", "ingest 资料到 wiki", "query 知识库", "lint wiki", "整理项目知识", or wants to apply LLM-maintained knowledge base methodology to a new OR existing project. Fresh project → Bootstrap (§2); existing project with scattered docs → Adoption (§2B); existing wiki → daily Ingest/Query/Lint workflows.
---

# wiki-management — LLM-maintained knowledge base methodology

You are the curator of a project's `wiki/` knowledge base. **Humans feed material and make decisions. You organize, archive, cross-link, and keep things consistent.**

This skill is **project-agnostic**: the methodology applies equally to a quant trading project, a SaaS codebase, a research lab notebook, or a personal lab. The templates in `templates/` give you a generic 5-category bootstrap; you extend with domain categories as needed. The companion `docs/maintenance-mechanisms.md` describes the automation that keeps a wiki alive over months; `tools/` holds reference implementations.

---

## 0. Trigger & first-step decision

Triggered when the user says any of: "建立 wiki / 知识库", "bootstrap wiki", "set up project wiki", "adopt wiki", "把 wiki 方法论用到现有项目", "整理项目知识", "ingest <material>", "query wiki", "lint wiki", "wiki 体检", or asks how to apply this methodology to their project.

**First action — detect state** (two probes, not one):

```bash
ls wiki/SCHEMA.md                      # exists → wiki already operating
ls README.md docs/ CLAUDE.md 2>/dev/null   # any hits → project has existing knowledge
```

Branch — three cases, not two:
- `wiki/SCHEMA.md` exists → **§3 Ingest / §4 Query / §5 Lint** based on user intent
- No SCHEMA, and the project is **fresh** (little/no existing docs, no accumulated CLAUDE.md, no machine artifacts) → **§2 Bootstrap**
- No SCHEMA, but the project **already has knowledge** — a grown README, a `docs/` folder, a CLAUDE.md fat with dated lessons, machine-produced artifacts/ledgers → **§2B Adoption**. Do *not* run bare Bootstrap here: a skeleton dropped next to an existing knowledge mess just becomes one more place to look.

---

## 1. Core philosophy (read once, internalize)

### 1.1 Three-layer data model

Every file in `wiki/` belongs to exactly **one** of these layers. The layer determines who is allowed to modify it.

| Layer | Definition | Who writes | Examples |
|---|---|---|---|
| **L1 SSOT** | Machine-generated raw truth. Single source. | Scripts / external systems. **Humans and LLMs must NOT hand-edit.** | Backtest JSON output, append-only ledgers (`release_history.jsonl`), runtime config files |
| **L2 Derived View** | Auto-generated *view* of L1 data. | A sync script reads L1 and rewrites L2. **Humans and LLMs must NOT hand-edit.** | A markdown summary of "current production state" generated from a JSON ledger |
| **L3 Narrative** | Stories, lessons, methodology, free-form analysis. | Humans and LLMs hand-write. **Scripts must NOT overwrite.** | `experiments/*.md`, `concepts/*.md`, `log.md` |

**The one rule that prevents 90% of drift**: the same fact lives in **exactly one place — in L1**. L2 and L3 *reference* L1 by link, they do not *copy* its content. If you find yourself about to write a number into a narrative page that already exists in an L1 ledger, instead write a link `see [release summary](../../build/v3/summary.json)`. This applies to `CLAUDE.md` and `README.md` too — they link to the derived view, never carry its numbers.

Within L1, two sub-kinds get extra rules once they appear (full spec: templates/SCHEMA.md §3):
- **Append-only ledgers**: history is immutable — corrections are superseding rows or overlay records, never in-place edits.
- **Rebuildable derived data** (observability JSON etc.): gitignored, never linked to as truth.

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

### 1.6 Status is structured, not prose

Anything a future tool or session must *act on* — closed, deprecated, superseded, invalid — must be a structured marker (frontmatter field, ledger column, overlay key) that consumers actually read. A prose note inside a registry or docstring ("this direction was abandoned") is an assertion nobody re-checks: it goes stale silently, and coverage tools can't see it, so the direction eventually gets reported as "never tried" and expensively re-explored.

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
├── ONBOARDING.md                    # from templates/ONBOARDING.md (optional but cheap)
├── concepts/                        # empty, .gitkeep
├── experiments/                     # empty, .gitkeep
├── sources/                         # empty, .gitkeep
└── architecture/                    # empty, .gitkeep
```

`${SKILL_DIR}` here means the skill's installation directory (user-global `~/.claude/skills/wiki-management/templates/`, or `${CLAUDE_PLUGIN_ROOT}/templates/` for a plugin install).

**Read the template files first** with the Read tool (their actual content lives in this skill's `templates/` folder), then **Write** them into the project's `wiki/` paths. Do not paraphrase — copy faithfully; the SCHEMA.md content is itself the methodology reference.

### 2.3 Customize SCHEMA.md for the project (5 lines max)

After copying, edit one or two fields in the new `wiki/SCHEMA.md`:
- Project-name placeholder → actual name
- The "domain categories" example list → reflect the categories the user picked in §2.1

Do not rewrite SCHEMA.md — its rules are project-agnostic. Only swap names. The scale sections (§9–§12) stay dormant until their trigger conditions are met.

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

## 2B. Adoption (for projects that already have knowledge)

Same install, different first motion. Bootstrap creates an empty home; adoption has to make a home *next to* a lived-in mess without pretending the mess isn't there. The cardinal rule: **coexist first, migrate incrementally, gate only the new** — a big-bang rewrite of existing docs into wiki format loses fidelity and stalls halfway, which is worse than never starting.

### 2B.1 Inventory (read-only, before creating anything)

Walk the project and list every knowledge carrier with its future layer and injection tier:

| Carrier | Typical classification | Adoption action |
|---|---|---|
| `README.md`, `docs/*.md` | L3 narrative (some are really L2 "current state" views) | stays put for now; facts migrate on touch |
| `CLAUDE.md` with accumulated dated lessons | T3 always-loaded carrying T1 content | becomes the first distillation target (§13) |
| Machine artifacts / ledgers / JSON outputs | L1 | **never move them** — producers break; declare them L1 where they live and link from wiki |
| Scattered notes, issue threads, chat exports | raw material | migration queue |
| Assistant private memory (if any) | unique facts at risk | Mechanism 8 queue |

Produce a one-page **adoption map** from this inventory and confirm it with the user in one question: which domain categories to create, and what is explicitly *not* worth migrating. Then proceed.

### 2B.2 Stand up the skeleton alongside

Run §2.2–§2.5 as-is (SCHEMA, index, log, routing, onboarding). Nothing existing moves. Two adoption-specific touches:

- Record the **adoption date as the project's cutoff date** in SCHEMA — every non-retroactive gate (entry form §13.4, log classes, new-page preflight) keys off it.
- First log entry uses class `adopt`, listing the adoption map so future sessions know what was deliberately left in place.

### 2B.3 Migrate incrementally, two lanes

- **Migrate-on-touch** (primary): the next time real work needs a legacy doc, route its facts into the wiki *then* — the work provides the context that makes the migration faithful.
- **Migration queue** (backlog): a small JSON tracker (file, bytes, status) worked in small batches. Small files can be automated with the Mechanism 8 headless driver (mechanical acceptance, fidelity floor, rollback); large or load-bearing docs stay interactive — quality over throughput.

Either lane ends the same way: the legacy location keeps a one-line pointer to the new page (so stale links keep working), and the queue/ledger records the move.

### 2B.4 Gates come last, and only the triggered ones

Wire mechanisms strictly by their adopt-when triggers (§6 / SCHEMA §9–§16). On day one of an adoption, usually only two are justified: the budget + entry-form gate on the fat always-loaded doc (its pain is why you're adopting), and the nightly lint skeleton in report-only mode for a week before giving it exit codes. Everything else waits for its trigger. Gating the legacy backlog on day one kills adoption — the same grace-period principle §9 applies to skills applies to the whole project here.

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
8. **Prose-only status** (if §1.6 markers are adopted): deprecation/closure recorded only as prose, with no structured marker a tool can read.

Output a categorized report. Do **not** auto-fix; ask the user to triage.

### 5.2 When to suggest splitting a page

A page exceeding ~500 lines OR covering >2 distinct sub-topics should be split. Propose the split and the new file names to the user; do not split unilaterally.

---

## 6. Scale features: event routing, enforcement, ledgers, generated pages

These patterns are heavier and pay off only when their trigger conditions are met. If none applies, **skip this section** — basic Ingest/Query/Lint is enough. Full specs live in templates/SCHEMA.md §9–§16; the operating machinery is documented in `docs/maintenance-mechanisms.md` with reference implementations in `tools/`.

### 6.1 Event-routing table (`MAINTENANCE_ROUTING.md`)

**Adopt when**: the same kind of event ("ship a new version", "add a data source", "fix a bug") keeps requiring updates to the same group of files, and steps keep getting missed.

Each row = one file; columns = event, layer, how to update, mandatory?. As the table matures, add two more columns per the template: **Symptom if skipped** (turns the table into a reverse diagnostic index) and **Backstop** (which automated check catches the omission — and which rows have no net).

Multi-step events (releases, migrations) additionally get: a **numbered checklist in strict order**, an **automatic safety-nets block** (backstops, not replacements), and a final **restart-the-long-lived-processes** step — configuration is not "in effect" until the process that loaded the old config restarts.

### 6.2 Dependency frontmatter + enforcement layers

**Adopt when**: 10+ skills/scripts read or write wiki content and "changed X, forgot Y" has bitten twice.

Executable docs declare `consumes / produces / upstream_skills / downstream_skills / load_bearing_for` in frontmatter (spec: SCHEMA §9). Three cost-controls: declare load-bearing only; one-way declarations (reverse views are script-derived); frontmatter is the SSOT, derived tables are DO-NOT-EDIT.

A written rule alone decays — enforcement is four-layered, each backstopping the last:
A (the written rule) → B (PostToolUse hook prints a draft the instant a skill is created; `tools/scan_skill_dependencies.py`) → C (Stop hook blocks session end for unregistered *new* skills; `tools/check_new_skills_registered.py`) → D (nightly drift detector; `tools/check_dependency_drift.py`).

### 6.3 Append-only ledgers + query-before-explore

**Adopt when**: "didn't we already try this?" has no provable answer.

Keep `release_history.jsonl` (what shipped) and `hypothesis_history.jsonl` (**every** exploration — hypothesis, result, failure reason). Rules: append-only, corrections by superseding row or overlay key (never in-place edits); every exploration-type workflow **queries the ledger before starting**; record *why* something was closed, not just that it was (SCHEMA §10).

### 6.4 Generated wiki pages over machine data

**Adopt when**: conclusions that exist only in machine ledgers keep being invisible to humans.

Generators render summary pages into the wiki under three rules (SCHEMA §11): format derives from the wiki's existing page types; **regenerate-without-clobber** for hand-written sections; **self-disclosure** — a generated page states what its own emptiness means ("no records ≠ nobody tried").

### 6.5 Navigation layer

**Adopt when**: new sessions keep re-deriving context. Add `ONBOARDING.md` (template provided — starts with a copy-paste first-message block and an SSOT warning header), then `USAGE_MANUAL.md` (scenario → command) and `SKILL_ROUTING.md` (trigger → skill) as the pain appears (SCHEMA §12).

### 6.6 Context budget & distillation

**Adopt when**: an always-loaded doc (`CLAUDE.md` etc.) outgrows what the harness comfortably injects. Classify content by **injection tier** (always-loaded / scene-loaded / atomic / raw truth — orthogonal to L1/L2/L3), set explicit byte budgets with a nightly check, and run the distillation SOP interactively when over: cluster by theme → UPDATE>MERGE>CREATE into pages → two-mode retirement (pointer+archive, or synthesize-only for embedded fragments) → distill ledger → **spot-check read-back** (the non-mechanizable human gate). A per-entry form gate ("new dated entries = one line + pointer", non-retroactive cutoff) catches mis-tiered writes the next morning instead of months later (SCHEMA §13).

### 6.7 Contradiction structure

**Adopt when**: corrections overwrite history, or two sessions' conflicting conclusions resolve as "last writer wins". Synthesis pages carry fixed `Evolution trail` / `Open contradictions` sections; contradictions land there *before* the body changes; merges keep both claims; corrections back-mark the original (SCHEMA §14).

### 6.8 Freshness arbitration (fingerprints / supersedes / tombstones)

**Adopt when**: concurrent sessions make "which page is current?" unanswerable. Pages declare load-bearing evidence in `sources:` frontmatter (artifact sha256 vs narrative-grade commit — two grades, never mixed; nightly 3-state check). Replacement declares `supersedes:` and the old page gets a tombstone banner; deleted pages enter a tombstone registry with **resurrection detection**. "Which is newest" follows a fixed ordering: derived view → filename semantics → tombstone/supersedes → `git log -1`; never mtime (SCHEMA §15).

### 6.9 Topic layer

**Adopt when**: "mention a topic → locate content / progress / history / sessions / code" has no single entry point. A small registry (`_topics.json`: name/aliases/status/anchors) is the only stored truth; the five-column answer is **derived at query time** by walking anchors. A `check-new` near-miss gate (topic-level fuzzy match) prevents duplicate topics; orphan pages get listed, not blocked (SCHEMA §16).

---

## 7. Anti-patterns to avoid

1. **"I'll just write a quick note"** — drives orphan pages. Always pick a category and link from `index.md`.
2. **Pasting raw content** — you are the curator, not a copy-paste machine. Summarize, extract key points, then link to the source.
3. **Mixing L1 / L2 / L3** — never put a number directly into a narrative page if that number lives in an L1 ledger. Link instead.
4. **Asking the user to write the page** — wiki is LLM-maintained. The user gives raw material; you produce the page. They review.
5. **Letting `log.md` grow unstructured** — one line per event, reverse chronological, no exceptions. If something needs more than a sentence, that something belongs in `experiments/` or `concepts/`.
6. **Status as prose** — "this is deprecated" written in a paragraph instead of a structured marker. Tools can't see prose; the direction gets re-explored later (§1.6).
7. **Editing ledger history** — fixing a wrong row in place desynchronizes every consumer. Append a superseding row or overlay record.
8. **A generator that clobbers human sections** — the second run wipes someone's verdict paragraph, and the pages stop being trusted. Regenerate-without-clobber or don't generate.

---

## 8. Quick reference card

| Situation | What to do |
|---|---|
| Fresh project, no `wiki/`, little existing doc | §2 Bootstrap |
| No `wiki/` but the project already has grown docs / fat CLAUDE.md / artifacts | §2B Adoption — inventory, coexist, migrate incrementally |
| User feeds new material | §3 Ingest — classify, host page, cross-ref, neighbors, index, log |
| User asks a project question | §4 Query — read `index.md` first, then candidate pages, cite sources |
| User asks for cleanup | §5 Lint — 8-item checklist, report, don't auto-fix |
| Same multi-file event keeps getting half-done | §6.1 routing table (+ symptom & backstop columns) |
| 10+ producers/consumers, drift has bitten | §6.2 frontmatter + 4-layer enforcement |
| "Didn't we try this already?" | §6.3 ledgers + query-before-explore |
| Machine conclusions invisible to humans | §6.4 generated pages (no-clobber, self-disclosing) |
| New sessions re-derive context every time | §6.5 ONBOARDING.md |
| `CLAUDE.md` / always-loaded docs keep growing | §6.6 budgets + distillation SOP + entry-form gate |
| Corrections overwrite history; "last writer wins" | §6.7 contradiction structure |
| Can't tell which of two pages is current | §6.8 fingerprints / supersedes / tombstones |
| "Topic X — where's everything about it?" | §6.9 topic layer (registry + derived view) |
| User asks a question whose answer is in code | Read code (current state), cite wiki only for *why* / history |

---

## 9. Hand-off to user

When the user invokes this skill, your first reply should:
1. State whether you're going to Bootstrap, Ingest, Query, or Lint (one sentence)
2. Confirm any project-specific details needed (one focused question max, only if truly needed)
3. Begin

Avoid laundry-list explanations of the methodology — the user invoked the skill, that's commitment enough. Show value through action, not exposition.
