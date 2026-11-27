"""VINTF of mondrian: the stock camera provider and the camera services the
CHI override registers, checked with the rules of sm8450-common's VINTF test
(FCM level 7, the framework matrix extension, servers in the lists)."""
import importlib.util
import unittest
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
_spec = importlib.util.spec_from_file_location("sm8450_vintf", COMMON / "tests/test_vintf.py")
common = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(common)

SERVERS = {
    "android.hardware.camera.provider": ["vendor/bin/hw/vendor.qti.camera.provider@2.7-service_64",
                                         "vendor/lib64/hw/camera.qcom.so"],
    "vendor.qti.hardware.camera.aon": [
        "vendor/lib64/hw/com.qti.chi.override.so",
        "vendor/lib64/vendor.qti.hardware.camera.aon@1.0-service-impl.so"],
    "vendor.qti.hardware.camera.postproc": [
        "vendor/lib64/hw/com.qti.chi.override.so",
        "vendor/lib64/vendor.qti.hardware.camera.postproc@1.0-service-impl.so"],
}


class MondrianVintfTest(common.VintfTest):
    MANIFEST = ROOT / "vintf/manifest.xml"
    FCM = ROOT / "vintf/framework_compatibility_matrix.xml"

    def setUp(self):
        # The servers are looked up in both lists: this tree is the device one.
        common.DEVICE = ROOT
        super().setUp()
        common.SERVERS.update(SERVERS)
        _, common_instances = common.manifest_instances(common.VintfTest.MANIFEST)
        self.all_instances = self.instances + common_instances

    def test_no_duplicate_instances(self):
        self.assertEqual(len(self.all_instances), len(set(self.all_instances)))

    def test_camera_provider_is_legacy_1_only(self):
        cams = [i for i in self.instances if i[1] == "android.hardware.camera.provider"]
        self.assertEqual(cams, [("hidl", "android.hardware.camera.provider", (2, 7),
                                 "ICameraProvider", "legacy/1")])

    def test_device_matrix_has_no_vendor_ndk(self):
        self.skipTest("the device matrix is sm8450-common's")

    def test_board_wiring(self):
        board = (ROOT / "BoardConfig.mk").read_text()
        self.assertIn("DEVICE_MANIFEST_FILE += $(DEVICE_PATH)/vintf/manifest.xml", board)
        self.assertIn("DEVICE_FRAMEWORK_COMPATIBILITY_MATRIX_FILE += "
                      "$(DEVICE_PATH)/vintf/framework_compatibility_matrix.xml", board)

    def test_kernel_is_kept_and_uffd_gc_is_explicit(self):
        self.skipTest("set in sm8450-common")


if __name__ == "__main__":
    unittest.main()
