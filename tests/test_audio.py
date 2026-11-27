"""Audio configuration of mondrian (rootdir/etc/audio/sku_cape).

The stock OS3.0.8.0 sku_cape files without the MiSound and Dolby effects and
without the Qualcomm Bluetooth audio HAL. Everything they load must be
shipped: the AOSP effect libraries and policy files by sm8450-common's
PRODUCT_PACKAGES, the stock ones by the proprietary lists.
"""
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
SKU = ROOT / "rootdir/etc/audio/sku_cape"
NS = {"e": "http://schemas.android.com/audio/audio_effects_conf/v2_0"}
# AOSP 17 vendor modules: installed name -> module name.
AOSP_FILES = {
    "libbundlewrapper.so": "libbundlewrapper", "libreverbwrapper.so": "libreverbwrapper",
    "libvisualizer.so": "libvisualizer", "libdownmix.so": "libdownmix", "libldnhncr.so": "libldnhncr",
    "libdynproc.so": "libdynproc", "libeffectproxy.so": "libeffectproxy",
    "/vendor/etc/r_submix_audio_policy_configuration.xml": "r_submix_audio_policy_configuration.xml",
    "/vendor/etc/default_volume_tables.xml": "default_volume_tables.xml",
}


def listed():
    paths = set()
    for lst in (COMMON / "proprietary-files.txt", ROOT / "proprietary-files.txt"):
        for line in lst.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                paths.add(line.split("|")[0].split(";")[0].lstrip("-"))
    return paths


class AudioConfigTest(unittest.TestCase):
    def setUp(self):
        self.listed = listed()
        self.common = (COMMON / "common.mk").read_text()

    def built(self, module):
        return re.search(rf"(?m)^\s+{re.escape(module)}( \\)?$", self.common) is not None

    def test_installed_to_sku_cape(self):
        device = (ROOT / "device.mk").read_text()
        for name in ("audio_effects.xml", "audio_policy_configuration.xml"):
            self.assertIn(f"device/xiaomi/mondrian/rootdir/etc/audio/sku_cape/{name}:"
                          f"$(TARGET_COPY_OUT_VENDOR)/etc/audio/sku_cape/{name}", device)
            self.assertNotIn(f"vendor/etc/audio/sku_cape/{name}", self.listed)

    def test_no_misound_or_dolby(self):
        for name in ("audio_effects.xml", "audio_policy_configuration.xml"):
            text = (SKU / name).read_text()
            code = re.sub(r"<!--.*?-->", "", text, flags=re.S)
            self.assertIsNone(re.search(r"(?i)dolby|misound|libhwdap|libswdap|libswgamedap|libswvqe", code), name)

    def test_effect_libraries_are_shipped(self):
        root = ET.parse(SKU / "audio_effects.xml").getroot()
        libraries = {lib.get("name"): lib.get("path") for lib in root.find("e:libraries", NS)}
        for path in libraries.values():
            with self.subTest(path=path):
                if path in AOSP_FILES:
                    self.assertTrue(self.built(AOSP_FILES[path]))
                else:
                    self.assertIn(f"vendor/lib64/soundfx/{path}", self.listed)
        used = {e.get("library") for e in root.find("e:effects", NS).iter()
                if e.get("library")}
        self.assertLessEqual(used, set(libraries))

    def test_policy_includes_are_shipped(self):
        text = (SKU / "audio_policy_configuration.xml").read_text()
        ET.fromstring(text.encode())
        for target in re.findall(r'<xi:include href="([^"]+)"', text):
            with self.subTest(target=target):
                if target in AOSP_FILES:
                    self.assertTrue(self.built(AOSP_FILES[target]))
                else:
                    self.assertIn(target.lstrip("/"), self.listed)
        self.assertNotIn("bluetooth_qti", text)

    def test_only_the_cape_sku(self):
        skus = {m[1] for p in self.listed for m in [re.match(r"vendor/etc/audio/(sku_[^/]+)/", p)] if m}
        self.assertEqual(skus, {"sku_cape"})


if __name__ == "__main__":
    unittest.main()
