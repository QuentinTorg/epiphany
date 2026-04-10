---
name: querying-database
description: Queries the Knowledge Database for information across topics, documents, and notes. Use this skill when the user asks you a direct question about past work, decisions, people, projects, tasks, or any other knowledge stored in the database.
---

# Querying the Knowledge Database

This skill guides you through the process of searching the Knowledge Database to answer a user's question accurately, concisely, and with proper citations. Queries are meant to be interactive—you do not need to find a perfect answer immediately if the request is ambiguous.

## Contract & Conventions

- **Database Location:** The Knowledge Database defaults to a `knowledge/` directory in the current workspace root. If you cannot find the Knowledge Database, you MUST ask the user if they want to initialize it here or if it is located elsewhere.
- **Research Strategies:** You are empowered to use the best research strategy for the query at hand. Two primary methods exist, each with different strengths:
  1. **Progressive Disclosure (Top-Down):** Starting at the Indexes (`knowledge/indexes/`) to find relevant Topic files, reading those Topics, and following relative links to raw sources only if deeper context is needed. This is highly effective for broad, conceptual queries where the knowledge has already been distilled.
  2. **Text Search / Grep (Bottom-Up):** Using full-text search across `knowledge/topics/` or `knowledge/parsed/`. This is highly effective for discovering specific dates, names, exact quotes, or finding mentions of a topic that haven't been fully distilled yet. 
- **Scanning Summaries:** When opening a raw parsed file (like a document or daily note), read the `**Summary:**` section at the top first. This summary acts as an index; use it to decide if you need to continue reading the rest of the file or if you can move on to your next search target.
- **Accuracy & Hallucinations:** Accuracy is key. You MUST NOT hallucinate facts. Information should be based strictly on a raw source of truth.
- **Citations:** Every factual claim in your answer MUST include a citation pointing to the file that provided the information, formatted as a clickable relative Markdown link (e.g., `([Source](knowledge/topics/project-alpha.md))`).
- **Assumptions & Logical Leaps:** If you draw logical conclusions from the information provided, you MUST explicitly label them as such (e.g., "Assumption:" or "Logical Conclusion:") and justify how you reached them based on the cited sources.
- **Outside Information:** If you need to pull new information from outside resources (e.g., web search, general knowledge) to answer the query, you MUST prompt the user to ask if that new information should be added to the Knowledge Database instead of just answering and discarding it.
- **Interactivity:** If a query is unclear, confusing, or yields no initial results, ask the user for clarification. Requesting more details to help narrow down the search is highly encouraged.

## Workflow

1. **Locate the Database:** Check if the Knowledge Database exists. If not, prompt the user for permission to initialize the `knowledge/` structure or ask if it is located elsewhere.
2. **Determine Research Path:** Based on the user's prompt, choose the most effective combination of research strategies:
   - **Use Indexes & Links:** If the question is about a broad concept or established project, read `topics-index.md` to find relevant Topic files. If the question asks about a specific document or URL, read `sources-index.md`.
   - **Use Text Search:** If the question involves a specific keyword, person, date, or undiscovered lead, perform a text search across `knowledge/topics/` and/or `knowledge/parsed/`.
3. **Explore & Synthesize:**
   - Open the most relevant Topic files or search results.
   - Follow relative links back to original `knowledge/parsed/` files if deeper context is needed.
   - When exploring `knowledge/parsed/` files, always read the `**Summary:**` at the top first. Scanning these short, dense summaries is a fast and effective way to discover information alongside your other search methods.
   - If you cannot find the answer, or if the request is ambiguous, stop and ask the user for clarification to help narrow the search.
4. **Validate:**
   - Double-check that every factual claim in your drafted answer has a corresponding citation.
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

- **Balancing Strategies:** Different queries require different approaches. A full text search might return too much noise for a broad topic (where a distilled Topic file is better), but relying only on Indexes might cause you to miss an important detail buried in yesterday's raw notes. Use your best judgment to balance the tools available to you.
- **Time/Entity Questions:** For queries like "What did Billy work on last week?", checking `knowledge/topics/billy.md` is a good conceptual start, but a text search for "Billy" inside recent `knowledge/parsed/notes/` will likely be necessary to find raw, undiscovered facts.
- **Contradictions:** If you find contradictory information, present both sides in your answer, citing both sources. Do not pick a "winner" unless a more recent source explicitly resolves the conflict.
- **Answer Style:** Prefer concise answers over long narrative walkthroughs. Escalate from high-level topics into deeper evidence only when needed.swer, citing both sources. Do not pick a "winner" unless a more recent source explicitly resolves the conflict.
- **Answer Style:** Prefer concise answers over long narrative walkthroughs. Escalate from high-level topics into deeper evidence only when needed.