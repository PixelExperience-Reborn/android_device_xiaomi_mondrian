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

# Recovery: the audio/ADSP kernel modules init.recovery.qcom.rc loads before
# it starts the ADSP (battery status), in the stock order of OS3.0.8.0.
# Their other dependencies are in modules.load.recovery of vendor_boot.
# (device/xiaomi/mondrian-kernel/Android.bp installs them.)
PRODUCT_PACKAGES += \
    mondrian_recovery_q6_pdr_dlkm \
    mondrian_recovery_q6_notifier_dlkm \
    mondrian_recovery_snd_event_dlkm \
    mondrian_recovery_gpr_dlkm \
    mondrian_recovery_spf_core_dlkm \
    mondrian_recovery_adsp_loader_dlkm
