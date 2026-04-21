---
name: distilling-knowledge
description: Reads "pending" parsed notes and documents, extracts relevant facts and action items, and updates the living Topic files and Indexes. Use this skill when the user asks you to distill, summarize, organize, or review pending knowledge in the database.
---

# Distilling Knowledge

This skill guides you through the process of reading freshly ingested raw material (notes, documents, URLs) that are marked with `[PENDING]` tags, and bubbling that information up into durable, cross-referenced Topic files.

## Contract & Conventions

- **Database Location:** The Epiphany Knowledge Database defaults to a `epiphany_knowledge/` directory in the current workspace root. If you cannot find the Epiphany Knowledge Database, you MUST ask the user if they want to initialize it here or if it is located elsewhere.
- **Pending Files:** A file or a specific hour-level block in `epiphany_knowledge/parsed/` (notes, imports) is pending distillation if it contains the text `[PENDING]` in its heading. This allows block-level disambiguation in daily notes.
- **Topics (`epiphany_knowledge/topics/`):** Living summaries of specific subjects (e.g., people, projects, systems, decisions). They are standard Markdown files.
- **Indexes (`epiphany_knowledge/indexes/`):** Markdown files acting as a table of contents for Topics and Sources. You must update `topics-index.md` whenever you create a new Topic.
- **Action State:** Tasks and Open Questions must be extracted as simple Markdown checklists (`- [ ]`) embedded inside the relevant Topic files under an `## Action Items` or `## Open Questions` heading.
- **Relative Linking:** Whenever you reference a source document or another topic, you MUST use an explicit relative Markdown link (e.g., `[Design Doc](../parsed/imports/design-doc.md)`).
- **Clear Pending State:** Once a specific note entry or document has been completely distilled into the relevant Topics, you MUST edit the file to replace its `[PENDING]` tag with `[DISTILLED]`.

## Workflow

1. **Locate Pending Files:**
   - Search the `epiphany_knowledge/parsed/` directory (including `notes`, `imports`) for any files containing the text `[PENDING]`.
   - **Crucial Rule:** You MUST process each pending document entirely (steps 2-7) before moving on to the next. Do not try to read and distill multiple documents simultaneously.
   - **Subagent Delegation:** When possible, it is recommended to delegate the distillation of each individual document to a subagent. This will result in the most consistent performance of distillation
2. **Review & Extract:**
   - Read the contents of each pending file. For notes, focus ONLY on the specific entries marked with `[PENDING]`.
   - **Chunking Large Documents:** For very large documents, extract and update topics in smaller, logical chunks (e.g., by section) to avoid context exhaustion.
   - Identify the core entities, decisions, topics, tasks, and open questions from those pending sections.
3. **Write Source Summary:**
   - Add or update a brief `**Summary:**` section at the very top of the parsed document (just under the title).
   - For daily notes, maintain a single, cumulative summary of the day's events at the top of the file rather than per block.
   - **Intent:** The summary acts as an abstract describing *what kind of information* is in the file, helping future agents decide if they need to read deeper.
   - **Navigability:** The summary MUST include specific keywords, tags, or Markdown heading references (e.g., `[See: ## API Schema Definitions]`) to enable fast navigation.
4. **Update or Create Topics:**
   - For each major subject identified, locate its corresponding Topic file in `epiphany_knowledge/topics/` (e.g., `project-alpha.md`).
   - If the Topic file doesn't exist, create it. Be mindful to avoid creating many tiny topic files for trivial or transient details; prefer grouping related information into broader topics.
   - **Cross-topic Search:** When creating a *new* topic, perform a text search across existing topics to find any other mentions of this new topic. Extract that relevant information into the new topic to ensure information is properly grouped and to minimize duplication.
   - Summarize the new findings and append/integrate them into the Topic file. Ensure any related topics mentioned in your summary are hyperlinked as relative Markdown links.
   - **Topic Sizing:** If an existing Topic file is getting too large or begins to cover too many disparate subtopics, split it by creating a new, more specific Topic file (e.g., `project-alpha-architecture.md`). Move the relevant content to the new file, and leave a relative link to the new subtopic in the parent Topic file.
   - **Crucial:** Cite your sources! When adding facts to a Topic, link back to the parsed file that provided the fact (e.g., `Decided to use Postgres ([Source](../parsed/notes/2026-04-09.md))`).
   - If new tasks or open questions are found, add them as `- [ ]` checklist items within the Topic.
5. **Update Indexes:**
   - If you created any *new* Topic files, you MUST add a relative link to them in `epiphany_knowledge/indexes/topics-index.md`, followed by a brief, single-line description of what the topic covers. Create the index file if it doesn't exist.
     - Example: `- [Project Alpha](../topics/project-alpha.md) - Main topic tracking the development and architecture of Project Alpha.`
   - If you updated the summary of a daily note file (e.g., `epiphany_knowledge/parsed/notes/2026-04-09.md`), ensure that note file is listed in `epiphany_knowledge/indexes/sources-index.md` with a single-line summary of the day's events.
6. **Mark as Distilled:**
   - After successfully distilling a parsed entry or document, edit that file to replace the `[PENDING]` tag with `[DISTILLED]`.
7. **Validate:**
   - Ensure that the information from the parsed file being marked `[DISTILLED]` has actually been appropriately distilled into the topics.
   - Verify that all newly added facts in the Topic files include a valid citation link back to the source document.
   - Read back the parsed file to ensure `[DISTILLED]` replaced `[PENDING]` without corrupting the rest of the file.
   - Check the syntax of any new relative Markdown links you created in Topics or Indexes.
8. **Confirm:**
   - Respond to the user using the strict formatting outlined in the "Assistant Persona & Response Format" section below.

## Assistant Persona & Response Format

Always format your response to the user using the following template. You MUST include clickable relative Markdown links to any files you updated or created (e.g., `[project-alpha.md](epiphany_knowledge/topics/project-alpha.md)`).

```markdown
**Distillation Complete!**

### Updated Topics
- [[Topic Name]]([Relative Markdown Link])

### Summary of Changes
[Briefly describe what facts or action items were extracted and where they were placed]

### Open Questions / Conflicts
- [ ] [List any open questions or contradictions that need user clarification based on the distilled text, if any]
```

## Gotchas

- **Do NOT delete the parsed files.** Distillation is about copying the *meaning* into Topics. The original parsed file must remain as evidence.
- **Conflict Handling:** If the pending file contradicts existing information in a Topic, do NOT just overwrite the old info. Instead, record both perspectives and create an Open Question (`- [ ] Resolve conflict between...`) in the Topic file, citing both sources.
- **Relative Pathing:** Be extremely careful with relative paths. A Topic in `epiphany_knowledge/topics/topic.md` linking to a note in `epiphany_knowledge/parsed/notes/note.md` must use `../parsed/notes/note.md`.
- **Pending State:** Keep the source pending if contradictions, missing information, or unresolved ambiguity still block completion. Do not mark a source complete only because structural updates succeeded.
- **Git Commits:** If the workspace is a Git repository, after successful distillation, offer to make a commit for the user. Since the database might not be in your current directory, use the `git -C <path>` argument to run the commit command on the remote directory (e.g., `git -C path/to/knowledge add . && git -C path/to/knowledge commit -m "..."`). Show the exact command but wait for explicit approval.
