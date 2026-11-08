import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MondrianHardwareProfileTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "hardware-profile.json").read_text(encoding="utf-8"))

    def test_physical_scope(self):
        d = self.data
        self.assertEqual(d["device"]["codename"], "mondrian")
        self.assertEqual(d["device"]["soc"], "SM8475")
        self.assertEqual(d["device"]["bsp_family"], "taro")
        self.assertEqual(d["base"], "AOSP 17")

    def test_verified_density_is_actually_configured(self):
        density = self.data["confirmed_source_based"]["logical_density_dpi"]
        board = (ROOT / "BoardConfig.mk").read_text(encoding="utf-8")
        self.assertEqual(density, 560)
        self.assertIn("TARGET_SCREEN_DENSITY := 560", board)

    def test_touch_binding_conflict_stays_explicit(self):
        t = self.data["reference_hardware_only"]["touch"]
        self.assertEqual(t["controller_dts_compatible"], "goodix,gt9916S")
        self.assertEqual(t["manufacturer_driver_compatible"], "goodix,brl-d")
        self.assertNotEqual(t["controller_dts_compatible"], t["manufacturer_driver_compatible"])
        self.assertEqual(t["firmware"], "goodix_firmware_m11a.bin")
        self.assertFalse(t["matching_driver_selected"])
        self.assertIsNone(t["physical_firmware_revision"])

    def test_udfps_is_not_touch_driver(self):
        f = self.data["reference_hardware_only"]["fingerprint"]
        self.assertTrue(f["separate_from_touch"])
        self.assertEqual(f["dts_compatible"], "goodix,fingerprint")
        self.assertFalse(f["hardware_hal_selected"])
        self.assertFalse(f["udfps_end_to_end_tested"])

    def test_no_false_release_claim_or_optional_fm(self):
        self.assertFalse(any(self.data["production_gates"].values()))
        self.assertIn("FM radio", self.data["excluded_from_initial_build"])


if __name__ == "__main__":
    unittest.main()
