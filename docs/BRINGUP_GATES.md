# PixelExperience-Reborn — mondrian AOSP 17 bring-up gates

Scope: **POCO F5 Pro / Redmi K60 (mondrian, SM8475)** only.
Branch: `seventeen`. Product: `pe_mondrian`. Source base: independently
maintained PE-Reborn on **official AOSP 17**.

This repository is an independent product scaffold. It is **not bootable**,
and neither a Soong build nor device-level validation has been completed.

## Gate 0 — product discovery (open)
- [x] Register `pe_mondrian` in `AndroidProducts.mk`.
- [x] Inherit only PE-Reborn `vendor/aosp` and our own device/common trees.
- [ ] Synchronize the vetted AOSP 17 manifest and PE vendor A17 changes.
- [ ] Run platform-native lunch/product discovery with an actual AOSP 17 release configuration.
- [ ] Run full `soong_ui` parse and validate source graph.

## Gate 1 — boot-chain and kernel (blocked)
- [ ] Qualify the Xiaomi/Qualcomm kernel BSP, patches, defconfig and compiler.
- [ ] Pin matching kernel, external modules and device-tree revisions.
- [ ] Verify boot header, exact partitions, `fstab`, dynamic super and A/B OTA.
- [ ] Design production AVB signing/rollback indexes. Never ship public test keys
      or blindly copy `vbmeta --flags 3`.
- [ ] Validate kernel build, DTBO and module load order.

## Gate 2 — vendor and Android interfaces (blocked)
- [ ] Obtain lawful, traceable proprietary blobs for **both** mondrian and common.
- [ ] Verify partition ownership, ELF dependencies, init services and firmware.
- [ ] Specify AOSP 17 VINTF/FCM, compatible HAL interfaces and SELinux contexts.
- [ ] Keep FM radio, extra ROM framework services and optional GMS out of the
      initial dependency graph.

## Gate 3 — input, fingerprint and display (blocked)
- [ ] Identify actual touch controller, driver and firmware; reproduce ghost taps
      under controlled conditions. Do not attribute them to a ROM without evidence.
- [ ] Confirm panel, DSI/DRM/HWC/display HAL and compatible kernel modules.
- [ ] Qualify optical UDFPS HAL, vendor blobs, sensor locations, illumination,
      wake-up/auth flows and keyguard integration.
- [ ] Test touch, swipe, rotation and multi-touch with kernel/input traces,
      plus UDFPS with real hardware. Do not substitute a different Xiaomi HAL.

## Gate 4 — first functional device build (blocked)
- [ ] AOSP 17 builds boot, vendor_boot, recovery, dtbo, vendor_dlkm and target-files.
- [ ] Validate boot and device runtime: `logcat`, `dmesg`, VINTF/SELinux,
      FBE/KeyMint, emergency calls/radio, Wi-Fi, Bluetooth, display and sensors.
- [ ] Validate camera/recording, NFC, UDFPS, charging/thermal, OTA and long-run stability.
- [ ] CTS/VTS and signing/release checks before describing the build as official.

References are technical research, **not ROM source dependencies**:
original PixelExperience official device architecture, official Xiaomi
kernel disclosure, Android AOSP documentation, and upstream Linux/Qualcomm sources.
