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
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "check_changes.py"
SPEC = importlib.util.spec_from_file_location("check_changes", MODULE_PATH)
assert SPEC and SPEC.loader
check_changes = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_changes)


class ChangedFilesTest(unittest.TestCase):

    def test_format_groups_preserve_external_exclusion(self):
        groups = check_changes.format_groups((
            "kernel/src/lib.rs",
            "build/tool.gni",
            "tools/ci/check.py",
            ".github/workflows/ci.yml",
            "external/gnrt/main.rs",
        ))

        self.assertEqual(groups["rust"], ["kernel/src/lib.rs"])
        self.assertEqual(groups["gn"], ["build/tool.gni"])
        self.assertEqual(groups["python"], ["tools/ci/check.py"])
        self.assertEqual(groups["yaml"], [".github/workflows/ci.yml"])

    def test_affected_license_roots_are_unique_and_ordered(self):
        roots = check_changes.affected_license_roots((
            "kernel/src/a.rs",
            "kernel/src/b.rs",
            "apps/example/src/main.rs",
            "tools/ci/run_profile.py",
            "book/src/ci.md",
        ))

        self.assertEqual([str(root) for root in roots],
                         ["kernel", "apps/example", "tools/ci"])

    def test_git_diff_uses_merge_base_and_handles_spaces(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            subprocess.run(("git", "init", "-q"), cwd=repo, check=True)
            subprocess.run(("git", "config", "user.email", "ci@example.com"),
                           cwd=repo,
                           check=True)
            subprocess.run(("git", "config", "user.name", "CI"),
                           cwd=repo,
                           check=True)
            changed_file = repo / "file with spaces.py"
            changed_file.write_text("print('first')\n", encoding="utf-8")
            subprocess.run(("git", "add", "."), cwd=repo, check=True)
            subprocess.run(("git", "commit", "-qm", "base"),
                           cwd=repo,
                           check=True)
            base = subprocess.run(("git", "rev-parse", "HEAD"),
                                  cwd=repo,
                                  check=True,
                                  capture_output=True,
                                  text=True).stdout.strip()
            changed_file.write_text("print('head')\n", encoding="utf-8")
            subprocess.run(("git", "commit", "-qam", "head"),
                           cwd=repo,
                           check=True)
            head = subprocess.run(("git", "rev-parse", "HEAD"),
                                  cwd=repo,
                                  check=True,
                                  capture_output=True,
                                  text=True).stdout.strip()

            files = check_changes.get_changed_files(base, head, repo)

        self.assertEqual(files, ["file with spaces.py"])

    def test_invalid_commit_fails(self):
        with self.assertRaises(check_changes.CheckFailure):
            check_changes.get_changed_files("not-a-commit", "HEAD")


if __name__ == "__main__":
    unittest.main()
