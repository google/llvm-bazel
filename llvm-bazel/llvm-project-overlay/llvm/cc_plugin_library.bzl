# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

"""A macro to produce a loadable plugin binary for the target OS.

This macro produces a `cc_binary` rule with the name `name + ".so"`. It
forces the rule to statically link in its dependencies but to be linked as a
shared "plugin" library. It then creates binary aliases to `.dylib` and
`.dll` suffixed names for use on various platforms.
"""

load("@rules_cc//cc:defs.bzl", "cc_binary")
load(":binary_alias.bzl", "binary_alias")

def cc_plugin_library(name, **kwargs):
    # Neither the name of the plugin binary nor tags on whether it is built are
    # configurable. Instead, we always build the plugin using a `.so` suffix.
    # Bazel appears to always invoke platform-specific shared library linking
    # logic here regardless of which platform's suffix is used, so any will do.
    # Then we create symlinks to other platform-specific names so they can be
    # used in dependencies (which *can* be configured).
    #
    # All-in-all, this is a pretty poor workaround. I think this is part of the
    # Bazel issue: https://github.com/bazelbuild/bazel/issues/7538
    #
    # Tensorflow has another approach that builds three `cc_binary` rules with
    # the correct name and selects the viable one into a `filegroup`. We could
    # replicate that here, but for now this at least seems enough to build on
    # MacOS and simpler.
    cc_binary(
        name = name + "_impl",
        linkshared = True,
        linkstatic = True,
        **kwargs
    )
    binary_alias(
        name = name + ".so",
        binary = ":" + name + "_impl",
    )
    binary_alias(
        name = name + ".dll",
        binary = ":" + name + "_impl",
    )
    binary_alias(
        name = name + ".dylib",
        binary = ":" + name + "_impl",
    )
    native.filegroup(
        name = name,
        srcs = select({
            "@bazel_tools//src/conditions:windows": [":" + name + ".dll"],
            "@bazel_tools//src/conditions:darwin": [":" + name + ".dylib"],
            "//conditions:default": [":" + name + ".so"],
        }),
    )
