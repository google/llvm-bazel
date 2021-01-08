# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

"""Configures an LLVM overlay project."""

load(":overlay_directories.bzl", "overlay_directories")

# Directory of overlay files relative to WORKSPACE
OVERLAY_DIR = "llvm-project-overlay"

def llvm_configure(name, overlay_path = OVERLAY_DIR, **kwargs):
    overlay_directories(name = name, overlay_path = overlay_path, **kwargs)
