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
| Ядра в образе recovery нет (`BOARD_EXCLUDE_KERNEL_FROM_RECOVERY_IMAGE`): грузится ядро из boot и vendor_boot **текущего слота** | стоковое ядро GKI 5.10.236 и модули OS3.0.8.0 (`kernel-files.txt`) в нашем boot и vendor_boot; тот же заголовок v4. Если в текущем слоте ядро не стартует, OrangeFox тоже не запустится — сначала `fastboot set_active` на рабочий слот |
| Модули по именам из vendor_dlkm установленной системы (`TW_LOAD_VENDOR_MODULES`) | vendor_dlkm — стоковые модули OS3.0.8.0, имена те же, что ждёт OrangeFox |
| `xiaomi_touch.ko`, `focaltech_*` | не собираются: у mondrian тач Goodix, наш драйвер работает без `xiaomi_touch` |
| `/proc/goodix_ts` (скрипт перезагрузки тача) | создаёт наш драйвер Berlin |
| `/sys/kernel/boot_adsp/boot`, `power_supply/battery` | есть |
| Расшифровка: свои keymint/qseecomd в образе OrangeFox + TrustZone телефона | TrustZone и KeyMint TA — из firmware OS3.0.8.0, которое прошивает сборка; fstab стоковый (те же опции FBE и metadata-шифрования) |

Проверить на устройстве: тач и расшифровка /data без пароля и с паролем
экрана блокировки (формат синтетического пароля Android 17).

## Установка из OrangeFox, шифрование и внутренняя память

Порядок с HyperOS (или с другой прошивки), загрузчик разблокирован, стоит
официальный OrangeFox:

1. **Format Data** (ввести `yes`) — первым делом. Обязательно при переходе с
   HyperOS и с любой прошивки с другой версией Android или другим
   шифрованием: ключи /data и данные системных приложений старой системы
   нашей не подходят. Форматирование стирает внутреннюю память, поэтому zip
   кладут на USB-OTG или ставят через `adb sideload`.
2. «Установить» zip: пакет A/B пишется в **неактивный** слот (слот выбирает
   установщик сам) вместе с firmware и нашим recovery; после записи этот
   слот становится активным.
3. Сразу перезагрузка в систему. Первая загрузка сама шифрует /data (FBE
   обязательно с Android 10, отключить нельзя и не нужно).

Data **не форматировать после установки** до первой загрузки: новая система
лежит в снапшоте Virtual A/B (`snapshot-update-status: snapshotted`), его
данные (COW) могут быть в /data, и форматирование их уничтожит; наш recovery
в этом состоянии форматировать и не даёт. Перезагружаться в recovery между
установкой и первой загрузкой не нужно.

Почему /data и внутренняя память доступны и в OrangeFox, и в системе:

| Что | Проверено |
|---|---|
| Шифрование | fstab как в стоке: FBE `aes-256-xts:aes-256-cts:v2+inlinecrypt_optimized+wrappedkey_v0`, metadata `aes-256-xts:wrappedkey_v0` (`tools/validate_fstab.py` в sm8450-common); ключи в TEE — та же TrustZone с KeyMint TA (разделы `tz`, `keymaster`) из firmware OS3.0.8.0; в OrangeFox — стоковые keymint/gatekeeper/qseecomd |
| Формат Android 17 против OrangeFox (Android 16) | синтетический пароль v3 без изменений; scrypt пароля в A17 2^9 вместо 2^11, но параметры хранятся в файле `.pwd`, и OrangeFox берёт их оттуда (`system/vold` fox_16.0, `Decrypt.cpp`); база keystore2 версии 2 в обеих; каталог ключей vold версии 1; `wrappedkey_v0` в A17 тот же |
| Ключи не портятся | OrangeFox представляется версией 99.87.36 с патчем 2099-12-31, а обновлённые KeyMint ключи пишет только в `/tmp` и в /data их не сохраняет |
| Файловая система | casefold и project quota включены, sdcardfs выключен — как в стоковом vendor и в OrangeFox (`emulated_storage.mk`), поэтому /data, отформатированная любым из них, подходит системе; механизм снятия casefold Android 17 (`ro.casefolding.original_folder`) не используется (`tests/test_storage.py` в sm8450-common) |
| Монтирование | стоковое ядро 5.10.236 и его модули ICE/HWKM (`ufshcd-crypto-qti`, `crypto-qti-*`, `hwkm`) в первой стадии и в списке recovery, как в стоке |
| Пакет | полный OTA без `REPLACE_ZSTD` (в A17 по умолчанию выключено), операции REPLACE/REPLACE_XZ понимает update_engine OrangeFox |

Когда внутренняя память бывает недоступна, и как мы этого избегаем:

- Не сделан Format Data при смене прошивки: ключи не подходят, в recovery
  имена файлов нечитаемы, в системе — бутлуп или «память недоступна».
  Поэтому шаг 3 обязателен.
- Понижение уровня патча безопасности в следующей сборке: KeyMint отказывает
  ключам, созданным при более новом патче. Уровни платформы/boot
  (2026-09-01) и vendor (2026-02-01) в следующих сборках только растут.
- Восстановление бэкапа /data другой прошивки или копирование файлов в
  /data/media в recovery с чужим владельцем или меткой SELinux: так делать не
  надо, при проблеме помогает «Исправить контексты» в OrangeFox.

Проверить на устройстве: расшифровку в OrangeFox без блокировки экрана, с
PIN и с паролем; MTP в recovery; внутреннюю память в системе после первой и
второй загрузки и после обновления OTA.

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

## Загрузчик не блокируется

- Флаг разблокировки хранится в `devinfo`; ни firmware, ни пакет A/B, ни
  recovery его не пишут (как и `frp`, `persist`, NV модема и т.п.; тест
  `tests/test_firmware.py`). В деревьях и скриптах сборки нет команд
  блокировки (тот же тест).
- Переключатель «Заводская разблокировка» (`ro.oem_unlock_supported=1`, как в
  стоке) загрузчик не блокирует: он только разрешает или запрещает будущую
  разблокировку (бит в разделе `frp`). Если ABL передаёт
  `ro.boot.flash.locked=0`, Android делает переключатель неактивным
  (`OemLockService`). fastbootd в recovery блокировать загрузчик не умеет —
  это делает только сам загрузчик.
- **Никогда не выполнять `fastboot flashing lock` / `fastboot oem lock` с
  кастомной прошивкой**: образы подписаны не ключом Xiaomi, после блокировки
  телефон откажется загружаться. Блокировать можно только после полной
  прошивки стока через Mi Flash.
