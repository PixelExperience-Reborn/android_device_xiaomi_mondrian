# SPDX-License-Identifier: Apache-2.0
"""Runtime resource overlays of mondrian (overlay/, odm), checked with the
rules of sm8450-common's overlay test, plus the values of the device: the
1440x3200 panel, automatic brightness, the power profile and both models
(Redmi K60 in China, POCO F5 Pro elsewhere, chosen by ro.boot.hwc)."""
import importlib.util
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sibling(*names):
    """A sibling tree: next to this one (device/xiaomi/* in the source tree,
    android_device_xiaomi_* side by side) or in .ci/ (checked out by CI)."""
    for base in (ROOT.parent, ROOT / ".ci"):
        for name in names:
            if (base / name).is_dir():
                return base / name
    return None


COMMON = sibling("sm8450-common", "android_device_xiaomi_sm8450-common")
if COMMON is None:
    raise unittest.SkipTest("needs the sm8450-common tree next to this one or in .ci/")
_spec = importlib.util.spec_from_file_location("sm8450_overlays", COMMON / "tests/test_overlays.py")
common = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(common)

FRAMEWORKS = ROOT / "overlay/FrameworksResMondrian/res"


def value(path, name):
    for element in ET.parse(path).getroot():
        if element.get("name") == name:
            items = element.findall("item")
            return [i.text for i in items] if len(element) else element.text
    raise KeyError(name)


class MondrianOverlayTest(unittest.TestCase):
    def test_device_overlays(self):
        found = common.check_tree(self, ROOT, "device_specific", ROOT / "device.mk", 700, 800)
        self.assertEqual(set(found), {
            "FrameworksResMondrian", "FrameworksResMondrianGlobal", "SettingsProviderResMondrian",
            "SettingsProviderResMondrianCN", "SettingsResMondrian", "SystemUIResMondrian",
            "WifiResMondrian", "WifiResMondrianCN"})
        # Region overlays apply over the default ones.
        for name, region in [("FrameworksResMondrianGlobal", "GL"), ("SettingsProviderResMondrianCN", "CN"),
                             ("WifiResMondrianCN", "CN")]:
            attrs = found[name][1]
            self.assertEqual(attrs["requiredSystemPropertyValue"], region)
            base = found[name.replace("Global", "").replace("CN", "")][1]
            self.assertGreater(int(attrs["priority"]), int(base["priority"]))
            self.assertEqual(attrs["targetPackage"], base["targetPackage"])

    def test_brightness_range(self):
        config = FRAMEWORKS / "values/config.xml"
        low, high, default, dim = (float(value(config, f"config_screenBrightness{n}Float"))
                                   for n in ("SettingMinimum", "SettingMaximum", "SettingDefault", "Dim"))
        self.assertTrue(0 < low <= default <= high <= 1.0)
        self.assertTrue(0 < dim <= default)

    def test_automatic_brightness_curve(self):
        # Simple mapping strategy: N lux levels, N + 1 backlight values in 1..255
        # (BrightnessSynchronizer), lux strictly and backlight weakly increasing.
        config = FRAMEWORKS / "values/config.xml"
        lux = [int(v) for v in value(config, "config_autoBrightnessLevels")]
        backlight = [int(v) for v in value(config, "config_autoBrightnessLcdBacklightValues")]
        self.assertEqual(len(backlight), len(lux) + 1)
        self.assertEqual(lux, sorted(set(lux)))
        self.assertEqual(backlight, sorted(backlight))
        self.assertTrue(1 <= backlight[0] and backlight[-1] == 255)
        levels = [int(v) for v in value(config, "config_ambientThresholdLevels")]
        for name in ("config_ambientBrighteningThresholds", "config_ambientDarkeningThresholds"):
            self.assertEqual(len(value(config, name)), len(levels) + 1, name)

    def test_panel_geometry(self):
        config = FRAMEWORKS / "values/config.xml"
        cutout = value(config, "config_mainBuiltInDisplayCutout")
        self.assertRegex(cutout, r"^M 0,0 H -\d+ V \d+ H \d+ V 0 H 0 Z$")
        height = int(re.search(r"V (\d+)", cutout)[1])
        dimens = FRAMEWORKS / "values/dimens.xml"
        portrait = int(value(dimens, "status_bar_height_portrait").removesuffix("px"))
        self.assertGreaterEqual(portrait, height, "the status bar must cover the camera cutout")
        self.assertEqual(value(config, "config_defaultPeakRefreshRate"), "120")

    def test_power_profiles_differ_only_in_battery(self):
        cn = (FRAMEWORKS / "xml/power_profile.xml").read_text()
        gl = (ROOT / "overlay/FrameworksResMondrianGlobal/res/xml/power_profile.xml").read_text()
        ET.fromstring(cn), ET.fromstring(gl)
        self.assertIn('name="battery.capacity">5500<', cn)
        self.assertIn('name="battery.capacity">5160<', gl)
        strip = lambda t: re.sub(r"<!--.*?-->", "", t, flags=re.S).replace(">5160<", ">5500<")
        self.assertEqual(strip(cn), strip(gl))

    def test_model_names(self):
        names = {}
        for d in ("SettingsProviderResMondrian", "SettingsProviderResMondrianCN"):
            names[d] = value(ROOT / f"overlay/{d}/res/values/defaults.xml", "def_device_name_simple")
        self.assertEqual(names, {"SettingsProviderResMondrian": "POCO F5 Pro",
                                 "SettingsProviderResMondrianCN": "Redmi K60"})
        for d, ssid in (("WifiResMondrian", "POCO F5 Pro"), ("WifiResMondrianCN", "Redmi K60")):
            self.assertEqual(value(ROOT / f"overlay/{d}/res/values/config.xml",
                                   "wifi_tether_configure_ssid_default"), ssid)


if __name__ == "__main__":
    unittest.main()
