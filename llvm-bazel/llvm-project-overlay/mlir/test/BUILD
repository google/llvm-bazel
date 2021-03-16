# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

load("//mlir:tblgen.bzl", "gentbl", "td_library")

package(
    default_visibility = [":test_friends"],
    licenses = ["notice"],
)

# Please only depend on this from MLIR tests.
package_group(
    name = "test_friends",
    packages = ["//..."],
)

cc_library(
    name = "IRProducingAPITest",
    hdrs = ["APITest.h"],
    includes = ["."],
)

cc_library(
    name = "TestAnalysis",
    srcs = glob(["lib/Analysis/*.cpp"]),
    includes = ["lib/Dialect/Test"],
    deps = [
        ":TestDialect",
        "//llvm:Support",
        "//mlir:Analysis",
        "//mlir:IR",
        "//mlir:Pass",
        "//mlir:Support",
    ],
)

td_library(
    name = "TestOpTdFiles",
    srcs = [
        "lib/Dialect/Test/TestInterfaces.td",
        "lib/Dialect/Test/TestOps.td",
        "//mlir:include/mlir/Dialect/DLTI/DLTIBase.td",
        "//mlir:include/mlir/IR/OpAsmInterface.td",
        "//mlir:include/mlir/IR/RegionKindInterface.td",
        "//mlir:include/mlir/IR/SymbolInterfaces.td",
        "//mlir:include/mlir/Interfaces/CallInterfaces.td",
        "//mlir:include/mlir/Interfaces/ControlFlowInterfaces.td",
        "//mlir:include/mlir/Interfaces/CopyOpInterface.td",
        "//mlir:include/mlir/Interfaces/DataLayoutInterfaces.td",
        "//mlir:include/mlir/Interfaces/InferTypeOpInterface.td",
    ],
    deps = [
        "//mlir:OpBaseTdFiles",
        "//mlir:SideEffectTdFiles",
    ],
)

gentbl(
    name = "TestOpsIncGen",
    strip_include_prefix = "lib/Dialect/Test",
    tbl_outs = [
        (
            "-gen-op-decls",
            "lib/Dialect/Test/TestOps.h.inc",
        ),
        (
            "-gen-op-defs",
            "lib/Dialect/Test/TestOps.cpp.inc",
        ),
        (
            "-gen-dialect-decls -dialect=test",
            "lib/Dialect/Test/TestOpsDialect.h.inc",
        ),
        (
            "-gen-enum-decls",
            "lib/Dialect/Test/TestOpEnums.h.inc",
        ),
        (
            "-gen-enum-defs",
            "lib/Dialect/Test/TestOpEnums.cpp.inc",
        ),
        (
            "-gen-struct-attr-decls",
            "lib/Dialect/Test/TestOpStructs.h.inc",
        ),
        (
            "-gen-struct-attr-defs",
            "lib/Dialect/Test/TestOpStructs.cpp.inc",
        ),
        (
            "-gen-rewriters",
            "lib/Dialect/Test/TestPatterns.inc",
        ),
    ],
    tblgen = "//mlir:mlir-tblgen",
    td_file = "lib/Dialect/Test/TestOps.td",
    test = True,
    deps = [
        ":TestOpTdFiles",
    ],
)

gentbl(
    name = "TestInterfacesIncGen",
    strip_include_prefix = "lib/Dialect/Test",
    tbl_outs = [
        (
            "-gen-type-interface-decls",
            "lib/Dialect/Test/TestTypeInterfaces.h.inc",
        ),
        (
            "-gen-type-interface-defs",
            "lib/Dialect/Test/TestTypeInterfaces.cpp.inc",
        ),
        (
            "-gen-op-interface-decls",
            "lib/Dialect/Test/TestOpInterfaces.h.inc",
        ),
        (
            "-gen-op-interface-defs",
            "lib/Dialect/Test/TestOpInterfaces.cpp.inc",
        ),
    ],
    tblgen = "//mlir:mlir-tblgen",
    td_file = "lib/Dialect/Test/TestInterfaces.td",
    test = True,
    deps = [
        "//mlir:OpBaseTdFiles",
        "//mlir:SideEffectInterfacesTdFiles",
    ],
)

