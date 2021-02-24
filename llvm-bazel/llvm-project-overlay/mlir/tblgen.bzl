# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

"""BUILD extensions for MLIR table generation."""

TdFilesInfo = provider(
    "Holds tablegen files and the dependencies and include paths necessary to build them.",
    fields = {
        "transitive_sources": "td files transitively used by this rule.",
        "transitive_includes": "include arguments to add to the final tablegen invocation.",
    },
)

# For now we allow anything that provides DefaultInfo to just forward its files.
# In particular, this allows filegroups to be used. This is mostly to ease
# transition. In the future, the TdFilesInfo provider will be required.
# TODO(gcmn): Switch to enforcing TdFilesInfo provider.
def _get_dep_transitive_srcs(dep):
    """Extract TdFilesInfo.transitive_sources, falling back to DefaultInfo.files."""
    if TdFilesInfo in dep:
        return dep[TdFilesInfo].transitive_sources
    return dep[DefaultInfo].files

def _get_dep_transitive_includes(dep):
    """Extract TdFilesInfo.transitive_includes, falling back to an empty depset()."""
    if TdFilesInfo in dep:
        return dep[TdFilesInfo].transitive_includes
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
        direct = srcs,
        transitive = [_get_dep_transitive_srcs(dep) for dep in deps],
    )

def _get_transitive_includes(includes, deps):
    """Obtain the includes paths for a target and its transitive dependencies.

    Args:
      includes: a list of include paths
      deps: a list of targets that are direct dependencies
    Returns:
      a collection of the transitive include paths
    """
    return depset(
        direct = includes,
        transitive = [_get_dep_transitive_includes(dep) for dep in deps],
    )

def _resolve_includes(ctx, raw_includes):
    """Resolves include paths as relative to the current package path."""
    includes = []
    package_path = ctx.build_file_path[:-len("BUILD")]
    for include in raw_includes:
        if include.startswith("/"):
            # TODO(gcmn): Figure out how to support absolute includes as
            # relative to the repository root.
            fail("Absolute includes not yet supported. Got: '%s'" % include)
        else:
            includes.append(package_path + include)
            includes.append(ctx.genfiles_dir.path + "/" + package_path + include)
    return includes

def _td_library_impl(ctx):
    trans_srcs = _get_transitive_srcs(ctx.files.srcs, ctx.attr.deps)
    trans_includes = _get_transitive_includes(
        _resolve_includes(ctx, ctx.attr.includes),
        ctx.attr.deps,
    )
    return [
        DefaultInfo(files = trans_srcs),
        TdFilesInfo(
            transitive_sources = trans_srcs,
            transitive_includes = trans_includes,
        ),
    ]

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

    trans_srcs = _get_transitive_srcs(ctx.files.td_srcs + [td_file], ctx.attr.deps)
    trans_includes = _get_transitive_includes(ctx.attr.td_relative_includes, ctx.attr.deps)

    args = ctx.actions.args()
    args.add_all(ctx.attr.opts)
    args.add(td_file)
    args.add("-I", ctx.genfiles_dir.path)
    args.add("-I", td_file.dirname)
    args.add_all(trans_includes, before_each = "-I")
    # Can't use map_each because we need ctx.genfiled_dir and map_each can't be
    # a closure.
    args.add_all(ctx.attr.td_includes, before_each = "-I")
    args.add_all(
        ctx.attr.td_includes,
        before_each = "-I",
        format_each = ctx.genfiles_dir.path + "/%s",
    )
    args.add("-o", ctx.outputs.output.path)

    ctx.actions.run(
        outputs = [ctx.outputs.output],
        inputs = trans_srcs,
        executable = ctx.executable.tblgen,
        arguments = [args],
    )
    return [DefaultInfo()]

gentbl_rule = rule(
    _gentbl_rule_impl,
    output_to_genfiles = True,
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
        test = False,
        **kwargs):
    """gentbl() generates tabular code from a table definition file.

    Args:
      name: The name of the build rule for use in dependencies.
      tblgen: The binary used to produce the output.
      td_file: The primary table definitions file.
      tbl_outs: A list of tuples (opts, out), where each opts is a string of
        options passed to tblgen, and the out is the corresponding output file
        produced.
      td_srcs: A list of table definition files included transitively.
      td_includes: A list of absolute include paths to add to the tablegen
        invocation.
      td_relative_includes: A list of include paths for relative includes,
        provided as relative path.
      deps: td_library dependencies used by td_file.
      strip_include_prefix: attribute to pass through to cc_library.
      test: whether to create a test to invoke the tool too.
      **kwargs: Extra keyword arguments to pass to the genrated rules.
    """
    for (opts_string, out) in tbl_outs:
        # TODO(gcmn): The API of opts as single string is preserved for backward
        # compatibility. Change to taking a sequence.

        opts = opts_string.split(" ") if opts_string else []

        # Filter out empty options
        opts = [opt for opt in opts if opt]

        first_opt = opts[0] if opts else ""
        rule_suffix = "_{}_{}".format(
            first_opt.replace("-", "_").replace("=", "_"),
            str(hash(opts_string)),
        )
        gentbl_rule(
            name = "%s_%s_genrule" % (name, rule_suffix),
            td_file = td_file,
            tblgen = tblgen,
            opts = opts,
            td_srcs = td_srcs,
            deps = deps,
            td_includes = td_includes,
            td_relative_includes = td_relative_includes,
            output = out,
            **kwargs
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
        **kwargs
    )
