"""odm ueventd rules of mondrian (rootdir/etc/ueventd.odm.rc).

From the stock OS3.0.8.0 odm/etc/ueventd.rc: only the display feature device
of the kernel (/dev/mi_display) is kept, and it is not world-writable.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "rootdir/etc/ueventd.odm.rc"


class UeventdTest(unittest.TestCase):
    def setUp(self):
        self.code = [l.split() for l in RULES.read_text().splitlines()
                     if l.strip() and not l.lstrip().startswith("#")]

    def test_installed_as_odm_ueventd(self):
        self.assertIn("device/xiaomi/mondrian/rootdir/etc/ueventd.odm.rc:"
                      "$(TARGET_COPY_OUT_ODM)/etc/ueventd.rc", (ROOT / "device.mk").read_text())

    def test_mi_display_subsystem(self):
        self.assertIn(["subsystem", "mi_display"], self.code)
        self.assertIn(["devname", "uevent_devpath"], self.code)
        self.assertIn(["dirname", "/dev/mi_display"], self.code)

    def test_device_nodes_are_not_world_accessible(self):
        nodes = [f for f in self.code if f[0].startswith("/dev/")]
        self.assertTrue(nodes)
        for node in nodes:
            self.assertEqual(len(node), 4, node)
            self.assertRegex(node[1], r"^0[0-7][0-7]0$", node)
        self.assertIn(["/dev/mi_display/*", "0660", "system", "graphics"], nodes)

    def test_left_out_stays_out(self):
        text = "\n".join(" ".join(f) for f in self.code)
        self.assertIsNone(re.search(r"vmmgr|trustedvm|ntag5|external_firmware_handler", text))


if __name__ == "__main__":
    unittest.main()
