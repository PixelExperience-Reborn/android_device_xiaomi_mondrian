# SPDX-License-Identifier: Apache-2.0
#
# PixelExperience-Reborn Android 17: the stock OS3.0.8.0 firmware of mondrian
# (firmware-files.txt), extracted from the official OTA into
# vendor/xiaomi/mondrian/radio by sm8450-common's tools/extract_proprietary.py.
# The images go to the RADIO/ files of the target files and, being in
# AB_OTA_PARTITIONS (BoardConfig.mk), into the A/B payload with the ROM.

ifeq ($(TARGET_DEVICE),mondrian)
LOCAL_PATH := vendor/xiaomi/mondrian

$(foreach p,$(MONDRIAN_FIRMWARE_PARTITIONS),\
  $(if $(wildcard $(LOCAL_PATH)/radio/$(p).img),,\
    $(error mondrian: $(LOCAL_PATH)/radio/$(p).img is missing; run device/xiaomi/sm8450-common/tools/extract_proprietary.py)))
$(foreach p,$(MONDRIAN_FIRMWARE_PARTITIONS),$(call add-radio-file,radio/$(p).img))
endif
