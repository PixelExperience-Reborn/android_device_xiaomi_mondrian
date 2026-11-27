# SPDX-License-Identifier: Apache-2.0
"""Kernel modules of the recovery and the module types Android 17 allows.

The recovery needs the audio/ADSP modules (battery status comes from the
ADSP). The release ships them for vendor_dlkm; BoardConfig.mk adds them to the
vendor_boot ramdisk and loads them in recovery after modules.load.recovery,
in the order of the stock recovery. Android 17 forbids prebuilt_vendor and the
other PRODUCT_COPY_FILES conversion types in Android.bp files, and an ELF file
(a .ko) in PRODUCT_COPY_FILES under a lib directory, so neither may install
them.
"""
import re
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORDER = ["q6_pdr_dlkm.ko", "q6_notifier_dlkm.ko", "snd_event_dlkm.ko", "gpr_dlkm.ko", "spf_core_dlkm.ko",
         "adsp_loader_dlkm.ko"]
# android/neverallow.go (createPrebuiltEtcBpDefineRule) of android-17.0.0_r1.
FORBIDDEN_TYPES = ("prebuilt_any", "prebuilt_usr_srec", "prebuilt_priv_app", "prebuilt_rfs", "prebuilt_framework",
                   "prebuilt_wlc_upt", "prebuilt_odm", "prebuilt_vendor_dlkm", "prebuilt_bt_firmware",
                   "prebuilt_tvservice", "prebuilt_optee", "prebuilt_tvconfig", "prebuilt_vendor", "prebuilt_sbin",
                   "prebuilt_system", "prebuilt_first_stage_ramdisk", "prebuilt_radio", "prebuilt_gpu",
                   "prebuilt_vendor_overlay", "prebuilt_tee")


def sibling(*names):
    for base in (ROOT.parent, ROOT / ".ci"):
        for name in names:
            if (base / name).is_dir():
                return base / name
    return None


COMMON = sibling("sm8450-common", "android_device_xiaomi_sm8450-common")
KERNEL = sibling("mondrian-kernel", "android_device_xiaomi_mondrian-kernel")


def modinfo(path):
    data = path.read_bytes()
    shoff, = struct.unpack_from("<Q", data, 0x28)
    shentsize, shnum, shstrndx = struct.unpack_from("<HHH", data, 0x3A)
    sections = [struct.unpack_from("<IIQQQQIIQQ", data, shoff + i * shentsize) for i in range(shnum)]
    names = sections[shstrndx][4]
    for section in sections:
        name = data[names + section[0]: data.index(b"\0", names + section[0])]
        if name == b".modinfo":
            body = data[section[4]: section[4] + section[5]].decode(errors="ignore")
            return dict(item.split("=", 1) for item in body.split("\0") if "=" in item)
    return {}


class RecoveryModulesTest(unittest.TestCase):
    def test_board_config_loads_them_in_recovery(self):
        board = (ROOT / "BoardConfig.mk").read_text()
        listed = re.search(r"MONDRIAN_RECOVERY_DLKM := (.*?)\n\S", board, re.S)[1].replace("\\", " ").split()
        self.assertEqual(listed, ORDER)
        self.assertIn("BOARD_VENDOR_RAMDISK_KERNEL_MODULES += "
                      "$(addprefix $(KERNEL_PATH)/vendor_dlkm/,$(MONDRIAN_RECOVERY_DLKM))", board)
        self.assertIn("BOARD_VENDOR_RAMDISK_RECOVERY_KERNEL_MODULES_LOAD += $(MONDRIAN_RECOVERY_DLKM)", board)
        # Normal boot keeps its own first stage list and loads them from vendor_dlkm.
        self.assertNotRegex(board, r"BOARD_VENDOR_RAMDISK_KERNEL_MODULES_LOAD \+=")

    def test_no_insmod_of_them_in_the_recovery_rc(self):
        if COMMON is None:
            self.skipTest("needs sm8450-common")
        rc = (COMMON / "rootdir/etc/init.recovery.qcom.rc").read_text()
        self.assertNotRegex(rc, r"(?m)^\s*insmod ")

    def test_dependencies_come_first(self):
        if KERNEL is None:
            self.skipTest("needs the mondrian-kernel release")
        norm = lambda name: name.removesuffix(".ko").replace("-", "_")
        loaded = {norm(l) for l in (KERNEL / "vendor_ramdisk/modules.load.recovery").read_text().split()}
        for module in ORDER:
            with self.subTest(module=module):
                info = modinfo(KERNEL / "vendor_dlkm" / module)
                self.assertTrue(info.get("vermagic"), module)
                for dep in filter(None, info.get("depends", "").split(",")):
                    self.assertIn(norm(dep), loaded, f"{module} needs {dep}")
                loaded.add(norm(module))

    def test_no_forbidden_module_type(self):
        trees = [ROOT] + [t for t in (COMMON, KERNEL) if t is not None]
        for tree in trees:
            for bp in tree.rglob("Android.bp"):
                if ".git" in bp.parts or ".ci" in bp.parts:
                    continue
                types = set(re.findall(r"(?m)^(\w+) \{", bp.read_text()))
                self.assertFalse(types & set(FORBIDDEN_TYPES), str(bp))


if __name__ == "__main__":
    unittest.main()
