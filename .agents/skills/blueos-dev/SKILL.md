---
name: blueos-dev
description: Build, test, diagnose, and prepare changes in the BlueOS repo-managed multi-repository workspace. Use for BlueOS GN/Ninja builds, QEMU tests, target selection, CI reproduction, formatting, coverage, development tooling, dependency updates, or multi-repository contribution work; do not use for unrelated Cargo-only Rust projects.
---

# BlueOS Development

Work from the directory containing `.repo/manifest.xml`, `.gn`, and the top-level `BUILD.gn`. Treat the manifest, current GN files, and CI scripts as authoritative when documentation disagrees with the checkout.

## Operating Rules

- This is a `repo` workspace, not a top-level Git repository. Resolve ownership with `repo list` and run Git commands with `git -C <project>`.
- Build BlueOS project code with GN and Ninja, not Cargo, unless a checked-in maintenance workflow explicitly requires Cargo.
- Preserve unrelated changes across all child repositories. Do not stash, reset, clean, switch branches, delete output directories, commit, push, or post externally unless the user requested the corresponding mutation.
- Keep a stable GN argument set per output directory. Inspect `<out>/args.gn` before reuse; use a distinct directory for each board, build type, and syscall-handler mode.
- Select validation by the changed code's actual GN target and test surface. `check_all` is board-specific and does not mean every repository target ran.
- Report failed checks as failures even when evidence attributes them to the baseline. Separate regression status from command status.

## Standard Workflow

1. Inspect tools and workspace state:

   ```bash
   direnv status
   repo list
   repo status -j1
   command -v gn ninja rustc rustfmt clippy-driver
   rustc --print target-list | rg 'vivo-blueos'
   ```

2. Map every changed path to its Git project, nearest `BUILD.gn`, crate or binary target, test targets, and relevant boards.

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

5. Run formatting and license checks in every changed Git project.

6. Report the repositories, board, build type, output directory, exact checks, failures and attribution evidence, skipped validation, and remaining external steps.

## Read the Relevant Reference

- For toolchain setup, checkout sync, board selection, GN generation, and ordinary builds, read [references/environment-and-build.md](references/environment-and-build.md).
- For target discovery, validation levels, `check_all`, CI reproduction, format/license checks, or baseline diagnosis, read [references/validation-and-ci.md](references/validation-and-ci.md).
- For QEMU shell, coverage, rust-analyzer, QEMU checker integration, or third-party crates, read [references/development-tools.md](references/development-tools.md).
- For branch, commit, push, or multi-repository PR preparation, read [references/contribution.md](references/contribution.md).

Load only the references relevant to the current request.
