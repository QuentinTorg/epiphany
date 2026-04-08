# Recovery Policy

Interrupted work must remain recoverable from durable state.

Use `memory/views/pending-distillation.md` as the recovery queue.

When recovering:

1. identify the pending source
2. read its current summary and distillation notes
3. inspect directly linked topics and action items
4. continue the semantic reconciliation work
5. apply the result structurally

Leave the source pending when:

- contradictions remain unresolved
- user clarification is still required
- the semantic reconciliation is incomplete

Do not mark a source complete only because structural updates succeeded.
