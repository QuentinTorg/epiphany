---
name: capturing-notes
description: Captures user notes and appends them to a daily log in the Epiphany Knowledge Database. Use this immediately when the user explicitly asks you to "remember" something, "capture" a note, or save details. You may also use this proactively to log valuable, enduring technical context (e.g., when the user explains facts about a system/environment, workflows, recurring issues, or long-standing bugs that were just resolved). DO NOT log transient session state, conversational interactions, or bugs that were created and fixed entirely within the current session.
---

# Capturing Notes

This skill guides you through capturing user notes and appending them to a chronologically ordered daily note file within the Epiphany Knowledge Database.

## Contract & Conventions

- **Database Location:** The Epiphany Knowledge Database defaults to a `epiphany_knowledge/` directory in the current workspace root. If you cannot find the Epiphany Knowledge Database, you MUST ask the user if they want to initialize it here or if it is located elsewhere.
- **File Path:** Captured notes MUST be appended to `epiphany_knowledge/parsed/notes/YYYY-MM-DD.md` where `YYYY-MM-DD` is the current date.
- **Format:** Group consecutive notes under hour-level timestamps (`HH:00`) instead of creating a new heading for every minute. This maintains readability when a user provides rapid-fire notes. You should fix obvious typos and break the input up into clear bullet points to improve readability, but you MUST directly use the user's original language and phrasing. Do not rewrite their input in your own voice.
- **Pending State:** The hour-level heading MUST be marked with a `[PENDING]` tag if any note underneath it has not been distilled yet.
- **Open Questions:** Unresolved questions should accumulate at the bottom of the daily log under an `## Open Questions` heading so they are not forgotten.
- **Global Context:** You MUST silently read the entirety of `epiphany_knowledge/context.md` (if it exists) to establish baseline context. You are strictly forbidden from modifying it.

## Workflow

1. **Locate the Database:** Check if `epiphany_knowledge/parsed/notes/` exists. If not, prompt the user for permission to initialize the `epiphany_knowledge/` structure. When prompting for initialization, you MUST also ask the user to provide a brief description of themselves, their role, and their core priorities so you can create the initial `epiphany_knowledge/context.md` file (using the standard format and Telegraphic Style). You are authorized to create this file during initialization, but you may not modify it afterwards.
2. **Determine Time:** Determine today's date (`YYYY-MM-DD`) and the current hour (`HH:00`).
3. **Initialize Daily Log (if needed):**
   If `epiphany_knowledge/parsed/notes/YYYY-MM-DD.md` does not exist, create it with the following template:
   ```markdown
   # Daily Log: YYYY-MM-DD

   ## Open Questions
   
   ```
4. **Append Note:**
   - Check if an hour-level heading for the current hour (e.g., `## 14:00 [PENDING]` or `## 14:00 [DISTILLED]`) already exists.
   - If it does **not** exist, append a new heading and the note above the `## Open Questions` section:
     ```markdown
     ## HH:00 [PENDING]

     - [Note text goes here]
     ```
   - If it **does** exist, append the note under the existing heading as a new bullet or paragraph. If the heading is currently marked `[DISTILLED]`, change it back to `[PENDING]` so the distilling agent knows new information has arrived. DO NOT change any of the previously logged information.
5. **Manage Open Questions:** Only generate clarifying questions if the missing context makes the note ambiguous or materially reduces its future value. Do not generate questions just for the sake of conversation. Append new questions as checklist items (`- [ ]`) under the `## Open Questions` heading at the bottom of the daily log. On every turn, re-evaluate the existing open questions. If a question is answered by the new note, or if you determine a question is low-value, stale, or no longer relevant, remove it from the list entirely to keep the tracker lean and actionable.
6. **Read Context:** Before replying, always silently read `epiphany_knowledge/context.md` (if it exists) to understand the user's established terminology, relationships, and identity so you do not ask redundant clarifying questions. Then, read the contents of today's log to understand the full context of what has been captured. If the user's note references unknown concepts, people, or projects not found in `context.md`, use your standard file search tools to quickly scan the existing database (`epiphany_knowledge/indexes/` or `epiphany_knowledge/topics/`) to establish context. Do not invoke the `querying-database` skill for this internal lookup. Identify any critical missing context that would improve the clarity of the note.
7. **Validate:** Read the file back to verify the note was appended correctly under the `## HH:00 [PENDING]` heading without corrupting previous content or the open questions section.
8. **Confirm & Assist:** Respond to the user using the strict formatting outlined in the "Assistant Persona & Response Format" section below.

## Assistant Persona & Response Format

You are an active participant in the note-taking process, not just a passive transcriber. If a note lacks context or seems unclear, point it out to the user to ensure the final distilled knowledge is as informative as possible.

Always format your response to the user using the following template. Ensure that the file path is formatted as a clickable relative markdown link (e.g., `[2026-04-09.md](epiphany_knowledge/parsed/notes/2026-04-09.md)`):

```markdown
**Note Captured to [[File Path]]([Relative Markdown Link])!** [Add any brief observations, missing context, or inconsistencies you noticed here]

### Current Context (HH:00)
> [Quote the recent notes captured in the current hour block so the user has an anchor of what was just recorded]

### Open Questions Tracker
[List the current unresolved questions from the daily log here, so the user has visibility]
```

## Gotchas

- **Do not summarize or revoice during capture:** Your job is to capture the raw evidence. While you should fix typos and organize into bullets, DO NOT attempt to summarize, distill, or rewrite the note in your own "terse" or "assistant" voice. Use the user's exact wording.
- **NEVER apply the `[DISTILLED]` tag:** As the note taker, you are strictly forbidden from marking any heading as `[DISTILLED]`. Even if a meeting is over or an hour has passed, new blocks MUST be marked `[PENDING]`. Only the `distilling-knowledge` skill may apply the `[DISTILLED]` tag.
- **Missing directories:** Use file creation tools that automatically create parent directories if `epiphany_knowledge/parsed/notes/` does not exist yet (assuming the user approved initialization).
DISTILLED]` tag.
- **Missing directories:** Use file creation tools that automatically create parent directories if `epiphany_knowledge/parsed/notes/` does not exist yet (assuming the user approved initialization).
