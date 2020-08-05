#!/bin/python3

# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

"""Generates a Bazel BUILD file for LLVM."""

import argparse
import ast
import collections
import configparser
import errno
import logging
import numbers
import os
import subprocess
import sys

import pasta

# A description of a Library component extracted from an LLVMBuild.txt file.
# Elements:
#   name: the original LLVM name of the target
#   deps: a list of dependencies of the target (LLVM names)
#   src_path: the relative path to the library's private sources
#   hdrs_path: the relative path to the library's public headers.
#   parent: the parent, if any. Used to compute target groups.
Library = collections.namedtuple(
    "Library", ["name", "deps", "src_path", "hdrs_path", "parent"])

# A description of a TargetGroup component extracted from an LLVMBuild.txt file.
TargetGroup = collections.namedtuple("TargetGroup", ["name"])


def _coerce_to_str_node(obj):
  """Coerce a Python string to Python Str node."""
  if isinstance(obj, str):
    return ast.Str(s=obj)
  else:
    return obj


def _coerce_to_expr_value_node(node):
  """Coerce a Expr node to its value node."""
  if isinstance(node, ast.Expr):
    return node.value
  else:
    return node


def _create_rule_node(rule_syntax_name, attributes):
  """Create a rule node ready to be injected into a BUILD AST.

  The order of attributes matters when determing AST nodes' equality and
  Python's `**kwargs` is an unordered dict. Thus, we pass the dictionary
  explicitly to accept OrderedDict when necessary.

  Args:
      rule_syntax_name: the name of the Bazel rule.
      attributes: A dict of keyword arguments to the rule, use OrderedDict if
        the order of the arguments matters.

  Returns:
      An AST Expr node representing the Bazel rule.

  Raises:
      ValueError: if an unsupported value type is given.
  """
  keywords = []
  for k, v in attributes.items():
    if isinstance(v, list) or isinstance(v, tuple):
      v = map(_coerce_to_expr_value_node, v)
      v = map(_coerce_to_str_node, v)
      l = ast.List(elts=list(v), ctx=ast.Load())
      keywords.append(ast.keyword(arg=k, value=l))
    elif isinstance(v, str):
      keywords.append(ast.keyword(arg=k, value=_coerce_to_str_node(v)))
    elif isinstance(v, numbers.Number):
      keywords.append(ast.keyword(arg=k, value=ast.Num(v)))
    elif isinstance(v, ast.AST):
      keywords.append(ast.keyword(arg=k, value=v))
    else:
      raise ValueError("Unsupported keyword value type: %s: %r" % (type(v), v))

  return ast.Expr(
      value=ast.Call(func=ast.Name(id=rule_syntax_name, ctx=ast.Load()),
                     args=[],
                     keywords=keywords,
                     starargs=None,
                     kwargs=None))


def _walk_llvm_repository(path, components, directory):
  """Walks an LLVM source repository to find libraries.

  Args:
    path: A path to an LLVM source directory containing LLVMBuild.txt files to
      traverse.
    components: A dictionary mapping target names to Library tuples, to be
      filled in by the traversal.
    directory: The current relative path from the root of the source tree.
  """

  # Parses the LLVMBuild.txt file. LLVM Build files are in INI format.
  llvmbuild_path = os.path.join(path, directory, "LLVMBuild.txt")
  config = configparser.RawConfigParser()
  config.read(llvmbuild_path)

  # Iterate over the components to find libraries.
  for section in config.sections():
    if section.startswith("component"):
      name = config.get(section, "name")
      section_type = config.get(section, "type")

      if section_type == "Library":
        # Parses the list of required libraries.
        required_libraries = []
        if config.has_option(section, "required_libraries"):
          required_libraries = config.get(section, "required_libraries").split()

        parent = None
        if config.has_option(section, "parent"):
          parent = config.get(section, "parent")

        # Forms the include path by string substitution.
        include_directory = directory.replace("lib/", "include/llvm/", 1)
        components[name] = Library(name, required_libraries, directory,
                                   include_directory, parent)
      elif section_type == "TargetGroup":
        components[name] = TargetGroup(name)
      elif section_type in [
          "LibraryGroup", "BuildTool", "Tool", "Group", "TargetGroup",
          "OptionalLibrary"
      ]:
        # We do not need this kind of component for a Tensorflow build; silently
        # ignore it.
        pass
      else:
        logging.error("Unknown section type: %s", section_type)

  # Recursively visits subdirectories, if any.
  if config.has_option("common", "subdirectories"):
    for subdirectory in config.get("common", "subdirectories").split():
      _walk_llvm_repository(path, components,
                            os.path.join(directory, subdirectory))


def _ast_string_list(alist):
  """Converts a list of strings into an AST string list."""
  return ast.List(elts=[ast.Str(s=s) for s in alist], ctx=ast.Load())


def _ast_glob_expr(path_list):
  """Builds an AST glob() expression that globs a list."""
  return ast.Call(func=ast.Name(id="glob", ctx=ast.Load()),
                  keywords=[],
                  starargs=None,
                  kwargs=None,
                  args=[path_list])


