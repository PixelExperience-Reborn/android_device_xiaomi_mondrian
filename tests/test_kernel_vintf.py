# SPDX-License-Identifier: Apache-2.0
"""The kernel: the stock GKI kernel of OS3.0.8.0 and the OTA VINTF check.

kernel-files.txt pins the stock boot, vendor_boot, dtbo and vendor_dlkm
images, the same as sm8450-common's ota-source.json. The stock kernel is
5.10.236, past the LTS 5.10.107 that the Android 17 framework matrices ask
for kernel FCM level 7, so the OTA VINTF check covers the kernel.
"""
import json
import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMON = next((p for p in (ROOT.parent / "android_device_xiaomi_sm8450-common", ROOT.parent / "sm8450-common",
                           ROOT / ".ci/android_device_xiaomi_sm8450-common") if p.is_dir()), None)
KERNEL = next((p for p in (Path(os.environ.get("MONDRIAN_KERNEL", "/nonexistent")),
                           ROOT.parent / "proprietary_vendor_xiaomi_mondrian/kernel",
                           ROOT.parents[2] / "vendor/xiaomi/mondrian/kernel")
               if (p / "kernel_release").is_file()), None)
MINIMUM_LTS = (5, 10, 107)
PARTITIONS = ["boot", "vendor_boot", "dtbo", "vendor_dlkm"]


def pins():
    out = {}
    for line in (ROOT / "kernel-files.txt").read_text().splitlines():
        if line and not line.startswith("#"):
            name, digest = line.split("|")
            out[name] = digest
    return out


class KernelTest(unittest.TestCase):
    def test_kernel_files_pin_the_stock_kernel_images(self):
        self.assertEqual(list(pins()), PARTITIONS)
        for digest in pins().values():
            self.assertRegex(digest, r"^[0-9a-f]{64}$")

    @unittest.skipUnless(COMMON, "needs sm8450-common")
    def test_pins_are_those_of_the_ota_source(self):
        source = json.loads((COMMON / "proprietary/ota-source.json").read_text())["partitions"]
        for name, digest in pins().items():
            self.assertEqual(source[name], {"size": source[name]["size"], "sha256": digest, "type": "kernel"})

    def test_board_config_uses_the_extracted_kernel(self):
        board = (ROOT / "BoardConfig.mk").read_text()
        self.assertIn("KERNEL_PATH := vendor/xiaomi/mondrian/kernel\n", board)
        self.assertIn("vendor/xiaomi/mondrian/kernel/Image:kernel", (ROOT / "device.mk").read_text())
        self.assertNotIn("mondrian-kernel", board)

    def test_vintf_checks_the_kernel(self):
        self.assertRegex((ROOT / "device.mk").read_text(),
                         r"(?m)^PRODUCT_OTA_ENFORCE_VINTF_KERNEL_REQUIREMENTS := true$")

    @unittest.skipUnless(KERNEL, "needs the extracted stock kernel (MONDRIAN_KERNEL)")
    def test_extracted_kernel_is_the_stock_gki_past_the_minimum_lts(self):
        release = (KERNEL / "kernel_release").read_text().strip()
        self.assertRegex(release, r"^5\.10\.\d+-android12-9-")
        version = tuple(int(x) for x in re.match(r"(\d+)\.(\d+)\.(\d+)", release).groups())
        self.assertGreaterEqual(version, MINIMUM_LTS)
        provenance = json.loads((KERNEL / "provenance.json").read_text())
        self.assertEqual(provenance["images"], pins())


if __name__ == "__main__":
    unittest.main()
