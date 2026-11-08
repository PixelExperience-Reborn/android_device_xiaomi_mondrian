# PE-Reborn device-specific board configuration for POCO F5 Pro / Redmi K60.
# The shared board file is authored for the independent PE-Reborn tree.

DEVICE_PATH := device/xiaomi/mondrian
include device/xiaomi/sm8450-common/BoardConfigCommon.mk

# TODO (hardware gate): verify all partition/boot/AVB parameters from
# official Xiaomi sources and on-device evidence before enabling images.
# No inherited vendor, LineageOS configuration, or test AVB keys here.
