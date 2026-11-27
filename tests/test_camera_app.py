# SPDX-License-Identifier: Apache-2.0
"""The camera app of mondrian: Aperture instead of AOSP Camera2.

vendor/aosp installs Aperture when the device sets PE_A17_PORT_APERTURE
(config/common.mk); the manifest pins packages/apps/Aperture (LineageOS
lineage-24.0, Android 17) and Aperture overrides Camera2. device.mk is
inherited before vendor/aosp, so the variable is set when common.mk reads it.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CameraAppTest(unittest.TestCase):
    def test_device_selects_aperture(self):
        self.assertRegex((ROOT / "device.mk").read_text(), r"(?m)^PE_A17_PORT_APERTURE := true$")

    def test_device_makefile_is_inherited_before_vendor_aosp(self):
        product = (ROOT / "aosp_mondrian.mk").read_text()
        device = product.index("device/xiaomi/mondrian/device.mk")
        vendor = product.index("vendor/aosp/config/common_full_phone.mk")
        self.assertLess(device, vendor)

    def test_camera_features_are_declared(self):
        device = (ROOT / "device.mk").read_text()
        for feature in ("camera.flash-autofocus", "camera.front", "camera.full", "camera.raw"):
            self.assertRegex(device, rf"android\.hardware\.{re.escape(feature)}\.xml")


if __name__ == "__main__":
    unittest.main()
