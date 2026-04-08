# Epiphany

This repository contains a skill-based note-taking system designed to turn a normal workspace into an agent-usable memory base.

The goal is not just to store notes. The goal is to let an agent:

- capture rough input without losing detail,
- distill that input into durable summaries and linked topics,
- track tasks and open questions as structured state,
- answer later questions without rereading everything,
- keep working even when the note corpus becomes large.

The result is a note-taking workflow that is much closer to a persistent research assistant or project memory system than a standard notebook.

## What It Does

The system is built for messy real-world input. A user can drop in rough scratch, meeting notes, fragments, follow-ups, copied text, or imported documents, and the agent can turn that material into a workspace that stays navigable over time.

At a high level, the system maintains:

- raw captured evidence,
- rolling thread summaries,
- canonical topics such as people, projects, systems, or customers,
- canonical action items and open questions,
- generated views that help agents navigate large workspaces efficiently.

This is meant to preserve both:

- fidelity: the original notes are still there,
- usefulness: the agent does not need to scan every raw note to answer a question.

## Why Use This Instead Of Standard Notes

Standard note-taking systems are usually good at capture and weak at retrieval. Over time they tend to become one of two things:

- a pile of raw notes that is hard to search meaningfully,
- or a pile of summaries that loses provenance and detail.

This system is designed to avoid both failure modes.

Advantages over ordinary note taking:

- You can capture rough notes without stopping to structure them perfectly.
- The agent can keep track of what is still unresolved.
- Tasks and open questions do not get buried in prose.
- The workspace supports questions across topic, time, and entity.
- Large amounts of information can remain useful because the agent can navigate through summaries, indexes, views, and citations instead of rereading everything.
- Answers can point back to evidence instead of relying on unsupported recall.
- Imported documents can become part of the same memory system instead of living as disconnected attachments.

## How It Is Used

This project is a skill package, not a standalone notes repository.

The expected setup is:

- this repository provides the skills, scripts, and implementation,
- the user's actual notes live in a separate workspace,
- the agent's working directory is normally the root of that user-owned workspace.

Inside the user's workspace, the system maintains a `memory/` directory containing threads, topics, action items, imports, and generated views.

In practice, the workflow looks like this:

1. The user captures notes into a thread or imports a document.
2. The agent preserves the raw evidence.
3. The agent updates derived natural-language sections such as summaries.
4. Lightweight tooling refreshes metadata and generated views.
5. When needed, the agent performs deeper distillation into topics and canonical action state.
6. Later, the user asks questions and the agent navigates the stored memory instead of starting from scratch.

## Quickstart

This repository is meant to be installed or exposed as a skill package for an agent. The normal quickstart is therefore:

1. Install or expose the [`skills`](skills) directory using your agent client's skill-loading mechanism.
2. Create or choose a separate user-owned workspace where notes should live.
3. Start the agent in that workspace root.
4. Use natural-language requests to capture notes, ingest documents, and query prior information.

This repository does not prescribe one client-specific installation path. The exact setup depends on your agent environment, but the important requirement is that the agent can discover the skill directories under [`skills`](skills).

The four user-facing skills are:

- `capturing-notes`
- `querying-notes`
- `distilling-threads`
- `ingesting-documents`

Once those skills are available to the agent, the expected workspace shape is:

```text
user workspace/
├── memory/
│   ├── README.md
│   ├── threads/
│   ├── topics/
│   ├── action-items/
│   ├── imports/
│   └── views/
└── other user files...
```

You should not need to invoke the bundled scripts manually during normal use. Those scripts are the implementation surface the agent uses behind the scenes to keep the workspace structurally consistent.

## Basic Workflow

After the skills are active, the normal workflow is conversational:

1. Ask the agent to remember rough notes as you work.
2. Ask the agent to import external documents when they should become part of memory.
3. Ask direct questions later and expect concise cited answers.
4. Ask the agent to reconcile or close threads when you want deeper distillation.

Representative prompts:

- `Remember this: Billy debugged Rover 3 CAN bus dropouts and wants to retest Friday.`
- `Import this requirements document into memory and summarize what matters.`
- `What was Billy working on last week?`
- `What is still blocked on Rover 3?`
- `Close out the current robot-debugging thread and reconcile it into the workspace.`

