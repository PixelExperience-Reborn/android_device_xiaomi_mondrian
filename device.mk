# PE-Reborn mondrian device product definitions.
LOCAL_PATH := $(call my-dir)

$(call inherit-product, device/xiaomi/sm8450-common/common.mk)

# Pending hardware-qualified implementations:
# - Verified mondrian vendor blobs and firmware provenance
# - Fstab/init, VINTF, SELinux, graphics, audio, radio, camera, NFC
# - In-display fingerprint, illumination, sensors and touch controller
# Do not add HAL packages or proprietary services without an ABI review.
