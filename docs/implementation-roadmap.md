# Implementation Roadmap: Epiphany

## Purpose

This document turns [implementation-spec.md](implementation-spec.md) into an incremental build plan.

The goal is to implement the system in small vertical slices so that:

- each milestone produces something testable,
- the user can review real artifacts before more complexity is added,
- later milestones build on proven mechanics instead of assumptions.

This roadmap is intentionally execution-focused. It does not replace the product or implementation specs.

## Working Style

Implementation should follow these rules:

- build one vertical slice at a time,
- keep agent-authored semantic work separate from Python structural tooling,
- prefer end-to-end usable increments over isolated internal plumbing,
- pause for review after each milestone,
- update the spec only when implementation reveals a real gap or contradiction.

## Milestone Sequence

## Milestone 1: Bootstrap The Workspace

Goal:

- create the workspace structure defined in the implementation spec,
- make the workspace safe to use in a Git repository,
- seed the minimum generated files needed for later workflows.

Scope:

- `skills/shared/python/notes_workspace/` package skeleton
- `skills/shared/scripts/bootstrap_workspace.py`
- workspace path resolution helpers
- directory creation for `memory/` and `.notes-runtime/`
- `.gitignore` handling for `.notes-runtime/`
- seeded generated files:
  - `memory/README.md`
  - `memory/views/open-threads.md`
  - `memory/views/imports.md`
  - `memory/views/action-items.md`
  - `memory/views/pending-distillation.md`
  - `memory/topics/index.md`

Acceptance criteria:

- bootstrap can create a valid empty workspace from a clean repository root,
- rerunning bootstrap does not corrupt existing note state,
- seeded files match the required frontmatter and section structure from the implementation spec,
- `.notes-runtime/` is not tracked in Git-backed workspaces.

Review gate:

- inspect generated directory structure,
- inspect one seeded file of each class,
- confirm the empty workspace feels understandable.

## Milestone 2: Capture A Thread End To End

Goal:

- support real note capture into one thread,
- maintain thread-local rolling state,
- update the open-thread view.

Scope:

- `skills/capturing-notes/scripts/capture_note.py`
- `skills/capturing-notes/scripts/sync_thread_state.py`
- `skills/capturing-notes/scripts/thread_status.py`
- thread file creation and append behavior
- snippet IDs and timestamps
- thread frontmatter transitions
- `memory/views/open-threads.md` rebuild logic

Behavioral model:

- Python appends raw snippets and updates structure,
- the agent edits thread-local summary/open-question/candidate-action prose directly,
- Python performs the lightweight structural sync afterward without inventing content.

Acceptance criteria:

- a new note can create a thread,
- later notes can append to the same thread,
- thread summaries, open questions, candidate action items, and preview fields update correctly,
- stale-open and ambiguous-thread selection rules can be exercised manually,
- `open-threads.md` stays consistent with thread state.

Review gate:

- inspect one realistic thread file after several captures,
- inspect `open-threads.md`,
- test a case that should create a new thread and a case that should reuse one.

## Milestone 3: Basic Retrieval

Goal:

- answer simple cited questions without deep distillation,
- validate the progressive-disclosure retrieval model.

Scope:

- `skills/querying-notes/scripts/query_memory.py`
- initial retrieval-oriented shared helpers
- use of `memory/README.md`, `memory/views/`, and topic indexes as the primary search surfaces
- citation formatting in answers and derived documents

Acceptance criteria:

- the agent can answer a simple thread-backed question with citations,
- retrieval starts at top-level navigation rather than opening raw threads first,
- coarse retrieval returns useful candidate paths and excerpts for agent synthesis,
- the system can warn when relevant pending distillation exists.

Review gate:

- test 3-5 realistic questions,
- inspect whether citations point to evidence anchors instead of summaries,
- verify the retrieval flow is context-efficient.

## Milestone 4: Canonical Action Items

Goal:

- create and maintain durable task and open-question records,
- generate a useful operational action-item view.

Scope:

- action-item upsert logic in shared Python
- `skills/querying-notes/scripts/list_action_items.py`
- canonical action-item file creation and update behavior
- `memory/views/action-items.md`
- linkage between threads and action items

Acceptance criteria:

- explicit tasks become canonical action-item files,
- explicit open questions become canonical action-item files,
- action items can be filtered by owner/topic/entity/status/time/source,
- action-item view reflects the underlying records reliably,
- tentative vs explicit state is preserved.

Review gate:

- inspect one task record and one open-question record,
- inspect `action-items.md`,
- test one question that should be tracked as a blocker rather than a task.

