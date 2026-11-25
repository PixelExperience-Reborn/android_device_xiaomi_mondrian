# PixelExperience-Reborn Android 17 product registration for mondrian.
PRODUCT_MAKEFILES := \
    $(LOCAL_DIR)/aosp_mondrian.mk

# cp2a is the stable build/release configuration of android-17.0.0_r1.
COMMON_LUNCH_CHOICES := \
    aosp_mondrian-cp2a-userdebug \
    aosp_mondrian-cp2a-user \
    aosp_mondrian-cp2a-eng
