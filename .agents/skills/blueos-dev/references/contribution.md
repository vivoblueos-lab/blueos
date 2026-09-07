# Contribution Workflow

Repo-managed projects may start on detached HEAD. Create a branch in every changed project before committing:

```bash
repo start <branch> <project...>
```

Or create branches per project:

```bash
git -C kernel switch -c <branch>
```

Before committing, summarize and validate each repository independently:

```bash
git -C kernel status --short
git -C kernel diff --check
git -C kernel diff
```

Keep commits and PRs separated by manifest project. Commit and publish only when explicitly requested:

```bash
git -C kernel commit
git -C kernel push <user-remote> <branch>
```

For changes spanning repositories, read `book/src/prs.md`, create one PR per repository, and use `build_prs <url...>` only after the user authorizes posting that CI-trigger comment.

The handoff must state which repositories changed, checks run per repository, outstanding failures, and any PR or CI coordination still required.
