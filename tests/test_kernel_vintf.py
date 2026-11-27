# SPDX-License-Identifier: Apache-2.0
"""Kernel requirements of the OTA VINTF check.

The Android 17 framework compatibility matrices require, for kernel FCM
level 7 (mondrian launched with Android 13), LTS 5.10.107 or later. The
prebuilt kernel is 5.10.81, so device.mk turns off the kernel part of the
OTA VINTF check (PRODUCT_OTA_ENFORCE_VINTF_KERNEL_REQUIREMENTS := false);
the HALs are still checked. Once the kernel reaches 5.10.107 the check
must be on again.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KERNEL = next((p for p in (ROOT.parent / "mondrian-kernel", ROOT.parent / "pixelexperience-reborn/mondrian-kernel",
                           ROOT.parent / "android_device_xiaomi_mondrian-kernel", ROOT / ".ci/mondrian-kernel")
               if (p / "provenance.json").is_file()), None)
MINIMUM_LTS = (5, 10, 107)


class KernelVintfTest(unittest.TestCase):
    def enforced(self):
        m = re.search(r"(?m)^PRODUCT_OTA_ENFORCE_VINTF_KERNEL_REQUIREMENTS := (\w+)$",
                      (ROOT / "device.mk").read_text())
        return m is not None and m[1] == "true"

    @unittest.skipUnless(KERNEL, "needs the mondrian-kernel release")
    def test_kernel_check_is_off_only_for_a_kernel_below_the_minimum_lts(self):
        release = json.loads((KERNEL / "provenance.json").read_text())["kernel_release"]
        version = tuple(int(x) for x in re.match(r"(\d+)\.(\d+)\.(\d+)", release).groups())
        self.assertEqual(self.enforced(), version >= MINIMUM_LTS, release)

    def test_setting_is_explicit(self):
        self.assertRegex((ROOT / "device.mk").read_text(),
                         r"(?m)^PRODUCT_OTA_ENFORCE_VINTF_KERNEL_REQUIREMENTS := (true|false)$")


if __name__ == "__main__":
    unittest.main()
