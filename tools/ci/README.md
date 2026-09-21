# Central CI tools

This directory contains CI orchestration that belongs only to the centralized
BlueOS repository. It is intentionally outside every subtree that has a
`josh-sync.toml` file, so it is not exported to a component repository.

`run_profile.py` runs one GN/Ninja build profile. `check_changes.py` checks the
format and license headers of files changed by a pull request.
`affected_subrepos.py` maps a merged change to component repositories using
their `josh-sync.toml` files. GitHub Actions invokes these tools from the
repository root.

The synchronization workflows require the `JOSH_SYNC_ENABLED` organization
variable to be available to the centralized repository and every component
repository. Synchronization jobs run only when its value is exactly `true`.
Setting it to any other value prevents new synchronization jobs from starting,
but does not cancel jobs that are already running. After re-enabling
synchronization, manually run `Pull changes from BlueOS` in each component repository if an
immediate catch-up is required.

The `Notify subrepos` workflow also requires the `APP_CLIENT_ID` repository
variable and `APP_PRIVATE_KEY` repository secret. The GitHub App must be
installed on the component repositories with `Contents: write`, which permits
the workflow to send their `blueos-pull` repository dispatch event.

When this workflow is deployed for the first time, run the existing `Sync
BlueOS` workflow once in every component repository (or wait for its scheduled
run) and merge the generated sync pull request. That bootstraps the
`repository_dispatch` trigger in each component's default branch.

Run the unit tests with:

```sh
python3 -m unittest discover -s tools/ci/tests -p 'test_*.py'
```
