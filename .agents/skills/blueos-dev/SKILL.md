---
name: blueos-dev
description: Build, test, diagnose, and prepare changes in the BlueOS centralized single-repository workspace. Use for BlueOS GN/Ninja builds, QEMU tests, target selection, CI reproduction, formatting, coverage, development tooling, dependency updates, or Git contribution work; do not use for unrelated Cargo-only Rust projects.
---

# BlueOS Development

Work from the repository root containing `.git`, `.gn`, and the top-level `BUILD.gn`. Treat the current GN files and CI scripts as authoritative when documentation disagrees with the checkout.

## Operating Rules

- This is a centralized Git repository. Run Git commands from the repository root; do not treat `kernel`, `build`, `external`, and similar directories as independent repositories.
- Build BlueOS project code with GN and Ninja, not Cargo, unless a checked-in maintenance workflow explicitly requires Cargo.
- Preserve unrelated changes in the worktree. Do not stash, reset, clean, switch branches, delete output directories, commit, push, or post externally unless the user requested the corresponding mutation.
- Keep a stable GN argument set per output directory. Inspect `<out>/args.gn` before reuse; use a distinct directory for each board, build type, and syscall-handler mode.
- Select validation by the changed code's actual GN target and test surface. `check_all` is board-specific and does not mean every target in the repository ran.
- Report failed checks as failures even when evidence attributes them to the baseline. Separate regression status from command status.

## Standard Workflow

1. Inspect tools and workspace state:

   ```bash
   direnv status
   git status --short --branch
   git remote -v
   command -v gn ninja rustc rustfmt clippy-driver
   rustc --print target-list | rg 'vivo-blueos'
   ```

2. Map every changed path to the nearest `BUILD.gn`, crate or binary target, test targets, and relevant boards.

3. Generate or inspect the selected output directory:

   ```bash
   gn gen out/qemu_mps2_an385 --args='board="qemu_mps2_an385" build_type="debug"'
   sed -n '1,120p' out/qemu_mps2_an385/args.gn
   ```

4. Run validation from narrow to broad:

   - directly affected compile or `*_clippy` target;
   - explicit unit-test and integration-test compile targets;
   - owning test and Clippy groups;
   - selected board's `check_all`;
   - release, alternate-board, or CI matrix checks when the risk requires them.

5. Run formatting and license checks for the changed paths.

6. Report the repository state, board, build type, output directory, exact checks, failures and attribution evidence, skipped validation, and remaining external steps.

## Read the Relevant Reference

- For toolchain setup, checkout management, board selection, GN generation, and ordinary builds, read [references/environment-and-build.md](references/environment-and-build.md).
- For target discovery, validation levels, `check_all`, CI reproduction, format/license checks, or baseline diagnosis, read [references/validation-and-ci.md](references/validation-and-ci.md).
- For QEMU shell, coverage, rust-analyzer, QEMU checker integration, or third-party crates, read [references/development-tools.md](references/development-tools.md).
- For branch, commit, push, or pull-request preparation, read [references/contribution.md](references/contribution.md).

Load only the references relevant to the current request.