def _ast_cc_library_rule(library,
                         extra_srcs=None,
                         extra_srcs_symbol=None,
                         extra_hdrs=None,
                         extra_glob_hdrs=None,
                         extra_deps=None,
                         extra_copts=None,
                         export_src_headers=False):
  """Builds an AST cc_library() rule.

  Args:
    library: a Library object describing the library
    extra_srcs: a list of extra glob patterns to add to the rule's 'srcs'
    extra_srcs_symbol: an additional symbol (e.g. externally defined variable)
      to add to the rule's 'srcs'.
    extra_hdrs: a list of filenames to add to the rule's 'hdrs'; not globbed.
    extra_glob_hdrs: a list of patterns to add to the rule's 'hdrs'; globbed.
    extra_deps: a list of extra targets to add to the rule's 'deps'.
    extra_copts: a list of 'copts' to pass to the rule.
    export_src_headers: should headers in the library's source path be placed in
      the 'hdrs' section of the rule?

  Returns:
    A python AST for a cc_library() rule.
  """
  deps = [":config"]
  deps += [":" + dep for dep in library.deps]
  deps += extra_deps

  src_hdrs = os.path.join(library.src_path, "*.h")
  src_globs = [
      os.path.join(library.src_path, "*.c"),
      os.path.join(library.src_path, "*.cpp"),
      os.path.join(library.src_path, "*.inc")
  ] + list(extra_srcs)
  if not export_src_headers:
    src_globs.append(src_hdrs)

  if extra_srcs_symbol is not None:
    srcs = ast.BinOp(left=_ast_glob_expr(_ast_string_list(src_globs)),
                     op=ast.Add(),
                     right=ast.Call(func=ast.Name(id=extra_srcs_symbol,
                                                  ctx=ast.Load()),
                                    keywords=[],
                                    starargs=None,
                                    kwargs=None,
                                    args=[]))
  else:
    srcs = _ast_glob_expr(_ast_string_list(src_globs))

  hdr_globs = [
      os.path.join(library.hdrs_path, "*.h"),
      os.path.join(library.hdrs_path, "*.def"),
      os.path.join(library.hdrs_path, "*.inc")
  ] + extra_glob_hdrs
  if export_src_headers:
    hdr_globs.append(src_hdrs)
  hdrs = _ast_glob_expr(_ast_string_list(hdr_globs))
  if extra_hdrs:
    hdrs = ast.BinOp(left=hdrs,
                     op=ast.Add(),
                     right=_ast_string_list(extra_hdrs))

  copts = ast.Name(id="llvm_copts", ctx=ast.Load())
  if extra_copts:
    copts = ast.BinOp(left=copts,
                      op=ast.Add(),
                      right=_ast_string_list(extra_copts))

  attrs = {
      "name": library.name,
      "deps": deps,
      "srcs": srcs,
      "hdrs": hdrs,
      "copts": copts,
  }

  return _create_rule_node("cc_library", attrs)


