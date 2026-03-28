# Ingestion Checklist

Before ingesting:

- pick a clear title
- prefer `.md`, `.txt`, `.docx`, or `.pdf`
- if the source is large, plan to read the normalized text in chunks

After ingesting:

1. Open the normalized text file and identify the relevant chunks.
2. Write a navigational `## Source Summary`.
3. Extract only explicit or clearly supported action items.
4. Run `sync_import_state.py`.
5. If the import should be fully reconciled now, switch to `distilling-threads`.

For PDF ingestion:

- the workspace needs a local extractor such as `pdftotext`
- if extraction fails, tell the user rather than pretending the text was available
