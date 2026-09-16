# Contribution Workflow

Check the current state first. If the checkout is detached, create or select a branch before committing:

```bash
git status --short --branch
git switch -c <branch>
```

Before committing, summarize and validate the changes:

Commit and publish only when explicitly requested:

```bash
git diff --check
git diff
git commit
git push <remote> <branch>
```

Prepare one pull request from the feature branch to `main` in `vivoblueos-lab/blueos`. Do not create separate pull requests for top-level areas such as `kernel` or `build`. Read `book/src/prs.md` only for historical context until the centralized contribution documentation is updated.

The handoff must state the branch and remote, changed paths, checks run, outstanding failures, and any pull-request or CI coordination still required.
