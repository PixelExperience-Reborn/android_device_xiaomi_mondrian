# SPDX-License-Identifier: Apache-2.0
#
# PixelExperience-Reborn Android 17: Xiaomi mondrian (POCO F5 Pro / Redmi K60).

$(call inherit-product, device/xiaomi/sm8450-common/common.mk)

# Proprietary files of the stock OS3.0.8.0 firmware.
$(call inherit-product, vendor/xiaomi/mondrian/mondrian-vendor.mk)

# Soong namespace of this tree (imported by the vendor build rules).
PRODUCT_SOONG_NAMESPACES += \
    device/xiaomi/mondrian

# odm ueventd rules: the display feature device of the fingerprint under the
# display (/dev/mi_display).
PRODUCT_COPY_FILES += \
    device/xiaomi/mondrian/rootdir/etc/ueventd.odm.rc:$(TARGET_COPY_OUT_ODM)/etc/ueventd.rc

# Audio configuration of sku_cape (rootdir/etc/audio): the stock one without
# the MiSound and Dolby effects and without the Qualcomm Bluetooth audio HAL.
PRODUCT_COPY_FILES += \
    device/xiaomi/mondrian/rootdir/etc/audio/sku_cape/audio_effects.xml:$(TARGET_COPY_OUT_VENDOR)/etc/audio/sku_cape/audio_effects.xml \
    device/xiaomi/mondrian/rootdir/etc/audio/sku_cape/audio_policy_configuration.xml:$(TARGET_COPY_OUT_VENDOR)/etc/audio/sku_cape/audio_policy_configuration.xml

# Runtime resource overlays of mondrian (overlay/, odm): brightness and
# automatic brightness, 120 Hz, always-on display, the camera cutout and
# rounded corners of the 1440x3200 panel, the power profile, and the names of
# both models chosen by ro.boot.hwc (docs/OVERLAYS.md in sm8450-common).
PRODUCT_PACKAGES += \
    FrameworksResMondrian \
    FrameworksResMondrianGlobal \
    SettingsProviderResMondrian \
    SettingsProviderResMondrianCN \
    SettingsResMondrian \
    SystemUIResMondrian \
    WifiResMondrian \
    WifiResMondrianCN

# Kernel image: the stock GKI kernel taken from the OTA (see BoardConfig.mk).
PRODUCT_COPY_FILES += \
    vendor/xiaomi/mondrian/kernel/Image:kernel

# The stock kernel is 5.10.236, past the LTS 5.10.107 the Android 17
# framework matrix asks for kernel FCM 7, and it carries its config (IKCONFIG):
# OTA packaging checks the kernel version and configs with the HALs.
PRODUCT_OTA_ENFORCE_VINTF_KERNEL_REQUIREMENTS := true

# mondrian launched with Android 13 (stock ro.product.first_api_level=33).
PRODUCT_SHIPPING_API_LEVEL := 33

# Camera app: Aperture (packages/apps/Aperture, LineageOS lineage-24.0 for
# Android 17) instead of AOSP Camera2, which it overrides. vendor/aosp adds
# it to the product (config/common.mk) when this is true.
PE_A17_PORT_APERTURE := true

# Hardware features of mondrian: the cameras and the sensors of the stock
# OS3.0.8.0 vendor (sku_cape), Android 17 definitions of frameworks/native.
PRODUCT_COPY_FILES += \
    frameworks/native/data/etc/android.hardware.camera.flash-autofocus.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.camera.flash-autofocus.xml \
    frameworks/native/data/etc/android.hardware.camera.front.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.camera.front.xml \
    frameworks/native/data/etc/android.hardware.camera.full.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.camera.full.xml \
    frameworks/native/data/etc/android.hardware.camera.raw.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.camera.raw.xml \
    frameworks/native/data/etc/android.hardware.sensor.accelerometer.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.sensor.accelerometer.xml \
    frameworks/native/data/etc/android.hardware.sensor.compass.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.sensor.compass.xml \
    frameworks/native/data/etc/android.hardware.sensor.gyroscope.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.sensor.gyroscope.xml \
    frameworks/native/data/etc/android.hardware.sensor.light.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.sensor.light.xml \
    frameworks/native/data/etc/android.hardware.sensor.proximity.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.sensor.proximity.xml \
    frameworks/native/data/etc/android.hardware.sensor.stepcounter.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.sensor.stepcounter.xml \
    frameworks/native/data/etc/android.hardware.sensor.stepdetector.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.sensor.stepdetector.xml
