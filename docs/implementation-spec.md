# Implementation Spec: Agentic Notes Workspace

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
- Topics are one Markdown file per topic, stored under a fixed typed directory scheme.
- Tasks and open questions share one canonical `action-item` record format and live as one Markdown file per item.
- Generated navigation and index pages live under `memory/views/` and typed topic index files.
- Lightweight distillation runs during capture and ingestion.
- Deep distillation runs during explicit reconciliation and close-thread flows and performs a broader re-check of affected topics and action state.
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
├── memory/
│   ├── README.md
│   ├── threads/
│   │   ├── open/
│   │   └── closed/
│   ├── imports/
│   │   ├── files/
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
- `memory/imports/records/`: Markdown records describing imported files and their distillation state.
- `memory/topics/`: canonical topic documents and topic indexes.
- `memory/action-items/`: canonical task and open-question records.
- `memory/views/`: generated navigation and workspace views.
- `<user-owned project files>`: arbitrary files unrelated to the note system that remain under user control.

## Common File Conventions

These rules apply to all Markdown documents in `memory/`:

- File extension is always `.md`.
- Encoding is UTF-8.
- Frontmatter is YAML and is required.
- All timestamps use ISO 8601 with timezone offset, for example `2026-03-26T14:22:33-04:00`.
- All IDs are stable, lowercase, hyphenated strings.
- All generated sections use explicit markers so scripts can safely rewrite them.
- If manual editing is allowed, the file contains a dedicated `## Manual Notes` section that scripts preserve.

### Generated section markers

Script-managed body content must be wrapped with these markers:

```markdown
<!-- BEGIN AUTO -->
...
<!-- END AUTO -->
```

If a document supports manual notes, that section must sit outside the auto-managed block.

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
    └── references/
```

The `skills/shared/` directory is not a skill. It must not contain `SKILL.md`.

## Skill Responsibilities

### `capturing-notes`

Use when the user is actively taking notes, asking the agent to remember something, resuming an in-progress thread, or adding more context to an already-open thread.

Responsibilities:

- choose or create the active thread,
- append snippets,
- update the embedded rolling summary,
- update the thread-local open-question list,
- perform lightweight duplicate and contradiction checks,
- perform lightweight action-item extraction,
- mark the thread as pending deep distillation after new content arrives.

This skill may update canonical action items when the evidence is explicit and the topic linkage is confident. It must not perform full topic reconciliation.

### `querying-notes`

Use when the user is asking questions about stored information, asking for a to-do view, asking what is blocked, or asking for history about a topic/person/project/system.

Responsibilities:

- navigate from workspace entrypoint to topic/action/evidence layers,
- answer by topic, time, and entity,
- support concise vs deeper investigation modes,
- query both narrative knowledge and structured action state,
- return citations,
- warn if relevant pending distillation exists.

This skill is read-only. It must not mutate durable state.

### `distilling-threads`

Use when the user asks to close a thread, reconcile or bubble up captured notes, refresh the workspace after a session, or recover interrupted note processing.

Responsibilities:

- run deep distillation for one or more threads/import records,
- update or create topic records,
- reconcile action items,
- refresh generated views,
- mark thread/import state as deeply distilled,
- resume incomplete prior attempts safely.

This skill owns close-thread behavior. There is no separate close-thread skill.

### `ingesting-documents`

Use when the user wants to import a requirements document, design doc, PDF, meeting agenda, transcript, or other large external source into the notes workspace.

Responsibilities:

- copy or register the source file,
- create the Markdown ingestion record,
- extract a source summary,
- identify candidate topics and action items,
- perform lightweight bubbling,
- mark the import as pending deep distillation,
- optionally invoke the distillation workflow when requested.

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

## Script Command Surface

Wrapper scripts are the callable interface described to agents in skills.

Unless explicitly overridden, all wrappers must treat the current working directory as the workspace root.

### `capturing-notes/scripts/`

- `capture_note.py`
  - Purpose: open/resume a thread, append a snippet, update rolling summary, update thread-local open questions, perform lightweight bubbling, and return the updated status bundle.
  - Required arguments:
    - `--thread-slug`
    - `--thread-title`
    - `--speaker`
    - `--stdin-body`
  - Optional arguments:
    - `--timestamp`
    - `--create-if-missing`
    - `--workspace-root`

- `thread_status.py`
  - Purpose: show current thread state, open questions, candidate tasks, linked topics, and distillation status.
  - Required arguments:
    - `--thread-path` or `--thread-slug`
  - Optional arguments:
    - `--workspace-root`

### `querying-notes/scripts/`

- `query_memory.py`
  - Purpose: run a cited query across topics, action items, threads, and imports.
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
  - Purpose: return filtered tasks/open questions and the paths that support them.
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
  - Purpose: run deep distillation for one thread and optionally close it.
  - Required arguments:
    - `--thread-path` or `--thread-slug`
  - Optional arguments:
    - `--close-thread`
    - `--rebuild-views`
    - `--workspace-root`

- `resume_pending.py`
  - Purpose: resume one or all pending deep-distillation items.
  - Optional arguments:
    - `--thread-slug`
    - `--import-slug`
    - `--all`
    - `--workspace-root`

### `ingesting-documents/scripts/`

- `ingest_document.py`
  - Purpose: register an external document, copy it into `memory/imports/files/`, create the matching Markdown record, perform lightweight extraction, and return the created paths.
  - Required arguments:
    - `--source-path`
    - `--title`
  - Optional arguments:
    - `--slug`
    - `--imported-at`
    - `--workspace-root`

- `bootstrap_workspace.py`
  - Purpose: create the expected `memory/` directory structure and seed generated workspace entry files inside the current workspace.
  - Optional arguments:
    - `--workspace-root`
    - `--force`

### Shared view maintenance

- `skills/shared/python/notes_workspace/views.py`
  - Exposed through the distillation wrappers.
  - Purpose: rebuild generated view files.

All scripts must emit machine-readable JSON on stdout and human-readable diagnostics on stderr.

All wrapper scripts must also:

- support `--help`,
- use non-interactive interfaces only,
- document distinct exit codes for common failure classes,
- reject ambiguous input with actionable errors instead of guessing,
- support pagination or file output when result size may exceed normal tool-output limits.

## Durable File Types

The system has seven durable file classes in `memory/`:

1. workspace entrypoint,
2. thread documents,
3. import source files,
4. import records,
5. topic documents,
6. action-item documents,
7. generated view files.

### 1. Workspace entrypoint

Path:

```text
memory/README.md
```

Purpose:

- explain the workspace,
- link to major navigation surfaces,
- expose pending recovery signals,
- orient new agents quickly.

Required frontmatter:

```yaml
doc_type: workspace-entrypoint
title: Workspace Memory Index
updated_at: <timestamp>
generated: true
```

Required sections:

- `## Workspace Summary`
- `## Key Navigation`
- `## Pending Recovery`
- `## Active Work`

