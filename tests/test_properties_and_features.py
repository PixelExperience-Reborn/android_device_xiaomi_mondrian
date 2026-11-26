"""vendor.prop and the hardware features of mondrian.

The properties come from the stock OS3.0.8.0.VMNCNXM vendor/build.prop:
the fingerprint under the display (FOD), the M11A panel for SurfaceFlinger
and the Dalvik heap. The platform ones live in sm8450-common.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANEL = (1440, 3200)
# Stock FOD: top-left corner and size of the sensor area, in panel pixels.
FOD_XY = (596, 2758)
FOD_SIZE = (248, 248)


def read_props(name):
    props = {}
    for line in (ROOT / name).read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            key, sep, value = line.partition("=")
            assert sep and key not in props, line
            props[key] = value
    return props


class PropertiesTest(unittest.TestCase):
    def setUp(self):
        self.props = read_props("vendor.prop")

    def test_fod_area_is_the_stock_one_and_on_the_panel(self):
        xy = tuple(map(int, self.props["persist.vendor.sys.fp.fod.location.X_Y"].split(",")))
        size = tuple(map(int, self.props["persist.vendor.sys.fp.fod.size.width_height"].split(",")))
        self.assertEqual(xy, FOD_XY)
        self.assertEqual(size, FOD_SIZE)
        self.assertLessEqual(xy[0] + size[0], PANEL[0])
        self.assertLessEqual(xy[1] + size[1], PANEL[1])
        # The sensor is centred horizontally on the panel.
        self.assertEqual(xy[0] + size[0] // 2, PANEL[0] // 2)
        self.assertEqual(self.props["ro.hardware.fp.fod"], "true")

    def test_only_device_properties(self):
        for key in self.props:
            self.assertRegex(key, r"^(ro\.hardware\.fp\.|persist\.vendor\.sys\.fp\.|"
                                  r"ro\.surface_flinger\.|debug\.sf\.|dalvik\.vm\.heap|"
                                  r"ro\.vendor\.audio\.spk\.stereo$|"
                                  r"persist\.vendor\.audio\.voicecall\.speaker\.stereo$)")

    def test_board_config_appends_after_common(self):
        board = (ROOT / "BoardConfig.mk").read_text()
        include = board.index("include device/xiaomi/sm8450-common/BoardConfigCommon.mk")
        append = board.index("TARGET_VENDOR_PROP += $(DEVICE_PATH)/vendor.prop")
        self.assertLess(include, append)


class FeaturesTest(unittest.TestCase):
    def test_camera_and_sensor_features(self):
        device = (ROOT / "device.mk").read_text()
        copies = dict((dst, src) for src, dst in re.findall(
            r"frameworks/native/data/etc/([\w.\-]+\.xml):"
            r"\$\(TARGET_COPY_OUT_VENDOR\)/etc/permissions/([\w.\-]+\.xml)", device))
        for feature in ("camera.flash-autofocus", "camera.front", "camera.full", "camera.raw",
                        "sensor.accelerometer", "sensor.compass", "sensor.gyroscope",
                        "sensor.light", "sensor.proximity", "sensor.stepcounter",
                        "sensor.stepdetector"):
            name = f"android.hardware.{feature}.xml"
            self.assertEqual(copies.get(name), name)


if __name__ == "__main__":
    unittest.main()
