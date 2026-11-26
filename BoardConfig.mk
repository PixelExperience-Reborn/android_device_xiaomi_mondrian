# SPDX-License-Identifier: Apache-2.0
#
# PixelExperience-Reborn Android 17: Xiaomi mondrian (POCO F5 Pro / Redmi K60).

DEVICE_PATH := device/xiaomi/mondrian
KERNEL_PATH := device/xiaomi/mondrian-kernel

include device/xiaomi/sm8450-common/BoardConfigCommon.mk

TARGET_OTA_ASSERT_DEVICE := mondrian

# Kernel: the prebuilt release of our CI (device/xiaomi/mondrian-kernel,
# built from android_kernel_xiaomi_sm8450, -modules and -devicetrees; the
# exact commits are in its provenance.json), installed the way AOSP installs
# the Pixel kernels. vendor/aosp's kernel build is not used.
ifeq ($(wildcard $(KERNEL_PATH)/Image),)
$(error mondrian: no prebuilt kernel in $(KERNEL_PATH); commit a release of the kernel CI there)
endif
TARGET_NO_KERNEL_OVERRIDE := true

# vendor_boot: the Cape base DTBs (msm-id 0x212/0x213/0x21c), as stock.
BOARD_PREBUILT_DTBIMAGE_DIR := $(KERNEL_PATH)/dtbs
# dtbo: one mondrian overlay (msm-id 530/531/540, board-id 0x10008 0).
BOARD_PREBUILT_DTBOIMAGE := $(KERNEL_PATH)/dtbo.img

# Modules and load lists in the places and order of stock: first stage and
# recovery from the vendor_boot ramdisk, the rest from vendor_dlkm.
BOARD_VENDOR_RAMDISK_KERNEL_MODULES := $(wildcard $(KERNEL_PATH)/vendor_ramdisk/*.ko)
BOARD_VENDOR_RAMDISK_KERNEL_MODULES_LOAD := \
    $(strip $(shell cat $(KERNEL_PATH)/vendor_ramdisk/modules.load))
BOARD_VENDOR_RAMDISK_RECOVERY_KERNEL_MODULES_LOAD := \
    $(strip $(shell cat $(KERNEL_PATH)/vendor_ramdisk/modules.load.recovery))
BOARD_USES_VENDOR_DLKMIMAGE := true
BOARD_VENDOR_KERNEL_MODULES := $(wildcard $(KERNEL_PATH)/vendor_dlkm/*.ko)
BOARD_VENDOR_KERNEL_MODULES_LOAD := \
    $(strip $(shell cat $(KERNEL_PATH)/vendor_dlkm/modules.load))

# Display: M11A, 1440x3200 WQHD+.
TARGET_SCREEN_DENSITY := 560

# Proprietary files
include vendor/xiaomi/mondrian/BoardConfigVendor.mk
