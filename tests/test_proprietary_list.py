"""Contract for the mondrian device-specific proprietary file list.

The list is consumed by device/xiaomi/sm8450-common/tools/extract_proprietary.py,
which reproduces every file from the pinned official OTA and checks its SHA-256.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
LIST = ROOT / "proprietary-files.txt"
# <file>[;<extract-utils argument>...]|<sha256>, as tools/extract_proprietary.py reads it.
LINE = re.compile(r"^((?:vendor|odm)/[A-Za-z0-9_@+.,/-]+)(?:;[A-Z_]+(?:=[A-Za-z0-9_@+.,/-]+)?)*\|([0-9a-f]{64})$")

FORBIDDEN = [
    r"libmialgoengine\.so$", r"/com\.xiaomi\.plugin\.", r"campostproc", r"/camera\.xiaomi\.so$",
    r"/bin/hw/vendor\.xiaomi\.", r"soter", r"mlipay", r"dolby", r"wfd", r"perf-hal",
    r"^vendor/etc/vintf/", r"/init\.(qcom|target)\.rc$", r"/rfsa/adsp/libVpp", r"tracker_6dof",
    r"_(8250|8350)\.so$",
    # IR is our own AIDL HAL over the kernel's /dev/ir_spi (CONFIG_IR_SPI); no IR blob.
    r"consumerir", r"android\.hardware\.ir@",
    # AOSP libraries are built from the AOSP 17 sources, not copied from the OTA.
    r"/libcodec2_(vndk|hidl)", r"/libhidltransport\.so$",
]
# The five mondrian cameras: wide (two module vendors), front, ultra-wide, macro.
CAMERA_SENSORS = ["mondrian_aac_ov64b40_wide_ii", "mondrian_sunny_ov64b40_wide_i", "ov16a1q_front",
                  "ov08d10_ultra", "ov02b10_macro"]


def entries():
    rows, section, seen = [], None, set()
    for number, raw in enumerate(LIST.read_text().splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("# === ") and line.endswith(" ==="):
            section = line[6:-4]
            continue
        if line.startswith("#"):
            continue
        match = LINE.match(line)
        assert match, f"line {number}: {raw!r}"
        assert section, f"line {number}: entry before the first section"
        assert match.group(1) not in seen, f"line {number}: duplicate {match.group(1)}"
        seen.add(match.group(1))
        rows.append((section, match.group(1)))
    return rows


class MondrianProprietaryList(unittest.TestCase):
    rows = entries()
    paths = {path for _, path in rows}

    def test_sections_are_sorted_and_explained(self):
        sections = {}
        for section, path in self.rows:
            sections.setdefault(section, []).append(path)
        for section, paths in sections.items():
            with self.subTest(section=section):
                self.assertEqual(paths, sorted(paths))
        text = LIST.read_text()
        for header in re.findall(r"^# === (.+) ===$", text, re.M):
            following = text.split(f"# === {header} ===", 1)[1].lstrip("\n").splitlines()[0]
            self.assertTrue(following.startswith("# "), header)

    def test_no_excluded_component(self):
        for path in self.paths:
            with self.subTest(path=path):
                for pattern in FORBIDDEN:
                    self.assertIsNone(re.search(pattern, path), pattern)

    def test_device_hardware_is_covered(self):
        for sensor in CAMERA_SENSORS:
            self.assertTrue(any("com.qti.sensor." in p and sensor in p for p in self.paths), sensor)
        for required in ("vendor/bin/hw/vendor.qti.camera.provider@2.7-service_64",
                         "vendor/lib64/hw/camera.qcom.so", "vendor/firmware/CAMERA_ICP.mdt",
                         "vendor/firmware/goodix_firmware_m11a.bin", "vendor/firmware/goodix_cfg_group_m11a.bin",
                         "vendor/firmware/aw882xx_acf.bin", "vendor/bin/hw/mfp-daemon",
                         "odm/lib64/vendor.xiaomi.hardware.fx.tunnel@1.0.so",
                         "vendor/etc/sensors/hals.conf"):
            self.assertIn(required, self.paths)

    def test_header_states_provenance_and_no_redistribution(self):
        head = LIST.read_text().split("# ===", 1)[0]
        self.assertIn("OS3.0.8.0.VMNCNXM", head)
        self.assertIn("ota-source.json", head)
        self.assertIn("not redistributed", head)


if __name__ == "__main__":
    unittest.main()
