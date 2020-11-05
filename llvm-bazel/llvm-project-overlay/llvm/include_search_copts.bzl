# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

"""This file contains Starlark macros for generating `copts` to tweak include
search paths."""

def include_search_genfiles_dir(dir):
    # Allow inclusion of generated files within this directory. We use a select
    # here to ensure we can adjust the flag syntax if needed.
    return select({
        "//conditions:default": ["-I$(GENDIR)/external/llvm-project/" + dir],
    })

def include_search_source_dir(dir):
    # Allow inclusion of source files within this directory. We use a select
    # here to ensure we can adjust the flag syntax if needed.
    return select({
        "//conditions:default": ["-Iexternal/llvm-project/" + dir],
    })
