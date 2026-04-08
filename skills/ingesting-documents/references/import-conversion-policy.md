# Import Conversion Policy

For v1, supported inputs are:

- `.md`
- `.txt`
- `.docx`
- `.pdf`

Ingestion must preserve:

- the original source file in `memory/imports/files/`
- a normalized text representation in `memory/imports/text/`
- an import record in `memory/imports/records/`

Prefer stable, repeatable text extraction over clever formatting reconstruction.

If conversion fails, preserve the original file and surface the failure clearly instead of pretending the source was ingested successfully.
