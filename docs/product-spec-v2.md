# Product Spec: Epiphany v2 (Epiphany Knowledge Database)

## Overview
Epiphany v2 is a markdown-native knowledge database. It acts as a comprehensive knowledge-base that ingests raw input from various sources, extracts it to text, and distills it into highly cross-referenced topic summaries. It is designed to be universally available across any user workspace to capture context, requirements, and debugging steps natively.

## Core Concepts & Hierarchy
1. **Raw Inputs (`knowledge/raw/`):** The immutable evidence base. This directory holds exact copies of uploaded documents (PDFs, DOCX), raw chat logs/notes, and raw HTML dumps.
2. **Parsed Text (`knowledge/parsed/`):** Markdown or plain-text conversions of the raw inputs. The agent uses tools to extract text from the raw inputs and places it here to make it readable for distillation. Notes captured via chat skip straight to this format.
3. **Pending Distillation Tracking:** A mechanism is enforced to track if files in `knowledge/parsed/` are "fresh" and awaiting distillation. This ensures no knowledge is lost if an import or capture session is interrupted.
4. **Topics (Distillation) (`knowledge/topics/`):** Freeform Markdown files representing durable subjects. The agent reads Parsed Text and "bubbles up" critical information into these living summaries.
5. **Indexes (`knowledge/indexes/`):** To prevent context bloat, the agent maintains explicit Markdown index files (e.g., `topics-index.md`, `sources-index.md`). These provide a high-level table of contents for future agents to start their queries.

## Hard Requirements & Contracts (Including Retained Features from v1)
- **Relative Markdown Linking:** Whenever a Topic references another Topic, a Document, or a Source, the agent **MUST** use explicit relative Markdown links (e.g., `[Project Alpha](../topics/project-alpha.md)`). This creates a traversable knowledge graph.
- **Explicit Agent Contracts:** Each skill will contain a clear "Contract" section dictating the exact directory paths, linking rules, and index updating requirements.
- **Citations:** When answering queries, the agent MUST provide citations linking back to the raw evidence or parsed text. This prevents hallucinations and ensures the provenance of the information.
- **Conflict & Ambiguity Handling:** If newly ingested knowledge contradicts existing Topics, the agent must surface the conflict as an "Open Question" rather than silently collapsing it into a false sense of certainty.
- **Human Readability & Editing:** The workspace must remain easily inspectable and editable by humans. If a human modifies a topic, the Markdown structure ensures the agent can still read and append to it later without breaking state.

## Product Usage & Skills
- **Capture Note Skill:** The user provides text input. The agent appends the raw text (with a timestamp) to today's notes in `knowledge/parsed/notes/` and marks it as pending distillation.
- **Ingest Document & URL Skill:** A single, consolidated skill. The user provides a file path or URL. The agent fetches binary data to `knowledge/raw/`, extracts its text to `knowledge/parsed/`, marks it as pending distillation, and adds a link to the `sources-index.md`. Plain-text and readable data documents skip the `raw` directory and go straight to parsing.
- **Distillation Skill:** The agent checks for pending parsed files, extracts relevant facts, updates `knowledge/topics/*.md`, ensures the information "bubbles up" into high-level summaries, updates `topics-index.md`, and marks the parsed file as successfully distilled.
- **Query Skill:** The agent answers questions by starting at the Indexes, following relative links to Topics, and reading the distilled knowledge. If the database path is unknown, it asks the user for the location or permission to initialize a new one.