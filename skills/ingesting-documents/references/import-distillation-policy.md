# Import Distillation Policy

After ingestion:

- edit the import record directly
- sync structural state
- keep the import pending by default until deep reconciliation finishes

Go directly into deep distillation when:

- the user explicitly wants the import fully reconciled now
- the imported source is the main purpose of the current session

Do not assume an import is complete just because the file was copied and normalized.
