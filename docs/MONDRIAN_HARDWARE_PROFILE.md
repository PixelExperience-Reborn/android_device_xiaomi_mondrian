# PE-Reborn AOSP 17 — mondrian hardware configuration

This is the **independently authored** device branch for POCO F5 Pro /
Redmi K60, physical SM8475, product `pe_mondrian`. It is not a
LineageOS port and is **not currently bootable**.

## Reviewed implementation

`BoardConfig.mk` sets `TARGET_SCREEN_DENSITY := 560`, the same
device-specific logical density present in the working mondrian sources.
560 dpi does **not** imply FHD+/WQHD+ switching or select a DSI mode.

The new `hardware-profile.json` is a **reference inventory** (not a
build-time interface) of the M11A panel, Goodix touch and distinct Goodix
fingerprint hardware. Hardware revisions are deliberately unqualified.

## Why touch and UDFPS are not integrated yet

The read-only mondrian DTS references a Goodix SPI touchscreen as
`goodix,gt9916S`, at 15 MHz, IRQ GPIO21 and reset GPIO20, with
`goodix_firmware_m11a.bin` and `goodix_cfg_group_m11a.bin`.
The independent Goodix manufacturer driver references
`goodix,brl-d`; this is **not** a compatible match without port review.
The `goodix,fingerprint` node is a different component.

We must verify touch PID, firmware/config and ESD handling, input
coordinate scaling, UDFPS TEE/HAL and actual panel firmware before
enabling any driver, firmware or UI adaptation. Old Xiaomi
DisplaySettings/HapticSettings patches from LF52406 are useful
technical references but must not be automatically invoked by
the new product, especially not as side-effecting build scripts.

## Integration with PE-Reborn common tree

- Device product: `device/xiaomi/mondrian/pe_mondrian.mk`.
- Device and hardware definition: `device/xiaomi/mondrian/device.mk`.
- Shared board: `device/xiaomi/sm8450-common/BoardConfigCommon.mk`.
- Platform: official Android 17 and separately reviewed PE `vendor/aosp`.

The physical device is SM8475 although the shared source tree is
named `sm8450-common`, per Qualcomm BSP conventions.

All kernel/module/DTBO image generation, fstab, VINTF, encryption,
AVB, HAL, firmware, vendor blob and recovery policies remain deferred
until a coherent source BOM and hardware evidence have been established.
Nothing in this audit supplies an active FM radio package, kernel module
or HAL. Do not merge before source build and real hardware acceptance.

Source evidence:
- https://github.com/LF52406/mondrian_android_device_xiaomi_mondrian/blob/lineage-24.0/BoardConfig.mk
- https://github.com/LineageOS/android_kernel_xiaomi_sm8450-devicetrees/blob/lineage-24.0/qcom/mondrian-sm8475.dtsi
- https://github.com/goodix/goodix_ts_berlin/blob/master/goodix_brl_spi.c
