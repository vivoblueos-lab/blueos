#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2026 vivo Mobile Communication Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path, PurePosixPath

MODULE_PATH = Path(__file__).resolve().parents[1] / "affected_subrepos.py"
SPEC = importlib.util.spec_from_file_location("affected_subrepos", MODULE_PATH)
assert SPEC and SPEC.loader
affected_subrepos = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(affected_subrepos)


class AffectedSubreposTest(unittest.TestCase):

    def test_loads_nested_component_configs(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            config = repo / "apps" / "example" / "josh-sync.toml"
            config.parent.mkdir(parents=True)
            config.write_text(
                'org = "example"\n'
                'repo = "apps_example"\n'
                'path = "apps/example"\n',
                encoding="utf-8")

            targets = affected_subrepos.load_subrepos(repo)

        self.assertEqual(targets, [
            affected_subrepos.Subrepo("example", "apps_example",
                                      PurePosixPath("apps/example"))
        ])

    def test_selects_only_component_path_boundaries(self):
        targets = [
            affected_subrepos.Subrepo("example", "kernel",
                                      PurePosixPath("kernel")),
            affected_subrepos.Subrepo("example", "apps_example",
                                      PurePosixPath("apps/example")),
        ]

        selected = affected_subrepos.affected_subrepos((
            "BUILD.gn",
            "kernelish/file.rs",
            "apps/example/src/main.rs",
        ), targets)

        self.assertEqual(selected, [targets[1]])

    def test_git_diff_reports_both_sides_of_cross_component_rename(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            subprocess.run(("git", "init", "-q"), cwd=repo, check=True)
            subprocess.run(("git", "config", "user.email", "ci@example.com"),
                           cwd=repo,
                           check=True)
            subprocess.run(("git", "config", "user.name", "CI"),
                           cwd=repo,
                           check=True)
            source = repo / "kernel" / "file.rs"
            source.parent.mkdir()
            source.write_text("content\n", encoding="utf-8")
            subprocess.run(("git", "add", "."), cwd=repo, check=True)
            subprocess.run(("git", "commit", "-qm", "base"),
                           cwd=repo,
                           check=True)
            base = subprocess.run(("git", "rev-parse", "HEAD"),
                                  cwd=repo,
                                  check=True,
                                  capture_output=True,
                                  text=True).stdout.strip()
            destination = repo / "librs" / "file.rs"
            destination.parent.mkdir()
            source.rename(destination)
            subprocess.run(("git", "add", "-A"), cwd=repo, check=True)
            subprocess.run(("git", "commit", "-qm", "move"),
                           cwd=repo,
                           check=True)
            head = subprocess.run(("git", "rev-parse", "HEAD"),
                                  cwd=repo,
                                  check=True,
                                  capture_output=True,
                                  text=True).stdout.strip()

            files = affected_subrepos.get_changed_files(base, head, repo)

        self.assertEqual(files, ["kernel/file.rs", "librs/file.rs"])

    def test_writes_empty_and_nonempty_github_outputs(self):
        target = affected_subrepos.Subrepo("example", "kernel",
                                           PurePosixPath("kernel"))
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output"
            affected_subrepos.write_github_output(output, [])
            affected_subrepos.write_github_output(output, [target])
            contents = output.read_text(encoding="utf-8")

        self.assertEqual(
            contents, "has-targets=false\n"
            "owner=\n"
            "repositories=\n"
            "has-targets=true\n"
            "owner=example\n"
            "repositories=kernel\n")

    def test_rejects_multiple_target_organizations(self):
        targets = [
            affected_subrepos.Subrepo("one", "kernel",
                                      PurePosixPath("kernel")),
            affected_subrepos.Subrepo("two", "librs", PurePosixPath("librs")),
        ]
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(affected_subrepos.TargetFailure):
                affected_subrepos.write_github_output(
                    Path(directory) / "output", targets)


if __name__ == "__main__":
    unittest.main()
