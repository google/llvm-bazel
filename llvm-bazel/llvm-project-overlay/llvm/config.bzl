# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

"""Defines variables that use selects to configure LLVM based on platform."""

posix_defines = [
    "LLVM_ON_UNIX=1",
    "HAVE_BACKTRACE=1",
    "BACKTRACE_HEADER=<execinfo.h>",
    "LTDL_SHLIB_EXT=\\\".so\\\"",
    "LLVM_ENABLE_THREADS=1",
]

win32_defines = [
    # MSVC specific
    "stricmp=_stricmp",
    "strdup=_strdup",

    # LLVM features
    "LTDL_SHLIB_EXT=\\\".dll\\\"",

    # ThreadPoolExecutor global destructor and thread handshaking do not work
    # on this platform when used as a DLL.
    # See: https://bugs.llvm.org/show_bug.cgi?id=44211
    "LLVM_ENABLE_THREADS=0",
]

llvm_config_defines = select({
    "@bazel_tools//src/conditions:windows": (
        [
            "LLVM_HOST_TRIPLE=\\\"x86_64-pc-win32\\\"",
            "LLVM_DEFAULT_TARGET_TRIPLE=\\\"x86_64-pc-win32\\\"",
            "LLVM_NATIVE_ARCH=\\\"X86\\\"",
        ] + win32_defines
    ),
    "//conditions:default": (
        [
            "LLVM_HOST_TRIPLE=\\\"x86_64-unknown-linux_gnu\\\"",
            "LLVM_DEFAULT_TARGET_TRIPLE=\\\"x86_64-unknown-linux_gnu\\\"",
            "LLVM_NATIVE_ARCH=\\\"X86\\\"",
        ] + posix_defines
    ),
})
