# Полнота device-деревьев mondrian / sm8450-common (Android 17)

Цель — полноценные деревья `device/xiaomi/mondrian` и
`device/xiaomi/sm8450-common` для первой сборки PixelExperience-Reborn
Android 17. Источники правды:

1. **Стоковая прошивка OS3.0.8.0.VMNCNXM** (официальный OTA): разделы
   vendor, odm, vendor_boot, vendor_dlkm, dtbo — init-скрипты, VINTF,
   конфигурации, свойства, оверлеи vendor, модули ядра.
2. **Исходники Xiaomi** (MiCode: ядро, DT, модули) — уже в репозиториях ядра
   организации.
3. **Репозитории организации** (143): HAL Qualcomm CAF для SM8450
   (`hardware_qcom-caf_sm8450_*`), sepolicy (`device_qcom_sepolicy_vndr_sm8450`),
   `vendor_qcom_opensource_*`, `android_hardware_xiaomi`, proprietary-репозитории.

LineageOS (`android_device_xiaomi_sm8450-common`, `android_device_xiaomi_mondrian`,
ветка lineage-24.0) — **только ориентир**, какие области должно покрыть дерево.
Код и файлы оттуда не берутся.

## Что есть сейчас

| Дерево | Есть |
|---|---|
| sm8450-common | `BoardConfigCommon.mk` (архитектура, EROFS), `common.mk` (A/B, dynamic partitions, fstab), `rootdir/etc/fstab.qcom` (из стока), `proprietary-files.txt` (416 закрытых файлов с sha256 из OTA) |
| mondrian | `BoardConfig.mk`, `device.mk`, `aosp_mondrian.mk`, `proprietary-files.txt` (919 файлов: камера, DSP, сенсоры, аудио-калибровка) |
| mondrian-kernel | проверка выпуска; первого выпуска ядра ещё нет |

## Чего не хватает и откуда берём

| Область | Что нужно | Источник правды | Порядок |
|---|---|---|---|
| Ядро | Image, DTB Cape, `dtbo.img`, модули vendor_ramdisk/vendor_dlkm со списками загрузки как в стоке; cmdline/bootconfig стока | выпуск CI в `android_device_xiaomi_mondrian-kernel`; `vendor_boot` стока | 1 |
| Образы и разделы | boot/vendor_boot v4, recovery, dtbo, vbmeta (AVB, цепочки как в стоке), super: группы и размеры, `AB_OTA_PARTITIONS` с разделами прошивки | payload OTA (metadata super, список разделов) | 1 |
| Прошивка | abl, aop, aop_config, bluetooth, cpucp, devcfg, dsp, featenabler, hyp, imagefv, keymaster, modem, qupfw, shrm, tz, uefi, uefisecapp, xbl, xbl_config, xbl_ramdump, vm-bootsys — в OTA сборки (без mi_ext) | payload OTA | 1 |
| init / ueventd | `init.qcom.rc`, `init.target.rc`, `init.qcom.usb.rc`, `init.qti.kernel.rc`, `init.qti.ufs.rc`, `ueventd.qcom.rc`, скрипты post_boot/early_boot; без MIUI-служб | `vendor/etc/init/hw`, `vendor/etc/ueventd.rc`, `vendor/bin/*.sh` стока | 2 |
| VINTF | `manifest.xml` (только HAL, которые мы ставим), `compatibility_matrix.xml`, framework matrix | `vendor/etc/vintf` стока, сверка с поставляемыми HAL | 2 |
| SELinux | sepolicy vendor/private: Xiaomi-узлы, сервисы, свойства | `device_qcom_sepolicy_vndr_sm8450` + контексты стока (`vendor/etc/selinux`) | 3 |
| HAL из исходников | дисплей (composer, allocator, mapper), аудио (PAL/AGM/HAL), медиа, IPACM, power, thermal, USB, health, vibrator, lights, Wi-Fi HAL, bootctrl, gatekeeper/keymint — блобы | `hardware_qcom-caf_sm8450_*`, `vendor_qcom_opensource_*`, `hardware_qcom-caf_*` (порт на Android 17) | 3 |
| Xiaomi HAL | отпечаток под экраном (Goodix/FOD), ИК, тач (режимы), сенсоры (уведомления ALS/AOD) | `android_hardware_xiaomi`, стоковые блобы | 4 |
| Оверлеи | frameworks-res (вырез, скругления, яркость, **60/90/120 Гц**, power_profile, автояркость), SystemUI, Settings, SettingsProvider, Wi-Fi, Tethering, CarrierConfig, Telephony | `vendor/overlay/*.apk` стока, `product/overlay` стока, панель M11A из DT | 4 |
| Конфиги | аудио (policy, effects, mixer/resourcemanager — из стока), медиа (codecs, profiles), Wi-Fi (WCNSS_qcom_cfg.ini, supplicant overlay), GPS, сенсоры, perf, thermal, keylayout, idc, public.libraries | `vendor/etc` стока | 4 |
| Свойства | vendor/odm/system/product props (без MIUI) | `vendor/build.prop`, `odm/etc/build.prop` стока | 4 |
| Извлечение блобов | `tools/extract_proprietary.py` (уже есть), правила сборки vendor | proprietary-репозитории организации | 3 |

## Обновление частоты 60/90/120 Гц

MIUI показывает в настройках только 60 и 120 Гц. Панель M11A в стоке
описывает три режима: 60, 90 и 120 Гц. Последовательности включения и
переключения для каждого режима мы берём из стока
(`mondrian-m11a-os3-panel-commands.dtsi`). В Android 17 выбор частоты
задаётся оверлеем frameworks-res и Settings (пиковая и минимальная
частота, список режимов), поэтому в настройках будут 60, 90 и 120 Гц.

## Порядок работы

1. Ядро и образы: выпуск ядра в `mondrian-kernel`; BoardConfig с готовым
   ядром (как `device/google/*-kernel` у Pixel); разделы, AVB и прошивка.
2. init/ueventd и VINTF из стока.
3. sepolicy и HAL из исходников организации (порт на Android 17).
4. Оверлеи (включая 60/90/120 Гц), конфиги, свойства, Xiaomi HAL.

Каждый шаг проверяется сборкой на ServerHive. В основные ветки
(`seventeen`) всё переносится только после стабильной сборки.
