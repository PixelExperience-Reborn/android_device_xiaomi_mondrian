# SPDX-License-Identifier: Apache-2.0
# PixelExperience-Reborn AOSP 17 product for mondrian (POCO F5 Pro / Redmi K60).
# The name follows the PixelExperience convention aosp_<device>: the PE
# build tooling (breakfast, CUSTOM_BUILD, org.pixelexperience.device)
# derives the device codename from it.
# This is a product skeleton, not a boot-ready device configuration.

$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)

# Own device and common hardware configuration.
$(call inherit-product, device/xiaomi/mondrian/device.mk)

# PE product layer (vendor/aosp, not vendor/lineage). The boot animation
# resolution must be set before it is inherited: M11A panel is 1440x3200.
TARGET_BOOT_ANIMATION_RES := 1440
# Google apps (MindTheGapps, vendor/gapps), as every PE build ships them.
WITH_GMS := true
$(call inherit-product, vendor/aosp/config/common_full_phone.mk)

PRODUCT_NAME := aosp_mondrian
PRODUCT_DEVICE := mondrian
PRODUCT_BRAND := POCO
PRODUCT_MANUFACTURER := Xiaomi
PRODUCT_MODEL := POCO F5 Pro

# Used by vendor/aosp only for WITH_GMS=true builds.
PRODUCT_GMS_CLIENTID_BASE := android-xiaomi
