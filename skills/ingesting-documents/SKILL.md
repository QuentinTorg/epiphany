---
name: ingesting-documents
description: Ingests documents (e.g., PDF, DOCX, TXT, ...) and web URLs by copying them to a raw inputs directory and extracting them into parsed Markdown text. Use this skill when the user asks you to import, read, or ingest a file or a web link into the Epiphany Knowledge Database.
---

# Ingesting Documents & URLs

This skill guides you through ingesting external files or web URLs into the Epiphany Knowledge Database. The process preserves the raw original evidence while extracting a parsed Markdown version that is ready for distillation.

## Contract & Conventions

- **Database Location:** The Epiphany Knowledge Database defaults to a `epiphany_knowledge/` directory in the current workspace root. If you cannot find the Epiphany Knowledge Database, you MUST ask the user if they want to initialize it here or if it is located elsewhere.
- **Global Context:** You MUST silently read the entirety of `epiphany_knowledge/context.md` (if it exists) to understand the user's perspective. You are strictly forbidden from modifying it.
- **Raw Inputs:** Exact copies of binary documents (e.g., PDFs, DOCX) or raw HTML from URLs MUST be saved to `epiphany_knowledge/raw/imports/`. If the source is already a plain-text or readable data file (e.g., `.txt`, `.md`, `.csv`, `.json`, source code), you may skip saving it to the `raw` directory and proceed directly to parsing.
- **Parsed Text:** Extracted, readable Markdown MUST be saved to `epiphany_knowledge/parsed/imports/`.
- **Pending State:** Parsed files MUST be marked with `[PENDING]` in their title header so the distilling agent knows they need to be processed.
- **Index Update:** An explicit relative link to the parsed text MUST be added to `epiphany_knowledge/indexes/sources-index.md`.

## Workflow

1. **Locate the Database:** Check if the Epiphany Knowledge Database exists. If not, prompt the user for permission to initialize the `epiphany_knowledge/` structure or ask if it is located elsewhere.
2. **Fetch Raw Evidence:**
   - **For Documents:** If the document is a binary format (e.g., PDF, DOCX), copy the original file into `epiphany_knowledge/raw/imports/`. If it is already plain-text or readable data (e.g., `.md`, `.txt`, `.csv`, `.json`), you may skip this step.
   - **For URLs:** Fetch the content of the URL and save the raw HTML or text into `epiphany_knowledge/raw/imports/`.
3. **Extract Text:**
   - Use standard utilities like `pdftotext` for PDFs or `pandoc` for documents to extract text. 
   - **Tooling Requirement:** If your preferred, high-quality extraction tool is missing from the system, DO NOT fall back to an inferior or lossy custom script. Instead, pause the workflow and explicitly ask the user to install the required tooling (e.g., "Please install `poppler-utils` to process this PDF").
   - **Handling Images & Diagrams (PDFs, DOCX, PPTX):** Standard text extraction tools often drop or poorly format images. To preserve critical diagrams without wasting context tokens on full-page rendering:
     1. **Extract Base Text:** Use `pdftotext` for PDFs, or `pandoc` for DOCX/PPTX to extract the core text document.
     2. **Extract Image Assets:**
        - *For PDFs:* Use `pdfimages -png <file.pdf> <output_prefix>` to extract embedded images to a temporary directory.
        - *For DOCX/PPTX:* Since these are zipped XML archives, use `unzip -j <file.docx> "word/media/*" -d <temp_dir>` or `unzip -j <file.pptx> "ppt/media/*" -d <temp_dir>` to extract the raw images.
     3. **Review & Filter:** Review the extracted images using your vision capabilities. Ignore purely decorative images (e.g., logos, backgrounds, simple icons) to save context.
     4. **Describe Data:** For images containing important information (charts, diagrams, dense tables), write a detailed Markdown description of the visual data.
     5. **Contextual Insertion:** Search the extracted text for context clues (e.g., "Figure 1 shows...", "As seen in the chart...") to determine where the image description belongs, and insert your text description there. If you cannot confidently determine the exact location, append a `## Extracted Diagrams & Images` section at the end of the parsed document and list the descriptions there.
   - Convert the extracted text into a clean Markdown format. 
   - If the source is extremely large, try to process it in chunks to avoid overwhelming your context.
   - If extraction completely fails, surface the failure clearly to the user instead of pretending the source was ingested successfully.
4. **Save Parsed Markdown:**
   - Save the extracted Markdown into `epiphany_knowledge/parsed/imports/`, using a descriptive filename based on the source (e.g., `epiphany_knowledge/parsed/imports/design-doc.md`).
   - Add the following header at the top of the new Markdown file:
     ```markdown
     # [Source Title or Filename] [PENDING]

     **Source:** [Path to raw file or original URL]

     ```
5. **Update Sources Index:**
   - Check if `epiphany_knowledge/indexes/sources-index.md` exists. If not, create it.
   - Append an explicit relative Markdown link pointing to the newly parsed file, followed by a brief, single-line description of its contents.
     - Example: `- [Design Doc](../parsed/imports/design-doc.md) - Raw imported PDF containing the v2 architecture design.`
6. **Validate:** Read back the updated `sources-index.md` and the newly created markdown file to verify they were formatted correctly and the links are valid.
7. **Confirm & Assist:** Respond to the user using the strict formatting outlined in the "Assistant Persona & Response Format" section below.

## Assistant Persona & Response Format

Always format your response to the user using the following template. Ensure that the file path is formatted as a clickable relative Markdown link (e.g., `[design-doc.md](epiphany_knowledge/parsed/imports/design-doc.md)`).

```markdown
**Document Ingested to [[File Path]]([Relative Markdown Link])!** [Add any brief observations or notes on extraction quality here]

### Missing Context
[Ask the user a clarifying question about how this document connects to the rest of the world. E.g., "What is the specific context of this document? How does it relate to our existing projects or goals?"]

Would you like me to distill this newly ingested document into topics right now using the \`distilling-knowledge\` skill?
```

## Gotchas

- **Do not distill yet:** Do not attempt to summarize or extract topics during this step. Your goal is simply to convert the source into a readable Markdown file that preserves the original information.
- **Handling Decorative Images:** If a document contains images that are purely decorative or completely irrelevant to the data, simply note `[Decorative image omitted]` in the parsed Markdown text so you do not waste context describing it. For important images, use your vision capabilities to describe them as instructed in the workflow.
- **Relative Linking:** Always use relative links (e.g., `../parsed/imports/file.md`) when updating the `sources-index.md` to ensure the Epiphany Knowledge Database is portable.
