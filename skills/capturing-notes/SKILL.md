---
name: capturing-notes
description: Captures raw user notes and appends them to a chronologically ordered daily log within the Knowledge Database. Use this skill when the user asks you to "remember" something, "capture" a note, record meeting notes, or save raw thoughts and details so they can be distilled later.
---

# Capturing Notes

This skill guides you through capturing raw user notes and appending them to a chronologically ordered daily log within the Knowledge Database.

## Contract & Conventions

- **Database Location:** The Knowledge Database defaults to a `knowledge/` directory in the current workspace root. If you cannot find the Knowledge Database, you MUST ask the user if they want to initialize it here or if it is located elsewhere.
- **File Path:** Captured notes MUST be appended to `knowledge/parsed/logs/YYYY-MM-DD.md` where `YYYY-MM-DD` is the current date.
- **Format:** Group consecutive notes under hour-level timestamps (`HH:00`) instead of creating a new heading for every minute. This maintains readability when a user provides rapid-fire notes. Append the raw content exactly as provided, usually as bullet points or consecutive paragraphs.
- **Pending State:** The hour-level heading MUST be marked with a `[PENDING]` tag if any note underneath it has not been distilled yet.

## Workflow

1. **Locate the Database:** Check if `knowledge/parsed/logs/` exists. If not, prompt the user for permission to initialize the `knowledge/` structure.
2. **Determine Time:** Determine today's date (`YYYY-MM-DD`) and the current hour (`HH:00`).
3. **Initialize Daily Log (if needed):**
   If `knowledge/parsed/logs/YYYY-MM-DD.md` does not exist, create it with the following template:
   ```markdown
   # Daily Log: YYYY-MM-DD

   ```
4. **Append Note:**
   - Check if an hour-level heading for the current hour (e.g., `## 14:00 [PENDING]` or `## 14:00 [DISTILLED]`) already exists.
   - If it does **not** exist, append a new heading and the note:
     ```markdown
     ## HH:00 [PENDING]

     - [Raw note text goes here]
     ```
   - If it **does** exist, append the note under the existing heading as a new bullet or paragraph. If the heading is currently marked `[DISTILLED]`, change it back to `[PENDING]` so the distilling agent knows new information has arrived.DO NOT change any of the previously logged information
5. **Validate:** Read the file back to verify the note was appended correctly under the `## HH:00 [PENDING]` heading without corrupting previous content.
6. **Read Context:** Before replying, read the contents of today's log to understand the full context of what has been captured so far, even if it was captured in a previous session. Identify any missing context that would improve the clarity of the note, or open questions.
7. **Confirm & Assist:** Respond to the user using the strict formatting outlined in the "Assistant Persona & Response Format" section below.

## Assistant Persona & Response Format

You are an active participant in the note-taking process, not just a passive transcriber. If a note lacks context or seems unclear, point it out to the user to ensure the final distilled knowledge is as informative as possible.

Always format your response to the user using the following template:

```markdown
**Note Captured to `[File Path]`!** [Add any brief observations, missing context, or inconsistencies you noticed here]

### Current Context (HH:00)
> [Quote the recent notes captured in the current hour block so the user has an anchor of what was just recorded]

### Open Questions
- [ ] [Explicit question the user asked]
- [ ] [Clarifying question you generated because the provided info was ambiguous]
```

## Gotchas

- **Do not summarize during capture:** Your job right now is purely to capture the raw evidence into the log. Do not attempt to rephrase, summarize, or distill the note yet. Preserve the exact fidelity of the user's input.
- **Capture first, clarify later:** Never block raw capture on perfect categorization or complete context. Capture the raw input first, then use your response to ask clarifying questions.
- **Missing directories:** Use file creation tools that automatically create parent directories if `knowledge/parsed/logs/` does not exist yet (assuming the user approved initialization).
