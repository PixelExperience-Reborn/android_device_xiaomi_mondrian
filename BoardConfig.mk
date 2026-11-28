# SPDX-License-Identifier: Apache-2.0
#
# PixelExperience-Reborn Android 17: Xiaomi mondrian (POCO F5 Pro / Redmi K60).

DEVICE_PATH := device/xiaomi/mondrian
KERNEL_PATH := vendor/xiaomi/mondrian/kernel

include device/xiaomi/sm8450-common/BoardConfigCommon.mk

TARGET_OTA_ASSERT_DEVICE := mondrian

# Kernel: the stock kernel of OS3.0.8.0, the Google GKI 5.10.236-android12-9
# the stock vendor and firmware run on, with its DTBs, DTBO and vendor
# modules. sm8450-common's tools/extract_proprietary.py takes them from the
# boot, vendor_boot, dtbo and vendor_dlkm images of the official OTA (pinned
# by SHA-256 in kernel-files.txt) into vendor/xiaomi/mondrian/kernel
# (tools/stock_kernel.py); they are not committed. Installed the way AOSP
# installs the Pixel kernels; vendor/aosp's kernel build is not used.
ifeq ($(wildcard $(KERNEL_PATH)/Image),)
$(error mondrian: no kernel in $(KERNEL_PATH); run device/xiaomi/sm8450-common/tools/extract_proprietary.py)
endif
TARGET_NO_KERNEL_OVERRIDE := true

# vendor_boot: the DTBs of the stock vendor_boot (all Cape variants).
BOARD_PREBUILT_DTBIMAGE_DIR := $(KERNEL_PATH)/dtbs
# dtbo: the DTBO table of the stock dtbo image.
BOARD_PREBUILT_DTBOIMAGE := $(KERNEL_PATH)/dtbo.img

