# mondrian: загрузочная цепочка и ядро

## Сейчас (27.11.2026): стоковое ядро OS3.0.8.0

Первая установка на устройство показала: с ядром нашего CI (5.10.81 из
исходников Xiaomi 2022 года, ни разу не загружавшимся) слот не стартует —
через секунду после логотипа перезагрузка в fastboot, recovery этого слота
висит. Тот же наш recovery со стоковым ядром работал. Стоковая прошивка
OS3.0.8.0 работает на **Google GKI 5.10.236-android12-9** (`ab14313284`),
и стоковые vendor и firmware рассчитаны на него.

Поэтому ядро берётся из официального OTA, как прошивка:
`kernel-files.txt` закрепляет образы `boot`, `vendor_boot`, `dtbo`,
`vendor_dlkm` по SHA-256 (те же хэши — в `ota-source.json` sm8450-common,
тип `kernel`), `tools/extract_proprietary.py` с `tools/stock_kernel.py`
раскладывает их в `vendor/xiaomi/mondrian/kernel` (`KERNEL_PATH`): `Image`,
`dtbs/stock.dtb`, `dtbo.img`, `vendor_ramdisk/` (354 модуля, стоковые
`modules.load`/`.recovery`/`.blocklist`), `vendor_dlkm/` (309 модулей).
В git ничего из этого не попадает. Ядро 5.10.236 выше LTS 5.10.107, которую
матрица A17 требует для FCM 7, поэтому проверка VINTF ядра при упаковке OTA
включена.

Ядро нашего CI (`device/xiaomi/mondrian-kernel`, раздел ниже) вернётся, когда
его выпуск загрузится на устройстве (`fastboot boot` с образами этого
выпуска) и будет сверен со стоковым по модулям и DT.

## Ядро нашего CI (решение от 25.11.2026, пока не используется)

Ядро, модули и DT подаются в сборку Android **готовыми** из нашего CI (как
`device/google/*-kernel` в AOSP), а не собираются внутри сборки Android.
Источник правды о раскладке — стоковая прошивка OS3.0.8.0.VMNCNXM;
LineageOS — только ориентир.

## Как устроен сток OS3.0.8.0

| Часть | Содержимое стока |
|---|---|
| `boot` | ядро GKI + общий ramdisk (header v4) |
| `vendor_boot` | header v4, page 4096; cmdline `video=vfb:640x400,bpp=32,memsize=3072000 disable_dma32=on bootconfig`; bootconfig `androidboot.hardware=qcom androidboot.memcg=1 androidboot.usbcontroller=a600000.dwc3`; ramdisk: 354 модуля, `modules.load` (111, первая стадия), `modules.load.recovery` (356), `first_stage_ramdisk/fstab.qcom`, `/avb` |
| DTB в `vendor_boot` | 14 базовых DTB семейства; для mondrian нужны `cape` (msm-id 0x212), `capep` (0x213), `cape-v2` (0x21c) |
| `dtbo` | 44 оверлея устройств Xiaomi; mondrian — один: «Mondrian based on Qualcomm Technologies, Inc SM8475», msm-id 0x213/0x21c/0x212, board-id `<0x10008 0x0>`, `qcom,cape-mtp` |
| `vendor_dlkm` | 309 модулей, `modules.load` (317) |
| прошивки в OTA | abl, aop, aop_config, bluetooth, cpucp, devcfg, dsp, featenabler, hyp, imagefv, keymaster, modem, qupfw, shrm, tz, uefi, uefisecapp, xbl, xbl_config, xbl_ramdump, vm-bootsys |
| MIUI | `mi_ext` (раздел в super + overlay-слои) — **не используется** в PE |

## Наше ядро

- Ядро `2efda4c`, модули `f87310d`, DT `c6f47f9` — проверены вместе CI №139.
- В конфигурации 327 драйверов собираются модулями (`=m`), включая базовые
  модули платформы (`arm_smmu`, `clk-rpmh`, `bam_dma`, `btpower`,
  `pinctrl-waipio`...), плюс внешние модули Qualcomm/Xiaomi (камера, дисплей,
  аудио, видео, EVA, MMRM, WLAN, IPA, rmnet).
- Проверочная сборка №139 выкладывала только 139 модулей для диагностики;
  выпускающая сборка должна ставить **все**.
- EROFS (с LZ4, xattr, SELinux) и F2FS со сжатием встроены (`=y`).
- Исходный оверлей платы Xiaomi `mondrian-sm8475-pm8008-overlay.dts` уже несёт
  стоковые model, msm-id 530/531/540 и board-id `<0x10008 0>`.

## Что должна выдавать выпускающая сборка ядра (CI)

1. `Image` (тот же компилятор Google LLVM 23 `r614150`, те же шаги, что №139).
2. Все модули: `make modules_install` + внешние модули, `strip --strip-debug`.
3. Списки загрузки: `vendor_boot` первая стадия и recovery, `vendor_dlkm` —
   по порядку стоковых `modules.load`, только для модулей нашего ядра;
   зависимости проверяются `depmod`.
4. DTB для `vendor_boot`: `cape.dtb`, `capep.dtb`, `cape-v2.dtb`.
5. `dtbo.img`: **один** оверлей mondrian (плата + дисплей M11A + камера +
   аудио + видео), слитый на уровне исходников DT, с msm-id/board-id стока.
6. `provenance.json`: коммиты ядра/модулей/DT, компилятор, номер запуска CI,
   sha256 каждого файла.

## Подключение в device-дереве

- Сейчас `KERNEL_PATH := vendor/xiaomi/mondrian/kernel` (стоковое ядро, см.
  выше); раскладка та же, что у выпуска CI.
- Отдельный репозиторий готового ядра CI `device/xiaomi/mondrian-kernel`.
- Ядро: `PRODUCT_COPY_FILES += <prebuilt>/Image:kernel`,
  `TARGET_NO_KERNEL_OVERRIDE := true` для `kernel.mk` из vendor/aosp.
- `BOARD_VENDOR_RAMDISK_KERNEL_MODULES(_LOAD)`, `BOARD_VENDOR_KERNEL_MODULES(_LOAD)`,
  `BOARD_RECOVERY_KERNEL_MODULES_LOAD`, `BOARD_PREBUILT_DTBOIMAGE`,
  `BOARD_PREBUILT_DTBIMAGE_DIR`, cmdline и bootconfig — по стоку.
- Гейты `PE_MONDRIAN_*` в `BoardConfigBootImages.mk` заменяются этой
  конфигурацией и проверками по стоку.

## Открытые пункты до первой прошивки

- Каталоги `/vendor/firmware_mnt`, `/vendor/dsp`, `/vendor/bt_firmware` в образе vendor.
- SELinux-типы для `context=` в fstab.
- Список прошивок (firmware) в `AB_OTA_PARTITIONS` из той же OTA.
- `super`: группа `qti_dynamic_partitions` без `mi_ext`.
