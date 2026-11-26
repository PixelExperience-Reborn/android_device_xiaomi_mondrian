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

# Kernel image from the prebuilt release (see BoardConfig.mk).
PRODUCT_COPY_FILES += \
    device/xiaomi/mondrian-kernel/Image:kernel

# mondrian launched with Android 13 (stock ro.product.first_api_level=33).
PRODUCT_SHIPPING_API_LEVEL := 33

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
