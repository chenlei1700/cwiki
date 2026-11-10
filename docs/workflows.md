# Workflows in practice — lookup & update, by scenario

> [中文（默认）](workflows.zh.md) | English - kept in sync; English is canonical where wording differs.

The rulebook ([SCHEMA](../templates/SCHEMA.md)) says what is *legal*; this file
says how things actually *run*. Each scenario gives four things: **what you say →
the steps the LLM walks → which files move → ⭐ where a capability unique to
cwiki does the work** (⭐ marks steps that higher-starred general tools don't
have — comparison in [README "Why cwiki"](../README.en.md#why-cwiki)).

## Scenario index

| # | You want to | Jump |
|---|---|---|
| Q1 | Look up a past conclusion: "what did we conclude about X?" | [↓](#q1-look-up-a-past-conclusion) |
| Q2 | Check current state: "which version runs now / what is the config?" | [↓](#q2-check-current-state) |
| Q3 | Pull everything about a topic | [↓](#q3-pull-everything-about-a-topic) |
| Q4 | Check before exploring: "did we already try this?" | [↓](#q4-check-before-exploring) |
| U1 | Feed new material into the wiki | [↓](#u1-feed-new-material-ingest) |
| U2 | Close out an experiment / incident | [↓](#u2-close-out-an-experiment) |
| U3 | New evidence contradicts an existing conclusion | [↓](#u3-new-evidence-contradicts-an-existing-conclusion) |
| U4 | Correct a wrong conclusion | [↓](#u4-correct-a-wrong-conclusion) |
| U5 | Ship/release-type multi-file events | [↓](#u5-releasetype-multi-file-events) |
| U6 | Record a lesson in CLAUDE.md | [↓](#u6-record-a-lesson-in-claudemd) |
| U7 | Supersede or delete a page | [↓](#u7-supersede-or-delete-a-page) |
| U8 | Handle a red nightly check | [↓](#u8-handle-a-red-nightly-check) |

---

## Lookup

### Q1 Look up a past conclusion

**You say**: `what did we conclude about X?` / `wiki 里有没有 X`

1. The LLM **reads `wiki/index.md` first** (always starts at the index, never
   jumps to a page from memory — the index is authoritative on page locations).
2. Reads 2–4 candidate pages in full (not just headings).
3. Answers with citations: *"per [[concepts/xxx]] §2 and [[experiments/yyy_20260520]]…"*.
4. ⭐ If the answer load-bearing depends on an artifact, the page's `sources:`
   fingerprints (SCHEMA §15.1) tell you whether that evidence **still holds
   today** — the nightly check reports intact / changed / missing per entry. A
   page whose conclusion stands but whose evidence changed gets *named*, not
   silently cited as current truth.
5. If the synthesis yields a new insight, the LLM proposes an ingest (never
   writes it unilaterally).

### Q2 Check current state

**You say**: `which version is shipped?` / `what is the current config?`

1. ⭐ **Derived views first** (`_current_*` files) — answering this question is
   their entire job, and they are regenerated nightly from L1 ledgers; hand
   edits can't get in.
2. No derived view → resolve by the ⭐ **fixed newest-truth ordering**
   (SCHEMA §15.3), never by vibes: filename semantics (`_current_*` vs
   date-stamped history) → tombstone/supersedes declarations → last resort
   `git log -1`. **Never mtime** (sync scripts and checkouts rewrite it
   meaninglessly).
3. Asking about *code* ("what does function X do now") → read the code; the
   wiki supplies *why* and history. Drift spotted between wiki and code →
   called out, with an offer to update the wiki.

### Q3 Pull everything about a topic

**You say**: `where does topic X stand?` (requires the topic layer, SCHEMA §16)

1. Resolve the name/alias in `wiki/_topics.json`.
2. ⭐ **The five-column view is derived on the spot** (never stored — a stored
   copy is a second thing that drifts): ① content pages ② current progress
   (read through anchored ledgers/derived views) ③ change history (log entries
   matching the topic) ④ related sessions ⑤ related code roots.
3. This is the single entry point for "mention a topic → locate content,
   progress, history, sessions, code" — without the topic layer that answer is
   smeared across ten places.

### Q4 Check before exploring

**You say**: `let's try direction Y` (first step of any exploration-type work)

1. ⭐ **Query the hypothesis ledger first** (`hypothesis_history.jsonl`,
   Mechanism 2): any `fail` rows on this theme? What was the failure
   *reason* — "closed because unmeasurable" and "closed because it doesn't
   work" lead to opposite decisions, and the ledger keeps them distinct.
2. ⭐ Direction-level closures are structured `action: close` records — so "no
   record found" genuinely means never tried, not "tried, but the verdict
   lives in prose no tool can see".
3. Only then start; close out via [U2](#u2-close-out-an-experiment). This is
   the highest-ROI habit in the whole system.

---

## Update

### U1 Feed new material (ingest)

**You say**: `ingest this: <material>` / `把这个加进 wiki`

1. Classify (concept / experiment / source / architecture / domain dir); ask
   once if unclear.
2. Locate or create the host page — default is **append** to an existing page;
   create new only for a self-contained dated event, a page past ~300 lines,
   or a new concept multiple pages will reference.
3. ⭐ New pages pass a **preflight near-duplicate search** (title similarity
   against existing page names), recorded as `similar_checked:` in
   frontmatter — stops near-duplicate pages accumulating chronically.
4. Add `[[cross-references]]`, **bi-directionally**: adding `[[X]]` in page A
   means page X gets a back-reference.
5. Entry in `index.md` + one classified line at the top of `log.md`.
6. Preliminary conclusions get `Status: tentative` — tentatives older than 60
   days are named by lint.

### U2 Close out an experiment

**After an experiment / incident**:

1. Create `experiments/<topic>_YYYYMMDD.md` (a frozen, dated historical event),
   one-line conclusion at the top.
2. ⭐ Pin load-bearing artifacts with `sources:` fingerprints (result JSON
   sha256 / code-state commit — the two grades never mix).
3. ⭐ **Append** a hypothesis-ledger row: hypothesis, what changed, result,
   failure reason, lesson links. **Losing experiments get recorded too** —
   that's what makes Q4 answerable.
4. Update affected concepts pages (walk the cross-reference graph); one log line.

### U3 New evidence contradicts an existing conclusion

**Found**: new data/experiment conflicts with a page's current conclusion.

1. ⭐ **Do not touch the body.** The contradiction lands first in the page's
   *Open contradictions* section with pointers to **both** sides' evidence
   (SCHEMA §14).
2. Only after adjudication (human decision, or more evidence) does the body
   change; the resolved entry moves to *Evolution trail*.
3. ⭐ Merging two conflicting conclusions keeps **both claims** with the
   disagreement stated — "last writer wins" is forbidden because it destroys
   the information that a disagreement ever existed.

### U4 Correct a wrong conclusion

**Found**: a page (or ledger row) carries a wrong conclusion.

1. Page: fix the body + add an *Evolution trail* line + ⭐ go back to the
   **original text** and add a `⛔ superseded → see [date]` back-mark — whoever
   reads the old passage later learns on the spot that it's void, instead of
   discovering it elsewhere afterwards.
2. Ledger row: ⭐ **never edit in place** — append a superseding row, or write
   an overlay record (with `invalidated_by` and the reason). N tools read the
   ledger; in-place edits silently desynchronize all of them.
3. If the correction touches a CLAUDE.md lesson line, update that pointer too.

### U5 Release-type multi-file events

**To do**: ship / deploy / config change — the kind of event that touches the
same group of files every time and always misses a step.

1. Open `MAINTENANCE_ROUTING.md`, find the event row, walk the **numbered
   checklist in strict order**.
2. ⭐ Each row carries two columns no general tool has: **symptom-if-skipped**
   (turns the table into a reverse diagnostic index — weird behavior? look up
   the symptom to find the missed step) and **backstop** (which automated check
   catches the omission — and which rows have *no* net, so extra care there).
3. Every such event ends with: **restart the long-lived processes** —
   "configured ≠ in effect"; workers/servers lock config at startup.
4. A next-day verification step confirms the change is actually live; append a
   release-ledger row.

### U6 Record a lesson in CLAUDE.md

**End of session, something worth keeping**:

1. The lesson's **facts** go into the wiki (an experiments or concepts page —
   tier T1/T2).
2. CLAUDE.md gets **one line + a pointer**: `- [date] one-line conclusion → source: [link]`.
3. ⭐ Writing long gets caught: the **entry-form gate** (SCHEMA §13.4) names
   new entries over ~800B, or over ~500B with no link, the next morning — a
   mis-tiered 3KB war story doesn't get to hide until the total budget bursts.
4. Total approaching the budget line → run the
   [distillation SOP](maintenance-mechanisms.md#mechanism-7--the-distillation-loop-context-budget)
   (interactive, with the spot-check read-back human gate).

### U7 Supersede or delete a page

**To do**: a new page replaces an old one, or a page should go.

1. Supersede: new page declares `supersedes: [old-path]` in frontmatter;
   ⭐ the old page **must** get a tombstone banner on top
   (`> **DEPRECATED** → see [[new-page]]`) — declared but unmarked = red
   nightly check.
2. Delete: register the path in `wiki/_tombstones.json` (date, reason,
   successor).
3. ⭐ **Resurrection detection**: whichever generator doesn't know about the
   tombstone and emits the dead page again gets caught the next night. The
   registry has teeth even for generators that never integrated it — that's
   what "tombstones are detection-type enforcement" means.
4. Repoint other pages' `[[links]]` to the successor while you're there.

### U8 Handle a red nightly check

**Nightly lint / drift detector exited 1**:

1. ⭐ The report is **evidence, not booleans**: every violation names the file,
   the problem, and the fix action — work through it line by line; there is no
   "3 violations, now what".
2. Fix, re-run that check, confirm green.
3. ⭐ If the red was the **check's own fault** (false positive): after fixing
   the judgment, run its `--selftest` and **add a fault injection** for the
   new failure mode — guard the guards; whoever breaks a judgment should get a
   red test, not a quietly green night.
4. Deciding *not* to fix a violation (accepting the state) → one log line with
   the decision and reason — don't let it nag nightly and train people to
   ignore the report.
