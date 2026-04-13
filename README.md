# Epiphany

This repository contains a skill-based Knowledge Database system designed to turn any user workspace into a powerful, agent-usable knowledge graph.

The goal is to let an agent:

- capture rough input without losing detail,
- ingest raw documents and URLs into parsed text,
- distill parsed information into durable, highly cross-referenced topic summaries and indexes,
- track tasks and open questions as simple Markdown checklists,
- answer questions using citations without rereading the entire workspace.

## What It Does

The system is built for messy real-world input. A user can capture notes, dump URLs, or drop in raw documents. The agent turns that material into a navigable knowledge base that stays useful over time.

At a high level, the Knowledge Database maintains:

- **Raw Inputs:** Immutable evidence (PDFs, DOCX, HTML, rough notes).
- **Parsed Text:** Extracted, readable text awaiting distillation.
- **Topics:** Distilled, living summaries of subjects (people, projects, systems).
- **Indexes:** Navigable tables of contents.
- **Action State:** Simple Markdown checklists (`- [ ]`) embedded in topics or central files.

## How It Is Used

These skills are designed to be universally available. They don't have to be restricted to a dedicated "notes" repository. You can use them directly inside an active coding project to store requirements, debugging logs, and architecture documentation, or even a general thought that pops into your head.

The core skills provided are:

- `capturing-notes`: Appends text to a daily parsed note file.
- `ingesting-documents`: Consolidates raw files/URLs and extracts text.
- `distilling-knowledge`: Reads pending parsed text and updates topics and indexes with explicit relative links.
- `querying-database`: Uses indexes to fast-travel to topics and provides cited answers.

When using these skills, the agent will attempt to locate the Knowledge Database (defaulting to `knowledge/` in the current workspace). If it cannot find it, it will ask the user for permission to create a new one or link to an existing path.

## Repository Contents

The most important documents in this repository are:

- [docs/product-spec-v2.md](docs/product-spec-v2.md): The current product-level behavior and guarantees.
- [docs/product-spec-v1-legacy.md](docs/product-spec-v1-legacy.md): The legacy product specification.

The implementation itself lives under [skills](skills).

## Quickstart

This repository is meant to be installed or exposed as a skill package for an agent.

1. Install or expose the [`skills`](skills) directory using your agent client's skill-loading mechanism.
2. In any workspace, begin capturing notes or documents:
   - `Capture this note: We decided to use Postgres instead of MySQL.`
   - `Ingest this document: ./design-doc.pdf`
3. Ask the agent to distill pending knowledge:
   - `Distill any pending logs and documents into topics.`
4. Ask direct questions later:
   - `Why did we choose Postgres?`

## Project Intent

This repository is trying to make a strong claim:

An AI agent does not need complex, fragile scripting to maintain a reliable memory base. It just needs explicit contracts for reading, writing, and linking Markdown.
