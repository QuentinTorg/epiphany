# Workspace Navigation

Use progressive disclosure.

1. Start at `memory/README.md`.
2. Read the relevant generated view:
   - `memory/views/open-threads.md`
   - `memory/views/pending-distillation.md`
   - `memory/views/action-items.md`
   - `memory/views/imports.md`
3. Read the relevant typed topic index under `memory/topics/`.
4. Open the most likely thread, topic, action-item, or import record.
5. Only then drill into thread snippets or normalized import text for evidence.

Directory roles:

- `memory/threads/`: raw captured note sessions
- `memory/imports/files/`: original imported bytes
- `memory/imports/text/`: normalized import text with stable chunk anchors
- `memory/imports/records/`: navigational import-state documents
- `memory/topics/`: canonical durable knowledge by type
- `memory/action-items/`: canonical tasks and questions
- `memory/views/`: generated navigation and operational views

When querying, prefer `query_memory.py` and `list_action_items.py` to narrow the search space before opening full documents.
