#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: PixelExperience-Reborn
# SPDX-License-Identifier: Apache-2.0
#
# Build rules for the proprietary files of mondrian (camera, sensors,
# audio calibration, DSP modules). The files are reproduced from the
# official OTA by device/xiaomi/sm8450-common/tools/extract_proprietary.py.

from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

namespace_imports = [
    'device/xiaomi/mondrian',
    'vendor/xiaomi/sm8450-common',
]

module = ExtractUtilsModule(
    'mondrian',
    'xiaomi',
    namespace_imports=namespace_imports,
)

if __name__ == '__main__':
    utils = ExtractUtils.device_with_common(module, 'sm8450-common', module.vendor)
    utils.run()
