# Independent PixelExperience-Reborn AOSP 17 product for mondrian.
# This is a product skeleton, not a boot-ready device configuration.

$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)

# Own device and common hardware configuration.
$(call inherit-product, device/xiaomi/mondrian/device.mk)

# Own PE-Reborn product layer; not vendor/lineage.
$(call inherit-product, vendor/aosp/config/common_full_phone.mk)

PRODUCT_NAME := pe_mondrian
PRODUCT_DEVICE := mondrian
PRODUCT_BRAND := POCO
PRODUCT_MANUFACTURER := Xiaomi
PRODUCT_MODEL := POCO F5 Pro
