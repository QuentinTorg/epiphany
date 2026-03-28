# Agent-Script Boundary

Use this project with one strict rule:

- agents do semantic work
- scripts do mechanical work

Semantic work:

- writing summaries
- deciding which topics are affected
- deciding which action items or open questions exist
- deciding how evidence changes current understanding
- synthesizing answers for the user

Mechanical work:

- creating files
- appending raw evidence
- stamping timestamps
- maintaining frontmatter
- validating document structure
- moving files between lifecycle locations
- rebuilding generated views and indexes
- applying already-authored structured results

Do not ask a script to figure out what a summary should say.
Do not ask a script to decide how a topic changes.

Use scripts after semantic edits to keep the workspace structurally consistent.