# Modules and load lists in the places and order of stock: first stage and
# recovery from the vendor_boot ramdisk, the rest from vendor_dlkm.
BOARD_VENDOR_RAMDISK_KERNEL_MODULES := $(wildcard $(KERNEL_PATH)/vendor_ramdisk/*.ko)
BOARD_VENDOR_RAMDISK_KERNEL_MODULES_LOAD := \
    $(strip $(shell cat $(KERNEL_PATH)/vendor_ramdisk/modules.load))
BOARD_VENDOR_RAMDISK_RECOVERY_KERNEL_MODULES_LOAD := \
    $(strip $(shell cat $(KERNEL_PATH)/vendor_ramdisk/modules.load.recovery))
BOARD_VENDOR_RAMDISK_KERNEL_MODULES_BLOCKLIST_FILE := $(KERNEL_PATH)/vendor_ramdisk/modules.blocklist
# Debug builds: Xiaomi's kernel log store on sda15. The bootloader puts
# "block2mtd.block2mtd=/dev/block/sda15,2097152" and "mtdoops.mtddev=0
# mtdoops.record_size=2097152 mtdoops.dump_oops=0" on the kernel command
# line, which libmodprobe applies (first stage init and /vendor/bin/modprobe
# alike). Stock loads these modules from vendor_dlkm (vendor_modprobe.sh, on
# early-init) and in recovery, so nothing before the second stage is ever
# recorded. Loaded at the end of the normal first stage list as well, in the
# order the recovery sessions load them (mtd is pulled in first as a
# dependency of ofpart there), a panic or a restart of a userdebug/eng boot
# from first stage mount on leaves its kernel log and pmsg in sda15
# ("LAST KMSG", "LAST LOGCAT"). pm8941-pwrkey is a dependency of mtdoops; all
# of them are in the vendor_boot ramdisk already.
ifneq ($(TARGET_BUILD_VARIANT),user)
MONDRIAN_MTDOOPS_MODULES := pm8941-pwrkey.ko mtd.ko ofpart.ko chipreg.ko block2mtd.ko \
    mtd_blkdevs.ko mtdblock.ko mtdoops.ko
BOARD_VENDOR_RAMDISK_KERNEL_MODULES_LOAD += $(MONDRIAN_MTDOOPS_MODULES)
endif
# Recovery also needs the audio/ADSP modules (battery status comes from the
# ADSP), which the release ships for vendor_dlkm only: the stock recovery
# insmods them in this order on early-init. They join the vendor_boot ramdisk
# and are loaded after modules.load.recovery, which holds their dependencies
# (pdr_interface, rproc_qcom_common); first stage init loads them in recovery
# only, normal boot keeps loading them from vendor_dlkm.
MONDRIAN_RECOVERY_DLKM := q6_pdr_dlkm.ko q6_notifier_dlkm.ko snd_event_dlkm.ko gpr_dlkm.ko \
    spf_core_dlkm.ko adsp_loader_dlkm.ko
BOARD_VENDOR_RAMDISK_KERNEL_MODULES += $(addprefix $(KERNEL_PATH)/vendor_dlkm/,$(MONDRIAN_RECOVERY_DLKM))
BOARD_VENDOR_RAMDISK_RECOVERY_KERNEL_MODULES_LOAD += $(MONDRIAN_RECOVERY_DLKM)
BOARD_USES_VENDOR_DLKMIMAGE := true
BOARD_VENDOR_KERNEL_MODULES_BLOCKLIST_FILE := $(KERNEL_PATH)/vendor_dlkm/modules.blocklist
# Modules of the stock vendor_dlkm that serve only the HyperOS/MIUI userspace:
# app freezing (millet, with its binder hooks binder_gki/binder_prio/binderinfo),
# game turbo (migt), MIUI network acceleration (sla, minet, miwill,
# miicmpfilter), Xiaomi tuning hooks (perf_helper, extend_reclaim,
# mi_freqwdg), the camera log service and two test modules. Without the MIUI
# userspace they only hook binder, the scheduler and memory reclaim.
# LineageOS for mondrian (Android 17) does not load them; no other module
# depends on them (tests/test_kernel_modules.py). Not installed.
MONDRIAN_MIUI_DLKM := \
    binder_gki.ko binder_prio.ko binderinfo.ko cameralog.ko extend_reclaim.ko \
    icc-test.ko mi_freqwdg.ko migt.ko miicmpfilter.ko millet_binder.ko \
    millet_core.ko millet_hs.ko millet_oem_cgroup.ko millet_pkg.ko millet_sig.ko \
    minet.ko miwill.ko miwill_mode_redudancy.ko mmrm_test_module.ko perf_helper.ko sla.ko
BOARD_VENDOR_KERNEL_MODULES := $(filter-out $(addprefix $(KERNEL_PATH)/vendor_dlkm/,$(MONDRIAN_MIUI_DLKM)), \
    $(wildcard $(KERNEL_PATH)/vendor_dlkm/*.ko))
BOARD_VENDOR_KERNEL_MODULES_LOAD := $(filter-out $(MONDRIAN_MIUI_DLKM), \
    $(strip $(shell cat $(KERNEL_PATH)/vendor_dlkm/modules.load)))

# Stock firmware of OS3.0.8.0 (China), flashed with the ROM: the partitions
# of firmware-files.txt, extracted to vendor/xiaomi/mondrian/radio and added
# as radio images (firmware/Android.mk) to the A/B payload.
MONDRIAN_FIRMWARE_PARTITIONS := $(shell sed -n 's/^\([a-z0-9_-]*\)|.*/\1/p' $(DEVICE_PATH)/firmware-files.txt)
AB_OTA_PARTITIONS += $(MONDRIAN_FIRMWARE_PARTITIONS)

# Display: M11A, 1440x3200 WQHD+.
TARGET_SCREEN_DENSITY := 560

# Properties of the stock OS3.0.8.0 vendor specific to mondrian (fingerprint
# under the display, panel, Dalvik heap), after those of sm8450-common.
TARGET_VENDOR_PROP += $(DEVICE_PATH)/vendor.prop

# VINTF: the stock camera provider and the camera services of the CHI
# override, after the platform manifest of sm8450-common.
DEVICE_MANIFEST_FILE += $(DEVICE_PATH)/vintf/manifest.xml
DEVICE_FRAMEWORK_COMPATIBILITY_MATRIX_FILE += $(DEVICE_PATH)/vintf/framework_compatibility_matrix.xml

# SELinux: the bring-up vendor policy of the mondrian services (generated by
# sm8450-common's tools/gen_bringup_sepolicy.py), after sm8450-common's.
BOARD_VENDOR_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy/vendor

# Proprietary files
include vendor/xiaomi/mondrian/BoardConfigVendor.mk
