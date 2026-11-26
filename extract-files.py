#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: PixelExperience-Reborn
# SPDX-License-Identifier: Apache-2.0
#
# Build rules for the proprietary files of mondrian (camera, sensors,
# audio calibration, DSP modules). The files are reproduced from the
# official OTA by device/xiaomi/sm8450-common/tools/extract_proprietary.py.

from extract_utils.fixups_lib import (
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

namespace_imports = [
    'device/xiaomi/mondrian',
    'vendor/xiaomi/sm8450-common',
]

def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_{partition}' if partition == 'vendor' else None


# Vendor copies of libraries that Android 17 builds for system only: the
# blob keeps its file name (MODULE_SUFFIX=_vendor in the list) and its
# users depend on the suffixed module.
lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
    'libmemunreachable': lib_fixup_vendor_suffix,
}

module = ExtractUtilsModule(
    'mondrian',
    'xiaomi',
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
)

if __name__ == '__main__':
    utils = ExtractUtils.device_with_common(module, 'sm8450-common', module.vendor)
    utils.run()
