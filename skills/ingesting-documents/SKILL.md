---
name: ingesting-documents
description: Use this skill when the user wants to add an external document such as markdown, text, docx, or pdf into the workspace as evidence. It stages the source file, creates normalized text and an import record, then uses direct import-record edits plus structural follow-up for later deep distillation.
compatibility: Requires Python 3, a writable workspace root, and local PDF extraction support for pdf ingestion.
metadata:
  owner: epiphany
---

# Ingesting Documents

Use this skill to turn an external document into durable workspace evidence without loading the full source into context unnecessarily.

Read [../shared/references/agent-script-boundary.md](../shared/references/agent-script-boundary.md) before using this skill.
Read [../shared/references/workspace-model.md](../shared/references/workspace-model.md) when deciding what should remain evidence versus what should become derived state.
Read [../shared/references/action-item-policy.md](../shared/references/action-item-policy.md) when the imported source introduces clear operational state.
Read [references/ingestion-checklist.md](references/ingestion-checklist.md) before ingesting a large source.
Read [references/import-conversion-policy.md](references/import-conversion-policy.md) before choosing how to stage the source.
Read [references/large-document-reading.md](references/large-document-reading.md) before reading a large normalized source.
Read [references/import-distillation-policy.md](references/import-distillation-policy.md) when deciding whether to continue into deep reconciliation now.
Read [references/script-invocations.md](references/script-invocations.md) before running ingestion scripts if you need argument guidance.
Read [../shared/references/citation-rules.md](../shared/references/citation-rules.md) before editing the import record summary.

## Available scripts

- [scripts/ingest_document.py](scripts/ingest_document.py) — copy/register the source, create normalized text, and create the import record
- [scripts/sync_import_state.py](scripts/sync_import_state.py) — refresh import-record metadata and generated views after direct import-record edits

## Checklist

- ingest the source first
- read normalized text instead of the original binary when possible
- edit the import record directly
- sync structural state after the edit
- continue to deep distillation only if full reconciliation is needed now

## Workflow

1. If the workspace is not initialized yet, run `python ../shared/scripts/bootstrap_workspace.py ...` first.
2. Run `python scripts/ingest_document.py ...`.
3. Read the normalized text in `memory/imports/text/...`, not the original binary, unless the original artifact is required.
4. Edit the import record’s `## Source Summary`, `## Open Questions`, `## Candidate Action Items`, and `## Distillation Notes` directly.
5. If the document introduced explicit canonical action items, prepare the structured payload for them.
6. Run `python scripts/sync_import_state.py ...`.
7. By default, continue into `distilling-threads` if the user wants the import fully reconciled immediately.

## Validation Loop

- Confirm the original file, normalized text, and import record all exist.
- Confirm the import record preview matches the `## Source Summary`.
- Confirm `memory/views/imports.md` and `memory/views/pending-distillation.md` reflect the import.
- If canonical action items were passed, confirm they appear in `memory/views/action-items.md`.

## Gotchas

- Prefer normalized text over the original binary for reading and citation.
- The `## Source Summary` should be navigational, not exhaustive.
- `sync_import_state.py` does not summarize the document for you. Edit the import record first, then sync.
- The current workflow does not use a separate import-update wrapper. Use direct edits plus `sync_import_state.py`.
- Only call wrappers in `scripts/` or `../shared/scripts/`. Do not treat shared Python modules as normal entrypoints.
