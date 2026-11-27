# Recovery, OrangeFox и firmware mondrian

## Своё recovery

Сборка делает своё recovery из `bootable/recovery` базы PE (как и boot,
vendor_boot, dtbo и vbmeta). Образ recovery из HyperOS не используется. От
стока взяты только `init.recovery.qcom.rc` и модули ядра для recovery
(vendor_boot `modules.load.recovery`). Обновление ROM (A/B) пишет и раздел
recovery, поэтому после него установленный OrangeFox заменяется нашим
recovery — его ставят заново (или опцией OrangeFox «переустановить после
прошивки»).

## Совместимость с официальным OrangeFox

Проверено по официальному дереву `gitlab.com/OrangeFox/device/mondrian`
(ветка `fox_16.0`, общая часть `device/sm84xx-common`):

| Что ждёт OrangeFox | У нас |
|---|---|
| Ядра в образе recovery нет (`BOARD_EXCLUDE_KERNEL_FROM_RECOVERY_IMAGE`): грузится ядро из boot и vendor_boot | наше ядро 5.10.81 и наш vendor_boot; тот же заголовок v4 |
| Модули по именам из vendor_dlkm установленной системы (`TW_LOAD_VENDOR_MODULES`) | все имена есть (тач `goodix_core`/`goodix_fod`, `qti_battery_charger`, `qcom-hv-haptics`, `aw882xx_dlkm`, ADSP/Q6, cnss2, `qca_cld3_qca6490`) |
| `xiaomi_touch.ko`, `focaltech_*` | не собираются: у mondrian тач Goodix, наш драйвер работает без `xiaomi_touch` |
| `/proc/goodix_ts` (скрипт перезагрузки тача) | создаёт наш драйвер Berlin |
| `/sys/kernel/boot_adsp/boot`, `power_supply/battery` | есть |
| Расшифровка: свои keymint/qseecomd в образе OrangeFox + TrustZone телефона | TrustZone и KeyMint TA — из firmware OS3.0.8.0, которое прошивает сборка; fstab стоковый (те же опции FBE и metadata-шифрования) |

Проверить на устройстве: тач и расшифровка /data без пароля и с паролем
экрана блокировки (формат синтетического пароля Android 17).

## Firmware

`firmware-files.txt`: 21 раздел firmware из OTA OS3.0.8.0.VMNCNXM (Китай) —
`abl xbl xbl_config xbl_ramdump tz hyp keymaster devcfg uefi uefisecapp
imagefv featenabler qupfw shrm cpucp aop aop_config modem dsp bluetooth
vm-bootsys`, с SHA-256 из манифеста payload. Это обычный набор firmware
кастомных прошивок; системные разделы, boot/vendor_boot/dtbo/recovery/vbmeta
и `mi_ext` из HyperOS не берутся. Образы извлекаются из официальной OTA при
сборке (`tools/extract_proprietary.py` в sm8450-common) и идут в пакет A/B
вместе с ROM.

Защита от отката (anti-rollback) загрузчиков Xiaomi: после прошивки этого
firmware вернуться на более старую стоковую прошивку может быть нельзя.
OS3.0.8.0 — самая свежая китайская, откатываться ниже неё не нужно.
