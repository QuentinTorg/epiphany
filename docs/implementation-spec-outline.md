# Implementation Spec Outline: Agentic Notes Workspace

## Purpose

This document outlines the implementation design for the Agentic Notes Workspace described in [product-spec.md](product-spec.md). It translates the product commitments into a concrete architecture, skill split, shared tool layer, and workspace state model.

This is an implementation-spec outline rather than a full low-level design. It defines the major implementation decisions, component boundaries, and responsibilities that the full implementation spec should elaborate.

## Skill Reference Documents

Future implementers should treat the documents in [docs/skill_references](skill_references) as normative background for skill authoring and packaging.

These documents are included as local references so the implementation work does not need to rely on external web access.

Reference guide:

- [agentskills.io_what_are_skills.md](skill_references/agentskills.io_what_are_skills.md): conceptual overview of what a skill is, how progressive disclosure works, and how agents activate skill instructions and optional resources.
- [agentskills.io_overview.md](skill_references/agentskills.io_overview.md): higher-level orientation to the Agent Skills ecosystem and the role skills play as a portable capability layer.
- [agentskills.io_skill_specification.md](skill_references/agentskills.io_skill_specification.md): formal directory structure and `SKILL.md` specification, including frontmatter fields, optional directories, and packaging constraints.
- [agentskills.io_skill_creator_best_practices.md](skill_references/agentskills.io_skill_creator_best_practices.md): guidance on grounding skills in real domain expertise, extracting them from real tasks, and refining them through execution.
- [agentskills.io_skill_creator_optimizing_skill_descriptions.md](skill_references/agentskills.io_skill_creator_optimizing_skill_descriptions.md): guidance on writing `description` fields so the right skill triggers reliably and irrelevant skills stay dormant.
- [agentskills.io_using_scripts_in_skills.md](skill_references/agentskills.io_using_scripts_in_skills.md): best practices for bundled scripts, including self-contained execution, script interfaces, structured output, helpful errors, and composable command design.
- [agentskills.io_evaluating_skills.md](skill_references/agentskills.io_evaluating_skills.md): guidance on eval-driven iteration and how to test skill output quality and triggering reliability over realistic prompts.
- [claude_skills_overview.md](skill_references/claude_skills_overview.md): Anthropic's conceptual overview of skills and how they function as modular filesystem-based capabilities.
- [claud_skills_best_practices.md](skill_references/claud_skills_best_practices.md): Anthropic's practical guidance on concise authoring, progressive disclosure, and keeping skill instructions focused and testable.

Agent-specific language in these documents should not be interpreted as a product constraint for this project. References to Claude or any other specific agent should be treated as examples of a skill-capable agent environment unless the guidance depends on a product-specific feature. The implementation target for this project remains agent-agnostic.

The full implementation spec should explicitly cite the relevant reference documents whenever it defines:

- `SKILL.md` structure and frontmatter,
- skill descriptions and triggering strategy,
- script interfaces and output conventions,
- skill length and progressive disclosure strategy,
- evals and validation methodology.

## Primary Implementation Direction

The system should be implemented as a repository-local skill suite under a top-level `skills/` directory, with Python scripts bundled inside the skills and shared support code available to those skills.

The implementation should follow this principle:

- skills define agent behavior and workflow,
- Python scripts enforce invariants and perform stateful operations,
- repository files remain the durable source of truth.

This means the product is implemented as skills with supporting scripts, not as a standalone application that skills merely call into from the outside.

The implementation should follow the referenced skill-authoring guidance closely, especially around concise `SKILL.md` files, workflow-oriented skill boundaries, and deterministic bundled scripts.

## Skill Layout

The `skills/` directory should contain a small number of high-value workflow skills rather than many narrow utility skills.

### `capturing-notes`

This skill owns the live note-taking workflow for an open thread.

Responsibilities:

- open or resume a thread,
- capture raw user snippets,
- maintain rolling thread summary state,
- identify likely topics,
- extract likely tasks and open questions,
- keep unresolved questions visible during the active thread,
- surface contradictions and likely duplicates during capture, (in both current thread, and compared to greater memory about the document)
- perform lightweight bubbling of new information into broader workspace state when appropriate.

This skill should handle ordinary note capture as well as lightweight structured capture that emerges during note-taking. It should not own the final deep reconciliation pass for a thread.

### `querying-notes`

This skill owns retrieval and reasoning over the workspace.

Responsibilities:

- navigate the workspace entrypoint and topic hierarchy,
- retrieve by topic, time, and entities,
- answer with citations by default,
- support deeper investigation on follow-up,
- query tasks and open questions as part of the same retrieval model,
- trace answers back to thread evidence when needed.

This skill should include action-state queries rather than splitting off separate task-only query skills in v1.

### `distilling-threads`

This skill owns deep propagation, reconciliation, and recovery workflows.

Responsibilities:

