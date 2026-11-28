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
В git ничего из этого не попадает.

VINTF: при target-level 7 Android 17 берёт уровень ядра из строки GKI и не
даёт задать его в манифесте; `android12` даёт уровень 6, а требований для
ядер уровня 6 во фреймворке Android 17 уже нет. По существу стоковое ядро
отвечает требованиям уровня 7 для 5.10: LTS 5.10.107+ и все параметры
`kernel/configs` `t/android-5.10` AOSP 17 (базовые и условные, 0 расхождений).
Поэтому при упаковке OTA VINTF проверяет HAL, а ядро проверяет
`tests/test_kernel_vintf.py` (`PRODUCT_OTA_ENFORCE_VINTF_KERNEL_REQUIREMENTS := false`).

Ядро нашего CI (`device/xiaomi/mondrian-kernel`, раздел ниже) вернётся, когда
его выпуск загрузится на устройстве (`fastboot boot` с образами этого
выпуска) и будет сверен со стоковым по модулям и DT.

## Журнал загрузки в sda15 (mtdoops Xiaomi)

Xiaomi хранит журнал ядра последних сессий в разделе `sda15`: `block2mtd`
делает из него MTD, `mtdoops` при панике и при каждой перезагрузке пишет
запись `## Index: N` / `## REASON: ...` с секциями `LAST KMSG` (кольцевой
буфер ядра) и `LAST LOGCAT` (pmsg, область `mtdoops_pmsg@0xa7000000` в DT).
Параметры дописывает загрузчик в cmdline:
`block2mtd.block2mtd=/dev/block/sda15,2097152` и
`mtdoops.mtddev=0 record_size=2097152 dump_oops=0` (только паники и
перезагрузки, без oops).

Параметры из cmdline применяет к модулям только init первого этапа
(libmodprobe). `vendor_modprobe.sh` второго этапа грузит модули toybox
`modprobe`, а он `/proc/cmdline` не читает: `block2mtd` поднимается без
устройства, `mtdoops` не к чему подключиться. В стоке модули стоят только в
`modules.load.recovery`, поэтому записи есть лишь для сессий recovery. В
дампе тестера от 28.11.2026 все 7 записей (Index 3664–3670) — сессии
OrangeFox и нашего recovery, обычных загрузок там нет и быть не могло.

На userdebug/eng `BoardConfig.mk` (`MONDRIAN_MTDOOPS_MODULES`) добавляет
`pm8941-pwrkey mtd ofpart chipreg block2mtd mtd_blkdevs mtdblock mtdoops` в
конец обычного `modules.load` первого этапа (после UFS, порядок — как в
сессиях recovery). Тогда паника или перезагрузка обычной загрузки тоже
оставляет запись. Аппаратный сброс watchdog/TZ записи не оставит: ядро в этот
момент уже не работает. Её отсутствие после сбоя само по себе указывает на
такой сброс.

Снять дамп из OrangeFox (Терминал или `adb shell` в обычном режиме ADB, не
sideload): `dd if=/dev/block/sda15 of=/usb_otg/sda15.img`, затем `sync` и
`umount /usb_otg`, либо `adb pull /dev/block/sda15 sda15.img` с ПК.

Причину предыдущего сброса загрузчик передаёт ядру в cmdline как
`bootinfo.pureason`/`bootinfo.pdreason` (печатаются в начале каждой записи и в
`dmesg`). Расшифровка по таблицам модуля `bootinfo.ko`:

| поле | биты | значения |
|---|---|---|
| `pureason`, биты 0–9 | событие включения | 0 hw_reset, 1 smpl, 2 rtc, 3 dc_chg, 4 usb_chg, 5 pon1, 6 cable, 7 keypad, 9 long_power_key |
| `pureason`, биты 16–23 | причина сброса | 16 wdog, 17 kpanic, 18 reboot, 19 other, 20 dm_verity_enforcing, 21 dm_verity_logging, 22 dm_verity_keysclear, 23 fastboot_reboot |
| `pdreason`, биты 0–7 | причина выключения (PMIC) | 0 soft, 1 ps_hold, 2 pmic_wd, 3 gp2, 4 gp1, 5 kpd_and_resin, 6 resin, 7 long_power_key |

Что видно в дампе и логах тестера 28.11.2026:

- `0x40001`/`0x2` — обычная перезагрузка (`reboot,userrequested,recovery` из
  нашего recovery в recovery).
- `0x80001`/`0x80` (лог `dmesg1`, сборка до 0240) — выключение долгим
  нажатием питания: телефон висел на логотипе, тестер сбросил его кнопкой.
- `0x80001`/`0x2` перед записью 3666 (сборки 0240/0408) — обычная загрузка
  сбросилась сама через PS_HOLD с причиной `other`. Это не `reboot` (init
  с известной целью), не `fastboot_reboot` и не dm-verity. Совпадает с
  перезагрузкой с нестандартной целью от init (`reboot_on_failure`, например
  `reboot,vold-failed` у vold) или со сбросом без cookie (паника, TZ).
  Следующий дамп с журналом первого этапа это различит.
- `/metadata/vold/metadata_encryption/key` создан, `/data` с metadata
  encryption, но FBE не настроено и раздел почти пустой (лог OrangeFox
  `recovery1`): ранняя сборка доходила до vold (`late-fs`, `mount_all
  --late`) и останавливалась до или во время `init_user0`.
- Раздел `modem` (`/vendor/firmware_mnt`: прошивки ADSP, CDSP, модема, IPA,
  доверенные приложения TEE) не монтировался ни в recovery, ни в обычной
  загрузке: fstab монтирует его с `context=u:object_r:firmware_file:s0`, а
  нашей vendor-политике этого типа не было (как и `bt_firmware_file`,
  `vendor_qmcs_file`). Ядро отвечает `security_context_str_to_sid(...) failed
  ... errno=-22`, и mount падает с EINVAL даже в permissive. Без ADSP нет
  pmic_glink (батарея, зарядка), UCSI (роль USB-C, поэтому в нашем recovery не
  было adb) и звука. Исправлено в sm8450-common: генератор политики объявляет
  типы всех `context=` из fstab по стоку (`tests/test_sepolicy.py`).

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
