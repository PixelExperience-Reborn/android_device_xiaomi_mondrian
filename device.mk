# SPDX-License-Identifier: Apache-2.0
#
# PixelExperience-Reborn Android 17: Xiaomi mondrian (POCO F5 Pro / Redmi K60).

$(call inherit-product, device/xiaomi/sm8450-common/common.mk)

# Proprietary files of the stock OS3.0.8.0 firmware.
$(call inherit-product, vendor/xiaomi/mondrian/mondrian-vendor.mk)

# Soong namespace of this tree (imported by the vendor build rules).
PRODUCT_SOONG_NAMESPACES += \
    device/xiaomi/mondrian

# Kernel image from the prebuilt release (see BoardConfig.mk).
PRODUCT_COPY_FILES += \
    device/xiaomi/mondrian-kernel/Image:kernel

# mondrian launched with Android 13 (stock ro.product.first_api_level=33).
PRODUCT_SHIPPING_API_LEVEL := 33
