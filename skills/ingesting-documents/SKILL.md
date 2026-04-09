---
name: ingesting-documents
description: >
  Ingests documents (e.g., PDF, DOCX, TXT) and web URLs by copying them to a raw inputs directory and
  extracting them into parsed Markdown text. Use this skill when the user asks you to import, read,
  or ingest a file or a web link into the Knowledge Database.
---

# Ingesting Documents & URLs

This skill guides you through ingesting external files or web URLs into the Knowledge Database. The process preserves the raw original evidence while extracting a parsed Markdown version that is ready for distillation.

## Contract & Conventions

- **Database Location:** The Knowledge Database defaults to `knowledge/` in the current workspace. If you cannot find it, ask the user for permission to initialize it.
- **Raw Inputs:** Exact copies of documents or raw HTML from URLs MUST be saved to `knowledge/raw/docs/` or `knowledge/raw/urls/` respectively.
- **Parsed Text:** Extracted, readable Markdown MUST be saved to `knowledge/parsed/docs/` or `knowledge/parsed/urls/`.
- **Pending State:** Parsed files MUST be marked with `**Status:** Pending Distillation` at the top.
- **Index Update:** An explicit relative link to the parsed text MUST be added to `knowledge/indexes/sources-index.md`.

## Workflow

1. **Locate the Database:** Check if the Knowledge Database exists. Initialize it if the user approves.
2. **Fetch Raw Evidence:**
   - **For Documents:** Copy the original file (e.g., PDF, DOCX) into `knowledge/raw/docs/`.
   - **For URLs:** Fetch the content of the URL and save the raw HTML or text into `knowledge/raw/urls/`.
3. **Extract Text:**
   - Read the document or URL using your available tools.
   - Extract the meaningful text and convert it into a clean Markdown format.
4. **Save Parsed Markdown:**
   - Save the extracted Markdown into `knowledge/parsed/docs/` (or `urls/`), using a descriptive filename based on the source (e.g., `knowledge/parsed/docs/design-doc.md`).
   - Add the following header at the top of the new Markdown file:
     ```markdown
     # [Source Title or Filename]
     
     **Source:** [Path to raw file or original URL]
     **Status:** Pending Distillation
     
     ```
5. **Update Sources Index:**
   - Check if `knowledge/indexes/sources-index.md` exists. If not, create it.
   - Append an explicit relative Markdown link pointing to the newly parsed file.
     - Example: `- [Design Doc](../parsed/docs/design-doc.md)`
6. **Confirm:** Let the user know the document/URL has been ingested and is pending distillation.

## Gotchas

- **Do not distill yet:** Do not attempt to summarize or extract topics during this step. Your goal is simply to convert the source into a readable Markdown file that preserves the original information.
- **Handling Images/Binary Data:** If the source document contains images that you cannot extract, simply note `[Image omitted]` in the parsed Markdown text.
- **Relative Linking:** Always use relative links (e.g., `../parsed/docs/file.md`) when updating the `sources-index.md` to ensure the Knowledge Database is portable.