In normal use, the agent should handle:

- bootstrapping the workspace when needed,
- choosing or creating the right thread,
- updating summaries and action state,
- ingesting source documents,
- retrieving information with citations.

If you are developing or testing the implementation itself, the wrapper scripts and their contracts are documented in the skill files and implementation docs. That is a development workflow, not the primary end-user quickstart.

## Input Flexibility

The system is intentionally broad about what can go in.

Useful inputs include:

- rough scratch notes,
- running meeting notes,
- status updates,
- ideas and reminders,
- copied text from chats or docs,
- explicit tasks,
- implicit tasks buried in narrative notes,
- unresolved questions,
- imported documents such as Markdown, text, PDF, and DOCX.

This flexibility matters because real note taking is not clean. People do not naturally sort everything into perfect folders and schemas while they are working. The system is designed to accept that mess, preserve it, and make it useful later.

## What Kinds Of Questions It Supports

The retrieval model is built around topic, time, and entities. That means the system is meant to support questions like:

- What was Billy working on last week?
- What is the latest status of the Rover 3 connectivity issue?
- What tasks are still open for Project X?
- What is blocked right now?
- Did we decide on 12V or 24V?
- What changed about this topic over time?
- What document mentioned the revised vendor quote?
- What evidence supports this answer?

These are the kinds of questions that standard notes often handle poorly once the note corpus becomes large.

## Why Large Note Volumes Stay Useful

One of the main design goals is that a very large amount of data can go into the workspace without becoming useless to the agent.

That works because the system does not treat every query as a full-text reread of the entire repository. Instead it uses layered retrieval:

- a workspace entrypoint,
- generated views,
- topic and action-item indexes,
- thread and import summaries,
- raw evidence only when needed.

This progressive-disclosure model lets the agent start broad, narrow quickly, and drill into evidence only when necessary. That is what makes the workspace scale better than ordinary note collections.

## Repository Contents

The most important documents in this repository are:

- [docs/product-spec.md](docs/product-spec.md): product-level behavior and guarantees
- [docs/implementation-spec.md](docs/implementation-spec.md): decision-complete implementation design
- [docs/implementation-spec-outline.md](docs/implementation-spec-outline.md): earlier planning outline
- [docs/implementation-roadmap.md](docs/implementation-roadmap.md): incremental build plan
- [docs/validation-audit.md](docs/validation-audit.md): current validation and coverage audit
- [project_goals_freeform.md](project_goals_freeform.md): original freeform design background

The implementation itself lives under [skills](skills).

Current user-facing skills:

- `capturing-notes`
- `querying-notes`
- `distilling-threads`
- `ingesting-documents`

## Current Implementation Status

The repository already includes the core mechanics for:

- bootstrapping a workspace,
- capturing notes into threads,
- syncing thread state after direct agent edits,
- maintaining canonical action items,
- coarse retrieval across the workspace,
- applying agent-authored deep-distillation results,
- ingesting documents and creating normalized text artifacts,
- rebuilding generated views and indexes,
- validating the system with unit tests and skill-eval fixtures.

The design assumes that agents do semantic work and scripts do structural work. In other words:

- the agent decides what a summary means,
- the tooling keeps the workspace consistent and queryable.

## Running Tests

Unit tests live under [tests](tests).

Run the full unit test suite from the repository root with:

```bash
pytest -q
```

Run a single test file with:

```bash
pytest -q tests/test_bootstrap.py
pytest -q tests/test_capture_flow.py
pytest -q tests/test_query_memory.py
```

Current automated coverage includes:

- workspace bootstrap and generated seed files,
- Git ignore handling for runtime state,
- thread creation during note capture,
- thread-local summary and status synchronization,
- wrapper JSON-envelope behavior and actionable error handling,
- canonical action-item creation and filtering,
- coarse retrieval and pending-distillation warnings,
- deep-distillation apply/finalize behavior for threads, topics, and imports,
- document ingestion, normalized text generation, and import-record sync.

## Project Intent

This repository is trying to make a strong claim:

notes can become a durable working memory for an agent without forcing the user into a rigid note-taking system.

That is the core idea behind the project. The specs and implementation are both aimed at making that claim practical.