- perform explicit close-thread behavior,
- complete deeper distillation from thread state into topics, tasks, and open questions,
- rebuild or refresh derived workspace views when needed,
- detect and resume incomplete distillation after interrupted sessions,
- reconcile pending thread-level state with broader workspace state.

This skill should absorb what might otherwise be called `close-thread` or `update-summary` skills. Those are workflow branches inside distillation, not separate user-facing skills.

### `ingesting-documents`

This skill owns bulk document ingestion.

Responsibilities:

- import large external documents into the evidence base,
- record source-level metadata appropriate for imported material,
- create or update thread-like ingestion state for the imported source,
- extract candidate topics, tasks, and open questions from the document,
- hand off deeper propagation to the same distillation path used for ordinary threads.

This should be a distinct skill rather than a branch inside `capturing-notes` because the workflow shape is materially different from live conversational capture. It is frequent enough and specialized enough to justify its own concise instructions.

## Why These Skills And Not More

The skill split should follow user workflows, not every reusable sub-operation.

The following should not be separate skills in v1:

- `workspace-navigation`
- `close-thread`
- `update-summary`
- `capture-todos`
- `query-todos`

These are either:

- shared reference material,
- shared Python operations,
- or branches inside a larger workflow skill.

If a capability is reused in many workflows but is not itself a distinct user intent, it should usually become a script or reference file before it becomes its own skill.

## Shared Implementation Layer

All skills will need common operational logic. The implementation should therefore include a shared Python layer under `skills/` that is not itself a skill.

Likely shared responsibilities:

- workspace path resolution,
- thread discovery and state inspection,
- evidence append and validation,
- topic lookup and linking,
- action-item record manipulation,
- citation generation,
- interrupted-session detection,
- derived-view refresh,
- structured query helpers.

This shared layer should be usable from multiple skills without duplicating logic or creating drift in core behavior.

## Script Design Rules

Python is the assumed scripting baseline for all agents targeted by this project.

Bundled scripts should follow these rules:

- non-interactive by default,
- deterministic where practical,
- idempotent where retries are plausible,
- structured output on stdout,
- diagnostics and guidance on stderr,
- clear error messages with corrective hints,
- explicit validation of ambiguous input,
- support dry-run mode for stateful or destructive operations where feasible.

Scripts should be small and composable. A skill may call multiple scripts as part of one workflow, but each script should have one clear operational responsibility.

These rules should be treated as direct applications of the bundled reference material in [docs/skill_references](skill_references), especially the script-interface and progressive-disclosure guidance.

## Workspace State Model

The repository should maintain three core categories of durable state:

1. immutable evidence,
2. derived knowledge surfaces,
3. structured action state.

The implementation spec should define concrete representations for:

- workspace entrypoint and navigation surfaces,
- threads and thread lifecycle state,
- raw snippets and imported source artifacts,
- rolling thread summaries,
- topics and topic links,
- tasks and open questions,
- citations and source references,
- interrupted or pending distillation state.

The design must guarantee that raw evidence remains durable even if all derived state is stale or incomplete.

The full implementation spec must also define the imposed workspace file structure clearly enough that an implementer does not need to guess where any class of information belongs. That includes the purpose of each planned directory, the document types expected in each location, and the file naming conventions used to keep the workspace organized.

## Thread Lifecycle

The implementation spec should define a concrete lifecycle for threads:

1. thread opened or resumed,
2. snippets appended,
3. rolling summary updated,
4. candidate topics/tasks/questions extracted,
5. thread remains open while unresolved work exists,
6. explicit close or distill action performs deeper reconciliation,
7. thread becomes closed only after required propagation is complete.

The system must also define how an interrupted thread is recognized and how a later session resumes it safely.

The full implementation spec must also define:

- where the rolling thread summary is stored,
- whether it is embedded in the thread document or split into a separate file,
- how thread files are named, including whether they use a `YYYY-MM-DD-<name>` filename convention,
- what metadata or state markers indicate open, updated, pending-distillation, interrupted, and closed thread states,
- how the system determines that a thread has never been fully distilled,
- how resumed distillation distinguishes incomplete prior work from completed propagation.

## Distillation Strategy

The implementation spec should separate lightweight and deep distillation.

Lightweight distillation:

- supports active note-taking,
- keeps thread summaries current,
- updates obvious action-state items,
- provides enough context for the assistant to participate live.

Deep distillation:

- runs during explicit close-thread or maintenance workflows,
- reconciles thread-derived knowledge against broader topics,
- resolves pending propagation steps,
- refreshes navigation surfaces and derived views,
- records enough completion state that interrupted sessions can be resumed safely.

This separation is important because the product requires both live assistant usefulness and resilience to incomplete sessions.

The full implementation spec must explicitly answer whether deep distillation performs a broader and more vetted scan of relevant topics and action state than the lightweight per-turn bubbling path. If so, it must define when that broader scan runs and what it is expected to cover.

## Retrieval Architecture

The implementation spec should preserve the product-level retrieval model:

