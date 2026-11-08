from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class IndependentProductScaffoldTest(unittest.TestCase):
    def test_product_is_registered(self):
        products = (ROOT / "AndroidProducts.mk").read_text()
        self.assertIn("$(LOCAL_DIR)/pe_mondrian.mk", products)

    def test_product_stays_on_aosp_and_own_pe_layer(self):
        product = (ROOT / "pe_mondrian.mk").read_text()
        self.assertIn("PRODUCT_NAME := pe_mondrian", product)
        self.assertIn("PRODUCT_DEVICE := mondrian", product)
        self.assertIn("vendor/aosp/config/common_full_phone.mk", product)
        self.assertIn("device/xiaomi/mondrian/device.mk", product)

    def test_common_device_chain_is_explicit(self):
        board = (ROOT / "BoardConfig.mk").read_text()
        device = (ROOT / "device.mk").read_text()
        self.assertIn("device/xiaomi/sm8450-common/BoardConfigCommon.mk", board)
        self.assertIn("device/xiaomi/sm8450-common/common.mk", device)

    def test_no_rom_specific_dependency_in_active_makefiles(self):
        for file in ("AndroidProducts.mk", "pe_mondrian.mk", "device.mk", "BoardConfig.mk"):
            with self.subTest(file=file):
                # Comments are exempt; check active statements only.
                body = "\n".join(
                    line for line in (ROOT / file).read_text().splitlines()
                    if line.strip() and not line.lstrip().startswith("#")
                ).lower()
                for forbidden in ("vendor/lineage", "org.lineageos", "vendor.lineage", "lineage_mondrian"):
                    self.assertNotIn(forbidden, body)


if __name__ == "__main__":
    unittest.main()
