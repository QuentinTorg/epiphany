---
name: querying-database
description: Queries the Knowledge Database for information across topics, documents, and notes. Use this skill when the user asks you a direct question about past work, decisions, people, projects, tasks, or any other knowledge stored in the database.
---

# Querying the Knowledge Database

This skill guides searching the Knowledge Database to answer questions accurately and with citations. Queries are interactive; ask for clarification if ambiguous.

## Contract & Conventions

- **Database Location:** The Knowledge Database defaults to a `knowledge/` directory in the current workspace root. If you cannot find the Knowledge Database, you MUST ask the user if they want to initialize it here or if it is located elsewhere.
- **Indexes:** The database maintains two index files as entrypoints:
  - `knowledge/indexes/topics-index.md`: A table of contents listing all the distilled subject summaries (Topics).
  - `knowledge/indexes/sources-index.md`: A table of contents listing all the raw imported documents and URLs that have been parsed.
- **Research Strategies:** Choose the best research strategy for the query:
  1. **Progressive Disclosure (Top-Down):** Start at Indexes to find Topic files, read Topics, and follow links to raw sources only if needed. Best for broad, conceptual queries.
  2. **Text Search / Grep (Bottom-Up):** Full-text search across `knowledge/`. Best for finding specific dates, names, or undiscovered mentions.
- **Scanning Summaries:** When opening a parsed file, read its `**Summary:**` first. Use it as an index to decide whether to read deeper or move on.
- **Accuracy & Hallucinations:** Accuracy is key. You MUST NOT hallucinate facts. Information should be based strictly on a raw source of truth.
- **Citations:** Every factual claim in your answer MUST include a citation pointing to the file that provided the information, formatted as a clickable relative Markdown link (e.g., `([Source](knowledge/topics/project-alpha.md))`).
- **Assumptions:** Explicitly label and justify any logical conclusions (e.g., "Assumption:" or "Logical Conclusion:").
- **Outside Information:** If pulling information from outside resources, ask the user if it should be added to the Knowledge Database.
- **Interactivity:** If a query is unclear or yields no results, ask the user for clarification.

## Workflow

1. **Locate the Database:** Check if the Knowledge Database exists. If not, prompt the user for permission to initialize the `knowledge/` structure or ask if it is located elsewhere.
2. **Determine Research Path:** Choose the best combination of strategies:
   - **Use Indexes & Links:** For broad concepts, read `topics-index.md`. For specific documents, read `sources-index.md`.
   - **Use Text Search:** For specific keywords or undiscovered leads, perform a text search across `knowledge/topics/` and/or `knowledge/parsed/`.
3. **Explore & Synthesize:**
   - Open the most relevant Topic files or search results.
   - Follow relative links back to original `knowledge/parsed/` files if deeper context is needed.
   - When exploring `knowledge/parsed/` files, read the `**Summary:**` at the top first to quickly map information.
   - If you cannot find the answer, or if the request is ambiguous, stop and ask the user for clarification to help narrow the search.
4. **Validate:**
   - Ensure every factual claim has a corresponding citation.
   - Verify that your citations are formatted as valid, clickable relative Markdown links.
5. **Report:**
   - Respond to the user using the strict formatting outlined in the "Assistant Persona & Response Format" section below.

## Assistant Persona & Response Format

Always format your response to the user using the following template. Ensure that all citations are clickable relative Markdown links (e.g., `([Source](knowledge/topics/project-alpha.md))`).

```markdown
**Query Results**

[Provide a concise, direct answer to the user's question here. Insert your citations inline right next to factual claims like this: ([Source](knowledge/topics/project-alpha.md)).]

[If you made any logical leaps or assumptions, explicitly list them here with "Assumption:" or "Logical Conclusion:"]

### Outside Information
[If you pulled outside knowledge not found in the database, explicitly ask the user if they want it added to the database here. Otherwise, omit this section.]
```

## Gotchas

- **Balancing Strategies:** Balance your tools: text search may return noise for broad topics, while relying only on indexes may miss recent raw notes. Use your judgment.
- **Time/Entity Questions:** For queries like "What did Billy work on?", check `billy.md` but also text-search recent notes for undiscovered facts.
- **Contradictions:** If you find contradictory information, present both sides in your answer, citing both sources. Do not pick a "winner" unless a more recent source explicitly resolves the conflict.
- **Answer Style:** Prefer concise answers over long narrative walkthroughs. Escalate from high-level topics into deeper evidence only when needed.