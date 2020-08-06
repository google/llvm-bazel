# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

"""Configures an LLVM overlay project."""

# Directory of overlay files relative to WORKSPACE
OVERLAY_DIR = "llvm-project-overlay"

def _is_absolute(path):
    """Returns `True` if `path` is an absolute path.

    Args:
      path: A path (which is a string).
    Returns:
      `True` if `path` is an absolute path.
    """
    return path.startswith("/") or (len(path) > 2 and path[1] == ":")

def _join_path(a, b):
    if _is_absolute(b):
        return b
    return str(a) + "/" + str(b)

def _llvm_configure_impl(repository_ctx):
    src_workspace_path = repository_ctx.path(
        repository_ctx.attr.workspace,
    ).dirname

    src_path = _join_path(src_workspace_path, repository_ctx.attr.src_path)

    if repository_ctx.attr.overlay_path:
        overlay_path = _join_path(
            src_workspace_path,
            repository_ctx.attr.overlay_path,
        )
    else:
        this_workspace_path = repository_ctx.path(
            repository_ctx.attr._this_workspace,
        ).dirname
        overlay_path = _join_path(this_workspace_path, OVERLAY_DIR)


    overlay_script = repository_ctx.path(
        repository_ctx.attr._overlay_script,
    )

    cmd = [
        overlay_script,
        "--src",
        src_path,
        "--overlay",
        overlay_path,
        "--target",
        ".",
    ]
    exec_result = repository_ctx.execute(cmd, timeout = 20)

    if exec_result.return_code != 0:
        fail(("Failed to execute overlay script: '{cmd}':\n" +
              "Exited with code {return_code}" +
              "stdout:\n{stdout}\n" + "stderr:\n{stderr}\n").format(
            cmd = " ".join(cmd),
            return_code = exec_result.return_code,
            stdout = exec_result.stdout,
            stderr = exec_result.stderr,
        ))

llvm_configure = repository_rule(
    implementation = _llvm_configure_impl,
    local = True,
    attrs = {
        "_this_workspace": attr.label(default = Label("//:WORKSPACE")),
        "_overlay_script": attr.label(
            default = Label("//:overlay_directories.py"),
            allow_single_file = True,
        ),
        "workspace": attr.label(default = Label("//:WORKSPACE")),
        "src_path": attr.string(mandatory = True),
        "overlay_path": attr.string(),
    },
)
