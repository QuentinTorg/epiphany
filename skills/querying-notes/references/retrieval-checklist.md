# Retrieval Checklist

Use this order unless there is a strong reason to skip a step:

1. `memory/README.md`
2. The relevant generated view or typed topic index
3. Candidate topic or action-item documents
4. Thread documents or import records
5. Thread snippets or normalized import text for supporting evidence
6. Original imported file only when the normalized text is insufficient

Use `query_memory.py` when:

- the question spans many files
- the user asks by time, topic, entity, or source
- you want pending-distillation warnings before answering

Use `list_action_items.py` when:

- the user asks what is open, blocked, assigned, or due
- the user asks for project/person/task slices of operational state
