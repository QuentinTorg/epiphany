---
name: capturing-notes
description: >
  Captures raw user notes and appends them to a chronologically ordered daily log within the Knowledge Database.
  Use this skill when the user asks you to "remember" something, "capture" a note, record meeting notes, or
  save raw thoughts and details so they can be distilled later.
---

# Capturing Notes

This skill guides you through capturing raw user notes and appending them to a chronologically ordered daily log within the Knowledge Database.

## Contract & Conventions

- **Database Location:** The Knowledge Database defaults to a `knowledge/` directory in the current workspace root. If you cannot find the Knowledge Database, you MUST ask the user if they want to initialize it here or if it is located elsewhere.
- **File Path:** Captured notes MUST be appended to `knowledge/parsed/logs/YYYY-MM-DD.md` where `YYYY-MM-DD` is the current date.
- **Format:** Every captured snippet MUST include a timestamp (`HH:MM`) heading, followed by the raw content exactly as the user provided it.
- **Pending State:** If a log file receives new notes, it MUST contain a clear indicator that it is awaiting distillation (e.g., `**Status:** Pending Distillation` at the top of the file).

## Workflow

1. **Locate the Database:** Check if `knowledge/parsed/logs/` exists. If not, prompt the user for permission to initialize the `knowledge/` structure.
2. **Determine Time:** Determine today's date (`YYYY-MM-DD`) and the current time (`HH:MM`).
3. **Initialize Daily Log (if needed):**
   If `knowledge/parsed/logs/YYYY-MM-DD.md` does not exist, create it with the following template:
   ```markdown
   # Daily Log: YYYY-MM-DD
   
   **Status:** Pending Distillation
   
   ```
4. **Update Pending State:**
   If the file already exists but does NOT have the `**Status:** Pending Distillation` indicator (because it was previously distilled), add the indicator back to the top of the file just below the title.
5. **Append Note:**
   Append the user's raw note exactly as provided, prefixed with the current timestamp heading:
   ```markdown
   ## HH:MM
   
   [Raw note text goes here]
   ```
6. **Confirm:** Let the user know the note was successfully captured and is pending distillation.

## Gotchas

- **Do not summarize during capture:** Your job right now is purely to capture the raw evidence. Do not attempt to rephrase, summarize, or distill the note yet. Preserve the exact fidelity of the user's input.
- **Capture first, clarify later:** Never block raw capture on perfect categorization. Capture the raw input first, then clarify if needed.
- **Missing directories:** Use file creation tools that automatically create parent directories if `knowledge/parsed/logs/` does not exist yet (assuming the user approved initialization).
