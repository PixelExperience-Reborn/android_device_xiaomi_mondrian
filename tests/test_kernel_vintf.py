# SPDX-License-Identifier: Apache-2.0
"""The kernel: the stock GKI kernel of OS3.0.8.0 and VINTF.

kernel-files.txt pins the stock boot, vendor_boot, dtbo and vendor_dlkm
images, the same as sm8450-common's ota-source.json.

With device target-level 7, Android 17 takes the kernel FCM level from the
GKI release and refuses an explicit <kernel target-level> in the manifest;
5.10.236-android12-9 gives level 6, for which the Android 17 framework keeps
no kernel requirements. The OTA VINTF check therefore leaves the kernel out
(PRODUCT_OTA_ENFORCE_VINTF_KERNEL_REQUIREMENTS := false), and this test
checks what it would have: the requirements of kernel FCM 7 for 5.10 (LTS
5.10.107, kernel/configs t/android-5.10) against the config of the kernel.
"""
import gzip
import json
import os
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMON = next((p for p in (ROOT.parent / "android_device_xiaomi_sm8450-common", ROOT.parent / "sm8450-common",
                           ROOT / ".ci/android_device_xiaomi_sm8450-common") if p.is_dir()), None)
KERNEL = next((p for p in (Path(os.environ.get("MONDRIAN_KERNEL", "/nonexistent")),
                           ROOT.parent / "proprietary_vendor_xiaomi_mondrian/kernel",
                           ROOT.parents[2] / "vendor/xiaomi/mondrian/kernel")
               if (p / "kernel_release").is_file()), None)
# kernel/configs of android-17.0.0_r1 (in an Android tree: kernel/configs).
CONFIGS = next((p for p in (Path(os.environ.get("AOSP_KERNEL_CONFIGS", "/nonexistent")),
                            ROOT.parents[2] / "kernel/configs") if (p / "t/android-5.10").is_dir()), None)
MINIMUM_LTS = (5, 10, 107)
PARTITIONS = ["boot", "vendor_boot", "dtbo", "vendor_dlkm"]


def pins():
    out = {}
    for line in (ROOT / "kernel-files.txt").read_text().splitlines():
        if line and not line.startswith("#"):
            name, digest = line.split("|")
            out[name] = digest
    return out


def kernel_config(image):
    data = Path(image).read_bytes()
    start = data.find(b"IKCFG_ST")
    config = gzip.decompress(data[start + 8:data.find(b"IKCFG_ED", start)]).decode()
    values = {}
    for line in config.splitlines():
        m = re.match(r"(CONFIG_\w+)=(.*)", line) or re.match(r"# (CONFIG_\w+) is not set", line)
        if m:
            values[m[1]] = m[2] if m.re.groups == 2 else "n"
    return values


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

    def test_vintf_leaves_the_kernel_to_this_test(self):
        self.assertRegex((ROOT / "device.mk").read_text(),
                         r"(?m)^PRODUCT_OTA_ENFORCE_VINTF_KERNEL_REQUIREMENTS := false$")
        manifests = [ROOT / "vintf/manifest.xml"] + ([COMMON / "vintf/manifest.xml"] if COMMON else [])
        for manifest in manifests:
            root = ET.parse(manifest).getroot()
            self.assertEqual(root.get("target-level"), "7")
            self.assertEqual(root.findall("kernel"), [], manifest)

    @unittest.skipUnless(KERNEL, "needs the extracted stock kernel (MONDRIAN_KERNEL)")
    def test_extracted_kernel_is_the_stock_gki_past_the_minimum_lts(self):
        release = (KERNEL / "kernel_release").read_text().strip()
        self.assertRegex(release, r"^5\.10\.\d+-android12-9-")
        version = tuple(int(x) for x in re.match(r"(\d+)\.(\d+)\.(\d+)", release).groups())
        self.assertGreaterEqual(version, MINIMUM_LTS)
        provenance = json.loads((KERNEL / "provenance.json").read_text())
        self.assertEqual(provenance["images"], pins())

    @unittest.skipUnless(KERNEL and CONFIGS, "needs the extracted kernel and kernel/configs (AOSP_KERNEL_CONFIGS)")
    def test_kernel_meets_the_level_7_configs_of_5_10(self):
        have = kernel_config(KERNEL / "Image")
        base = CONFIGS / "t/android-5.10"
        for line in (base / "android-base.config").read_text().splitlines():
            m = re.match(r"(CONFIG_\w+)=(.*)", line) or re.match(r"# (CONFIG_\w+) is not set", line)
            if m:
                want = m[2] if m.re.groups == 2 else "n"
                self.assertEqual(have.get(m[1], "n"), want, m[1])
        text = re.sub(r"<\?xml[^>]*\?>", "", (base / "android-base-conditional.xml").read_text())
        for group in ET.fromstring(f"<root>{text}</root>").iter("group"):
            conditions = group.find("conditions")
            if conditions is not None and any(have.get(c.find("key").text, "n") != c.find("value").text
                                              for c in conditions.findall("config")):
                continue
            for config in group.findall("config"):
                key, value = config.find("key").text, config.find("value").text
                self.assertEqual(have.get(key, "n"), value, key)


if __name__ == "__main__":
    unittest.main()