gentbl(
    name = "TestAttrDefsIncGen",
    strip_include_prefix = "lib/Dialect/Test",
    tbl_outs = [
        (
            "-gen-attrdef-decls",
            "lib/Dialect/Test/TestAttrDefs.h.inc",
        ),
        (
            "-gen-attrdef-defs",
            "lib/Dialect/Test/TestAttrDefs.cpp.inc",
        ),
    ],
    tblgen = "//mlir:mlir-tblgen",
    td_file = "lib/Dialect/Test/TestAttrDefs.td",
    td_srcs = [
        ":TestOpTdFiles",
    ],
    test = True,
)

gentbl(
    name = "TestTypeDefsIncGen",
    strip_include_prefix = "lib/Dialect/Test",
    tbl_outs = [
        (
            "-gen-typedef-decls",
            "lib/Dialect/Test/TestTypeDefs.h.inc",
        ),
        (
            "-gen-typedef-defs",
            "lib/Dialect/Test/TestTypeDefs.cpp.inc",
        ),
    ],
    tblgen = "//mlir:mlir-tblgen",
    td_file = "lib/Dialect/Test/TestTypeDefs.td",
    test = True,
    deps = [
        ":TestOpTdFiles",
    ],
)

cc_library(
    name = "TestDialect",
    srcs = [
        "lib/Dialect/Test/TestAttributes.cpp",
        "lib/Dialect/Test/TestDialect.cpp",
        "lib/Dialect/Test/TestInterfaces.cpp",
        "lib/Dialect/Test/TestPatterns.cpp",
        "lib/Dialect/Test/TestTraits.cpp",
        "lib/Dialect/Test/TestTypes.cpp",
    ],
    hdrs = [
        "lib/Dialect/Test/TestAttributes.h",
        "lib/Dialect/Test/TestDialect.h",
        "lib/Dialect/Test/TestInterfaces.h",
        "lib/Dialect/Test/TestTypes.h",
    ],
    includes = [
        "lib/Dialect/Test",
    ],
    deps = [
        ":TestAttrDefsIncGen",
        ":TestInterfacesIncGen",
        ":TestOpsIncGen",
        ":TestTypeDefsIncGen",
        "//llvm:Support",
        "//mlir:ControlFlowInterfaces",
        "//mlir:CopyOpInterface",
        "//mlir:DLTIDialect",
        "//mlir:DataLayoutInterfaces",
        "//mlir:DerivedAttributeOpInterface",
        "//mlir:Dialect",
        "//mlir:IR",
        "//mlir:InferTypeOpInterface",
        "//mlir:MemRefDialect",
        "//mlir:Pass",
        "//mlir:SideEffects",
        "//mlir:StandardOps",
        "//mlir:StandardOpsTransforms",
        "//mlir:TransformUtils",
        "//mlir:Transforms",
    ],
)

cc_library(
    name = "TestIR",
    srcs = [
        "lib/IR/TestFunc.cpp",
        "lib/IR/TestInterfaces.cpp",
        "lib/IR/TestMatchers.cpp",
        "lib/IR/TestPrintDefUse.cpp",
        "lib/IR/TestPrintNesting.cpp",
        "lib/IR/TestSideEffects.cpp",
        "lib/IR/TestSlicing.cpp",
        "lib/IR/TestSymbolUses.cpp",
        "lib/IR/TestTypes.cpp",
        "lib/IR/TestVisitors.cpp",
    ],
    deps = [
        ":TestDialect",
        "//llvm:Support",
        "//mlir:Analysis",
        "//mlir:IR",
        "//mlir:LinalgOps",
        "//mlir:Pass",
        "//mlir:StandardOps",
        "//mlir:Support",
    ],
)

cc_library(
    name = "TestPass",
    srcs = [
        "lib/Pass/TestPassManager.cpp",
    ],
    deps = [
        "//llvm:Support",
        "//mlir:IR",
        "//mlir:Pass",
        "//mlir:Support",
    ],
)

