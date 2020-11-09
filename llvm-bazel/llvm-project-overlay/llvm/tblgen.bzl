# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

"""This file contains BUILD extensions for generating source code from LLVM's
table definition files using the TableGen tool.

See http://llvm.org/cmds/tblgen.html for more information on the TableGen
tool.
TODO(chandlerc): Currently this expresses include-based dependencies as
"sources", and has no transitive understanding due to these files not being
correctly understood by the build system.
"""

def gentbl(name, tblgen, td_file, td_srcs, tbl_outs, library = True, **kwargs):
    """gentbl() generates tabular code from a table definition file.

    Args:
      name: The name of the build rule for use in dependencies.
      tblgen: The binary used to produce the output.
      td_file: The primary table definitions file.
      td_srcs: A list of table definition files included transitively.
      tbl_outs: A list of tuples (opts, out), where each opts is a string of
        options passed to tblgen, and the out is the corresponding output file
        produced.
      library: Whether to bundle the generated files into a library.
      **kwargs: Keyword arguments to pass to subsidiary cc_library() rule.
    """
    if td_file not in td_srcs:
        td_srcs += [td_file]
    for (opts, out) in tbl_outs:
        rule_suffix = "_".join(opts.replace("-", "_").replace("=", "_").split(" "))
        native.genrule(
            name = "%s_%s_genrule" % (name, rule_suffix),
            srcs = td_srcs,
            outs = [out],
            tools = [tblgen],
            message = "Generating code from table: %s" % td_file,
            # MSVC isn't happy with long string literals, while other compilers
            # which support them get significant compile time improvements with
            # them enabled.
            # See https://github.com/google/llvm-bazel/pull/71 for context.
            cmd = select({
                "@bazel_tools//src/conditions:windows": (("$(location %s) -I external/llvm-project/llvm/include " +
                                                          "-I external/llvm-project/clang/include " +
                                                          "-I $$(dirname $(location %s)) " +
                                                          "%s $(location %s) --long-string-literals=0 -o $@") % (
                    tblgen,
                    td_file,
                    opts,
                    td_file,
                )),
                "//conditions:default": (("$(location %s) -I external/llvm-project/llvm/include " +
                                          "-I external/llvm-project/clang/include " +
                                          "-I $$(dirname $(location %s)) " +
                                          "%s $(location %s) -o $@") % (
                    tblgen,
                    td_file,
                    opts,
                    td_file,
                )),
            }),
        )

    # For now, all generated files can be assumed to comprise public interfaces.
    # If this is not true, you should specify library = False
    # and list the generated '.inc' files in "srcs".
    if library:
        native.cc_library(
            name = name,
            # FIXME: This should be `textual_hdrs` instead of `hdrs`, but
            # unfortunately that doesn't work with `strip_include_prefix`:
            # https://github.com/bazelbuild/bazel/issues/12424
            #
            # Once that issue is fixed and released, we can switch this to
            # `textual_hdrs` and remove the feature disabling the various Bazel
            # features (both current and under-development) that motivated the
            # distinction between these two.
            hdrs = [f for (_, f) in tbl_outs],
            features = ["-parse_headers", "-header_modules"],
            **kwargs
        )