def _format_build_source(source, path):
  """Formats a BUILD file's contents with buildifier."""
  try:
    buildifier = subprocess.Popen(
        ["buildifier", "-type=build",
         "-path=\"%s\"" % path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf8")
    formatted_source, err = buildifier.communicate(source)
  except OSError as os_error:
    logging.error("Formatting failed on BUILD file: %s",
                  path,
                  exc_info=os_error)
    return source

  if err:
    logging.error("Buildifier: %s", err)
  return formatted_source


TABLEGEN_INTRINSIC_HEADER_TARGETS = [
    "aarch64", "amdgcn", "arm", "bpf", "hexagon", "mips", "nvvm", "ppc", "r600",
    "riscv", "s390", "wasm", "x86", "xcore"
]

# A dictionary mapping LLVM targets to lists of additional `deps` to include in
# the generated cc_library() rule.
EXTRA_DEPS = {
    # The Core module requires the output of the gentbl() rules.
    "Core": [":attributes_gen", ":intrinsic_enums_gen", ":intrinsics_impl_gen"]
            + [
                ":" + target + "_enums_gen"
                for target in TABLEGEN_INTRINSIC_HEADER_TARGETS
            ],
    "TableGen": [":MC"],
    "Scalar": [":Target"],
    "Support": ["@zlib"],
    "AArch64Desc": [
        ":AArch64CommonTableGen", ":attributes_gen", ":intrinsic_enums_gen",
        ":intrinsics_impl_gen"
    ],
    "CodeGen": [":Instrumentation"],
    "AArch64Info": [":CodeGen", ":Target"],
    "AArch64Utils": [":AArch64CommonTableGen", ":MC"],
    "AMDGPUInfo": [":AMDGPUCommonTableGen", ":r600_target_gen", ":Core"],
    "AMDGPUUtils": [":AMDGPUCommonTableGen", ":r600_target_gen"],
    "ARMDesc": [
        ":ARMCommonTableGen", ":attributes_gen", ":intrinsic_enums_gen",
        ":intrinsics_impl_gen"
    ],
    "ARMInfo": [":ARMCommonTableGen", ":Target"],
    "ARMUtils": [":ARMCommonTableGen", ":MC"],
    "DebugInfoCodeView": [":BinaryFormat"],
    "FrontendOpenMP": [":omp_gen", ":omp_gen_impl"],
    "MC": [":BinaryFormat", ":DebugInfoCodeView"],
    "InstCombine": [":InstCombineTableGen"],
    "NVPTXDesc": [":NVPTXCommonTableGen"],
    "NVPTXInfo": [
        ":NVPTXCommonTableGen", ":attributes_gen", ":Core", ":Target"
    ],
    "Passes": [":CodeGen"],
    "PowerPCDesc": [
        ":PowerPCCommonTableGen", ":attributes_gen", ":intrinsic_enums_gen",
        ":intrinsics_impl_gen"
    ],
    "PowerPCInfo": [
        ":PowerPCCommonTableGen", ":attributes_gen", ":Core", ":Target"
    ],
    "RuntimeDyld": [":MCDisassembler"],
    "Vectorize": [":Scalar"],
    "X86CodeGen": [":x86_defs"],
    "X86Info": [":MC", ":X86CommonTableGen"],
    "X86Utils": [":CodeGen"],
    "SystemZInfo": [":SystemZCommonTableGen"],
    "SystemZDesc": [":SystemZCommonTableGen"],
}

# A dictionary mapping LLVM targets to lists of additional `hdrs` to include in
# the generated cc_library() rule. The header strings are not globbed.
EXTRA_HDRS = {
    "Support": [
        "include/llvm/BinaryFormat/MachO.def",
        # The Support module must include the generated VCSRevision.h header;
        # since it is generated, it will not appear in a glob().
        "include/llvm/Support/VCSRevision.h",
    ],
    "TextAPI": [
        "include/llvm/TextAPI/ELF/TBEHandler.h",
        "include/llvm/TextAPI/ELF/ELFStub.h",
        "include/llvm/TextAPI/MachO/Architecture.def",
        "include/llvm/TextAPI/MachO/PackedVersion.h",
        "include/llvm/TextAPI/MachO/InterfaceFile.h",
        "include/llvm/TextAPI/MachO/Symbol.h",
        "include/llvm/TextAPI/MachO/ArchitectureSet.h",
        "include/llvm/TextAPI/MachO/TextAPIWriter.h",
        "include/llvm/TextAPI/MachO/TextAPIReader.h",
        "include/llvm/TextAPI/MachO/Architecture.h"
    ]
}

# Most of these exist to work around layering violations or headers that aren't
# in the usual place.
EXTRA_GLOB_HDRS = {
    "AArch64Info": [
        "lib/Target/AArch64/*.def",
        "lib/Target/AArch64/AArch64*.h",
    ],
    "AsmPrinter": ["lib/CodeGen/AsmPrinter/*.def"],
    "ARMAsmPrinter": ["lib/Target/ARM/*.h"],
    "BinaryFormat": [
        "include/llvm/BinaryFormat/ELFRelocs/*.def",
        "include/llvm/BinaryFormat/WasmRelocs/*.def",
    ],
    "BitReader": ["include/llvm/Bitcode/BitstreamReader.h"],
    "BitWriter": [
        "include/llvm/Bitcode/BitcodeWriter.h",
        "include/llvm/Bitcode/BitcodeWriterPass.h",
        "include/llvm/Bitcode/BitstreamWriter.h",
    ],
    "CodeGen": ["include/llvm/CodeGen/**/*.h"],
    "Core": ["include/llvm/*.h", "include/llvm/Analysis/*.def"],
    "Instrumentation": [
        "include/llvm/Transforms/GCOVProfiler.h",
        "include/llvm/Transforms/Instrumentation.h",
        "include/llvm/Transforms/InstrProfiling.h",
        "include/llvm/Transforms/PGOInstrumentation.h",
    ],
    "NVPTXInfo": ["lib/Target/NVPTX/NVPTX.h",],
    "PowerPCInfo": ["lib/Target/PowerPC/PPC*.h",],
    "RuntimeDyld": [
        "include/llvm/DebugInfo/DIContext.h",
        "include/llvm/ExecutionEngine/RTDyldMemoryManager.h",
        "include/llvm/ExecutionEngine/RuntimeDyld*.h",
    ],
    "Scalar": [
        "include/llvm/Transforms/IPO.h",
        "include/llvm/Transforms/IPO/SCCP.h",
    ],
    "Support": [
        "include/llvm/ADT/*.h",
        "include/llvm/Support/ELFRelocs/*.def",
        "include/llvm/Support/WasmRelocs/*.def",
    ],
    "Target": [
        "include/llvm/CodeGen/*.def",
        "include/llvm/CodeGen/*.inc",
    ],
    "TableGen": ["include/llvm/Target/*.def",],
    "Vectorize": ["include/llvm/Transforms/Vectorize.h",],
}

# A dictionary mapping LLVM targets to lists of additional `srcs` to include in
# the generated cc_library() rule. The sources are passed to glob().
# Most of these exist to work around layering violations.
EXTRA_SRCS = {
    "Analysis": [
        "include/llvm/Transforms/Utils/Local.h",
        "include/llvm/Transforms/Scalar.h",
    ],
    "Core": [
        "include/llvm/Analysis/*.h",
        "include/llvm/Bitcode/BitcodeReader.h",
        "include/llvm/Bitcode/BitCodes.h",
        "include/llvm/Bitcode/LLVMBitCodes.h",
        "include/llvm/CodeGen/MachineValueType.h",
        "include/llvm/CodeGen/ValueTypes.h",
    ],
    "ObjCARC": ["include/llvm/Transforms/ObjCARC.h",],
    "RuntimeDyld": [
        "include/llvm/ExecutionEngine/JITSymbol.h",
        "include/llvm/ExecutionEngine/RTDyldMemoryManager.h",
        "lib/ExecutionEngine/RuntimeDyld/*.h",
        "lib/ExecutionEngine/RuntimeDyld/Targets/*.h",
        "lib/ExecutionEngine/RuntimeDyld/Targets/*.cpp",
    ],
    "Scalar": [
        "include/llvm-c/Transforms/Scalar.h",
        "include/llvm/Transforms/Scalar.h",
        "include/llvm/Target/TargetMachine.h",
    ],
    "Support": [
        "include/llvm-c/*.h",
        "include/llvm/CodeGen/MachineValueType.h",
        "include/llvm/BinaryFormat/COFF.h",
        "include/llvm/BinaryFormat/MachO.h",
    ],
    "Target": [
        "include/llvm/CodeGen/*.h",
        "include/llvm-c/Initialization.h",
        "include/llvm-c/Target.h",
    ],
    "IPO": [
        "include/llvm/Transforms/SampleProfile.h",
        "include/llvm-c/Transforms/IPO.h",
        "include/llvm-c/Transforms/PassManagerBuilder.h",
    ],
    "TableGen": ["include/llvm/CodeGen/*.h",],
    "TransformUtils": [
        "include/llvm/Transforms/IPO.h",
        "include/llvm/Transforms/Scalar.h",
    ],
    "Vectorize": ["include/llvm-c/Transforms/Vectorize.h",],
    "AArch64Info": ["lib/Target/AArch64/MCTargetDesc/*.h"],
    "AArch64Utils": ["lib/Target/AArch64/MCTargetDesc/*.h"],
    "AArch64CodeGen": ["lib/Target/AArch64/GISel/*.cpp"],
    "ARMDesc": [
        "lib/Target/ARM/*.h",
        "include/llvm/CodeGen/GlobalISel/*.h",
    ],
    "ARMInfo": ["lib/Target/ARM/MCTargetDesc/*.h"],
    "ARMUtils": ["lib/Target/ARM/MCTargetDesc/*.h"],
    "NVPTXInfo": ["lib/Target/NVPTX/MCTargetDesc/*.h"],
    "PowerPCInfo": ["lib/Target/PowerPC/MCTargetDesc/*.h"],
    "X86Info": ["lib/Target/X86/MCTargetDesc/*.h"],
    "TextAPI": [
        "lib/TextAPI/ELF/*.cpp", "lib/TextAPI/MachO/*.cpp",
        "lib/TextAPI/MachO/*.h"
    ],
    "SystemZInfo": ["lib/Target/SystemZ/MCTargetDesc/*.h"]
}

# A prelude to emit at the start of the generated BUILD file.
PRELUDE = R"""
# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
# This BUILD file is auto-generated; do not edit!
# See generate_bazel_build.py

load(
    "//llvm:llvm.bzl",
    "cmake_var_string",
    "expand_cmake_vars",
    "gentbl",
    "llvm_all_cmake_vars",
    "llvm_copts",
    "llvm_defines",
    "llvm_linkopts",
    "llvm_support_platform_specific_srcs_glob",
)
load(
    "//llvm:template_rule.bzl",
    "template_rule",
)

package(default_visibility = ["//visibility:public"], licenses = ["notice"])

exports_files(["LICENSE.TXT"])

llvm_host_triple = "x86_64-unknown-linux_gnu"
llvm_targets = [
    "AArch64",
    "AMDGPU",
    "ARM",
    "NVPTX",
    "PowerPC",
    "SystemZ",
    "X86",
]
llvm_target_asm_parsers = llvm_targets
llvm_target_asm_printers = llvm_targets
llvm_target_disassemblers = llvm_targets

# Performs CMake variable substitutions on configuration header files.
expand_cmake_vars(
    name = "config_gen",
    src = "include/llvm/Config/config.h.cmake",
    dst = "include/llvm/Config/config.h",
    cmake_vars = llvm_all_cmake_vars,
)

expand_cmake_vars(
    name = "llvm_config_gen",
    src = "include/llvm/Config/llvm-config.h.cmake",
    dst = "include/llvm/Config/llvm-config.h",
    cmake_vars = llvm_all_cmake_vars,
)

expand_cmake_vars(
    name = "abi_breaking_gen",
    src = "include/llvm/Config/abi-breaking.h.cmake",
    cmake_vars = llvm_all_cmake_vars,
    dst = "include/llvm/Config/abi-breaking.h",
)

# Performs macro expansions on .def.in files
template_rule(
    name = "targets_def_gen",
    src = "include/llvm/Config/Targets.def.in",
    out = "include/llvm/Config/Targets.def",
    substitutions = {
        "@LLVM_ENUM_TARGETS@": "\n".join(
            ["LLVM_TARGET({})".format(t) for t in llvm_targets],
        ),
    },
)

template_rule(
    name = "asm_parsers_def_gen",
    src = "include/llvm/Config/AsmParsers.def.in",
    out = "include/llvm/Config/AsmParsers.def",
    substitutions = {
        "@LLVM_ENUM_ASM_PARSERS@": "\n".join(
            ["LLVM_ASM_PARSER({})".format(t) for t in llvm_target_asm_parsers],
        ),
    },
)

template_rule(
    name = "asm_printers_def_gen",
    src = "include/llvm/Config/AsmPrinters.def.in",
    out = "include/llvm/Config/AsmPrinters.def",
    substitutions = {
        "@LLVM_ENUM_ASM_PRINTERS@": "\n".join(
            ["LLVM_ASM_PRINTER({})".format(t) for t in llvm_target_asm_printers],
        ),
    },
)

template_rule(
    name = "disassemblers_def_gen",
    src = "include/llvm/Config/Disassemblers.def.in",
    out = "include/llvm/Config/Disassemblers.def",
    substitutions = {
        "@LLVM_ENUM_DISASSEMBLERS@": "\n".join(
            ["LLVM_DISASSEMBLER({})".format(t) for t in llvm_target_disassemblers],
        ),
    },
)

# A common library that all LLVM targets depend on.
# TODO(b/113996071): We need to glob all potentially #included files and stage
# them here because LLVM's build files are not strict headers clean, and remote
# build execution requires all inputs to be depended upon.
cc_library(
    name = "config",
    hdrs = glob(["**/*.h", "**/*.def", "**/*.inc.cpp"]) + [
        "include/llvm/Config/AsmParsers.def",
        "include/llvm/Config/AsmPrinters.def",
        "include/llvm/Config/Disassemblers.def",
        "include/llvm/Config/Targets.def",
        "include/llvm/Config/config.h",
        "include/llvm/Config/llvm-config.h",
        "include/llvm/Config/abi-breaking.h",
    ],
    defines = llvm_defines,
    includes = ["include"],
)

# A creator of an empty file include/llvm/Support/VCSRevision.h.
# This is usually populated by the upstream build infrastructure, but in this
# case we leave it blank. See upstream revision r300160.
genrule(
    name = "vcs_revision_gen",
    srcs = [],
    outs = ["include/llvm/Support/VCSRevision.h"],
    cmd = "echo '' > \"$@\"",
)

# Rules that apply the LLVM tblgen tool.
gentbl(
    name = "attributes_gen",
    tbl_outs = [("-gen-attrs", "include/llvm/IR/Attributes.inc")],
    tblgen = ":llvm-tblgen",
    td_file = "include/llvm/IR/Attributes.td",
    td_srcs = ["include/llvm/IR/Attributes.td"],
)

gentbl(
    name = "InstCombineTableGen",
    tbl_outs = [(
        "-gen-searchable-tables",
        "lib/Target/AMDGPU/InstCombineTables.inc",
    )],
    tblgen = ":llvm-tblgen",
    td_file = "lib/Target/AMDGPU/InstCombineTables.td",
    td_srcs = glob([
        "include/llvm/CodeGen/*.td",
        "include/llvm/IR/Intrinsics*.td",
    ]) + ["include/llvm/TableGen/SearchableTable.td"],
)

gentbl(
    name = "intrinsic_enums_gen",
    tbl_outs = [("-gen-intrinsic-enums", "include/llvm/IR/IntrinsicEnums.inc")],
    tblgen = ":llvm-tblgen",
    td_file = "include/llvm/IR/Intrinsics.td",
    td_srcs = glob([
        "include/llvm/CodeGen/*.td",
        "include/llvm/IR/Intrinsics*.td",
    ]),
)


gentbl(
    name = "aarch64_enums_gen",
    tbl_outs = [("-gen-intrinsic-enums -intrinsic-prefix=aarch64",
                 "include/llvm/IR/IntrinsicsAArch64.h")],
    tblgen = ":llvm-tblgen",
    td_file = "include/llvm/IR/Intrinsics.td",
    td_srcs = glob([
        "include/llvm/CodeGen/*.td",
        "include/llvm/IR/Intrinsics*.td",
    ]),
)

gentbl(
    name = "amdgcn_enums_gen",
    tbl_outs = [("-gen-intrinsic-enums -intrinsic-prefix=amdgcn",
                 "include/llvm/IR/IntrinsicsAMDGPU.h")],
    tblgen = ":llvm-tblgen",
    td_file = "include/llvm/IR/Intrinsics.td",
    td_srcs = glob([
        "include/llvm/CodeGen/*.td",
        "include/llvm/IR/Intrinsics*.td",
    ]),
)

gentbl(
    name = "arm_enums_gen",
    tbl_outs = [("-gen-intrinsic-enums -intrinsic-prefix=arm",
                 "include/llvm/IR/IntrinsicsARM.h")],
    tblgen = ":llvm-tblgen",
    td_file = "include/llvm/IR/Intrinsics.td",
    td_srcs = glob([
        "include/llvm/CodeGen/*.td",
        "include/llvm/IR/Intrinsics*.td",
    ]),
)

gentbl(
    name = "bpf_enums_gen",
    tbl_outs = [("-gen-intrinsic-enums -intrinsic-prefix=bpf",
                 "include/llvm/IR/IntrinsicsBPF.h")],
    tblgen = ":llvm-tblgen",
    td_file = "include/llvm/IR/Intrinsics.td",
    td_srcs = glob([
        "include/llvm/CodeGen/*.td",
        "include/llvm/IR/Intrinsics*.td",
    ]),
)

gentbl(
    name = "hexagon_enums_gen",
    tbl_outs = [("-gen-intrinsic-enums -intrinsic-prefix=hexagon",
                 "include/llvm/IR/IntrinsicsHexagon.h")],
    tblgen = ":llvm-tblgen",
    td_file = "include/llvm/IR/Intrinsics.td",
    td_srcs = glob([
        "include/llvm/CodeGen/*.td",
        "include/llvm/IR/Intrinsics*.td",
    ]),
)

gentbl(
    name = "mips_enums_gen",
    tbl_outs = [("-gen-intrinsic-enums -intrinsic-prefix=mips",
                 "include/llvm/IR/IntrinsicsMips.h")],
    tblgen = ":llvm-tblgen",
    td_file = "include/llvm/IR/Intrinsics.td",
    td_srcs = glob([
        "include/llvm/CodeGen/*.td",
        "include/llvm/IR/Intrinsics*.td",
    ]),
)

gentbl(
    name = "nvvm_enums_gen",
    tbl_outs = [("-gen-intrinsic-enums -intrinsic-prefix=nvvm",
                 "include/llvm/IR/IntrinsicsNVPTX.h")],
    tblgen = ":llvm-tblgen",
    td_file = "include/llvm/IR/Intrinsics.td",
    td_srcs = glob([
        "include/llvm/CodeGen/*.td",
        "include/llvm/IR/Intrinsics*.td",
    ]),
)

gentbl(
    name = "ppc_enums_gen",
    tbl_outs = [("-gen-intrinsic-enums -intrinsic-prefix=ppc",
                 "include/llvm/IR/IntrinsicsPowerPC.h")],
    tblgen = ":llvm-tblgen",
    td_file = "include/llvm/IR/Intrinsics.td",
    td_srcs = glob([
        "include/llvm/CodeGen/*.td",
        "include/llvm/IR/Intrinsics*.td",
    ]),
)

gentbl(
    name = "r600_enums_gen",
    tbl_outs = [("-gen-intrinsic-enums -intrinsic-prefix=r600",
                 "include/llvm/IR/IntrinsicsR600.h")],
    tblgen = ":llvm-tblgen",
    td_file = "include/llvm/IR/Intrinsics.td",
    td_srcs = glob([
        "include/llvm/CodeGen/*.td",
        "include/llvm/IR/Intrinsics*.td",
    ]),
)

gentbl(
    name = "riscv_enums_gen",
    tbl_outs = [("-gen-intrinsic-enums -intrinsic-prefix=riscv",
                 "include/llvm/IR/IntrinsicsRISCV.h")],
    tblgen = ":llvm-tblgen",
    td_file = "include/llvm/IR/Intrinsics.td",
    td_srcs = glob([
        "include/llvm/CodeGen/*.td",
        "include/llvm/IR/Intrinsics*.td",
    ]),
)

gentbl(
    name = "s390_enums_gen",
    tbl_outs = [("-gen-intrinsic-enums -intrinsic-prefix=s390",
                 "include/llvm/IR/IntrinsicsS390.h")],
    tblgen = ":llvm-tblgen",
    td_file = "include/llvm/IR/Intrinsics.td",
    td_srcs = glob([
        "include/llvm/CodeGen/*.td",
        "include/llvm/IR/Intrinsics*.td",
    ]),
)

gentbl(
    name = "wasm_enums_gen",
    tbl_outs = [("-gen-intrinsic-enums -intrinsic-prefix=wasm",
                 "include/llvm/IR/IntrinsicsWebAssembly.h")],
    tblgen = ":llvm-tblgen",
    td_file = "include/llvm/IR/Intrinsics.td",
    td_srcs = glob([
        "include/llvm/CodeGen/*.td",
        "include/llvm/IR/Intrinsics*.td",
    ]),
)

gentbl(
    name = "x86_enums_gen",
    tbl_outs = [("-gen-intrinsic-enums -intrinsic-prefix=x86",
                 "include/llvm/IR/IntrinsicsX86.h")],
    tblgen = ":llvm-tblgen",
    td_file = "include/llvm/IR/Intrinsics.td",
    td_srcs = glob([
        "include/llvm/CodeGen/*.td",
        "include/llvm/IR/Intrinsics*.td",
    ]),
)

gentbl(
    name = "xcore_enums_gen",
    tbl_outs = [("-gen-intrinsic-enums -intrinsic-prefix=xcore",
                 "include/llvm/IR/IntrinsicsXCore.h")],
    tblgen = ":llvm-tblgen",
    td_file = "include/llvm/IR/Intrinsics.td",
    td_srcs = glob([
        "include/llvm/CodeGen/*.td",
        "include/llvm/IR/Intrinsics*.td",
    ]),
)

gentbl(
    name = "intrinsics_impl_gen",
    tbl_outs = [("-gen-intrinsic-impl", "include/llvm/IR/IntrinsicImpl.inc")],
    tblgen = ":llvm-tblgen",
    td_file = "include/llvm/IR/Intrinsics.td",
    td_srcs = glob([
        "include/llvm/CodeGen/*.td",
        "include/llvm/IR/Intrinsics*.td",
    ]),
)

cc_library(
    name = "tblgen",
    srcs = glob([
        "utils/TableGen/*.cpp",
        "utils/TableGen/*.h",
        "utils/TableGen/GlobalISel/*.cpp",
    ]),
    hdrs = glob([
        "utils/TableGen/GlobalISel/*.h",
    ]),
    deps = [
        ":MC",
        ":Support",
        ":TableGen",
        ":config",
    ],
)

# Binary targets used by Tensorflow.
cc_binary(
    name = "llvm-tblgen",
    srcs = glob([
        "utils/TableGen/*.cpp",
        "utils/TableGen/*.h",
    ]),
    copts = llvm_copts,
    linkopts = llvm_linkopts,
    stamp = 0,
    deps = [
        ":config",
        ":Support",
        ":TableGen",
        ":tblgen",
    ],
)

cc_binary(
    name = "FileCheck",
    testonly = 1,
    srcs = glob([
        "utils/FileCheck/*.cpp",
        "utils/FileCheck/*.h",
    ]),
    copts = llvm_copts,
    linkopts = llvm_linkopts,
    stamp = 0,
    deps = [":Support"],
)

llvm_target_list = [
    {
        "name": "AArch64",
        "lower_name": "aarch64",
        "short_name": "AArch64",
        "dir_name": "AArch64",
        "tbl_outs": [
            ("-gen-register-bank", "lib/Target/AArch64/AArch64GenRegisterBank.inc"),
            ("-gen-register-info", "lib/Target/AArch64/AArch64GenRegisterInfo.inc"),
            ("-gen-instr-info", "lib/Target/AArch64/AArch64GenInstrInfo.inc"),
            ("-gen-emitter", "lib/Target/AArch64/AArch64GenMCCodeEmitter.inc"),
            ("-gen-pseudo-lowering", "lib/Target/AArch64/AArch64GenMCPseudoLowering.inc"),
            ("-gen-asm-writer", "lib/Target/AArch64/AArch64GenAsmWriter.inc"),
            ("-gen-asm-writer -asmwriternum=1", "lib/Target/AArch64/AArch64GenAsmWriter1.inc"),
            ("-gen-asm-matcher", "lib/Target/AArch64/AArch64GenAsmMatcher.inc"),
            ("-gen-dag-isel", "lib/Target/AArch64/AArch64GenDAGISel.inc"),
            ("-gen-fast-isel", "lib/Target/AArch64/AArch64GenFastISel.inc"),
            ("-gen-global-isel", "lib/Target/AArch64/AArch64GenGlobalISel.inc"),
            ("-gen-global-isel-combiner -combiners=AArch64PreLegalizerCombinerHelper", "lib/Target/AArch64/AArch64GenPreLegalizeGICombiner.inc"),
            ("-gen-global-isel-combiner -combiners=AArch64PostLegalizerCombinerHelper", "lib/Target/AArch64/AArch64GenPostLegalizeGICombiner.inc"),
            ("-gen-callingconv", "lib/Target/AArch64/AArch64GenCallingConv.inc"),
            ("-gen-subtarget", "lib/Target/AArch64/AArch64GenSubtargetInfo.inc"),
            ("-gen-disassembler", "lib/Target/AArch64/AArch64GenDisassemblerTables.inc"),
            ("-gen-searchable-tables", "lib/Target/AArch64/AArch64GenSystemOperands.inc"),
        ],
    },
    {
        "name": "AMDGPU",
        "lower_name": "amdgpu",
        "short_name": "AMDGPU",
        "dir_name": "AMDGPU",
        "tbl_outs": [
            ("-gen-register-bank", "lib/Target/AMDGPU/AMDGPUGenRegisterBank.inc"),
            ("-gen-register-info", "lib/Target/AMDGPU/AMDGPUGenRegisterInfo.inc"),
            ("-gen-instr-info", "lib/Target/AMDGPU/AMDGPUGenInstrInfo.inc"),
            ("-gen-emitter", "lib/Target/AMDGPU/AMDGPUGenMCCodeEmitter.inc"),
            ("-gen-pseudo-lowering", "lib/Target/AMDGPU/AMDGPUGenMCPseudoLowering.inc"),
            ("-gen-asm-writer", "lib/Target/AMDGPU/AMDGPUGenAsmWriter.inc"),
            ("-gen-asm-matcher", "lib/Target/AMDGPU/AMDGPUGenAsmMatcher.inc"),
            ("-gen-dag-isel", "lib/Target/AMDGPU/AMDGPUGenDAGISel.inc"),
            ("-gen-callingconv", "lib/Target/AMDGPU/AMDGPUGenCallingConv.inc"),
            ("-gen-subtarget", "lib/Target/AMDGPU/AMDGPUGenSubtargetInfo.inc"),
            ("-gen-disassembler", "lib/Target/AMDGPU/AMDGPUGenDisassemblerTables.inc"),
            ("-gen-searchable-tables", "lib/Target/AMDGPU/AMDGPUGenSearchableTables.inc"),
        ],
        "tbl_deps": [
            ":amdgpu_isel_target_gen",
        ],
    },
    {
        "name": "ARM",
        "lower_name": "arm",
        "short_name": "ARM",
        "dir_name": "ARM",
        "tbl_outs": [
            ("-gen-register-bank", "lib/Target/ARM/ARMGenRegisterBank.inc"),
            ("-gen-register-info", "lib/Target/ARM/ARMGenRegisterInfo.inc"),
            ("-gen-searchable-tables", "lib/Target/ARM/ARMGenSystemRegister.inc"),
            ("-gen-instr-info", "lib/Target/ARM/ARMGenInstrInfo.inc"),
            ("-gen-emitter", "lib/Target/ARM/ARMGenMCCodeEmitter.inc"),
            ("-gen-pseudo-lowering", "lib/Target/ARM/ARMGenMCPseudoLowering.inc"),
            ("-gen-asm-writer", "lib/Target/ARM/ARMGenAsmWriter.inc"),
            ("-gen-asm-matcher", "lib/Target/ARM/ARMGenAsmMatcher.inc"),
            ("-gen-dag-isel", "lib/Target/ARM/ARMGenDAGISel.inc"),
            ("-gen-fast-isel", "lib/Target/ARM/ARMGenFastISel.inc"),
            ("-gen-global-isel", "lib/Target/ARM/ARMGenGlobalISel.inc"),
            ("-gen-callingconv", "lib/Target/ARM/ARMGenCallingConv.inc"),
            ("-gen-subtarget", "lib/Target/ARM/ARMGenSubtargetInfo.inc"),
            ("-gen-disassembler", "lib/Target/ARM/ARMGenDisassemblerTables.inc"),
        ],
    },
    {
        "name": "NVPTX",
        "lower_name": "nvptx",
        "short_name": "NVPTX",
        "dir_name": "NVPTX",
        "tbl_outs": [
            ("-gen-register-info", "lib/Target/NVPTX/NVPTXGenRegisterInfo.inc"),
            ("-gen-instr-info", "lib/Target/NVPTX/NVPTXGenInstrInfo.inc"),
            ("-gen-asm-writer", "lib/Target/NVPTX/NVPTXGenAsmWriter.inc"),
            ("-gen-dag-isel", "lib/Target/NVPTX/NVPTXGenDAGISel.inc"),
            ("-gen-subtarget", "lib/Target/NVPTX/NVPTXGenSubtargetInfo.inc"),
        ],
    },
    {
        "name": "PowerPC",
        "lower_name": "powerpc",
        "short_name": "PPC",
        "dir_name": "PowerPC",
        "tbl_outs": [
            ("-gen-asm-writer", "lib/Target/PowerPC/PPCGenAsmWriter.inc"),
            ("-gen-asm-matcher", "lib/Target/PowerPC/PPCGenAsmMatcher.inc"),
            ("-gen-emitter", "lib/Target/PowerPC/PPCGenMCCodeEmitter.inc"),
            ("-gen-register-info", "lib/Target/PowerPC/PPCGenRegisterInfo.inc"),
            ("-gen-instr-info", "lib/Target/PowerPC/PPCGenInstrInfo.inc"),
            ("-gen-dag-isel", "lib/Target/PowerPC/PPCGenDAGISel.inc"),
            ("-gen-fast-isel", "lib/Target/PowerPC/PPCGenFastISel.inc"),
            ("-gen-callingconv", "lib/Target/PowerPC/PPCGenCallingConv.inc"),
            ("-gen-subtarget", "lib/Target/PowerPC/PPCGenSubtargetInfo.inc"),
            ("-gen-disassembler", "lib/Target/PowerPC/PPCGenDisassemblerTables.inc"),
        ],
    },
    {
        "name": "SystemZ",
        "lower_name": "system_z",
        "short_name": "SystemZ",
        "dir_name": "SystemZ",
        "tbl_outs": [
            ("-gen-asm-writer", "lib/Target/SystemZ/SystemZGenAsmWriter.inc"),
            ("-gen-asm-matcher", "lib/Target/SystemZ/SystemZGenAsmMatcher.inc"),
            ("-gen-emitter", "lib/Target/SystemZ/SystemZGenMCCodeEmitter.inc"),
            ("-gen-register-info", "lib/Target/SystemZ/SystemZGenRegisterInfo.inc"),
            ("-gen-instr-info", "lib/Target/SystemZ/SystemZGenInstrInfo.inc"),
            ("-gen-dag-isel", "lib/Target/SystemZ/SystemZGenDAGISel.inc"),
            ("-gen-callingconv", "lib/Target/SystemZ/SystemZGenCallingConv.inc"),
            ("-gen-subtarget", "lib/Target/SystemZ/SystemZGenSubtargetInfo.inc"),
            ("-gen-disassembler", "lib/Target/SystemZ/SystemZGenDisassemblerTables.inc"),
        ],
    },
    {
        "name": "X86",
        "lower_name": "x86",
        "short_name": "X86",
        "dir_name": "X86",
        "tbl_outs": [
            ("-gen-register-bank", "lib/Target/X86/X86GenRegisterBank.inc"),
            ("-gen-register-info", "lib/Target/X86/X86GenRegisterInfo.inc"),
            ("-gen-disassembler", "lib/Target/X86/X86GenDisassemblerTables.inc"),
            ("-gen-instr-info", "lib/Target/X86/X86GenInstrInfo.inc"),
            ("-gen-asm-writer", "lib/Target/X86/X86GenAsmWriter.inc"),
            ("-gen-asm-writer -asmwriternum=1", "lib/Target/X86/X86GenAsmWriter1.inc"),
            ("-gen-asm-matcher", "lib/Target/X86/X86GenAsmMatcher.inc"),
            ("-gen-dag-isel", "lib/Target/X86/X86GenDAGISel.inc"),
            ("-gen-fast-isel", "lib/Target/X86/X86GenFastISel.inc"),
            ("-gen-global-isel", "lib/Target/X86/X86GenGlobalISel.inc"),
            ("-gen-callingconv", "lib/Target/X86/X86GenCallingConv.inc"),
            ("-gen-subtarget", "lib/Target/X86/X86GenSubtargetInfo.inc"),
            ("-gen-x86-EVEX2VEX-tables", "lib/Target/X86/X86GenEVEX2VEXTables.inc"),
            ("-gen-exegesis", "lib/Target/X86/X86GenExegesis.inc"),
        ],
    },
]

filegroup(
    name = "common_target_td_sources",
    srcs = glob([
        "include/llvm/CodeGen/*.td",
        "include/llvm/Frontend/Directive/*.td",
        "include/llvm/IR/Intrinsics*.td",
        "include/llvm/TableGen/*.td",
        "include/llvm/Target/*.td",
        "include/llvm/Target/GlobalISel/*.td",
    ]),
)

gentbl(
    name = "amdgpu_isel_target_gen",
    tbl_outs = [
        ("-gen-global-isel", "lib/Target/AMDGPU/AMDGPUGenGlobalISel.inc"),
        ("-gen-global-isel-combiner -combiners=AMDGPUPreLegalizerCombinerHelper", "lib/Target/AMDGPU/AMDGPUGenPreLegalizeGICombiner.inc"),
        ("-gen-global-isel-combiner -combiners=AMDGPUPostLegalizerCombinerHelper", "lib/Target/AMDGPU/AMDGPUGenPostLegalizeGICombiner.inc"),
        ("-gen-global-isel-combiner -combiners=AMDGPURegBankCombinerHelper", "lib/Target/AMDGPU/AMDGPUGenRegBankGICombiner.inc"),
    ],
    tblgen = ":llvm-tblgen",
    td_file = "lib/Target/AMDGPU/AMDGPUGISel.td",
    td_srcs = [
        ":common_target_td_sources",
    ] + glob([
        "lib/Target/AMDGPU/*.td",
    ]),
)

gentbl(
    name = "r600_target_gen",
    tbl_outs = [
        ("-gen-asm-writer", "lib/Target/AMDGPU/R600GenAsmWriter.inc"),
        ("-gen-callingconv", "lib/Target/AMDGPU/R600GenCallingConv.inc"),
        ("-gen-dag-isel", "lib/Target/AMDGPU/R600GenDAGISel.inc"),
        ("-gen-dfa-packetizer", "lib/Target/AMDGPU/R600GenDFAPacketizer.inc"),
        ("-gen-instr-info", "lib/Target/AMDGPU/R600GenInstrInfo.inc"),
        ("-gen-emitter", "lib/Target/AMDGPU/R600GenMCCodeEmitter.inc"),
        ("-gen-register-info", "lib/Target/AMDGPU/R600GenRegisterInfo.inc"),
        ("-gen-subtarget", "lib/Target/AMDGPU/R600GenSubtargetInfo.inc"),
    ],
    tblgen = ":llvm-tblgen",
    td_file = "lib/Target/AMDGPU/R600.td",
    td_srcs = [
        ":common_target_td_sources",
    ] + glob([
        "lib/Target/AMDGPU/*.td",
    ]),
)

[gentbl(
    name = target["name"] + "CommonTableGen",
    tbl_outs = target["tbl_outs"],
    tblgen = ":llvm-tblgen",
    td_file = "lib/Target/" + target["dir_name"] + "/" + target["short_name"] + ".td",
    td_srcs = [
        ":common_target_td_sources",
    ] + glob([
        "lib/Target/" + target["dir_name"] + "/*.td",
    ]),
    deps = target.get("tbl_deps", []),
) for target in llvm_target_list]


# This target is used to provide *.def files to x86_code_gen.
# Files with '.def' extension are not allowed in 'srcs' of 'cc_library' rule.
cc_library(
    name = "x86_defs",
    hdrs = glob([
        "lib/Target/X86/*.def",
    ]),
    visibility = ["//visibility:private"],
)

# This filegroup provides the docker build script in LLVM repo
filegroup(
    name = "docker",
    srcs = glob([
         "utils/docker/build_docker_image.sh",
    ]),
    visibility = ["//visibility:public"],
)

py_binary(
    name = "lit",
    srcs = ["utils/lit/lit.py"] + glob(["utils/lit/lit/**/*.py"]),
)

cc_binary(
    name = "count",
    srcs = ["utils/count/count.c"],
)

cc_binary(
    name = "not",
    srcs = ["utils/not/not.cpp"],
    copts = llvm_copts,
    linkopts = llvm_linkopts,
    deps = [
        ":Support",
    ],
)

cc_library(
    name = "AllTargetsCodeGens",
    deps = [
        target["name"] + "CodeGen"
        for target in llvm_target_list
    ],
)

gentbl(
    name = "omp_gen",
    tbl_outs = [("--gen-directive-decl", "include/llvm/Frontend/OpenMP/OMP.h.inc")],
    tblgen = ":llvm-tblgen",
    td_file = "include/llvm/Frontend/OpenMP/OMP.td",
    td_srcs = glob([
        "include/llvm/Frontend/OpenMP/*.td",
        "include/llvm/Frontend/Directive/*.td",
    ]),
)

gentbl(
    name = "omp_gen_impl",
    tbl_outs = [("--gen-directive-impl", "include/llvm/Frontend/OpenMP/OMP.cpp.inc")],
    tblgen = ":llvm-tblgen",
    td_file = "include/llvm/Frontend/OpenMP/OMP.td",
    td_srcs = glob([
        "include/llvm/Frontend/OpenMP/*.td",
        "include/llvm/Frontend/Directive/*.td",
    ]),
)

# TODO(b/159809163): autogenerate this after enabling release-mode ML
# InlineAdvisor
cc_library(
    name = "Analysis",
    srcs = glob(
        [
            "lib/Analysis/*.c",
            "lib/Analysis/*.cpp",
            "lib/Analysis/*.inc",
            "include/llvm/Transforms/Utils/Local.h",
            "include/llvm/Transforms/Scalar.h",
            "lib/Analysis/*.h",
        ],
        exclude = [
            "lib/Analysis/DevelopmentModeInlineAdvisor.cpp",
            "lib/Analysis/MLInlineAdvisor.cpp",
            "lib/Analysis/ReleaseModeModelRunner.cpp",
            "lib/Analysis/TFUtils.cpp",
        ],
    ),
    hdrs = glob([
        "include/llvm/Analysis/*.h",
        "include/llvm/Analysis/*.def",
        "include/llvm/Analysis/*.inc",
    ]),
    copts = llvm_copts,
    deps = [
        ":BinaryFormat",
        ":Core",
        ":Object",
        ":ProfileData",
        ":Support",
        ":config",
    ],
)

########################## Begin generated content ##########################
"""


def parse_arguments():
  """Parses command-line options for the script."""
  parser = argparse.ArgumentParser(
      description="Generate a Bazel Build file for LLVM by walking the LLVM"
      " directory and reading LLVMBuild.txt files.")
  parser.add_argument(
      "--llvm_root",
      required=True,
      type=str,
      help="Local path to the LLVM subproject with the LLVMBuild.txt files to"
      " read.")
  args = parser.parse_args()
  return args


def main(args):
  # Walks the LLVM source repository to enumerate library components.
  components = {}
  llvmbuild_path = os.path.join(args.llvm_root, "LLVMBuild.txt")
  if not os.path.exists(llvmbuild_path):
    raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), llvmbuild_path)
  _walk_llvm_repository(args.llvm_root, components, "")

  rules = []
  library_names = [
      name for name, component in components.items()
      if isinstance(component, Library)
  ]
  library_names.sort()
  for name in library_names:
    component = components[name]
    extra_copts = []
    export_src_headers = False
    if component.parent in components:
      parent = components[component.parent]
      if isinstance(parent, TargetGroup):
        extra_copts += [
            "-Iexternal/llvm-project/llvm/lib/Target/" + parent.name
        ]
        export_src_headers = True
    extra_srcs_symbol = None
    if name == "Support":
      extra_srcs_symbol = "llvm_support_platform_specific_srcs_glob"
    if name == "Analysis":
      continue
    rules.append(
        _ast_cc_library_rule(component,
                             extra_deps=EXTRA_DEPS.get(name, []),
                             extra_srcs=EXTRA_SRCS.get(name, []),
                             extra_srcs_symbol=extra_srcs_symbol,
                             extra_hdrs=EXTRA_HDRS.get(name, []),
                             extra_glob_hdrs=EXTRA_GLOB_HDRS.get(name, []),
                             extra_copts=extra_copts,
                             export_src_headers=export_src_headers))

  # Output and format as a BUILD file.
  module = ast.Module(body=rules)
  output = PRELUDE + pasta.dump(module)
  output = _format_build_source(output, "@llvm-project//llvm")
  sys.stdout.write(output)


if __name__ == "__main__":
  main(parse_arguments())
