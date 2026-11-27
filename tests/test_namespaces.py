# SPDX-License-Identifier: Apache-2.0
"""The prebuilt modules of vendor/xiaomi/mondrian and vendor/xiaomi/sm8450-common
must have distinct names.

The vendor build rules turn each library, binary, app and jar of a
proprietary list into one Soong module named after the file (plus its
MODULE_SUFFIX), with all its architectures in that module. Android 17 refuses
a name found in two namespaces imported for the vendor partition ("found in
multiple namespaces ... when including in vendor partition"), so both
architectures of a library belong to one list.
"""
import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sibling(*names):
    for base in (ROOT.parent, ROOT / ".ci"):
        for name in names:
            if (base / name).is_dir():
                return base / name
    return None


COMMON = sibling("sm8450-common", "android_device_xiaomi_sm8450-common")
if COMMON is None:
    raise unittest.SkipTest("needs the sm8450-common tree next to this one or in .ci/")
MODULE = re.compile(r"/(bin|lib|lib64|app|priv-app|framework)/|\.(so|apk|jar)$")


def modules(path):
    out = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        spec = line.split("|")[0]
        file, *options = spec.split(";")
        file = file.lstrip("-")
        if not MODULE.search(file):
            continue
        suffix = next((o.split("=", 1)[1] for o in options if o.startswith("MODULE_SUFFIX=")), "")
        name = re.sub(r"\.(so|apk|jar)$", "", os.path.basename(file)) + suffix
        out.setdefault(name, []).append(file)
    return out


class NamespaceTest(unittest.TestCase):
    def test_no_module_in_both_lists(self):
        mondrian = modules(ROOT / "proprietary-files.txt")
        common = modules(COMMON / "proprietary-files.txt")
        both = {n: (common[n], mondrian[n]) for n in set(mondrian) & set(common)}
        self.assertEqual(both, {})

    def test_both_architectures_of_a_library_are_in_one_list(self):
        for path in (ROOT / "proprietary-files.txt", COMMON / "proprietary-files.txt"):
            for name, files in modules(path).items():
                self.assertEqual(len(files), len(set(files)), name)


if __name__ == "__main__":
    unittest.main()
