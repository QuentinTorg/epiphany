# Script Invocations

Use these command shapes for normal document-ingestion workflows.

## `ingest_document.py`

Always provide:

- `--source-path`
- `--title`

Use only when needed:

- `--slug`
- `--imported-at`
- `--workspace-root`
- `--dry-run`

Examples:

```bash
python scripts/ingest_document.py \
  --source-path ./docs/vendor-quote.pdf \
  --title "Vendor Quote"
```

```bash
python scripts/ingest_document.py \
  --source-path ./notes/requirements.docx \
  --title "Rover 3 Requirements" \
  --slug rover-3-requirements
```

Only pass `--slug` when you need a stable custom slug instead of the default derived slug.

Use `--imported-at` only when the import must be recorded with a non-current import time.

Use `--workspace-root` only when the current working directory is not already the target workspace root.

Use `--dry-run` only for preview or verification.

## `sync_import_state.py`

Always provide:

- `--import-record-path`

Use only when needed:

- `--canonical-action-items-json`
- `--workspace-root`
- `--dry-run`

Example:

```bash
python scripts/sync_import_state.py \
  --import-record-path memory/imports/records/2026/2026-04-08-rover-3-requirements.md
```

Run this only after you already edited the import record directly.

Pass `--canonical-action-items-json` only when you already prepared explicit canonical action-item upserts.

Use `--workspace-root` only when the current working directory is not already the target workspace root.

Use `--dry-run` only for preview or verification.
