# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

# This file must exist to reference .bzl files in this package
# Furthermore, we perform diff testing here to avoid any in-tree BUILD files
# depending on bazel_sklyib

load("@bazel_skylib//rules:diff_test.bzl", "diff_test")

diff_test(
    name = "diff_config.h.cmake",
    file1 = "@llvm-project//llvm:include/llvm/Config/config.h.cmake",
    file2 = "config.h.cmake",
)

diff_test(
    name = "diff_llvm-config.h.cmake",
    file1 = "@llvm-project//llvm:include/llvm/Config/llvm-config.h.cmake",
    file2 = "llvm-config.h.cmake",
)

diff_test(
    name = "diff_abi-breaking.h.cmake",
    file1 = "@llvm-project//llvm:include/llvm/Config/abi-breaking.h.cmake",
    file2 = "abi-breaking.h.cmake",
)
