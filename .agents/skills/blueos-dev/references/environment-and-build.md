# Environment and Build

## Environment

Prefer the checked-in `.envrc` over copied PATH values:

```bash
direnv status
command -v gn ninja rustc rustfmt clippy-driver license-eye
rustc -vV
rustc --print target-list | rg 'vivo-blueos'
gn --version
ninja --version
```

Check board-specific tools too. For `qemu_mps2_an385`:

```bash
command -v arm-none-eabi-gcc qemu-system-arm
arm-none-eabi-gcc --version
qemu-system-arm --version
```

If the shell hook did not load `.envrc`, use `direnv exec . <command>` for one command. Inspect an untrusted `.envrc` and obtain approval before `direnv allow`, which changes user-level trust state.

For a new machine or missing tools, read `book/src/getting-started.md`. Read `book/src/build-rust-toolchain.md` only when the custom Rust toolchain must be built. The installed versions may differ from the documentation, so verify the active binaries.

## Initialize and Sync

Run these only when requested because they use the network and update checkout state:

```bash
repo init -u https://github.com/vivoblueos/manifests.git -b main -m manifest.xml
repo sync -j<N>
```

Use the SSH manifest URL when the user has configured GitHub SSH access.

## Repository Ownership and Status

The current manifest has these separate Git projects:

- `apps/example`
- `apps/shell`
- `book`
- `build`
- `external`
- `kernel`
- `libc`
- `librs`

`apps/` is only a container. Use:

```bash
repo list
repo status -j1
git -C kernel status --short
```

Prefer `repo status -j1` in constrained environments because the default parallel form can fail when process creation is restricted.

## Generate and Build

Use explicit arguments and an output name that conveys them:

```bash
gn gen out/qemu_mps2_an385 --args='board="qemu_mps2_an385" build_type="debug"'
ninja -C out/qemu_mps2_an385 default

gn gen out/qemu_mps2_an385.release --args='board="qemu_mps2_an385" build_type="release"'
ninja -C out/qemu_mps2_an385.release default
```

Ninja without an explicit target currently builds `default`, but spelling it makes the intent clear. Inspect effective arguments before reuse:

```bash
sed -n '1,120p' out/qemu_mps2_an385/args.gn
gn args out/qemu_mps2_an385 --list
```

Discover boards from `build/boards/`. Generate only boards whose compiler and runtime dependencies are installed. When the user did not select a board and the change is board-independent, start with `qemu_mps2_an385` debug; expand according to validation risk.