cc_library(
    name = "TestRewrite",
    srcs = [
        "lib/Rewrite/TestPDLByteCode.cpp",
    ],
    deps = [
        "//mlir:IR",
        "//mlir:Pass",
        "//mlir:Support",
        "//mlir:TransformUtils",
    ],
)

cc_library(
    name = "TestReducer",
    srcs = [
        "lib/Reducer/MLIRTestReducer.cpp",
    ],
    deps = [
        "//mlir:IR",
        "//mlir:Pass",
        "//mlir:Support",
    ],
)

cc_library(
    name = "TestTransforms",
    srcs = glob(["lib/Transforms/*.cpp"]),
    defines = ["MLIR_CUDA_CONVERSIONS_ENABLED"],
    includes = ["lib/Dialect/Test"],
    deps = [
        ":TestDialect",
        "//llvm:NVPTXCodeGen",
        "//llvm:Support",
        "//mlir:Affine",
        "//mlir:AffineTransforms",
        "//mlir:Analysis",
        "//mlir:DLTIDialect",
        "//mlir:EDSC",
        "//mlir:GPUDialect",
        "//mlir:GPUToGPURuntimeTransforms",
        "//mlir:GPUTransforms",
        "//mlir:IR",
        "//mlir:LLVMDialect",
        "//mlir:LLVMToLLVMIRTranslation",
        "//mlir:LLVMTransforms",
        "//mlir:LinalgOps",
        "//mlir:LinalgTransforms",
        "//mlir:MathDialect",
        "//mlir:MathTransforms",
        "//mlir:MemRefDialect",
        "//mlir:NVVMDialect",
        "//mlir:NVVMToLLVMIRTranslation",
        "//mlir:Pass",
        "//mlir:ROCDLDialect",
        "//mlir:ROCDLToLLVMIRTranslation",
        "//mlir:SCFDialect",
        "//mlir:SPIRVDialect",
        "//mlir:StandardOps",
        "//mlir:StandardOpsTransforms",
        "//mlir:Support",
        "//mlir:ToLLVMIRTranslation",
        "//mlir:TransformUtils",
        "//mlir:Transforms",
        "//mlir:VectorOps",
        "//mlir:VectorToLLVM",
        "//mlir:VectorToSCF",
    ],
)

cc_library(
    name = "TestAffine",
    srcs = glob([
        "lib/Dialect/Affine/*.cpp",
    ]),
    deps = [
        "//llvm:Support",
        "//mlir:Affine",
        "//mlir:AffineTransforms",
        "//mlir:AffineUtils",
        "//mlir:Analysis",
        "//mlir:IR",
        "//mlir:MemRefDialect",
        "//mlir:Pass",
        "//mlir:Support",
        "//mlir:Transforms",
        "//mlir:VectorOps",
    ],
)

cc_library(
    name = "TestShapeDialect",
    srcs = [
        "lib/Dialect/Shape/TestShapeFunctions.cpp",
    ],
    deps = [
        "//llvm:Support",
        "//mlir:IR",
        "//mlir:InferTypeOpInterface",
        "//mlir:Pass",
        "//mlir:Shape",
    ],
)

cc_library(
    name = "TestSPIRV",
    srcs = glob([
        "lib/Dialect/SPIRV/*.cpp",
    ]),
    deps = [
        "//mlir:GPUDialect",
        "//mlir:IR",
        "//mlir:Pass",
        "//mlir:SPIRVConversion",
        "//mlir:SPIRVDialect",
        "//mlir:SPIRVModuleCombiner",
        "//mlir:Transforms",
    ],
)

cc_library(
    name = "TestTypeDialect",
    srcs = glob([
        "lib/Dialect/LLVMIR/*.cpp",
    ]),
    deps = [
        ":TestDialect",
        "//mlir:IR",
        "//mlir:LLVMDialect",
    ],
)

cc_library(
    name = "TestTosaDialect",
    srcs = glob([
        "lib/Dialect/Tosa/*.cpp",
    ]),
    deps = [
        "//mlir:IR",
        "//mlir:Pass",
        "//mlir:StandardOps",
        "//mlir:TosaDialect",
        "//mlir:Transforms",
    ],
)
