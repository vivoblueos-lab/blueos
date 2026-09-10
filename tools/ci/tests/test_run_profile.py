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
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "run_profile.py"
SPEC = importlib.util.spec_from_file_location("run_profile", MODULE_PATH)
assert SPEC and SPEC.loader
run_profile = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(run_profile)


class ProfileTest(unittest.TestCase):

    def test_dsc_profile_commands(self):
        profile = run_profile.Profile("qemu_mps2_an385", "release", "dsc")

        commands = run_profile.commands_for(profile)

        self.assertEqual(profile.out_dir, "out/qemu_mps2_an385.release.dsc")
        self.assertEqual(commands[0], (
            "gn",
            "gen",
            "out/qemu_mps2_an385.release.dsc",
            '--args=board="qemu_mps2_an385" build_type="release" '
            "direct_syscall_handler=true",
        ))
        self.assertEqual(commands[1][-1], "default")
        self.assertEqual(commands[2][-1], "check_all")

    def test_host_rejects_dsc(self):
        profile = run_profile.Profile("none", "debug", "dsc")

        with self.assertRaisesRegex(ValueError, "only supports swi"):
            run_profile.commands_for(profile)

    def test_host_omits_irrelevant_direct_syscall_argument(self):
        profile = run_profile.Profile("none", "debug", "swi")

        self.assertNotIn("direct_syscall_handler", profile.gn_args)

    def test_first_failure_is_returned(self):
        calls = []

        def fake_runner(command, **kwargs):
            calls.append((command, kwargs))
            return subprocess.CompletedProcess(command, 23)

        result = run_profile.run_profile(run_profile.Profile(
            "qemu_riscv32", "debug", "swi"),
                                         command_runner=fake_runner)

        self.assertEqual(result, 23)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1]["cwd"], run_profile.REPO_ROOT)
        self.assertFalse(calls[0][1]["check"])


if __name__ == "__main__":
    unittest.main()
