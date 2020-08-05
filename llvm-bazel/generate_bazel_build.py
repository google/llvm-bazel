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
                         extra_glob_srcs=None,
                         extra_symbol_srcs=None,
                         extra_hdrs=None,
                         extra_glob_hdrs=None,
                         extra_deps=None,
                         extra_copts=None,
                         export_src_headers=False):
  """Builds an AST cc_library() rule.

  Args:
    library: a Library object describing the library
    extra_glob_srcs: a list of extra glob patterns to add to the rule's 'srcs'
    extra_symbol_srcs: additional symbols (e.g. externally defined variables)
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
  extra_glob_srcs = extra_glob_srcs if extra_glob_srcs else []
  extra_hdrs = extra_hdrs if extra_hdrs else []
  extra_glob_hdrs = extra_glob_hdrs if extra_glob_hdrs else []
  extra_deps = extra_deps if extra_deps else []
  extra_copts = extra_copts if extra_copts else []
  extra_symbol_srcs = extra_symbol_srcs if extra_symbol_srcs else []

  deps = [":config"]
  deps += [":" + dep for dep in library.deps]
  deps += extra_deps

  src_hdrs = os.path.join(library.src_path, "*.h")
  src_globs = [
      os.path.join(library.src_path, "*.c"),
      os.path.join(library.src_path, "*.cpp"),
      os.path.join(library.src_path, "*.inc")
  ] + extra_glob_srcs
  if not export_src_headers:
    src_globs.append(src_hdrs)

  srcs = _ast_glob_expr(_ast_string_list(src_globs))
  for extra_srcs_symbol in extra_symbol_srcs:
    srcs = ast.BinOp(left=srcs,
                     op=ast.Add(),
                     right=ast.Call(func=ast.Name(id=extra_srcs_symbol,
                                                  ctx=ast.Load()),
                                    keywords=[],
                                    starargs=None,
                                    kwargs=None,
                                    args=[]))

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

# Extra dependencies for generated rules.
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

# Extra files to include in generated rules.
# These map LLVM targets to lists of globbed or unglobbed files to add to the
# target's source and headers.
# Most of these exist to work around layering violations or headers that aren't
# in the usual place.

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

EXTRA_GLOB_SRCS = {
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

EXTRA_SYMBOL_SRCS = {
    "Support": ["llvm_support_platform_specific_srcs_glob"],
}

# A prelude to emit at the start of the generated section of the BUILD file.
PRELUDE = """
########################## Begin autogenerated content #########################
###  This content is autogenerated by generate_bazel_build.py. Do not edit!  ###
################################################################################
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
    if name == "Analysis":
      continue
    rules.append(
        _ast_cc_library_rule(component,
                             extra_deps=EXTRA_DEPS.get(name),
                             extra_glob_srcs=EXTRA_GLOB_SRCS.get(name),
                             extra_symbol_srcs=EXTRA_SYMBOL_SRCS.get(name),
                             extra_hdrs=EXTRA_HDRS.get(name),
                             extra_glob_hdrs=EXTRA_GLOB_HDRS.get(name),
                             extra_copts=extra_copts,
                             export_src_headers=export_src_headers))

  # Output and format as a BUILD file.
  module = ast.Module(body=rules)
  output = PRELUDE + pasta.dump(module)
  output = _format_build_source(output, "@llvm-project//llvm")
  sys.stdout.write(output)


if __name__ == "__main__":
  main(parse_arguments())
