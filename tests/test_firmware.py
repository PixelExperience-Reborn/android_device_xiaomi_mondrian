"""Stock firmware of mondrian flashed with the ROM (firmware-files.txt).

The raw firmware images of the official OS3.0.8.0 OTA, pinned with their
SHA-256 in sm8450-common's ota-source.json, added to the A/B payload. The
images this build makes itself, its own recovery included, and the logical
partitions are never taken from the stock firmware.
"""
import json
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
OWN_IMAGES = {"boot", "vendor_boot", "init_boot", "dtbo", "recovery", "vbmeta", "vbmeta_system",
              "system", "system_ext", "product", "vendor", "odm", "vendor_dlkm", "mi_ext", "super"}

# Partitions with the state of the device: the bootloader lock (devinfo), FRP,
# calibration and modem NV data, keys. A ROM must never write them.
DEVICE_STATE = {"devinfo", "frp", "persist", "misc", "modemst1", "modemst2", "fsg", "fsc", "ssd",
                "keystore", "secdata", "storsec", "dip", "spunvm", "limits", "logdump", "splash",
                "cust", "rawdump", "ddr", "apdp", "qmcs", "toolsfv", "uefivarstore", "multiimgoem"}


def firmware():
    out = []
    for line in (ROOT / "firmware-files.txt").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            name, digest = line.split("|")
            out.append((name, digest))
    return out


class FirmwareTest(unittest.TestCase):
    def test_list_is_well_formed(self):
        entries = firmware()
        names = [n for n, _ in entries]
        self.assertEqual(len(names), len(set(names)))
        for name, digest in entries:
            self.assertRegex(name, r"^[a-z0-9_-]+$")
            self.assertRegex(digest, r"^[0-9a-f]{64}$")
        self.assertLessEqual({"abl", "xbl", "xbl_config", "tz", "hyp", "keymaster", "modem", "dsp",
                              "bluetooth", "aop", "devcfg", "uefisecapp"}, set(names))

    def test_own_images_and_logical_partitions_are_not_stock(self):
        self.assertFalse(OWN_IMAGES & {n for n, _ in firmware()})

    def test_device_state_is_never_written(self):
        self.assertFalse(DEVICE_STATE & {n for n, _ in firmware()})
        board = (ROOT / "BoardConfig.mk").read_text()
        for name in DEVICE_STATE:
            self.assertNotRegex(board, rf"AB_OTA_PARTITIONS.*\b{name}\b")

    def test_nothing_locks_the_bootloader(self):
        # A custom ROM is never relocked: no lock command in this tree.
        pattern = re.compile(r"(?i)fastboot\s+(flashing|oem)\s+lock|flashing_lock|flash_all_lock")
        for path in ROOT.rglob("*"):
            if ".git" in path.parts or ".ci" in path.parts or not path.is_file():
                continue
            if path.suffix in (".mk", ".sh", ".rc", ".txt", ".py", ".bp", ".xml", ".json") and path.name != "test_firmware.py":
                self.assertIsNone(pattern.search(path.read_text(errors="ignore")), str(path))

    def test_pinned_with_the_ota(self):
        if COMMON is None:
            self.skipTest("needs the sm8450-common tree next to this one or in .ci/")
        source = json.loads((COMMON / "proprietary/ota-source.json").read_text())
        for name, digest in firmware():
            with self.subTest(name=name):
                pinned = source["partitions"][name]
                self.assertEqual((pinned["sha256"], pinned["type"]), (digest, "firmware"))

    def test_board_and_radio_wiring(self):
        board = (ROOT / "BoardConfig.mk").read_text()
        self.assertIn("AB_OTA_PARTITIONS += $(MONDRIAN_FIRMWARE_PARTITIONS)", board)
        self.assertIn("$(DEVICE_PATH)/firmware-files.txt", board)
        mk = (ROOT / "firmware/Android.mk").read_text()
        self.assertIn("$(call add-radio-file,radio/$(p).img)", mk)
        self.assertIn("$(error mondrian:", mk)


if __name__ == "__main__":
    unittest.main()
