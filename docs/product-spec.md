# Product Spec: Agentic Notes Workspace

## Overview

The Agentic Notes Workspace is a repository-backed note-taking system that turns rough user input into durable memory, structured action state, and useful answers later. It is designed to behave like an active note-taking assistant rather than a passive storage mechanism.

The product captures raw evidence exactly as the user provides it, distills that evidence into living summaries of current understanding, tracks actionable and unresolved items, and helps the user retrieve information later without rereading the entire workspace.

This product is intended to support broad note-taking domains such as work, home, school, research, or other recurring contexts where information accumulates over time and needs to remain both inspectable and queryable.

## Goals

- Preserve raw note input with minimal information loss.
- Maintain up-to-date summaries of current understanding across topics.
- Track tasks and unresolved questions as first-class operational state.
- Support efficient retrieval and reasoning without requiring the agent to read every note.
- Keep the workspace human-readable while still optimized for agent use.
- Let the assistant actively improve note quality during capture by asking for clarifications and surfacing missing detail.

## Non-Goals

- Prescribing a specific implementation architecture, toolchain, or plugin format.
- Requiring users to fully define a rigid taxonomy before they can start taking notes.
- Guaranteeing perfect autonomous classification or contradiction resolution.
- Replacing every external task tracker, ticketing system, or document system in all workflows.
- Treating every kind of extracted information as its own first-class artifact.

## Core Concepts

### Workspace

A workspace is one broad memory base for a domain such as work, home, or school. It contains captured evidence, derived summaries, structured action state, and navigation surfaces that help both humans and agents work through the stored information.

Each workspace should expose a clear top-level entrypoint that explains the major contents of the workspace and links to its important navigation surfaces. This entrypoint should help both humans and agents orient themselves without scanning the entire repository.

### Thread

A thread is an active note-taking session. The user adds rough notes to a thread over time, and the thread remains open until it is explicitly closed or distilled.

### Snippet

A snippet is a raw piece of captured evidence. It preserves the user-provided content as faithfully as possible and serves as part of the immutable evidence base of the workspace.

### Thread Summary

A thread summary is a readable rolling synthesis of one thread. It helps the user and the assistant quickly understand what has been captured so far without replacing the underlying evidence.

### Topic

A topic is a living summary of the current best understanding of a subject. Topics are freeform with light types. A topic may represent a person, project, customer, system, class, product, document, place, or other meaningful subject that is likely to accumulate ongoing state across multiple threads.

Topics are not created for every mention. A topic should exist when it is likely to become a durable retrieval surface rather than a one-off reference.

Topics should make it possible to understand not only the current best understanding, but also how current that understanding is and what evidence supports it.

### Task / Action Item

A task is a first-class piece of operational state derived from evidence. Tasks are not only prose inside summaries. They represent work that remains actionable and should support reliable querying, filtering, and status tracking.

### Open Question

An open question is a first-class unresolved item derived from evidence. It may represent ambiguity, contradiction, missing detail, a blocker, or another unresolved condition that requires follow-up. Open questions use the same general operational model as tasks but represent unresolved state rather than committed work.

### Citation

A citation links a summary, task, question, or answer back to the evidence that supports it. Citations are required so that the user and the assistant can verify where a claim came from and evaluate uncertainty.

### Bulk Source

A bulk source is an imported external document or large body of text that becomes part of the evidence base. Bulk sources should be preservable as evidence while also contributing to topics, tasks, and open questions when relevant.

## Product Usage

### Capture

The user should be able to provide rough notes in natural language without first restructuring them into a rigid format. During capture, the assistant should preserve the raw input, recognize likely topics, infer tasks or open questions when appropriate, and ask for clarification when the note would otherwise be difficult to file correctly.

The assistant should behave as a note-taking collaborator. It should help the user improve the quality of what gets captured, not merely accept text as input.

### Distillation

As information accumulates within a thread, the workspace should maintain a readable thread summary and update relevant topic summaries and operational state as needed. The purpose of distillation is to preserve useful current understanding without losing the supporting evidence.

