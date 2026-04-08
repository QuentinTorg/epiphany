# Close-Thread Git Prompt

Use this only during an explicit close-thread workflow.

If deep distillation succeeds and the workspace root is a Git repository:

- tell the user this is a good time to make a commit
- offer to make the commit
- show the exact `git commit` command before asking for confirmation
- do not create the commit without explicit approval

Skip this entire behavior when:

- the workspace is not a Git repository
- the user did not ask to close the thread
- deep distillation did not succeed
