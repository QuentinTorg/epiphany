---
name: ingesting-documents
description: Ingests documents (e.g., PDF, DOCX, TXT, ...) and web URLs by copying them to a raw inputs directory and extracting them into parsed Markdown text. Use this skill when the user asks you to import, read, or ingest a file or a web link into the Knowledge Database.
---

# Ingesting Documents & URLs

This skill guides you through ingesting external files or web URLs into the Knowledge Database. The process preserves the raw original evidence while extracting a parsed Markdown version that is ready for distillation.

## Contract & Conventions

- **Database Location:** The Knowledge Database defaults to a `knowledge/` directory in the current workspace root. If you cannot find the Knowledge Database, you MUST ask the user if they want to initialize it here or if it is located elsewhere.
- **Raw Inputs:** Exact copies of documents or raw HTML from URLs MUST be saved to `knowledge/raw/imports/`.
- **Parsed Text:** Extracted, readable Markdown MUST be saved to `knowledge/parsed/imports/`.
- **Pending State:** Parsed files MUST be marked with `[PENDING]` in their title header so the distilling agent knows they need to be processed.
- **Index Update:** An explicit relative link to the parsed text MUST be added to `knowledge/indexes/sources-index.md`.

## Workflow

1. **Locate the Database:** Check if the Knowledge Database exists. If not, prompt the user for permission to initialize the `knowledge/` structure or ask if it is located elsewhere.
2. **Fetch Raw Evidence:**
   - **For Documents:** Copy the original file (e.g., PDF, DOCX) into `knowledge/raw/imports/`.
   - **For URLs:** Fetch the content of the URL and save the raw HTML or text into `knowledge/raw/imports/`.
3. **Extract Text:**
   - Use whatever tools are at your disposal to extract text from the source. For example, you might use standard utilities like `pdftotext` for PDFs, `pandoc` for documents, or even write a quick Python script if no direct tool is available.
   - If the source is extremely large, try to process it in chunks to avoid overwhelming your context.
   - Convert the extracted text into a clean Markdown format. Prefer stable, repeatable text extraction over perfect formatting reconstruction.
   - If extraction completely fails, surface the failure clearly to the user instead of pretending the source was ingested successfully.
4. **Save Parsed Markdown:**
   - Save the extracted Markdown into `knowledge/parsed/imports/`, using a descriptive filename based on the source (e.g., `knowledge/parsed/imports/design-doc.md`).
   - Add the following header at the top of the new Markdown file:
     ```markdown
     # [Source Title or Filename] [PENDING]

     **Source:** [Path to raw file or original URL]

     ```
5. **Update Sources Index:**
   - Check if `knowledge/indexes/sources-index.md` exists. If not, create it.
   - Append an explicit relative Markdown link pointing to the newly parsed file.
     - Example: `- [Design Doc](../parsed/imports/design-doc.md)`
6. **Validate:** Read back the updated `sources-index.md` and the newly created markdown file to verify they were formatted correctly and the links are valid.
7. **Confirm & Offer Distillation:** Respond to the user using the strict formatting outlined in the "Assistant Persona & Response Format" section below.

## Assistant Persona & Response Format

Always format your response to the user using the following template. Ensure that the file path is formatted as a clickable relative Markdown link (e.g., `[design-doc.md](knowledge/parsed/imports/design-doc.md)`).

```markdown
**Document Ingested to [[File Path]]([Relative Markdown Link])!** [Add any brief observations or notes on extraction quality here, especially if images/data were omitted]

Would you like me to distill this newly ingested document into topics right now using the \`distilling-knowledge\` skill?
```

## Gotchas

- **Do not distill yet:** Do not attempt to summarize or extract topics during this step. Your goal is simply to convert the source into a readable Markdown file that preserves the original information.
- **Handling Images/Binary Data:** If the source document contains images that you cannot extract, simply note `[Image omitted]` in the parsed Markdown text.
- **Relative Linking:** Always use relative links (e.g., `../parsed/imports/file.md`) when updating the `sources-index.md` to ensure the Knowledge Database is portable.
