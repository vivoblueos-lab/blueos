# Central CI tools

This directory contains CI orchestration that belongs only to the centralized
BlueOS repository. It is intentionally outside every subtree that has a
`josh-sync.toml` file, so it is not exported to a component repository.

`run_profile.py` runs one GN/Ninja build profile. `check_changes.py` checks the
format and license headers of files changed by a pull request. GitHub Actions
invokes both tools from the repository root.

Run the unit tests with:

```sh
python3 -m unittest discover -s tools/ci/tests -p 'test_*.py'
```
