---
name: distilling-knowledge
description: >
  Reads "pending" parsed logs and documents, extracts relevant facts and action items, and updates
  the living Topic files and Indexes. Use this skill when the user asks you to distill, summarize,
  organize, or review pending knowledge in the database.
---

# Distilling Knowledge

This skill guides you through the process of reading freshly ingested raw material (logs, documents, URLs) that are marked as "Pending Distillation," and bubbling that information up into durable, cross-referenced Topic files.

## Contract & Conventions

- **Database Location:** The Knowledge Database defaults to `knowledge/` in the current workspace. If you cannot find it, ask the user for the location.
- **Pending Files:** A file in `knowledge/parsed/` (logs, docs, urls) is pending distillation if it contains the text `**Status:** Pending Distillation` at or near the top.
- **Topics (`knowledge/topics/`):** Living summaries of specific subjects (e.g., people, projects, systems, decisions). They are standard Markdown files.
- **Indexes (`knowledge/indexes/`):** Markdown files acting as a table of contents for Topics and Sources. You must update `topics-index.md` whenever you create a new Topic.
- **Action State:** Tasks and Open Questions must be extracted as simple Markdown checklists (`- [ ]`) embedded inside the relevant Topic files under an `## Action Items` or `## Open Questions` heading.
- **Relative Linking:** Whenever you reference a source document or another topic, you MUST use an explicit relative Markdown link (e.g., `[Design Doc](../parsed/docs/design-doc.md)`).
- **Clear Pending State:** Once a file has been completely distilled into the relevant Topics, you MUST remove the `**Status:** Pending Distillation` line from it, replacing it with `**Status:** Distilled on YYYY-MM-DD`.

## Workflow

1. **Locate Pending Files:**
   - Search the `knowledge/parsed/` directory (including `logs`, `docs`, `urls`) for any files containing `**Status:** Pending Distillation`.
2. **Review & Extract:**
   - Read the contents of each pending file.
   - Identify the core entities, decisions, topics, tasks, and open questions.
3. **Update or Create Topics:**
   - For each major subject identified, locate its corresponding Topic file in `knowledge/topics/` (e.g., `project-alpha.md`).
   - If the Topic file doesn't exist, create it.
   - Summarize the new findings and append/integrate them into the Topic file.
   - **Crucial:** Cite your sources! When adding facts to a Topic, link back to the parsed file that provided the fact (e.g., `Decided to use Postgres ([Source](../parsed/logs/2026-04-09.md))`).
   - If new tasks or open questions are found, add them as `- [ ]` checklist items within the Topic.
4. **Update Indexes:**
   - If you created any *new* Topic files, you MUST add a relative link to them in `knowledge/indexes/topics-index.md`. Create the index file if it doesn't exist.
5. **Mark as Distilled:**
   - After successfully distilling a parsed file, edit that file to change `**Status:** Pending Distillation` to `**Status:** Distilled on YYYY-MM-DD` (using the current date).
6. **Confirm:**
   - Summarize to the user which files were distilled and which Topics were updated.

## Gotchas

- **Do NOT delete the parsed files.** Distillation is about copying the *meaning* into Topics. The original parsed file must remain as evidence.
- **Conflict Handling:** If the pending file contradicts existing information in a Topic, do NOT just overwrite the old info. Instead, record both perspectives and create an Open Question (`- [ ] Resolve conflict between...`) in the Topic file, citing both sources.
- **Relative Pathing:** Be extremely careful with relative paths. A Topic in `knowledge/topics/topic.md` linking to a log in `knowledge/parsed/logs/log.md` must use `../parsed/logs/log.md`.
- **Pending State:** Keep the source pending if contradictions, missing information, or unresolved ambiguity still block completion. Do not mark a source complete only because structural updates succeeded.
- **Git Commits:** If the workspace is a Git repository, after successful distillation, offer to make a commit for the user. Show the exact `git commit` command but wait for explicit approval.
