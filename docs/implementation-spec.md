# Implementation Spec: Agentic Notes Workspace

## Table Of Contents

- [Purpose](#purpose)
- [Skill Authoring References](#skill-authoring-references)
- [Decisions Summary](#decisions-summary)
- [Deployment Model](#deployment-model)
- [Skill Package Layout](#skill-package-layout)
  - [Skill package directory intent](#skill-package-directory-intent)
- [Workspace Layout](#workspace-layout)
  - [Workspace directory intent](#workspace-directory-intent)
- [Common File Conventions](#common-file-conventions)
  - [Generated section markers](#generated-section-markers)
  - [Citation notation](#citation-notation)
- [Skills Layout](#skills-layout)
- [Skill Responsibilities](#skill-responsibilities)
  - [`capturing-notes`](#capturing-notes)
  - [`querying-notes`](#querying-notes)
  - [`distilling-threads`](#distilling-threads)
  - [`ingesting-documents`](#ingesting-documents)
- [Shared Code Reuse](#shared-code-reuse)
- [Agent-Script Boundary](#agent-script-boundary)
- [Script Command Surface](#script-command-surface)
  - [Common wrapper conventions](#common-wrapper-conventions)
  - [`capturing-notes/scripts/`](#capturing-notesscripts)
  - [`querying-notes/scripts/`](#querying-notesscripts)
  - [`distilling-threads/scripts/`](#distilling-threadsscripts)
  - [`ingesting-documents/scripts/`](#ingesting-documentsscripts)
  - [Shared view maintenance](#shared-view-maintenance)
  - [`shared/scripts/`](#sharedscripts)
  - [Update payload contracts](#update-payload-contracts)
- [Durable File Types](#durable-file-types)
  - [1. Workspace entrypoint](#1-workspace-entrypoint)
  - [2. Thread documents](#2-thread-documents)
  - [3. Import source files](#3-import-source-files)
  - [4. Normalized import text files](#4-normalized-import-text-files)
  - [5. Import records](#5-import-records)
  - [6. Topic documents](#6-topic-documents)
  - [7. Action-item documents](#7-action-item-documents)
  - [8. Generated view files](#8-generated-view-files)
- [Thread Lifecycle](#thread-lifecycle)
- [Thread Selection And Reopen Policy](#thread-selection-and-reopen-policy)
- [Lightweight Distillation](#lightweight-distillation)
- [Deep Distillation](#deep-distillation)
  - [Git-aware close-thread prompt](#git-aware-close-thread-prompt)
- [Interruption And Recovery](#interruption-and-recovery)
  - [Pending indicators](#pending-indicators)
  - [Recovery index](#recovery-index)
  - [Recovery behavior](#recovery-behavior)
  - [Concurrent-session protection](#concurrent-session-protection)
- [Retrieval Architecture](#retrieval-architecture)
  - [Topic](#topic)
  - [Time](#time)
  - [Entity](#entity)
- [Retrieval Workflow](#retrieval-workflow)
- [Topic Creation Rules](#topic-creation-rules)
- [Action-Item Rules](#action-item-rules)
  - [Creation](#creation)
  - [Confidence](#confidence)
  - [Close / resolution](#close--resolution)
- [Generated Views](#generated-views)
  - [View content rules](#view-content-rules)
  - [View update policy](#view-update-policy)
- [Manual Editing Rules](#manual-editing-rules)
- [Skill File Expectations](#skill-file-expectations)
  - [`SKILL.md` rules](#skillmd-rules)
  - [Shared references](#shared-references)
  - [Required skill-local references](#required-skill-local-references)
- [Evaluation And Testing](#evaluation-and-testing)
- [File Intent Summary](#file-intent-summary)
- [Non-Goals For V1](#non-goals-for-v1)

## Purpose

This document is the decision-complete implementation specification for the Agentic Notes Workspace defined in [product-spec.md](product-spec.md).

It defines:

- the repository layout,
- the `skills/` layout,
- the durable file formats,
- the thread and import lifecycles,
- the distillation and recovery mechanics,
- the retrieval model,
- the script command surface,
- the testing strategy.

An implementer should be able to create the full system from this document without making additional product-shaping decisions.

The central implementation rule is:

- agents perform semantic work,
- scripts perform structural work.

Semantic work includes summarization, retrieval reasoning, contradiction analysis, topic selection, and deciding how new information should update current understanding. Structural work includes file creation, timestamps, frontmatter maintenance, validation, moving files, applying agent-authored updates, and rebuilding generated views.

## Skill Authoring References

The implementation must follow the local reference material in [skill_references](skill_references).

These documents should be used as follows:

- [agentskills.io_skill_specification.md](skill_references/agentskills.io_skill_specification.md): authoritative format and packaging rules for `SKILL.md`, `scripts/`, `references/`, and `assets/`.
- [agentskills.io_skill_creator_best_practices.md](skill_references/agentskills.io_skill_creator_best_practices.md): workflow design and how to ground skills in real usage.
- [agentskills.io_skill_creator_optimizing_skill_descriptions.md](skill_references/agentskills.io_skill_creator_optimizing_skill_descriptions.md): how to write descriptions so the correct skill triggers reliably.
- [agentskills.io_using_scripts_in_skills.md](skill_references/agentskills.io_using_scripts_in_skills.md): script interface design and packaging guidance.
- [agentskills.io_evaluating_skills.md](skill_references/agentskills.io_evaluating_skills.md): eval structure and iterative quality testing.
- [agentskills.io_what_are_skills.md](skill_references/agentskills.io_what_are_skills.md) and [agentskills.io_overview.md](skill_references/agentskills.io_overview.md): conceptual background and progressive disclosure model.
- [claude_skills_overview.md](skill_references/claude_skills_overview.md) and [claud_skills_best_practices.md](skill_references/claud_skills_best_practices.md): practical authoring guidance on concise skills, structured references, and skill/test hygiene.

References to Claude or any other named agent in these files are not product constraints for this project. They should be treated as examples of a skill-capable agent environment unless a passage depends on a product-specific feature. This implementation remains agent-agnostic.

## Decisions Summary

The implementation will use these major decisions:

- The skill package and the user workspace are separate filesystem roots.
- The agent's working directory is the root of the user's note-taking workspace.
- The skill package is installed or made available to the agent, but does not own the workspace root.
- The workspace root contains `memory/` and any user-owned project files.
- The skill package contains `skills/` and shared Python code.
- All durable knowledge-state documents use Markdown with YAML frontmatter.
- Raw conversational evidence is stored in one thread document per thread.
- Thread files use the naming pattern `YYYY-MM-DD-<slug>.md`.
- The rolling thread summary lives inside the thread document, not in a separate file.
- Imported documents keep their original file format and extension, paired with a Markdown ingestion record.
- Imported documents get a normalized text representation for agent use when the original format is not already plain-text Markdown.
- Topics are one Markdown file per topic, stored under a fixed typed directory scheme.
- The initial topic-type set is fixed, but new custom top-level topic types may be added later with explicit user approval.
- Tasks and open questions share one canonical `action-item` record format and live as one Markdown file per item.
- Generated navigation and index pages live under `memory/views/` and typed topic index files.
- `memory/README.md` is a lightweight entrypoint and must not duplicate the detailed views.
- Lightweight distillation runs during capture and ingestion.
- Deep distillation is agent-led, may run with or without closing a thread, and performs a broader re-check of affected topics and action state.
- Recovery from interrupted distillation is explicit and file-backed.
- Shared code is reused through a shared Python package under `skills/shared/python/`; no symlinks are used.

## Deployment Model

This system is deployed as two separate filesystem contexts:

1. a skill repository or installed skill package that contains the reusable skills and Python code,
2. a user-owned note-taking workspace, usually an independent Git repository, whose root is the agent's working directory during use.

The implementation must assume:

- the note-taking workspace already exists or will be initialized by the user,
- the skill package may live outside the workspace,
- skill scripts operate on the current working directory as the workspace root unless a workspace path is explicitly provided,
- all durable note state lives in the user workspace, not in the skill repository.

The implementation may include a bootstrap script that creates the expected workspace structure inside the user's workspace.

If the workspace is a Git repository, the bootstrap process must ensure `.notes-runtime/` is ignored by Git, either by updating `.gitignore` or by giving the user an explicit follow-up instruction.

Because skill clients vary in how they execute bundled scripts, `SKILL.md` instructions should prefer passing `--workspace-root` explicitly whenever client behavior is ambiguous.

## Skill Package Layout

The skill package layout is fixed as follows:

```text
<skill-package-root>/
├── skills/
│   ├── capturing-notes/
│   ├── querying-notes/
│   ├── distilling-threads/
│   ├── ingesting-documents/
│   └── shared/
└── docs/
```

### Skill package directory intent

- `skills/`: skill packages, wrapper scripts, shared Python code, shared references, and evals.
- `docs/`: human-authored documentation for the skill package, including this spec.

## Workspace Layout

The user workspace layout is fixed as follows:

```text
<workspace-root>/
├── .notes-runtime/
│   └── locks/
├── memory/
│   ├── README.md
│   ├── threads/
│   │   ├── open/
│   │   └── closed/
│   ├── imports/
│   │   ├── files/
│   │   ├── text/
│   │   └── records/
│   ├── topics/
│   │   ├── index.md
│   │   ├── people/
│   │   ├── projects/
│   │   ├── customers/
│   │   ├── systems/
│   │   ├── classes/
│   │   ├── products/
│   │   ├── documents/
│   │   ├── places/
│   │   ├── concepts/
│   │   ├── custom/
│   │   └── other/
│   ├── action-items/
│   │   ├── open/
│   │   └── closed/
│   └── views/
└── <user-owned project files>
```

### Workspace directory intent

- `memory/`: all durable note state and derived knowledge for this workspace.
- `memory/threads/`: conversational evidence threads.
- `memory/imports/files/`: original imported files with original extensions.
- `memory/imports/text/`: normalized text or Markdown representations of imported sources for efficient agent reading and search.
- `memory/imports/records/`: Markdown records describing imported files and their distillation state.
- `memory/topics/`: canonical topic documents and topic indexes.
- `memory/action-items/`: canonical task and open-question records.
- `memory/views/`: generated navigation and workspace views.
- `.notes-runtime/locks/`: transient lock files used to reduce concurrent mutation conflicts between agent sessions. These files are runtime-only and should not be committed.
- `<user-owned project files>`: arbitrary files unrelated to the note system that remain under user control.

## Common File Conventions

These rules apply to all Markdown documents in `memory/`:

- File extension is always `.md`.
- Encoding is UTF-8.
- Frontmatter is YAML and is required.
- All timestamps use ISO 8601 with timezone offset, for example `2026-03-26T14:22:33-04:00`.
- All IDs are stable, lowercase, hyphenated strings.
- All slugs and custom type names are lowercase, ASCII, and hyphenated.
- Once created, IDs, slugs, and custom type names are stable and must not be silently renamed.
- All generated sections use explicit markers so scripts can safely rewrite them.
- If manual editing is allowed, the file contains a dedicated `## Manual Notes` section that scripts preserve.
- Wrapper commands that accept slugs rather than explicit paths must fail with an actionable ambiguity error if the slug matches more than one durable record.
- Navigational and derived documents must include a short frontmatter `preview` field for fast triage without opening the full body.

The `preview` field is required for:

- `memory/README.md`
- thread documents
- import records
- topic documents
- action-item documents
- generated view files

The `preview` field must:

- be one or two short sentences,
- stay under 240 characters,
- summarize the current purpose or state of the document,
- avoid citations and detailed prose,
- be rewritten whenever the document's current state materially changes.

The `preview` field is not required for raw imported source files or normalized import text files.

### Generated section markers

Script-managed body content must be wrapped with these markers:

```markdown
<!-- BEGIN AUTO -->
...
<!-- END AUTO -->
```

If a document supports manual notes, that section must sit outside the auto-managed block.

### Citation notation

All generated semantic content that makes factual claims must use parseable inline citation tags of this form:

```markdown
[sources: thr-YYYY-MM-DD-<slug>#snp-0001, imp-YYYY-MM-DD-<slug>#txt-0003]
```

Rules:

- citations must point to raw evidence anchors in thread snippets or normalized import text chunks,
- citations must not point only to other derived summaries or generated views,
- a cited claim may have one or more source anchors,
- if a statement is uncertain or synthesized from incomplete evidence, the prose must say so explicitly rather than pretending the citations imply certainty.

Canonical source-anchor forms:

- thread snippet: `thr-YYYY-MM-DD-<slug>#snp-0001`
- normalized import text chunk: `imp-YYYY-MM-DD-<slug>#txt-0001`

Topic links and action-item links may still reference derived documents for navigation, but citations for factual claims must resolve to evidence anchors.

## Skills Layout

The skill set is fixed to four user-facing skills plus one shared support area:

```text
skills/
├── capturing-notes/
│   ├── SKILL.md
│   ├── scripts/
│   ├── references/
│   ├── assets/
│   └── evals/
├── querying-notes/
├── distilling-threads/
├── ingesting-documents/
└── shared/
    ├── python/
    ├── scripts/
    └── references/
```

The `skills/shared/` directory is not a skill. It must not contain `SKILL.md`.

## Skill Responsibilities

### `capturing-notes`

Use when the user is actively taking notes, asking the agent to remember something, resuming an in-progress thread, or adding more context to an already-open thread. It should be assumed that the default state of an agent working in a note workspace with access to this skill is capturing notes unless the agent instructions indicate otherwise.

Responsibilities:

- choose or create the active thread,
- ask or infer whether the current note belongs in an existing open thread or a new thread,
- append snippets,
- draft updates to the embedded rolling summary,
- draft updates to the thread-local open-question list,
- perform lightweight duplicate and contradiction checks,
- draft lightweight action-item extraction,
- apply those agent-authored updates through structural scripts,
- mark the thread as pending deep distillation after new content arrives.

This skill may update canonical action items when the evidence is explicit and the topic linkage is confident. It must not perform full topic reconciliation.

### `querying-notes`

Use when the user is asking questions about stored information, asking for a to-do view, asking what is blocked, or asking for history about a topic/person/project/system.

Responsibilities:

- start from the workspace entrypoint and generated views,
- use progressive disclosure through indexes, views, topics, and then evidence,
- answer by topic, time, and entity,
- support concise vs deeper investigation modes,
- use scripts only for coarse retrieval and structured filtering,
- perform the final semantic answer synthesis itself,
- query both narrative knowledge and structured action state,
- return citations,
- warn if relevant pending distillation exists.

This skill is read-only. It must not mutate durable state.

### `distilling-threads`

Use when the user asks to close a thread, reconcile or bubble up captured notes, refresh the workspace after a session, or recover interrupted note processing.

Responsibilities:

- run agent-led deep distillation for one or more threads/import records,
- update or create topic and action-item drafts based on semantic review,
- apply those updates through structural scripts,
- refresh generated views,
- mark thread/import state as deeply distilled,
- resume incomplete prior attempts safely,
- during explicit close-thread workflows, check whether the current workspace root is a Git repository and, if so, prompt the user that this is a good time to make a commit.

This skill owns close-thread behavior. There is no separate close-thread skill.

### `ingesting-documents`

Use when the user wants to import a requirements document, design doc, PDF, meeting agenda, transcript, or other large external source into the notes workspace.

Responsibilities:

- copy or register the source file,
- convert the source into a normalized text or Markdown representation when needed,
- create the Markdown ingestion record,
- draft a source summary oriented around what the document contains and where to look in it,
- draft candidate topics and action items,
- apply lightweight bubbling through structural scripts,
- mark the import as pending deep distillation,
- by default, continue directly into full deep distillation unless the user explicitly asks for staged ingestion only.

The skill must treat large-document handling as a context-management workflow:

- prefer normalized text plus targeted reads over loading the full source into context at once,
- use the source summary to record what the document contains and where key sections live,
- rely on the original binary file only when the normalized text is insufficient or the user wants the original artifact.

## Shared Code Reuse

Shared Python code lives under:

```text
skills/shared/python/notes_workspace/
```

This package is the only shared logic layer. Symlinks must not be used.

Each wrapper script in a skill's `scripts/` directory must:

- resolve the skill-package root relative to `__file__`,
- resolve the workspace root from the current working directory by default,
- prepend `skills/shared/python` to `sys.path`,
- import from `notes_workspace`,
- call one specific shared entrypoint.

This makes the project portable without requiring installation into the global Python environment and without requiring the skills to be copied into the workspace.

Shared reference documents live under:

```text
skills/shared/references/
```

Skill `SKILL.md` files may reference files in `../shared/references/`.

Shared utility wrappers that are not specific to one workflow skill live under:

```text
skills/shared/scripts/
```

## Agent-Script Boundary

The implementation must preserve this division of responsibility:

- Agents decide what summaries should say.
- Agents decide which topics are affected and how current understanding changes.
- Agents decide what contradictions exist and which open questions should be surfaced.
- Agents decide how retrieved evidence answers a user's question.
- Scripts create files, stamp timestamps, maintain frontmatter, preserve section structure, move files, apply agent-authored updates, and regenerate views.

No script should be specified as if it can independently perform the semantic interpretation that the agent is expected to do.

## Script Command Surface

Wrapper scripts are the callable interface described to agents in skills.

Unless explicitly overridden, all wrappers must treat the current working directory as the workspace root.

### Common wrapper conventions

- `--update-json` arguments must accept either an inline JSON string or an `@path/to/file.json` reference.
- Stateful wrappers must support `--dry-run` where feasible and clearly report when a dry run made no durable changes.
- All wrappers must return a common JSON envelope on stdout with these top-level keys:
  - `ok`: `true` or `false`
  - `workspace_root`: absolute path used for the operation
  - `warnings`: array of human-readable warning strings
  - `paths_created`: array of workspace-relative paths created
  - `paths_updated`: array of workspace-relative paths updated
  - `result`: operation-specific payload when `ok` is `true`
  - `error`: structured error object when `ok` is `false`
- The `error` object must include:
  - `code`: stable machine-readable error code
  - `message`: concise human-readable explanation
  - `hint`: corrective next step when one exists

### `capturing-notes/scripts/`

- `capture_note.py`
  - Purpose: open/resume a thread, append a raw snippet, stamp metadata, and return the thread path and current thread state so the agent can perform semantic updates.
  - Required arguments:
    - one of `--thread-path` or `--thread-slug`
    - `--stdin-body`
  - Optional arguments:
    - `--thread-title`
    - `--speaker`
    - `--timestamp`
    - `--create-if-missing`
    - `--dry-run`
    - `--workspace-root`

  If `--timestamp` is omitted, the script must apply the current system timestamp itself.
  If `--create-if-missing` is used, `--thread-title` becomes required.

- `apply_thread_update.py`
  - Purpose: apply agent-authored updates to a thread document's summary, open questions, candidate action items, and link fields while preserving metadata and structure.
  - Required arguments:
    - `--thread-path`
    - `--update-json`
  - Optional arguments:
    - `--dry-run`
    - `--workspace-root`

- `thread_status.py`
  - Purpose: show current thread state, open questions, candidate tasks, linked topics, and distillation status.
  - Required arguments:
    - `--thread-path` or `--thread-slug`
  - Optional arguments:
    - `--workspace-root`

### `querying-notes/scripts/`

- `query_memory.py`
  - Purpose: perform coarse retrieval across topics, action items, threads, imports, and generated views and return candidate paths, metadata, and excerpts for agent-led synthesis.
  - Required arguments:
    - `--query`
  - Optional arguments:
    - `--mode concise|research`
    - `--topic`
    - `--entity`
    - `--date-from`
    - `--date-to`
    - `--source-thread`
    - `--source-import`
    - `--limit`
    - `--offset`
    - `--output-file`
    - `--workspace-root`

- `list_action_items.py`
  - Purpose: return filtered tasks/open questions and supporting paths for agent review. This script is a structured narrowing tool, not the final semantic filter.
  - Optional arguments:
    - `--kind task|question|all`
    - `--status`
    - `--owner`
    - `--topic`
    - `--entity`
    - `--date-from`
    - `--date-to`
    - `--source-thread`
    - `--source-import`
    - `--include-closed`
    - `--limit`
    - `--offset`
    - `--output-file`
    - `--workspace-root`

### `distilling-threads/scripts/`

- `distill_thread.py`
  - Purpose: apply agent-authored deep-distillation results to one thread or import record, update state markers, optionally close the thread, and rebuild affected views.
  - Required arguments:
    - one of `--thread-path`, `--thread-slug`, `--import-record-path`, or `--import-slug`
  - Optional arguments:
    - `--update-json`
    - `--close-thread`
    - `--rebuild-views`
    - `--dry-run`
    - `--workspace-root`

- `resume_pending.py`
  - Purpose: enumerate pending deep-distillation items, acquire recovery locks, and prepare them for the agent-driven recovery workflow. It does not itself perform semantic distillation.
  - Optional arguments:
    - `--thread-slug`
    - `--import-slug`
    - `--all`
    - `--dry-run`
    - `--workspace-root`

### `ingesting-documents/scripts/`

- `ingest_document.py`
  - Purpose: register an external document, copy it into `memory/imports/files/`, create a normalized text representation in `memory/imports/text/` when needed, create the matching Markdown record, and return the created paths for agent-led semantic processing.
  - Required arguments:
    - `--source-path`
    - `--title`
  - Optional arguments:
    - `--slug`
    - `--imported-at`
    - `--dry-run`
    - `--workspace-root`

  If `--imported-at` is omitted, the script must apply the current system timestamp itself.

- `apply_import_update.py`
  - Purpose: apply agent-authored summary, topic, and action-item updates to an import record while preserving metadata and structure.
  - Required arguments:
    - `--import-record-path`
    - `--update-json`
  - Optional arguments:
    - `--dry-run`
    - `--workspace-root`

### Shared view maintenance

- `skills/shared/python/notes_workspace/views.py`
  - Exposed through the distillation wrappers.
  - Purpose: rebuild generated view files.

### `shared/scripts/`

- `bootstrap_workspace.py`
  - Purpose: create the expected `memory/` directory structure and seed generated workspace entry files inside the current workspace.
  - Optional arguments:
    - `--workspace-root`
    - `--force`
    - `--dry-run`

All scripts must emit machine-readable JSON on stdout and human-readable diagnostics on stderr.

All wrapper scripts must also:

- support `--help`,
- use non-interactive interfaces only,
- document distinct exit codes for common failure classes,
- reject ambiguous input with actionable errors instead of guessing,
- support pagination or file output when result size may exceed normal tool-output limits.

### Update payload contracts

The minimum required `--update-json` contracts are:

- `apply_thread_update.py`
  - must accept:
    - `summary_markdown`
    - `open_questions_markdown`
    - `candidate_action_items_markdown`
    - `distillation_notes_markdown`
    - `primary_topic_refs`
    - `primary_entity_refs`
  - may also accept:
    - `action_item_refs`
    - `pending_reason`

- `apply_import_update.py`
  - must accept:
    - `source_summary_markdown`
    - `open_questions_markdown`
    - `candidate_action_items_markdown`
    - `distillation_notes_markdown`
    - `primary_topic_refs`
    - `primary_entity_refs`
  - may also accept:
    - `action_item_refs`
    - `pending_reason`

- `distill_thread.py`
  - must accept:
    - `source_patch`
    - `topic_upserts`
    - `action_item_upserts`
    - `views_to_rebuild`
  - `source_patch` must be able to express:
    - updated `distillation_state`
    - updated `pending_reason`
    - `deep_distilled_at`
    - `thread_status` or import-record equivalent state when relevant
  - each `topic_upsert` and `action_item_upsert` must carry a stable target ID or enough fields to create one deterministically.

## Durable File Types

The system has eight durable file classes in `memory/`:

1. workspace entrypoint,
2. thread documents,
3. import source files,
4. normalized import text files,
5. import records,
6. topic documents,
7. action-item documents,
8. generated view files.

### 1. Workspace entrypoint

Path:

```text
memory/README.md
```

Purpose:

- explain the workspace,
- link to major navigation surfaces,
- expose pending recovery signals,
- give a brief status snapshot,
- orient new agents quickly without duplicating detailed views.

Required frontmatter:

```yaml
doc_type: workspace-entrypoint
title: Workspace Memory Index
preview: <short workspace orientation summary>
updated_at: <timestamp>
generated: true
```

Required sections:

- `## Workspace Summary`
- `## Key Navigation`
- `## Pending Recovery`
- `## Active Work`

This file is generated. Manual edits are not allowed.

`## Pending Recovery` and `## Active Work` must remain short, link-oriented rollups. They are not the authoritative source for detailed recovery or work-state listings. The authoritative detail lives in the generated view files.

### 2. Thread documents

Paths:

```text
memory/threads/open/YYYY/YYYY-MM-DD-<slug>.md
memory/threads/closed/YYYY/YYYY-MM-DD-<slug>.md
```

The year directory is taken from the thread open date.

Required frontmatter:

```yaml
doc_type: thread
id: thr-YYYY-MM-DD-<slug>
title: <title>
slug: <slug>
preview: <short thread state summary>
thread_status: open | closed
source_type: conversation
opened_at: <timestamp>
last_updated_at: <timestamp>
closed_at: <timestamp or null>
distillation_state: pending | complete
light_distilled_at: <timestamp or null>
deep_distilled_at: <timestamp or null>
last_deep_distill_attempt_at: <timestamp or null>
pending_reason:
  - new-snippets
  - interrupted-distillation
  - awaiting-user-resolution
primary_topic_refs: []
primary_entity_refs: []
action_item_refs: []
```

When no pending reason applies, `pending_reason` must be an empty list rather than omitted or set to null.

Required body layout:

```markdown
# <title>

<!-- BEGIN AUTO -->
## Current Summary
...

## Open Questions
...

## Candidate Action Items
...

## Distillation Notes
...

## Snippets

### snp-0001 | <timestamp>
- speaker: <speaker or omitted>
- kind: note
- distill_status: pending | lightly-distilled | deeply-distilled

<raw snippet body>
<!-- END AUTO -->
```

Decisions:

- The rolling thread summary is embedded in `## Current Summary` at the top of the thread file.
- Thread files are canonical evidence files and must only be modified through scripts.
- Per-snippet speaker metadata is optional and should be omitted when unknown rather than blocking note capture.
- A thread is considered never fully distilled when `deep_distilled_at` is null or `distillation_state` is `pending`.
- A thread is considered interrupted when `last_deep_distill_attempt_at` is newer than `deep_distilled_at`, or when `distillation_state` is `pending` and `thread_status` is still `closed`.

### 3. Import source files

Path:

```text
memory/imports/files/YYYY/YYYY-MM-DD-<slug>.<original-extension>
```

Purpose:

- preserve the original imported bytes,
- keep original extension and format,
- serve as the evidence artifact for bulk ingestion.

These files are copied, never rewritten.

Supported import formats for v1 are:

- Markdown (`.md`)
- plain text (`.txt`)
- PDF (`.pdf`)
- Word (`.docx`)

Legacy Word (`.doc`), spreadsheets, slides, and other rich binary formats are out of scope for v1 unless later implementation work adds reliable conversion support.

### 4. Normalized import text files

Path:

```text
memory/imports/text/YYYY/YYYY-MM-DD-<slug>.md
```

Purpose:

- provide a stable, text-searchable representation of the imported source,
- let agents inspect large documents efficiently without repeatedly reconverting them,
- preserve page or section cues where possible.

Required frontmatter:

```yaml
doc_type: import-text
id: imt-YYYY-MM-DD-<slug>
title: <title>
slug: <slug>
derived_from_import: imp-YYYY-MM-DD-<slug>
source_format: <ext>
generated_at: <timestamp>
```

The body should contain normalized plain text or Markdown, with section or page delimiters preserved when available.

Normalized import text must be chunked into stable anchors using this body pattern:

```markdown
# <title>

<!-- BEGIN AUTO -->
### txt-0001 | <page or section label>
...

### txt-0002 | <page or section label>
...
<!-- END AUTO -->
```

For already-textual inputs such as Markdown or plain text, the normalized text file may be a lightly normalized copy rather than a heavy conversion.

### 5. Import records

Path:

```text
memory/imports/records/YYYY/YYYY-MM-DD-<slug>.md
```

Required frontmatter:

```yaml
doc_type: import-record
id: imp-YYYY-MM-DD-<slug>
title: <title>
slug: <slug>
preview: <short source and state summary>
source_filename: <filename>
source_path: ../files/YYYY/YYYY-MM-DD-<slug>.<ext>
normalized_text_path: ../text/YYYY/YYYY-MM-DD-<slug>.md
source_format: <ext>
imported_at: <timestamp>
distillation_state: pending | complete
light_distilled_at: <timestamp or null>
deep_distilled_at: <timestamp or null>
last_deep_distill_attempt_at: <timestamp or null>
pending_reason:
  - new-import
  - interrupted-distillation
  - awaiting-user-resolution
primary_topic_refs: []
primary_entity_refs: []
action_item_refs: []
```

When no pending reason applies, `pending_reason` must be an empty list rather than omitted or set to null.

Required body layout:

```markdown
# <title>

<!-- BEGIN AUTO -->
## Source Summary
...

## Open Questions
...

## Candidate Action Items
...

## Distillation Notes
...
<!-- END AUTO -->
```

Import records are the thread-like state container for bulk sources.

The `## Source Summary` section must be navigational rather than exhaustive. Its purpose is to tell the agent what the document contains and where to look next, not to replace the underlying source.

### 6. Topic documents

Path:

```text
memory/topics/<type>/<slug>.md
memory/topics/custom/<custom-type>/<slug>.md
```

`<type>` must be one of:

- `people`
- `projects`
- `customers`
- `systems`
- `classes`
- `products`
- `documents`
- `places`
- `concepts`
- `custom`
- `other`

Required frontmatter:

```yaml
doc_type: topic
id: top-<type>-<slug>
title: <title>
slug: <slug>
preview: <short current-understanding summary>
type: people | projects | customers | systems | classes | products | documents | places | concepts | custom | other
custom_type: <name or null>
entity: true | false
status: active | archived
created_at: <timestamp>
updated_at: <timestamp>
summary_updated_at: <timestamp>
freshness: current | needs-review | stale
aliases: []
related_topic_refs: []
source_thread_refs: []
source_import_refs: []
action_item_refs: []
```

Required body layout:

```markdown
# <title>

<!-- BEGIN AUTO -->
## Summary
...

## Current Understanding
...

## Key Facts
...

## Related Topics
...

## Recent Evidence
...

## Change History
...
<!-- END AUTO -->

## Manual Notes
...
```

Decisions:

- Topics use frontmatter.
- `entity: true` is required for topics that should participate as named retrieval entities.
- Default `entity` values by type:
  - `people`, `projects`, `customers`, `systems`, `classes`, `products`, `documents`, `places`: `true`
  - `concepts`, `other`, `custom`: `false` unless explicitly promoted.
- Topic documents are human-readable and may contain manual notes, but scripts own the auto-managed block and frontmatter.

### 7. Action-item documents

Path:

```text
memory/action-items/open/YYYY/YYYY-MM-DD-<kind>-<slug>.md
memory/action-items/closed/YYYY/YYYY-MM-DD-<kind>-<slug>.md
```

`<kind>` is `task` or `question`.

Required frontmatter:

```yaml
doc_type: action-item
id: act-YYYY-MM-DD-<kind>-<slug>
kind: task | question
title: <title>
slug: <slug>
preview: <short current-state summary>
status: open | tentative | blocked | done | cancelled | resolved
created_at: <timestamp>
updated_at: <timestamp>
closed_at: <timestamp or null>
due_at: <timestamp or null>
priority: low | medium | high
confidence: explicit | inferred | tentative
owner_topic_refs: []
linked_topic_refs: []
source_thread_refs: []
source_import_refs: []
```

Required body layout:

```markdown
# <title>

<!-- BEGIN AUTO -->
## Summary
...

## Current State
...

## Evidence
...

## Resolution History
...
<!-- END AUTO -->

## Manual Notes
...
```

Decisions:

- Tasks and open questions use the same record type and differ by `kind` and `status`.
- Canonical storage is one file per action item.
- Human-readable master views are generated from these records.

### 8. Generated view files

Paths:

```text
memory/topics/index.md
memory/topics/<type>/index.md
memory/views/action-items.md
memory/views/open-threads.md
memory/views/imports.md
memory/views/pending-distillation.md
```

Required frontmatter:

```yaml
doc_type: generated-view
view_type: <view-kind>
preview: <short description of what this view lists>
updated_at: <timestamp>
generated: true
```

These files are generated and must not be manually edited.

## Thread Lifecycle

The lifecycle is fixed:

1. thread created in `memory/threads/open/YYYY/`
2. snippets appended through `capture_note.py`
3. the agent drafts a `Current Summary` update and `apply_thread_update.py` applies it
4. the agent drafts thread-local open-question and candidate-action updates and `apply_thread_update.py` applies them
5. thread frontmatter sets `distillation_state: pending`
6. explicit deep distillation updates canonical topics/action items and generated views
7. if closed, the file moves to `memory/threads/closed/YYYY/`
8. `deep_distilled_at` is set and `distillation_state: complete`

The move from `open/` to `closed/` happens only after deep distillation succeeds.

## Thread Selection And Reopen Policy

When new notes arrive, the agent must choose between an existing open thread and a new thread using this policy:

1. If there is exactly one clearly related open thread, append to it.
2. If there are no clearly related open threads, create a new thread.
3. If there are multiple plausible open threads, ask the user before choosing.
4. If the best-matching open thread was last updated on a prior day, treat it as stale-open and ask whether to resume it or start a new thread.

Closed threads are not reopened by default.

A closed thread may be reopened only when:

- the user explicitly asks to reopen it, or
- the agent has strong evidence that the user is continuing the same bounded work item and asks for confirmation first.

## Lightweight Distillation

Lightweight distillation is agent-led and happens on every successful note append and every successful document ingestion.

It must do all of the following:

- update the thread/import summary,
- apply the agent-authored summary update through a structural script,
- update thread/import-local open questions,
- apply agent-authored open-question and candidate-action updates through a structural script,
- identify obvious topic references,
- identify explicit action items,
- mark the source record as `distillation_state: pending`,
- update `light_distilled_at`,
- leave the source in a recoverable state if later steps are interrupted.

Lightweight distillation must not:

- create or rename large numbers of topics,
- perform broad workspace rebuilds,
- mark a thread closed,
- clear the pending deep-distillation state.

## Deep Distillation

Deep distillation is an agent-led, broader, and more vetted reconciliation pass than lightweight bubbling.

It must do all of the following:

- re-read the entire source thread/import record or normalized import text,
- inspect all directly linked topics,
- inspect directly linked action items,
- search typed topic indexes for likely missed matches,
- update existing topics,
- create new topics when the source clearly establishes a durable subject,
- reconcile task/question records,
- update freshness and change-history sections,
- rebuild generated views,
- update `deep_distilled_at`,
- clear `pending_reason` and set `distillation_state: complete`.

Deep distillation runs when:

- the user explicitly asks to close a thread,
- the user explicitly asks to distill or reconcile a thread,
- the user asks to finish pending workspace recovery,
- an imported document is explicitly finalized,
- the distillation skill is invoked because `memory/views/pending-distillation.md` is non-empty and the user asks for recovery.

Deep distillation may run without closing a thread.

If the user asks for deep distillation but wants to keep the thread open, the agent must:

- perform the full reconciliation workflow,
- keep the thread in `memory/threads/open/`,
- leave `thread_status: open`,
- keep or create unresolved open questions if contradictions remain,
- ask the user for clarification when those contradictions block completion of the semantic distillation work.

If deep distillation is blocked on unresolved contradictions or missing user input, the source must remain pending:

- do not set `distillation_state: complete`,
- set `pending_reason` to include `awaiting-user-resolution`,
- record enough `Distillation Notes` detail that a later session can resume without rediscovering the same blocker from scratch.

### Git-aware close-thread prompt

When a thread is explicitly closed and deep distillation succeeds, the agent must check whether the current workspace root is a Git repository.

If the workspace is a Git repository, the agent must:

- prompt the user that closing the thread is a good time to make a commit,
- offer to make the commit,
- show the exact `git commit` command it would run before asking for confirmation,
- avoid creating the commit unless the user explicitly agrees.

If the workspace root is not a Git repository, this behavior must be skipped entirely.

This behavior belongs only to the explicit close-thread workflow. It must not run after every lightweight update or every deep-distillation pass that was not initiated as a thread close.

## Interruption And Recovery

Interrupted processing is detected entirely from durable state.

### Pending indicators

A thread or import record is pending if any of the following is true:

- `distillation_state: pending`
- `deep_distilled_at` is null
- `last_deep_distill_attempt_at` is newer than `deep_distilled_at`

Open threads from a prior day are considered `stale-open`. They are not automatically pending-close, but they must appear in the open-thread and recovery surfaces so the agent can ask whether to resume, distill, or close them.

### Recovery index

The file:

```text
memory/views/pending-distillation.md
```

must list:

- open threads with pending deep distillation,
- closed-but-not-deeply-distilled threads,
- import records with pending deep distillation.

This file is the canonical recovery surface for agents.

### Recovery behavior

`resume_pending.py` must:

- scan pending records,
- present pending records to the agent-driven recovery workflow one record at a time,
- avoid duplicating topic/action updates by matching on stable IDs,
- rebuild views after each successful recovery batch,
- leave the record pending if any step fails.

### Concurrent-session protection

To reduce conflicts between simultaneous agent sessions, any workflow that mutates thread, import, topic, action-item, or generated-view state must acquire a lock file under:

```text
.notes-runtime/locks/
```

Lock scope:

- one lock per thread or import record for source-specific mutation,
- one workspace-level view rebuild lock for generated views.

If a required lock is already present, the agent must stop and ask the user how to proceed rather than attempting concurrent mutation.

## Retrieval Architecture

Retrieval uses three axes:

- topic,
- time,
- entity.

### Topic

Topic retrieval uses topic documents plus related topic links.

### Time

Time retrieval uses:

- thread/import timestamps,
- action-item timestamps,
- topic `summary_updated_at`,
- evidence timestamps inside thread snippets.

Action-item views and queries must support filtering by:

- owner,
- linked topic,
- linked entity,
- status,
- time range,
- source thread or source import.

### Entity

In this implementation, an entity is any topic with `entity: true`. Entity retrieval is therefore a typed subset of topic retrieval optimized for named people, projects, customers, systems, places, documents, and similar subjects.

Entity-aware querying differs from plain topic querying in two ways:

- entity topics are explicitly indexed as named retrieval anchors,
- action items and threads may refer to entity topics even when the query itself is not phrased as a topic name.

Examples:

- `Billy` is an entity topic in `memory/topics/people/`.
- `Rover 3` is an entity topic in `memory/topics/systems/`.
- `robot connectivity` is usually a concept topic, not an entity.

## Retrieval Workflow

The query skill must use progressive disclosure in this order unless there is a clear reason to skip a step:

1. Start at `memory/README.md`.
2. Read the relevant generated view or typed topic index.
3. Read the most likely topic or action-item documents.
4. Only then drill into thread documents, import records, or normalized import text for supporting evidence.
5. Use the original imported file only when the normalized text is insufficient or the user needs the original artifact.

The purpose of generated views and indexes is to keep retrieval efficient and prevent the agent from filling context with broad, low-signal source documents too early.

Scripts in the query workflow are support tools. They should:

- narrow candidate sets,
- filter by date/status/source/topic/entity,
- return paths and excerpts.

The agent itself must decide:

- what evidence is actually relevant,
- how different pieces of evidence relate,
- how to synthesize the final answer,
- when to escalate from summaries into source evidence.

## Topic Creation Rules

A new topic may be created during deep distillation only if at least one of these is true:

- the subject is named and likely to recur,
- the subject already appears in more than one source record,
- the subject is needed as a stable target for action-item linking,
- the subject is a major durable object in the workspace domain.

A topic must not be created for:

- one-off mentions with no ongoing value,
- transient phrases that do not define a durable subject,
- action items that already belong in the action-item model.

The initial topic-type list is a starting taxonomy, not a permanently closed set.

Custom top-level topic types may be introduced only when:

- multiple topics have accumulated in `other/` and form a coherent durable group,
- deep distillation identifies that group as stable and useful,
- the agent prompts the user with the proposed new type and receives approval.

Until user approval is given, topics that do not fit the initial types must remain in `other/`.

The `## Change History` section in every topic must record enough information to answer:

- what changed,
- when it changed,
- what the prior understanding was,
- what evidence caused the revision.

## Action-Item Rules

### Creation

Create a canonical action-item file when:

- the user explicitly states work to do,
- the source contains a clear blocker or unresolved question,
- the system can confidently infer a follow-up and link it to a subject.

### Confidence

- `explicit`: directly stated by the user or imported document.
- `inferred`: strongly implied and useful.
- `tentative`: plausible but should be treated cautiously.

### Close / resolution

- For `kind: task`, normal terminal statuses are `done` or `cancelled`.
- For `kind: question`, normal terminal status is `resolved`.
- `blocked` is non-terminal.
- When evidence is ambiguous, do not close automatically; keep the item open or tentative.

## Generated Views

The implementation must generate these views:

- `memory/README.md`
- `memory/topics/index.md`
- `memory/topics/<type>/index.md` for every type directory
- `memory/topics/custom/index.md`
- `memory/views/action-items.md`
- `memory/views/open-threads.md`
- `memory/views/imports.md`
- `memory/views/pending-distillation.md`

### View content rules

- `memory/README.md` is a lightweight entrypoint. It links to all major views, shows a short status summary, and must not duplicate the full contents of the detailed views.
- `memory/topics/index.md` links to typed topic indexes and highlights recently updated topics.
- each typed topic `index.md` lists topic files in that directory with path, title, one-sentence summary, freshness, and updated timestamp.
- `memory/topics/custom/index.md` lists approved custom topic-type groups.
- if custom topic types exist, each `memory/topics/custom/<custom-type>/index.md` lists the topics in that custom group.
- `memory/views/action-items.md` lists open tasks and open questions grouped by kind and status, with owner, linked topics, due date, and confidence where present.
- `memory/views/open-threads.md` is a compact live-session routing surface. It lists all open threads with title, last updated time, distillation state, preview, and open-question count.
- `memory/views/open-threads.md` must call out stale-open threads separately.
- `memory/views/imports.md` lists imported source records with title, source format, imported time, and distillation state.
- `memory/views/pending-distillation.md` is the recovery queue. It lists anything needing deep reconciliation, the source type, why it is pending, and its last attempted distillation time.

For avoidance of doubt:

- `memory/README.md` is a starting surface, not a second copy of the operational views,
- `memory/views/open-threads.md`, `memory/views/imports.md`, `memory/views/action-items.md`, and `memory/views/pending-distillation.md` are the authoritative detailed generated listings for those domains.
- `memory/views/open-threads.md` and `memory/views/pending-distillation.md` intentionally remain separate because "currently open" and "still needs deep reconciliation" are different states that only partially overlap.

### View update policy

- `memory/views/open-threads.md` is updated after every capture-note append and after any thread state transition.
- `memory/views/imports.md` is updated after every document ingestion and after any import state transition.
- `memory/views/action-items.md` is rebuilt after any canonical action-item mutation and after every deep distillation or recovery batch.
- topic indexes are rebuilt after any canonical topic mutation and after every deep distillation or recovery batch.
- `memory/views/pending-distillation.md` is rebuilt whenever any thread or import enters or leaves pending state, including capture, ingestion, deep distillation, and recovery.
- `memory/README.md` is rebuilt whenever the views it links to materially change.

## Manual Editing Rules

- Files under `memory/views/` and topic type index files are generated-only.
- Thread documents and import records are script-owned and must not be manually edited except in emergencies.
- Topic and action-item documents may be manually edited only in `## Manual Notes` and in safe frontmatter fields:
  - `aliases`
  - `status` for topics
  - `custom_type` for topics only after explicit user-approved taxonomy changes
- Scripts must preserve `## Manual Notes`.

## Skill File Expectations

Every skill directory must contain:

- `SKILL.md`
- `scripts/`
- `references/`
- `evals/`

`assets/` is optional.

Client-specific metadata directories such as `agents/` are optional. If present, they must be treated as packaging metadata only. They must not contain behavioral logic that is missing from `SKILL.md`, scripts, or references.

### `SKILL.md` rules

- `name` is lowercase hyphenated.
- `name` matches the parent directory name exactly.
- `description` uses imperative “Use this skill when…” phrasing.
- `description` focuses on user intent, not internal mechanics.
- `description` must stay under the Agent Skills 1024-character limit.
- The agent-agnostic default for this project is imperative phrasing even though some agent-specific docs suggest third-person wording.
- Instructions stay concise and push detail into `references/`.
- Each skill references shared guidance only as needed to preserve progressive disclosure.
- `SKILL.md` should stay under 500 lines and roughly under 5,000 tokens.
- `SKILL.md` must include an `Available scripts` section listing bundled wrappers.
- `SKILL.md` must reference support files and scripts using paths relative to the skill directory root.
- `SKILL.md` must tell the agent when to load specific reference files instead of generically pointing at `references/`.
- Skills with non-obvious pitfalls must keep a concise `Gotchas` section in `SKILL.md`.
- Multi-step skills must include an explicit checklist and validation loop in `SKILL.md`.
- Skills should set the optional `compatibility` field because these workflows depend on Python, filesystem access, and a writable note-taking workspace.
- When present, `compatibility` should stay concise, describe real environment requirements, and avoid client-brand-specific wording unless a client-specific behavior is genuinely required.
- `SKILL.md` should link directly to its reference files instead of creating deep chains of references between reference files.
- Skill directories must not add auxiliary documentation such as `README.md`, `INSTALLATION_GUIDE.md`, `QUICK_REFERENCE.md`, or `CHANGELOG.md`. Operational guidance belongs in `SKILL.md` and `references/`.

### Shared references

The shared references directory must contain:

- `workspace-model.md`
- `filing-rules.md`
- `citation-policy.md`
- `action-item-policy.md`
- `recovery-policy.md`

These documents define reusable conventions rather than workflow entrypoints.

### Required skill-local references

Each user-facing skill must also define focused local references so `SKILL.md` can stay concise:

- `capturing-notes/references/`
  - `thread-selection.md`
  - `lightweight-distillation.md`
  - `capture-edge-cases.md`
- `querying-notes/references/`
  - `retrieval-workflow.md`
  - `answer-style.md`
  - `query-escalation.md`
- `distilling-threads/references/`
  - `deep-distillation-checklist.md`
  - `recovery-workflow.md`
  - `close-thread-git-prompt.md`
- `ingesting-documents/references/`
  - `import-conversion-policy.md`
  - `large-document-reading.md`
  - `import-distillation-policy.md`

## Evaluation And Testing

Each user-facing skill must include:

```text
evals/evals.json
evals/files/
evals/trigger-queries.train.json
evals/trigger-queries.validation.json
```

`evals/evals.json` must follow the documented shape with:

- `skill_name`,
- a list of eval cases,
- `prompt`,
- `expected_output`,
- optional `files`,
- assertions after the first round of output review.

Trigger-query files must contain both should-trigger and should-not-trigger near-miss cases. They are used to evaluate whether the skill description triggers correctly and generalizes beyond a single hand-tuned query set.

The evaluation process for each skill must compare:

- current skill vs no skill for initial development, or
- current skill vs previous skill snapshot for iterative improvement.

Each evaluation iteration must be capable of producing:

- run outputs,
- `timing.json`,
- `grading.json`,
- `benchmark.json`.

The test plan must cover:

- thread creation and append behavior,
- rolling summary updates,
- action-item extraction,
- topic retrieval by topic/time/entity,
- contradiction surfacing,
- deep distillation correctness,
- interrupted-session recovery,
- bulk ingestion,
- generated view rebuilding,
- skill triggering quality for all four skills.

Behavior-focused automated tests should target the shared Python package. Skill evals should validate trigger quality and end-to-end outcomes.

Trigger-quality evaluation must:

- use train and validation splits for trigger queries,
- test both should-trigger and should-not-trigger prompts,
- include realistic file paths, user context, and casual phrasing,
- verify that descriptions do not overfit to one narrow phrasing.

## File Intent Summary

This section states the intended role of every planned file class:

- `memory/README.md`: global workspace entrypoint.
- `memory/threads/.../*.md`: canonical conversational evidence and embedded rolling summary.
- `memory/imports/files/.../*`: preserved original imported source.
- `memory/imports/text/.../*.md`: normalized text representation used for efficient agent reading and search.
- `memory/imports/records/.../*.md`: thread-like state for imported sources.
- `memory/topics/<type>/*.md`: canonical derived knowledge for durable subjects.
- `memory/action-items/.../*.md`: canonical task/open-question records.
- `memory/topics/*/index.md`: generated typed navigation.
- `memory/views/*.md`: generated operational and recovery views.
- `skills/*/SKILL.md`: agent-facing workflow instructions.
- `skills/*/scripts/*.py`: wrapper scripts for that skill's workflows.
- `skills/shared/python/notes_workspace/*`: shared deterministic implementation.
- `skills/shared/references/*.md`: shared conventions used by multiple skills.

## Non-Goals For V1

This implementation spec does not include:

- multi-user collaboration semantics,
- permissions or privacy tiers,
- external integrations such as calendars or ticket trackers,
- a database or server component,
- vector indexes or embedding stores,
- non-Python scripting.
