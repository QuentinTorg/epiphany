---
name: querying-database
description: Queries the Knowledge Database for information across topics, documents, and logs. Use this skill when the user asks you a direct question about past work, decisions, people, projects, tasks, or any other knowledge stored in the database.
---

# Querying the Knowledge Database

This skill guides you through the process of searching the Knowledge Database to answer a user's question accurately, concisely, and with proper citations. Queries are meant to be interactive—you do not need to find a perfect answer immediately if the request is ambiguous.

## Contract & Conventions

- **Database Location:** The Knowledge Database defaults to a `knowledge/` directory in the current workspace root. If you cannot find the Knowledge Database, you MUST ask the user if they want to initialize it here or if it is located elsewhere.
- **Entrypoints:** You should generally begin your search at the Indexes (`knowledge/indexes/topics-index.md` or `knowledge/indexes/sources-index.md`).
- **Progressive Disclosure:** The primary intent of this database is progressive disclosure. Try to use the Indexes to find relevant Topics, read those Topics, and follow relative links (e.g., `[Source](../parsed/logs/2026-04-09.md)`) only if you need deeper context. 
- **Text Search (Grep):** Full-text search is a valuable tool in your arsenal. Use your best judgment: if index searches do not provide relevant leads, or if you need to find specific dates, names, or mentions across different topics and raw materials, use text search for breadth.
- **Accuracy & Hallucinations:** Accuracy is key. You MUST NOT hallucinate facts. Information should be based strictly on a raw source of truth.
- **Citations:** Every factual claim in your answer MUST include a citation pointing to the file that provided the information. 
- **Assumptions & Logical Leaps:** If you draw logical conclusions from the information provided, you MUST explicitly label them as such (e.g., "Assumption:" or "Logical Conclusion:") and justify how you reached them based on the cited sources.
- **Outside Information:** If you need to pull new information from outside resources (e.g., web search, general knowledge) to answer the query, you MUST prompt the user to ask if that new information should be added to the Knowledge Database instead of just answering and discarding it.
- **Interactivity:** If a query is unclear, confusing, or yields no initial results, ask the user for clarification. Requesting more details to help narrow down the search is highly encouraged.

## Workflow

1. **Locate the Database:** Identify the location of the `knowledge/` directory.
2. **Review Indexes (Primary Path):**
   - Read `knowledge/indexes/topics-index.md` to identify Topic files likely to contain the answer.
   - Read `knowledge/indexes/sources-index.md` if the question asks about a specific document or URL.
3. **Broad Text Search (Fallback/Breadth Path):**
   - If Indexes don't reveal clear leads, or you are looking for specific keywords/names, perform a text search across `knowledge/topics/` or `knowledge/parsed/`.
4. **Explore & Synthesize:**
   - Open the most relevant Topic files or search results.
   - If a Topic summary is too brief, follow its relative links back to the original `knowledge/parsed/` files for deeper context.
   - If you cannot find the answer, or if the request is ambiguous, stop and ask the user for clarification to help narrow the search.
5. **Validate:**
   - Double-check that every factual claim in your drafted answer has a corresponding citation.
   - Verify that your citations are formatted as valid, clickable relative Markdown links.
6. **Report:**
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

- **Progressive Disclosure vs. Search:** While text search is allowed and encouraged for finding specific details or casting a wide net, remember that Topics are designed to hold the distilled, current understanding. Prefer reading a summarized Topic over piecing together raw logs if the Topic exists.
- **Time/Entity Questions:** For queries like "What did Billy work on last week?", checking `knowledge/topics/billy.md` is a good start, but a text search for "Billy" inside recent `knowledge/parsed/notes/` might also be necessary.
- **Contradictions:** If you find contradictory information, present both sides in your answer, citing both sources. Do not pick a "winner" unless a more recent source explicitly resolves the conflict.
- **Answer Style:** Prefer concise answers over long narrative walkthroughs. Escalate from high-level topics into deeper evidence only when needed.
needed.
high-level topics into deeper evidence only when needed.
needed.
