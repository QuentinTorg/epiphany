# Action-Item Policy

Use canonical action items for operational state that must remain visible and queryable.

Create or update an action item when:

- the user explicitly assigns or requests work,
- a source clearly states a blocker or unresolved question,
- a follow-up is strongly implied and useful to track.

Do not create canonical action items for:

- weak hunches with no operational value,
- every passing mention of work,
- notes that are still too ambiguous to distinguish from background context.

Kinds and intent:

- `task`: work to be done
- `question`: unresolved ambiguity, blocker, contradiction, or missing detail

Confidence:

- `explicit`
- `inferred`
- `tentative`

When uncertain, prefer tentative state or ask the user rather than manufacturing confident operational state.
