# Validation and CI

## Find Targets

Inspect the nearest `BUILD.gn` and identify its `build_rust`, `run_clippy`, test, runner, or group target. Confirm generated names:

```bash
ninja -C out/qemu_mps2_an385 -t targets all | rg -i 'infra|kernel|test_harness|clippy|unittest|integration'
gn desc out/qemu_mps2_an385 //kernel/infra:blueos_infra_clippy
ninja -C out/qemu_mps2_an385 -t query phony/kernel/infra/check_infra_by_clippy
```

Current useful mappings are:

| Change area | Fast target | Test compile targets | Execution or group |
| --- | --- | --- | --- |
| `kernel/infra/src/**` | `blueos_infra_clippy` | `infra_unittest_clippy` | `check_infra`, `check_infra_by_clippy` |
| `kernel/kernel/src/**` | `blueos_clippy` | `kernel_unittest_clippy`, `kernel_integration_test_clippy` | `check_kernel`, `check_kernel_by_clippy` |
| `kernel/test_harness/src/lib.rs` | `host/obj/kernel/test_harness/libblueos_test_macro.so` | Kernel test crates that consume it | `check_kernel`, `check_kernel_by_clippy` |

Re-query after build-file changes. Generated output paths may move.

## Validation Ladder

Run the directly affected crate first:

```bash
ninja -C out/qemu_mps2_an385 blueos_infra_clippy
ninja -C out/qemu_mps2_an385 blueos_clippy
```

Compile test-only configurations explicitly:

```bash
ninja -C out/qemu_mps2_an385 infra_unittest_clippy
ninja -C out/qemu_mps2_an385 kernel_unittest_clippy kernel_integration_test_clippy
```

Then run owning groups:

```bash
ninja -C out/qemu_mps2_an385 check_infra check_infra_by_clippy
ninja -C out/qemu_mps2_an385 check_kernel check_kernel_by_clippy
```

Typical subsystem groups also include `check_adapter`, `check_loader`, `check_rsrt`, `check_librs`, and corresponding `*_by_clippy` targets. Confirm availability with `ninja -t targets all` because boards differ.

Run the board's configured gate when warranted:

```bash
ninja -C out/qemu_mps2_an385 check_all
```

On the current `qemu_mps2_an385` graph this includes default apps, selected subsystem checks and Clippy groups, CMSIS validation, thread-metric tests, and QEMU execution. It does not include `check_infra` or `check_infra_by_clippy`, so infra changes require those explicit targets. Inspect exact coverage with:

```bash
ninja -C out/qemu_mps2_an385 -t query phony/build/boards/qemu_mps2_an385/check_all
```

The common Rust config denies warnings but explicitly allows `unused`, `dead_code`, and `static_mut_refs`; do not claim every warning category is fatal.

## Release and Multiple Boards

Run release checks when optimization, layout, timing, panic behavior, or deliverable readiness matters:

```bash
ninja -C out/qemu_mps2_an385.release default
ninja -C out/qemu_mps2_an385.release check_all
```

For shared code sensitive to word size, endianness, architecture, linker, atomics, ABI, or `cfg`, generate relevant ARM, AArch64, RISC-V 32-bit, and/or RISC-V 64-bit boards. One QEMU board is not cross-board coverage.

## CI Runner

`build/ci/run_ci.py` invokes format and license stages, then runs `gn gen`, `default`, and `check_all`. It always tests both `direct_syscall_handler=true` and `false`, creating `.dsc` and `.swi` outputs.

Pass repository paths when format and license validation is intended. With no positional paths, the current implementation checks an empty repository list:

```bash
python3 build/ci/run_ci.py --board qemu_mps2_an385 --build_type debug kernel
python3 build/ci/run_ci.py --board qemu_mps2_an385 --build_type debug kernel build
```

The format stage fetches the configured upstream branch before diffing, so it needs network access and updates remote-tracking refs. Omitting `--board` or `--build_type` expands the matrix. `--setup_only` generates output directories without building them.

## Formatting and License

Run checks from each changed Git project:

```bash
rustfmt --edition=2021 --check --unstable-features --skip-children <changed-rust-files>
gn format --dry-run <changed-gn-files>
yapf3 -d <changed-python-files>
clang-format --dry-run --Werror <changed-c-or-cpp-files>
license-eye header check
```

Use `yapf` on macOS. Review `yapf -d` output rather than trusting only its exit code. The current CI format helper covers Rust, GN, and Python, not C/C++; check changed C/C++ manually.

License rules are repository-specific. Run `license-eye` where `.licenserc.yaml` exists. The current CI helper skips `libc`, `book`, and `external`. Run `license-eye header fix` only when header modification was requested, then review its diff.

## Baseline Attribution

Record the exact command, output directory, `args.gn`, target, and first actionable diagnostic. Inspect the worktree and baseline without changing user state:

```bash
git -C kernel diff -- infra/src/tinyrwlock.rs
git -C kernel show HEAD:infra/src/tinyrwlock.rs | sed -n '<start>,<end>p'
```

If the failing line and condition exist at `HEAD` and the change does not affect them, report both facts: the command failed, and the evidence attributes it to baseline. When an executable baseline is necessary, prefer a separate worktree or checkout. Do not stash user changes merely for comparison. Prefer a fresh named output directory over deleting an existing one when stale output is supported by evidence.