Closing a thread should represent a deeper pass of distillation so that the information in the thread has been properly incorporated into the broader workspace.

The product must be robust to interrupted sessions. If a session ends before all captured information has been fully distilled into the broader workspace, the captured evidence and thread state must remain recoverable and the system must be able to resume or complete the missing distillation later without losing track of what still needs to be propagated.

### Retrieval

The user should be able to ask direct questions about the stored information and receive concise, cited answers. The system should support progressive disclosure, allowing the assistant to start with higher-level summaries and drill into more detailed topics and evidence only when needed.

### Review Of Action State

The user should be able to view open work and unresolved issues without manually rereading notes. Tasks and open questions should remain visible as operational state that can be reviewed independently of the original capture threads.

### Bulk Ingestion

The user should be able to add larger documents into the workspace as evidence. Those documents should remain available in original form while also contributing to the workspace's derived knowledge and action state.

## Knowledge Model

The workspace has three major layers of information:

1. Immutable evidence captured from the user or imported from external sources.
2. Derived current understanding represented by thread summaries and topics.
3. Derived operational state represented by tasks and open questions.

This separation exists to avoid a common failure mode where a system either stores only raw notes and becomes hard to query, or stores only summaries and loses provenance.

Topics are the main knowledge surface of the workspace. They summarize current understanding of durable subjects and may point to other related topics when more detail exists elsewhere. A person topic may point to a project topic, a project topic may point to a customer topic, and a system topic may point to deeper component topics.

The workspace should also preserve enough historical understanding to answer questions about how knowledge changed over time. It should be possible to determine not only what the current understanding is, but when and why a prior understanding was replaced or revised.

The workspace should use a hybrid hierarchy. It should have a small, opinionated top-level structure that remains stable enough to navigate, while allowing the assistant to create lower-level topics as needed. The system should not require a universal ontology or exhaustive up-front filing plan.

## Retrieval Model

Retrieval axes must be first-class: topic + time + entities, with project/person views emerging from that model. This means the system should support answering questions by subject, timeframe, and involved people or things without maintaining separate disconnected knowledge silos for each view.

This requirement exists because many real questions are intersections of these axes rather than simple requests for one document. Examples include:

- What was Billy working on last week?
- What is the latest status of the robot connectivity issue?
- What decisions did we make about the 24V bus this month?
- What open work is tied to a specific project or person?

The product should be designed so that project views, person views, and other focused views emerge from the same underlying knowledge model instead of requiring independently maintained silos that drift over time.

## Action State

Tasks and open questions are first-class operational state and should not be treated as incidental text inside topic summaries.

The product should support these expectations:

- Tasks remain human-readable.
- Tasks support reliable status tracking over time.
- Tasks can be viewed by owner, linked topic, linked project, linked person, status, time horizon, and source thread.
- Open questions use the same general model as tasks but represent unresolved conditions rather than committed work.
- Open questions remain visible until resolved instead of disappearing into summary prose.

The product should treat structured operational state as canonical for tasks and open questions, with readable views built from that state. This requirement exists so the workspace can support multiple consistent views of the same underlying work, such as a personal to-do view, a project-specific view, and a person-specific view, without duplicating or drifting.

The assistant may infer a task or open question from rough notes. When the evidence is ambiguous, the assistant should mark the item as tentative or request clarification rather than presenting low-confidence operational state as settled fact.

## Assistant Behavior

The assistant is expected to be an active participant in the workflow.

During capture, the assistant should:

- preserve rough input with minimal loss,
- detect likely topics,
- infer likely tasks or open questions when appropriate,
- keep unresolved questions visible during an active thread,
- point out contradictions or duplication when useful,
- warn when newly captured information appears to overlap with or repeat already tracked knowledge,
- ask for clarifying detail when the information would otherwise be hard to use later.

During retrieval, the assistant should:

- answer concisely by default,
- provide citations,
- acknowledge uncertainty when evidence is incomplete or conflicting,
- support deeper investigation when the user wants more detail.

