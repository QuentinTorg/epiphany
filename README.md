# Epiphany

This repository contains a skill-based **Epiphany Knowledge Database** system designed to turn any user workspace into a powerful, agent-usable knowledge graph.

The goal is to let an AI agent:
- Capture rough input and daily notes without losing detail.
- Ingest raw documents and URLs into parsed text.
- Distill parsed information into durable, highly cross-referenced topic summaries and indexes.
- Track tasks and open questions as simple Markdown checklists.
- Answer questions using citations without needing to re-read the entire workspace.

This system relies on a **Minimalist Markdown** architecture. It avoids complex Python scripts or rigid hybrid JSON/Markdown state files in favor of relying entirely on the agent's natural ability to parse, write, and link Markdown files.

## What It Does

The system is built for messy real-world input. A user can capture rapid-fire notes, dump URLs, or drop in raw documents (PDFs, DOCX). The agent turns that material into a navigable knowledge base that stays useful over time.

At a high level, the Epiphany Knowledge Database maintains a strict directory hierarchy (defaulting to `epiphany_knowledge/` in your workspace):

- **`epiphany_knowledge/raw/`**: Immutable evidence (PDFs, DOCX, HTML).
- **`epiphany_knowledge/parsed/`**: Extracted, readable Markdown awaiting distillation. Includes `notes/` for your daily chronological notes and `imports/` for converted documents/URLs.
- **`epiphany_knowledge/topics/`**: Distilled, living summaries of subjects (people, projects, systems).
- **`epiphany_knowledge/indexes/`**: Navigable tables of contents (`topics-index.md` and `sources-index.md`) that act as entry points for agent queries.

## The Core Skills

These skills are designed to be universally available. They don't have to be restricted to a dedicated "notes" repository. You can use them directly inside an active coding project to store requirements, debugging logs, and architecture documentation.

1. **`capturing-notes`**: Appends your rapid-fire text to a daily parsed note file (`YYYY-MM-DD.md`), grouped under hour-level timestamps (e.g., `## 14:00 [PENDING]`).
2. **`ingesting-documents`**: Fetches raw files or URLs, extracts their text using available tools, saves them as parsed Markdown, and adds them to the `sources-index.md`.
3. **`distilling-knowledge`**: Reads parsed files marked with `[PENDING]`, extracts the facts, updates the cross-referenced Topic files, and replaces the tag with `[DISTILLED]`. It also writes top-level summaries on the parsed files to serve as future abstracts.
4. **`querying-database`**: Uses Progressive Disclosure (starting at the Indexes and moving into Topics) combined with text search to find answers. It strictly provides clickable relative Markdown links for all its citations and explicitly avoids hallucinations.

When using these skills, the agent will attempt to locate the Epiphany Knowledge Database. If it cannot find it, it will ask you for permission to create a new one or link to an existing path.

## Quickstart (For Users)

This repository is meant to be installed or exposed as a skill package for an agent.

1. Install or expose the [`skills`](skills) directory using your agent client's skill-loading mechanism.
2. In any workspace, begin capturing notes or documents:
   - `Capture this note: We decided to use Postgres instead of MySQL.`
   - `Ingest this document: ./design-doc.pdf`
3. Ask the agent to distill pending knowledge:
   - `Distill any pending notes and documents into topics.`
4. Ask direct questions later:
   - `Why did we choose Postgres?`

## Contributing (For Developers)

If you are modifying or adding new skills to the Epiphany Knowledge Database, adhere to the following design philosophies:

1. **Minimalist Markdown:** Do not introduce external scripts to manage state. The agent must use standard file reading/writing tools to manage the database.
2. **Explicit Contracts:** Every skill must have a `Contract & Conventions` section dictating exact file paths, linking rules, and state management (e.g., using `[PENDING]`).
3. **Validation Loops:** Agents are prone to format hallucinations. Every skill that writes data must include a `Validate` step in its workflow instructing the agent to read back the file it just wrote to ensure it didn't corrupt the formatting or drop links.
4. **Response Templates:** Provide a strict ````markdown ```` template block in the `Assistant Persona & Response Format` section of the skill. Agents pattern-match extremely well to concrete syntax.
5. **Context Preservation:** Explicitly instruct the agent to chunk large documents or use subagent delegation to prevent context window exhaustion during heavy tasks like distillation.

## Project Intent

This repository makes a strong claim:

An AI agent does not need complex, fragile scripting to maintain a reliable memory base. It just needs explicit contracts for reading, writing, and linking Markdown.