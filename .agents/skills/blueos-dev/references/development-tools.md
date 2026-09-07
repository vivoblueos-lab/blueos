# Development Tools and Extended Workflows

## Interactive QEMU Shell

Read `book/src/run-shell.md`, then build and run:

```bash
gn gen out/shell_test --args='board="qemu_mps2_an385" build_type="release"'
ninja -C out/shell_test shell_runner
out/shell_test/bin/shell_runner-qemu.sh
```

Use generated `*-qemu-test.sh` scripts for automated checks and `*-qemu-dbg.sh` for debugger-oriented work. Start an interactive QEMU session only when the request needs it.

## QEMU Checker Integration

Read `book/src/qemu-checker.md`. Define the runner and checker in the same `BUILD.gn`, place checker directives at the test source header, and attach the checker target to a group reachable from the selected board's `check_all`. Confirm reachability in the generated Ninja graph.

## Coverage

Read `book/src/run-coverage.md`, then use the coverage target:

```bash
gn gen out/qemu_riscv64.cov --args='build_type="coverage" board="qemu_riscv64"'
ninja -C out/qemu_riscv64.cov check_coverage
```

The merged HTML report is under `out/qemu_riscv64.cov/cov_report/`. Installing missing `grcov` uses the network and writes outside the workspace; obtain approval first.

## rust-analyzer

Read `book/src/config-rust-analyzer.md`. Generate the model for the intended board and update the root link:

```bash
gn gen out/qemu_mps2_an385 --export-rust-project --args='board="qemu_mps2_an385" build_type="debug"'
ln -sfn out/qemu_mps2_an385/rust-project.json rust-project.json
```

The link selects editor semantics for the workspace. Preserve its current board unless the user requested a change.

## Third-Party Crates

Read `book/src/third-party.md`. Edit `external/Cargo.toml`, then regenerate GN metadata:

```bash
ninja -C <generated-out> run_gnrt
```

Review generated changes in the `external` Git project, add the generated `//external/vendor/<crate-version>:<target>` label to the consumer `BUILD.gn`, and validate both repositories. Dependency resolution can require network access.
