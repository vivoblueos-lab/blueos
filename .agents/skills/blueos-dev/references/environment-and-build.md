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

## Clone and Update

Run these only when requested because they use the network and update checkout state:

```bash
git clone https://github.com/vivoblueos-lab/blueos.git blueos-dev
git -C blueos-dev status --short --branch
git -C blueos-dev pull --ff-only
```

Use the SSH URL `git@github.com:vivoblueos-lab/blueos.git` when the user has configured GitHub SSH access.

## Repository Status

The centralized repository contains these top-level areas:

- `apps/example`
- `apps/shell`
- `book`
- `build`
- `external`
- `kernel`
- `libc`
- `librs`

`apps/` is only a directory container. Use:

```bash
git status --short --branch
git remote -v
git branch -vv
```

The upstream remote is `https://github.com/vivoblueos-lab/blueos.git`, and the default branch is `main`. Top-level project directories no longer have independent `.git` directories.

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