The assistant should help the user stay ahead of ambiguity instead of allowing the workspace to silently accumulate low-quality or contradictory state.

## Conflict And Ambiguity Handling

Contradictions must not be silently collapsed into a false sense of certainty.

When new evidence conflicts with the workspace's current understanding, the assistant should surface the conflict and preserve the unresolved state until the user clarifies it or later evidence resolves it explicitly.

Open questions and contradictions are closely related in this product. A contradiction that matters operationally should remain visible as an unresolved item rather than disappearing into narrative prose.

Task closure should be handled conservatively:

- if evidence clearly shows that a task is complete, the system may close it,
- if completion is ambiguous, the system should ask for confirmation or mark the item as tentatively complete,
- the product should avoid silently closing work based on weak inference.

## Human Readability And Editing

The workspace should remain inspectable by humans. Users should be able to read the evidence, summaries, and operational views directly without needing a specialized interface to understand what is stored.

Human editing of derived knowledge should be allowed, but the product must preserve provenance and support later reconciliation with new evidence. Manual edits should not sever the connection between current understanding and supporting evidence.

Derived knowledge should also expose enough recency information that a user or agent can quickly judge whether a summary or topic reflects recent evidence or may need review.

## Representative Scenarios

### Rough Work Notes

The user is debugging a robot and writes rough notes into an active thread. The assistant preserves the raw notes, recognizes likely topics such as the robot, the connectivity issue, and the people involved, and extracts a follow-up task and one unresolved question about root cause.

### Person + Time Query

Later, the user asks what Billy was working on last week. The assistant answers by combining topic, time, and entity retrieval rather than scraping one transcript, and provides citations to supporting evidence.

### Conflicting Decision

The user asks whether the team chose 12V or 24V. If the workspace contains conflicting evidence, the assistant should surface the contradiction and show the relevant citations rather than flattening the disagreement into a single unsupported answer.

### Project And Person Task Views

A task is associated with both a project and a person. The workspace should be able to show that same underlying task in a project-oriented view and a person-oriented view without creating two drifting copies of the task.

### Bulk Import

The user imports a requirements document. The original document remains preserved as evidence, while relevant understanding and action items are distilled into topics, tasks, and open questions.

### Manual Summary Adjustment

The user manually adjusts a topic summary to improve phrasing or clarify the current understanding. The workspace should still preserve provenance and allow future evidence to reconcile with that edited summary.

### Interrupted Session Recovery

The user closes an agent session before a thread has been fully distilled into topics and operational state. The workspace should preserve the captured thread, make the incomplete state discoverable, and allow a later session to resume distillation without losing evidence or silently dropping pending updates.

## Quality Bar

The product should be judged by the following qualities:

- capture remains durable and trustworthy,
- current understanding is easier to navigate than raw notes alone,
- tasks and unresolved issues remain operationally useful,
- answers can be traced back to evidence,
- the workspace remains resilient to interrupted or partially completed note-processing sessions,
- the system tolerates messy real-world input without demanding heavy up-front structure,
- the workspace remains useful to both larger and smaller agents.

## Default Expectations

- A workspace usually covers one broad domain rather than one tiny category.
- Topics are freeform with light types.
- Each workspace has a top-level entrypoint that helps agents and humans navigate the memory base.
- The product supports progressive disclosure from broad summaries to detailed evidence.
- Concise cited answers are the default retrieval behavior.
- Tasks and open questions are the only clearly required first-class operational artifacts beyond summaries and evidence.
- Derived knowledge should preserve both current understanding and enough historical context to answer change-over-time questions.
- Other information, such as decisions or meeting outcomes, may often be recoverable from topics and evidence without becoming separate first-class artifact types.

## Out Of Scope For This Spec

This product spec intentionally does not define:

- exact directory layout,
- exact metadata schema,
- exact trigger mechanism for agent skills or commands,
- exact file formats for evidence, summaries, or operational state,
- exact timing of updates during and after a thread,
- exact scripts or tools used to maintain invariants.

Those details belong in the implementation document.
