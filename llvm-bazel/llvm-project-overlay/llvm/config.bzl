# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

"""Defines variables that use selects to configure LLVM based on platform."""

def native_arch_defines(arch):
    return [
        "LLVM_NATIVE_ARCH=\\\"{}\\\"".format(arch),
        "LLVM_NATIVE_ASMPARSER=LLVMInitialize{}AsmParser".format(arch),
        "LLVM_NATIVE_ASMPRINTER=LLVMInitialize{}AsmPrinter".format(arch),
        "LLVM_NATIVE_DISASSEMBLER=LLVMInitialize{}Disassembler".format(arch),
        "LLVM_NATIVE_TARGET=LLVMInitialize{}Target".format(arch),
        "LLVM_NATIVE_TARGETINFO=LLVMInitialize{}TargetInfo".format(arch),
        "LLVM_NATIVE_TARGETMC=LLVMInitialize{}TargetMC".format(arch),
    ]

posix_defines = [
    "LLVM_ON_UNIX=1",
    "HAVE_BACKTRACE=1",
    "BACKTRACE_HEADER=<execinfo.h>",
    "LTDL_SHLIB_EXT=\\\".so\\\"",
    "LLVM_ENABLE_THREADS=1",
    "HAVE_SYSEXITS_H=1",
    "HAVE_UNISTD_H=1",
    "HAVE_STRERROR_R=1",
    "HAVE_LIBPTHREAD=1",
    "HAVE_PTHREAD_GETNAME_NP=1",
    "HAVE_PTHREAD_SETNAME_NP=1",
    "HAVE_PTHREAD_GETSPECIFIC=1",
]

win32_defines = [
    # MSVC specific
    "stricmp=_stricmp",
    "strdup=_strdup",

    # LLVM features
    "LTDL_SHLIB_EXT=\\\".dll\\\"",
]

llvm_config_defines = select({
    "@bazel_tools//src/conditions:windows": (
        native_arch_defines("X86") +
        [
            "LLVM_HOST_TRIPLE=\\\"x86_64-pc-win32\\\"",
            "LLVM_DEFAULT_TARGET_TRIPLE=\\\"x86_64-pc-win32\\\"",
        ] + win32_defines
    ),
    "//conditions:default": (
        native_arch_defines("X86") +
        [
            "LLVM_HOST_TRIPLE=\\\"x86_64-unknown-linux-gnu\\\"",
            "LLVM_DEFAULT_TARGET_TRIPLE=\\\"x86_64-unknown-linux-gnu\\\"",
        ] + posix_defines
    ),
})
