# SPDX-License-Identifier: Apache-2.0
"""The stock kernel modules this build installs and loads (BoardConfig.mk).

MONDRIAN_MIUI_DLKM leaves out the vendor_dlkm modules that serve only the
HyperOS/MIUI userspace. None of the modules that stay may depend on them, and
none of them may be one LineageOS for mondrian (Android 17) loads.
"""
import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KERNEL = Path(os.environ.get("MONDRIAN_KERNEL", ROOT.parents[1] / "vendor/xiaomi/mondrian/kernel"))
if not KERNEL.is_dir():
    KERNEL = ROOT.parent / "proprietary_vendor_xiaomi_mondrian/kernel"
MIUI_ONLY = {
    "binder_gki", "binder_prio", "binderinfo", "cameralog", "extend_reclaim", "icc_test", "mi_freqwdg",
    "migt", "miicmpfilter", "millet_binder", "millet_core", "millet_hs", "millet_oem_cgroup", "millet_pkg",
    "millet_sig", "minet", "miwill", "miwill_mode_redudancy", "mmrm_test_module", "perf_helper", "sla",
}


def name(path):
    return re.sub(r"\.ko$", "", path.split("/")[-1]).replace("-", "_")


def miui_list():
    board = (ROOT / "BoardConfig.mk").read_text()
    block = re.search(r"(?ms)^MONDRIAN_MIUI_DLKM := \\\n(.*?)\nBOARD_VENDOR_KERNEL_MODULES :=", board).group(1)
    return block.replace("\\", " ").split()


class KernelModulesTest(unittest.TestCase):
    def test_miui_only_modules_are_left_out(self):
        files = miui_list()
        self.assertEqual({name(f) for f in files}, MIUI_ONLY)
        board = (ROOT / "BoardConfig.mk").read_text()
        self.assertIn("$(filter-out $(addprefix $(KERNEL_PATH)/vendor_dlkm/,$(MONDRIAN_MIUI_DLKM))", board)
        self.assertIn("BOARD_VENDOR_KERNEL_MODULES_LOAD := $(filter-out $(MONDRIAN_MIUI_DLKM)", board)

    @unittest.skipUnless((KERNEL / "vendor_dlkm/modules.dep").is_file(), "needs the extracted stock kernel")
    def test_no_kept_module_depends_on_them(self):
        for listing in ("vendor_ramdisk", "vendor_dlkm"):
            for line in (KERNEL / listing / "modules.dep").read_text().splitlines():
                module, _, deps = line.partition(":")
                if name(module) in MIUI_ONLY:
                    continue
                with self.subTest(module=module):
                    self.assertFalse({name(d) for d in deps.split()} & MIUI_ONLY)
        for f in miui_list():
            self.assertTrue((KERNEL / "vendor_dlkm" / f).is_file(), f)
        first_stage = {name(m) for m in (KERNEL / "vendor_ramdisk/modules.load").read_text().split()}
        self.assertFalse(first_stage & MIUI_ONLY)


def mtdoops_list():
    board = (ROOT / "BoardConfig.mk").read_text()
    block = re.search(r"(?ms)^ifneq \(\$\(TARGET_BUILD_VARIANT\),user\)\nMONDRIAN_MTDOOPS_MODULES := (.*?)\n"
                      r"BOARD_VENDOR_RAMDISK_KERNEL_MODULES_LOAD \+= \$\(MONDRIAN_MTDOOPS_MODULES\)\nendif", board)
    return block.group(1).replace("\\", " ").split() if block else None


class MtdoopsFirstStageTest(unittest.TestCase):
    """Debug builds load Xiaomi's sda15 log store in the normal first stage."""

    def test_debug_builds_only(self):
        self.assertIsNotNone(mtdoops_list(), "MONDRIAN_MTDOOPS_MODULES must be added for non-user builds only")

    @unittest.skipUnless((KERNEL / "vendor_ramdisk/modules.dep").is_file(), "needs the extracted stock kernel")
    def test_modules_dependencies_and_order(self):
        files = mtdoops_list()
        ramdisk = KERNEL / "vendor_ramdisk"
        for f in files:
            self.assertTrue((ramdisk / f).is_file(), f)
        deps = {}
        for line in (ramdisk / "modules.dep").read_text().splitlines():
            module, _, rest = line.partition(":")
            deps[name(module)] = {name(d) for d in rest.split()}
        listed = [name(f) for f in files]
        for i, module in enumerate(listed):
            with self.subTest(module=module):
                self.assertLessEqual(deps[module], set(listed[:i]), "dependencies must load first")
        recovery = {name(m) for m in (ramdisk / "modules.load.recovery").read_text().split()}
        self.assertLessEqual(set(listed), recovery, "the recovery sessions load all of them")
        normal = (ramdisk / "modules.load").read_text().split()
        self.assertFalse(set(files) & set(normal), "not in the stock normal list yet")
        for ufs in ("ufs_qcom.ko", "ufshcd-crypto-qti.ko"):
            self.assertIn(ufs, normal, "block2mtd needs the UFS host loaded before it")


if __name__ == "__main__":
    unittest.main()
