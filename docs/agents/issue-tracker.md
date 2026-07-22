# Issue Tracker: Local Markdown

This repository uses a local Markdown-based issue tracker. Issues and feature tasks live as Markdown files under `.scratch/<feature>/` inside the repository.

## Workflow

1. **Feature Directories:** Work for a specific feature or bug is grouped under `.scratch/<feature-name>/`.
2. **Issue Files:** Individual issue specs and todo checklists are saved as `.md` files within that directory.
3. **Execution:** AI agent skills (`to-tickets`, `to-spec`, `qa`, `tdd`) read and write task specs directly to `.scratch/<feature-name>/`.
