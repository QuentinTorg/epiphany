# Workspace Model

The workspace has three durable layers:

- evidence:
  - thread snippets
  - imported source files
  - normalized import text
- derived understanding:
  - thread summaries
  - import summaries
  - topic documents
- derived operational state:
  - canonical action-item documents
  - generated operational views

Use this model when deciding where information belongs.

- Raw user input belongs in evidence.
- Natural-language synthesis belongs in derived understanding.
- tasks, blockers, and unresolved questions that must stay queryable belong in canonical action-item state.

Do not replace evidence with summaries.
Do not hide operational state only inside prose.
