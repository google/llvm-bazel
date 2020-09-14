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
    includes = []
    for (opts, out) in tbl_outs:
        outdir = out[:out.rindex("/")]
        if outdir not in includes:
            includes.append(outdir)
        rule_suffix = "_".join(opts.replace("-", "_").replace("=", "_").split(" "))
        native.genrule(
            name = "%s_%s_genrule" % (name, rule_suffix),
            srcs = td_srcs,
            outs = [out],
            tools = [tblgen],
            message = "Generating code from table: %s" % td_file,
            cmd = (("$(location %s) " + "-I external/llvm-project/llvm/include " +
                    "-I external/llvm-project/clang/include " +
                    "-I $$(dirname $(location %s)) " + ("%s $(location %s) --long-string-literals=0 " +
                                                        "-o $@")) % (
                tblgen,
                td_file,
                opts,
                td_file,
            )),
        )

    # For now, all generated files can be assumed to comprise public interfaces.
    # If this is not true, you should specify library = False
    # and list the generated '.inc' files in "srcs".
    if library:
        native.cc_library(
            name = name,
            textual_hdrs = [f for (_, f) in tbl_outs],
            includes = includes,
            **kwargs
        )
