# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

"""Creates a copy of a binary giving it a different basename.

binary_alias(
    name = "my_binary_other_name",
    binary = ":some_cc_binary",
)
"""

def _binary_alias_impl(ctx):
    ctx.actions.expand_template(
      template = ctx.file.binary,
      output = ctx.outputs.executable,
      substitutions = {},
      is_executable = True,
    )

    return [DefaultInfo(
        executable = ctx.outputs.executable,
        runfiles = ctx.attr.binary[DefaultInfo].default_runfiles,
    )]

binary_alias = rule(
    _binary_alias_impl,
    attrs = {
        "binary": attr.label(
            mandatory = True,
            allow_single_file = True,
        ),
    },
    executable = True,
)
