# Agentic Notes Workspace

This repository contains planning and specification work for an agent-assisted notes workspace.

Primary document:

- [docs/product-spec.md](docs/product-spec.md)
- [docs/implementation-spec.md](docs/implementation-spec.md)
- [docs/implementation-spec-outline.md](docs/implementation-spec-outline.md)
- [docs/implementation-roadmap.md](docs/implementation-roadmap.md)

Background notes:

- [project_goals_freeform.md](project_goals_freeform.md)

## Running Tests

Unit tests live under [tests](tests).

Run the full unit test suite from the repository root with:

```bash
pytest -q
```

Run a single test file with:

```bash
pytest -q tests/test_bootstrap.py
pytest -q tests/test_capture_flow.py
```

Current test coverage is focused on the first implementation slice:

- workspace bootstrap and generated seed files,
- Git ignore handling for runtime state,
- thread creation during note capture,
- thread-local summary and status updates.
- wrapper JSON-envelope behavior and actionable error handling,
- canonical action-item creation and filtering.