This file is generated. Manual edits are not allowed.

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
primary_topic_refs: []
primary_entity_refs: []
action_item_refs: []
```

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

### snp-0001 | <timestamp> | <speaker>
- kind: note
- distill_status: pending | lightly-distilled | deeply-distilled

<raw snippet body>
<!-- END AUTO -->
```

Decisions:

- The rolling thread summary is embedded in `## Current Summary` at the top of the thread file.
- Thread files are canonical evidence files and must only be modified through scripts.
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

### 4. Import records

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
source_filename: <filename>
source_path: ../files/YYYY/YYYY-MM-DD-<slug>.<ext>
source_format: <ext>
imported_at: <timestamp>
distillation_state: pending | complete
light_distilled_at: <timestamp or null>
deep_distilled_at: <timestamp or null>
last_deep_distill_attempt_at: <timestamp or null>
primary_topic_refs: []
primary_entity_refs: []
action_item_refs: []
```

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

### 5. Topic documents

Path:

```text
memory/topics/<type>/<slug>.md
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
- `other`

Required frontmatter:

```yaml
doc_type: topic
id: top-<type>-<slug>
title: <title>
slug: <slug>
type: people | projects | customers | systems | classes | products | documents | places | concepts | other
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
  - `concepts`, `other`: `false` unless explicitly promoted.
- Topic documents are human-readable and may contain manual notes, but scripts own the auto-managed block and frontmatter.

### 6. Action-item documents

Path:

```text
memory/action-items/open/YYYY-MM-DD-<kind>-<slug>.md
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

### 7. Generated view files

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
updated_at: <timestamp>
generated: true
```

These files are generated and must not be manually edited.

## Thread Lifecycle

The lifecycle is fixed:

1. thread created in `memory/threads/open/YYYY/`
2. snippets appended through `capture_note.py`
3. `Current Summary` updated
4. lightweight extraction updates thread-local open questions and candidate action items
5. thread frontmatter sets `distillation_state: pending`
6. explicit deep distillation updates canonical topics/action items and generated views
7. if closed, the file moves to `memory/threads/closed/YYYY/`
8. `deep_distilled_at` is set and `distillation_state: complete`

The move from `open/` to `closed/` happens only after deep distillation succeeds.

## Lightweight Distillation

Lightweight distillation happens on every successful note append and every successful document ingestion.

It must do all of the following:

- update the thread/import summary,
- update thread/import-local open questions,
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

Deep distillation is a broader and more vetted reconciliation pass than lightweight bubbling.

It must do all of the following:

- re-read the entire source thread/import record,
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

## Interruption And Recovery

Interrupted processing is detected entirely from durable state.

### Pending indicators

A thread or import record is pending if any of the following is true:

- `distillation_state: pending`
- `deep_distilled_at` is null
- `last_deep_distill_attempt_at` is newer than `deep_distilled_at`

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
- retry deep distillation one record at a time,
- avoid duplicating topic/action updates by matching on stable IDs,
- rebuild views after each successful recovery batch,
- leave the record pending if any step fails.

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
- `memory/views/action-items.md`
- `memory/views/open-threads.md`
- `memory/views/imports.md`
- `memory/views/pending-distillation.md`

### View content rules

- `memory/README.md` links to all major views and shows pending recovery status.
- `memory/topics/index.md` links to typed topic indexes and highlights recently updated topics.
- each typed topic `index.md` lists topic files in that directory with short summaries.
- `memory/views/action-items.md` lists open tasks and open questions grouped by kind and status.
- `memory/views/open-threads.md` lists all open threads and their open questions.
- `memory/views/imports.md` lists imported source records and their distillation state.
- `memory/views/pending-distillation.md` lists anything needing deep reconciliation.

## Manual Editing Rules

- Files under `memory/views/` and topic type index files are generated-only.
- Thread documents and import records are script-owned and must not be manually edited except in emergencies.
- Topic and action-item documents may be manually edited only in `## Manual Notes` and in safe frontmatter fields:
  - `aliases`
  - `status` for topics
- Scripts must preserve `## Manual Notes`.

## Skill File Expectations

Every skill directory must contain:

- `SKILL.md`
- `scripts/`
- `references/`
- `evals/`

`assets/` is optional.

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

### Shared references

The shared references directory must contain:

- `workspace-model.md`
- `filing-rules.md`
- `citation-policy.md`
- `action-item-policy.md`
- `recovery-policy.md`

These documents define reusable conventions rather than workflow entrypoints.

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
