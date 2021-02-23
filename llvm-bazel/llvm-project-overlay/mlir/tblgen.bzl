# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

"""BUILD extensions for MLIR table generation."""

# A provider with one field, transitive_sources.
TdFiles = provider(fields = ["transitive_sources", "transitive_includes"])

def _get_dep_transitive_srcs(dep):
    if TdFiles in dep:
        return dep[TdFiles].transitive_sources
    return dep[DefaultInfo].files

def _get_dep_transitive_includes(dep):
    if TdFiles in dep:
        return dep[TdFiles].transitive_includes
    return depset()

def _get_transitive_srcs(srcs, deps):
    """Obtain the source files for a target and its transitive dependencies.

    Args:
      srcs: a list of source files
      deps: a list of targets that are direct dependencies
    Returns:
      a collection of the transitive sources
    """
    return depset(
        srcs,
        transitive = [_get_dep_transitive_srcs(dep) for dep in deps],
    )

def _get_transitive_includes(includes, deps):
    return depset(
        includes,
        transitive = [_get_dep_transitive_includes(dep) for dep in deps],
    )

def _td_library_impl(ctx):
    trans_srcs = _get_transitive_srcs(ctx.files.srcs, ctx.attr.deps)
    trans_includes = _get_transitive_includes(ctx.attr.includes, ctx.attr.deps)
    return [TdFiles(
        transitive_sources = trans_srcs,
        transitive_includes = trans_includes,
    )]

td_library = rule(
    _td_library_impl,
    attrs = {
        "srcs": attr.label_list(allow_files = True),
        "includes": attr.string_list(),
        "deps": attr.label_list(),
    },
)

def _gentbl_rule_impl(ctx):
    td_file = ctx.file.td_file
    srcs = []
    srcs.extend(ctx.files.td_srcs)
    if td_file not in srcs:
        srcs.append(td_file)

    trans_srcs = _get_transitive_srcs(srcs, ctx.attr.deps)
    trans_includes = _get_transitive_includes(ctx.attr.td_includes, ctx.attr.deps)

    td_includes_cmd = ["-I%s" % (include,) for include in trans_includes.to_list()]

    td_includes_cmd += [
        "-I=external/llvm-project/mlir/include",
        "-I=%s/external/llvm-project/mlir/include" % (ctx.genfiles_dir.path,),
    ]
    for td_include in ctx.attr.td_includes:
        td_includes_cmd += [
            "-I=%s" % td_include,
            "-I=%s/%s" % (ctx.genfiles_dir.path, td_include),
        ]
    for td_relative_include in ctx.attr.td_relative_includes:
        td_includes_cmd += [
            "-I=%s/%s" % (native.package_name(), td_relative_include),
            "-I=%s/%s/%s" % (ctx.genfiles_dir.path, native.package_name(), td_relative_include),
        ]

    td_includes_cmd.append("-I=%s" % td_file.dirname)

    output = "-o=%s" % (ctx.outputs.output.path,)

    args = ctx.attr.opts + [
        td_file.path,
        "-I=%s" % (ctx.genfiles_dir.path,),
    ] + td_includes_cmd + [output]

    ctx.actions.run(
        outputs = [ctx.outputs.output],
        inputs = trans_srcs.to_list(),
        executable = ctx.executable.tblgen,
        arguments = args,
    )
    return [DefaultInfo()]

gentbl_rule = rule(
    _gentbl_rule_impl,
    attrs = {
        "tblgen": attr.label(
            executable = True,
            cfg = "exec",
        ),
        "td_file": attr.label(allow_single_file = True, mandatory = True),
        "td_srcs": attr.label_list(allow_files = True),
        "deps": attr.label_list(),
        "output": attr.output(mandatory = True),
        "opts": attr.string_list(),
        "td_includes": attr.string_list(),
        "td_relative_includes": attr.string_list(),
    },
)

def gentbl(
        name,
        tblgen,
        td_file,
        tbl_outs,
        td_srcs = [],
        td_includes = [],
        td_relative_includes = [],
        deps = [],
        strip_include_prefix = None,
        test = False):
    """gentbl() generates tabular code from a table definition file.

    Args:
      name: The name of the build rule for use in dependencies.
      tblgen: The binary used to produce the output.
      td_file: The primary table definitions file.
      tbl_outs: A list of tuples (opts, out), where each opts is a string of
        options passed to tblgen, and the out is the corresponding output file
        produced.
      td_srcs: A list of table definition files included transitively.
      td_includes: A list of include paths for relative includes, provided as build targets.
      td_relative_includes: A list of include paths for relative includes, provided as relative path.
      strip_include_prefix: attribute to pass through to cc_library.
      test: whether to create a test to invoke the tool too.
    """
    for (opts, out) in tbl_outs:
        first_opt = opts.split(" ", 1)[0]
        rule_suffix = "_{}_{}".format(first_opt.replace("-", "_").replace("=", "_"), str(hash(opts)))

        gentbl_rule(
            name = "%s_%s_genrule" % (name, rule_suffix),
            td_file = td_file,
            tblgen = tblgen,
            opts = opts.split(" "),
            td_srcs = td_srcs,
            deps = deps,
            td_includes = td_includes,
            td_relative_includes = td_relative_includes,
            output = out,
        )

    # List of opts that do not generate cc files.
    skip_opts = ["-gen-op-doc"]
    hdrs = [f for (opts, f) in tbl_outs if opts not in skip_opts]
    native.cc_library(
        name = name,
        # include_prefix does not apply to textual_hdrs.
        hdrs = hdrs if strip_include_prefix else [],
        strip_include_prefix = strip_include_prefix,
        textual_hdrs = hdrs,
    )