- topic,
- time,
- entities.

The implementation must support answering compound queries by intersecting these axes instead of relying only on broad text search over summaries.

The design should also define:

- how the workspace entrypoint helps agents start narrow,
- how topic links support progressive disclosure,
- how action-state queries share the same retrieval model,
- how citations are attached to answers and summaries,
- how historical state is preserved for change-over-time questions.

The full implementation spec should also define what `entities` means in this system. It should explain how entities relate to topics, when a thing is treated as an entity for retrieval purposes, and how entity-aware queries differ from plain topic lookup.

## Action-State Architecture

Tasks and open questions should share one structured operational model with subtype or status differences.

The implementation spec should define:

- canonical task/question storage,
- view generation for master and filtered lists,
- linking between action items and topics,
- ownership and status fields,
- tentative vs confirmed action-state handling,
- closure and resolution rules,
- how open questions remain visible during active capture and after interruptions.

The full implementation spec must define the storage format for tasks and open questions explicitly, including file type, file extension, internal layout, required fields, and the mechanism that keeps the format reliably parseable while still human-readable.

## Topic Architecture

The implementation spec should define how topics are created, updated, and linked.

Important design points:

- topics are freeform with light types,
- not every mention becomes a topic,
- topics must preserve current understanding plus citations,
- topics should expose recency or freshness signals,
- topics should preserve enough history to answer change-over-time questions,
- related topics should link to each other without forcing a rigid ontology.

The full implementation spec must also decide whether topic files use frontmatter or another metadata block, what required metadata fields exist, and how an agent can quickly understand a topic's scope without fully scanning arbitrary prose.

## Navigation Surfaces

The product requires a workspace-level entrypoint. The implementation spec should define the major navigation surfaces needed for both humans and agents.

At minimum, this likely includes:

- one workspace-level entrypoint,
- one or more high-level knowledge navigation surfaces,
- task and open-question views,
- discoverable access to open or incomplete threads,
- discoverable access to imported bulk sources.

The full implementation spec should describe the intended role of each planned navigation file or surface clearly enough that an implementer can create it without guessing what information belongs there.

## Interruption And Recovery

Interrupted sessions are a core product concern, not a side case.

The implementation spec should define:

- how incomplete propagation is recorded,
- how a later session detects unfinished work,
- how the assistant is guided to resume distillation safely,
- how recovery avoids duplicating updates or losing citations,
- how the system distinguishes stale derived state from lost evidence.

This area should receive the same design attention as normal happy-path capture.

## References And Supporting Files

Each skill should keep `SKILL.md` focused and move detail into support files.

The implementation spec should likely define:

- `references/` files for filing heuristics, answer style, and edge cases,
- templates or schemas in `assets/` where useful,
- shared Python modules for reusable logic,
- validation and smoke-test strategy for the skills and scripts.

This section of the full implementation spec should explicitly tie its decisions back to the local reference documents for skill specification, best practices, script usage, trigger descriptions, and eval methodology.

The full implementation spec must also define how scripts and shared Python code are reused across multiple skills in a portable way, rather than leaving cross-skill sharing as an ad hoc convention.

## Testing Strategy

The full implementation spec should define behavior-focused tests around persistent product guarantees rather than refactor-sensitive internal details.

Priority test areas:

- raw evidence capture durability,
- task and open-question extraction and update behavior,
- citation preservation,
- topic retrieval and progressive disclosure behavior,
- contradiction and ambiguity handling,
- interrupted-session recovery,
- bulk document ingestion and propagation.

## Open Decisions For The Full Implementation Spec

This outline intentionally leaves these decisions for the full implementation spec:

- exact `skills/` directory structure,
- exact shared-code location under `skills/`,
- exact file formats and schemas,
- exact command interfaces for Python scripts,
- exact update timing rules between lightweight and deep distillation,
- exact high-level workspace taxonomy,
- exact rules for topic creation thresholds,
- exact historical-state representation.

In addition, the full implementation spec must make explicit decisions about:

- the imposed repository file structure for notes and derived state,
- thread file naming conventions, including whether `YYYY-MM-DD-<name>` is required,
- where rolling thread summaries live,
- whether each document type uses Markdown, frontmatter, structured sections, or another internal layout,
- the required content and required metadata for each document type,
- how distillation and reconciliation are triggered,
- how pending or incomplete propagation is marked,
- how imported documents differ structurally from conversational threads,
- what each planned file or file class is intended to contain.

## Recommended Next Step

The next document should turn this outline into a full implementation specification that is decision-complete about:

- repository layout,
- skill directory layout,
- shared Python module layout,
- script command surface,
- durable file formats,
- thread lifecycle states,
- propagation and recovery mechanics,
- query execution flow,
- test plan.

It should provide enough detail that a future implementer can understand the intent of every planned file and document type without guessing, while stopping short of embedding full file contents unless a file is small enough or constrained enough that inline examples are the clearest way to specify it.