## Milestone 5: Deep Distillation For Threads

Goal:

- bubble thread knowledge into canonical topics and action items,
- make pending/recovery state real and durable.

Scope:

- `skills/distilling-threads/scripts/apply_distillation_result.py`
- `skills/distilling-threads/scripts/resume_pending.py`
- topic upsert application logic for agent-authored distillation results
- change-history and freshness updates
- pending state transitions
- `memory/views/pending-distillation.md`
- rebuild of topic indexes after topic mutation
- explicit close-thread flow including Git-aware commit prompt

Acceptance criteria:

- deep distillation can update existing topics,
- deep distillation can create a new topic when allowed by the rules,
- deep distillation may run without closing a thread,
- blocked distillation leaves durable pending state and recovery notes,
- close-thread flow moves threads only after successful deep distillation,
- Git-aware commit prompt appears only in the explicit close-thread case and only in Git workspaces.

Review gate:

- inspect one topic created from real thread material,
- inspect a change-history entry,
- inspect `pending-distillation.md`,
- test one unresolved contradiction case.

Implementation note:

- the agent performs the semantic review, decides topic/action-item updates, and writes or prepares the natural-language changes,
- the scripts in this milestone only apply those already-decided changes, update state markers, and rebuild generated views.

## Milestone 6: Document Ingestion

Goal:

- import external documents as evidence,
- create normalized text,
- reuse the same distillation path used for threads.

Scope:

- `skills/ingesting-documents/scripts/ingest_document.py`
- `skills/ingesting-documents/scripts/sync_import_state.py`
- import file copy/register behavior
- normalized text generation for v1 formats
- import record creation
- `memory/views/imports.md`
- immediate deep-distillation handoff by default

Acceptance criteria:

- a supported document can be ingested into the workspace,
- the original file is preserved,
- normalized text is generated with stable chunk anchors,
- the import record summary is navigational rather than exhaustive,
- import distillation can update topics and action items,
- import view reflects state transitions.

Review gate:

- inspect one imported file, one normalized text file, and one import record,
- test retrieval that cites imported evidence,
- confirm the workflow does not require loading the full document into context.

Implementation note:

- the agent owns the source summary, candidate-topic interpretation, and candidate action-item interpretation,
- the scripts in this milestone only stage files, create normalized text, and perform structural follow-up after already-authored import-record updates.

## Milestone 7: Recovery And Concurrency Hardening

Goal:

- make interrupted workflows safe and resumable,
- reduce concurrent mutation conflicts between sessions.

Scope:

- lock acquisition/release behavior
- recovery batch behavior
- idempotency review for state-changing scripts
- failure-path testing for partial updates

Acceptance criteria:

- a partial distillation leaves the workspace recoverable,
- recovery can continue without duplicating topics or action items,
- conflicting concurrent mutations are blocked cleanly,
- pending views and source records remain internally consistent after failures.

Review gate:

- simulate one interrupted distillation,
- simulate one lock conflict,
- inspect resulting source records and pending views.

## Milestone 8: Skill Authoring And Evals

Goal:

- turn the working mechanics into high-quality portable skills,
- verify skill triggering and workflow quality.

Scope:

- `SKILL.md` files for all four user-facing skills
- shared references and required skill-local references
- `compatibility` metadata
- script help output cleanup
- eval fixtures and trigger-query sets
- end-to-end workflow evals

Acceptance criteria:

- each skill satisfies the implementation spec's skill-authoring rules,
- each skill has trigger evals and workflow evals,
- descriptions trigger reliably on intended prompts and avoid near-miss false positives,
- skills remain concise and push detail into references.

Review gate:

- review each `SKILL.md`,
- inspect one eval file per skill,
- run a small manual trigger sanity check.

## Recommended Immediate Next Step

Start with Milestone 1 and Milestone 2 together.

Reason:

- they create the first usable end-to-end loop quickly,
- they validate the most important structural choices,
- they give the user concrete artifacts to review before retrieval and distillation complexity is added.

The first implementation batch should therefore produce:

- shared Python package skeleton,
- bootstrap script,
- capture-note script,
- sync-thread-state script,
- thread-status script,
- initial generated view rebuild for `open-threads.md`.

## Suggested Review Rhythm

After each milestone:

1. inspect the resulting files directly,
2. run 2-3 realistic scenarios,
3. record any spec mismatches or awkward workflows,
4. patch the spec only if the implementation exposed a real design issue,
5. then move to the next milestone.

This keeps the user involved in the build without forcing all design decisions to be revisited from scratch each time.
