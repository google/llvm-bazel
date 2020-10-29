# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

package(
    default_visibility = ["//visibility:public"],
    licenses = ["notice"],
)

cc_test(
    name = "ast_tests",
    size = "medium",
    timeout = "long",
    srcs = glob([
        "AST/*.cpp",
        "AST/*.h",
    ]),
    deps = [
        "//clang:ast",
        "//clang:ast_matchers",
        "//clang:basic",
        "//clang:frontend",
        "//clang:lex",
        "//clang:testing",
        "//clang:tooling",
        "//llvm:Core",
        "//llvm:Support",
        "//llvm:TestingSupport",
        "//llvm:gmock",
        "//llvm:gtest",
        "//llvm:gtest_main",
    ],
)

cc_library(
    name = "ast_matchers_tests_hdrs",
    testonly = 1,
    hdrs = glob(["ASTMatchers/*.h"]),
    deps = [
        "//clang:ast_matchers",
        "//clang:frontend",
        "//clang:testing",
        "//clang:tooling",
        "//llvm:gtest",
    ],
)

cc_test(
    name = "ast_matchers_tests",
    size = "large",
    srcs = glob(["ASTMatchers/*.cpp"]),
    deps = [
        ":ast_matchers_tests_hdrs",
        "//clang:ast",
        "//clang:ast_matchers",
        "//clang:frontend",
        "//clang:tooling",
        "//llvm:Support",
        "//llvm:TestingSupport",
        "//llvm:gtest",
        "//llvm:gtest_main",
    ],
)

cc_test(
    name = "ast_matchers_dynamic_tests",
    size = "small",
    srcs = glob(["ASTMatchers/Dynamic/*.cpp"]),
    deps = [
        ":ast_matchers_tests_hdrs",
        "//clang:ast_matchers",
        "//clang:ast_matchers_dynamic",
        "//clang:frontend",
        "//clang:tooling",
        "//llvm:Support",
        "//llvm:gtest",
        "//llvm:gtest_main",
    ],
)

cc_test(
    name = "analysis_tests",
    size = "small",
    srcs = glob([
        "Analysis/*.cpp",
        "Analysis/*.h",
    ]),
    deps = [
        "//clang:analysis",
        "//clang:ast",
        "//clang:ast_matchers",
        "//clang:tooling",
        "//llvm:Support",
        "//llvm:gmock",
        "//llvm:gtest",
        "//llvm:gtest_main",
    ],
)

cc_test(
    name = "basic_tests",
    size = "small",
    srcs = glob(["Basic/*.cpp"]),
    deps = [
        "//clang:basic",
        "//clang:frontend",
        "//clang:lex",
        "//llvm:Support",
        "//llvm:config",
        "//llvm:gmock",
        "//llvm:gtest",
        "//llvm:gtest_main",
    ],
)

cc_test(
    name = "codegen_tests",
    size = "small",
    srcs = glob([
        "CodeGen/*.cpp",
        "CodeGen/*.h",
    ]),
    deps = [
        "//clang:ast",
        "//clang:basic",
        "//clang:codegen",
        "//clang:frontend",
        "//clang:lex",
        "//clang:parse",
        "//clang:sema",
        "//llvm:Core",
        "//llvm:Support",
        "//llvm:gtest",
        "//llvm:gtest_main",
    ],
)

cc_test(
    name = "format_tests",
    size = "medium",
    srcs = glob([
        "Format/*.cpp",
        "Format/*.h",
    ]),
    copts = ["$(STACK_FRAME_UNLIMITED)"],
    deps = [
        ":tooling_tests_hdrs",
        "//clang:basic",
        "//clang:format",
        "//clang:frontend",
        "//clang:tooling_core",
        "//llvm:Support",
        "//llvm:gtest",
        "//llvm:gtest_main",
    ],
)

cc_test(
    name = "frontend_tests",
    size = "small",
    srcs = glob(
        ["Frontend/*.cpp"],
    ),
    deps = [
        "//clang:ast",
        "//clang:basic",
        "//clang:codegen",
        "//clang:driver_options_inc_gen",
        "//clang:frontend",
        "//clang:frontend_tool",
        "//clang:lex",
        "//clang:sema",
        "//clang:serialization",
        "//llvm:Support",
        "//llvm:gmock",
        "//llvm:gtest",
        "//llvm:gtest_main",
    ],
)

cc_test(
    name = "lex_tests",
    size = "small",
    srcs = glob(["Lex/*.cpp"]),
    copts = ["$(STACK_FRAME_UNLIMITED)"],
    deps = [
        "//clang:ast",
        "//clang:basic",
        "//clang:lex",
        "//clang:parse",
        "//clang:sema",
        "//clang:serialization",
        "//llvm:Support",
        "//llvm:gmock",
        "//llvm:gtest",
        "//llvm:gtest_main",
    ],
)

cc_test(
    name = "rename_tests",
    size = "small",
    timeout = "moderate",
    srcs = glob(
        [
            "Rename/*.cpp",
            "Rename/*.h",
        ],
    ),
    copts = [
        # TODO: The `:tooling_test_hdrs` are reached using include paths that
        # need this, but it would be better to restructure things so they could
        # have a more natural location and not rely on a Bazel internal.
        "-Iexternal/llvm-project/clang",
    ],
    deps = [
        ":tooling_tests_hdrs",
        "//clang:ast_matchers",
        "//clang:basic",
        "//clang:format",
        "//clang:frontend",
        "//clang:tooling",
        "//clang:tooling_refactoring",
        "//llvm:Support",
        "//llvm:gtest",
        "//llvm:gtest_main",
    ],
)

cc_test(
    name = "rewrite_tests",
    size = "small",
    srcs = glob(["Rewrite/*.cpp"]),
    deps = [
        "//clang:rewrite",
        "//clang:tooling",
        "//llvm:gtest",
        "//llvm:gtest_main",
    ],
)

cc_test(
    name = "sema_tests",
    size = "small",
    srcs = glob(["Sema/*.cpp"]),
    deps = [
        ":ast_matchers_tests_hdrs",
        "//clang:ast",
        "//clang:ast_matchers",
        "//clang:frontend",
        "//clang:lex",
        "//clang:parse",
        "//clang:sema",
        "//clang:tooling",
        "//llvm:TestingSupport",
        "//llvm:gmock",
        "//llvm:gtest",
        "//llvm:gtest_main",
    ],
)

cc_library(
    name = "static_analyzer_test_headers",
    testonly = 1,
    hdrs = glob(["StaticAnalyzer/*.h"]),
    deps = [
        "//clang:ast_matchers",
        "//clang:crosstu",
        "//clang:frontend",
        "//clang:static_analyzer_core",
        "//clang:static_analyzer_frontend",
        "//clang:tooling",
        "//llvm:gtest",
    ],
)

cc_test(
    name = "static_analyzer_tests",
    size = "small",
    srcs = glob(
        ["StaticAnalyzer/*.cpp"],
        exclude = [
            # New test has unused-variable warnings.
            "StaticAnalyzer/ParamRegionTest.cpp",
        ],
    ),
    deps = [
        ":static_analyzer_test_headers",
        "//clang:basic",
        "//clang:frontend",
        "//clang:static_analyzer_core",
        "//clang:static_analyzer_frontend",
        "//clang:tooling",
        "//llvm:Support",
        "//llvm:config",
        "//llvm:gtest",
        "//llvm:gtest_main",
    ],
)

cc_library(
    name = "tooling_tests_hdrs",
    testonly = 1,
    hdrs = glob(["Tooling/*.h"]),
    deps = [
        "//clang:ast",
        "//clang:basic",
        "//clang:frontend",
        "//clang:rewrite",
        "//clang:tooling",
        "//clang:tooling_core",
        "//llvm:Support",
        "//llvm:gtest",
    ],
)

cc_test(
    name = "tooling_tests",
    size = "medium",
    srcs = glob(["Tooling/*.cpp"]),
    deps = [
        ":tooling_tests_hdrs",
        "//clang:ast",
        "//clang:ast_matchers",
        "//clang:basic",
        "//clang:format",
        "//clang:frontend",
        "//clang:lex",
        "//clang:rewrite",
        "//clang:tooling",
        "//clang:tooling_core",
        "//clang:tooling_inclusions",
        "//clang:tooling_refactoring",
        "//clang:transformer",
        "//llvm:Support",
        "//llvm:TestingSupport",
        "//llvm:gmock",
        "//llvm:gtest",
        "//llvm:gtest_main",
    ],
)

cc_test(
    name = "tooling_recursive_ast_visitor_tests",
    size = "medium",
    srcs = glob(["Tooling/RecursiveASTVisitorTests/*.cpp"]) + [
        "Tooling/RecursiveASTVisitorTests/CallbacksCommon.h",
    ],
    copts = [
        # TOOD: Would be nice to rework the headers here to avoid the need for
        # this and relying on Bazel internals.
        "-Iexternal/llvm-project/clang/unittests/Tooling",
    ],
    deps = [
        ":tooling_tests_hdrs",
        "//clang:ast",
        "//clang:basic",
        "//clang:frontend",
        "//clang:lex",
        "//clang:tooling",
        "//clang:tooling_syntax",
        "//llvm:Support",
        "//llvm:TestingSupport",
        "//llvm:gmock",
        "//llvm:gtest",
        "//llvm:gtest_main",
    ],
)

cc_test(
    name = "tooling_syntax_tests",
    size = "medium",
    srcs = glob([
        "Tooling/Syntax/*.cpp",
        "Tooling/Syntax/*.h",
    ]),
    deps = [
        "//clang:ast",
        "//clang:basic",
        "//clang:frontend",
        "//clang:lex",
        "//clang:testing",
        "//clang:tooling",
        "//clang:tooling_core",
        "//clang:tooling_syntax",
        "//llvm:Support",
        "//llvm:TestingSupport",
        "//llvm:gmock",
        "//llvm:gtest",
        "//llvm:gtest_main",
    ],
)

cc_test(
    name = "libclang_tests",
    size = "small",
    srcs = glob(["libclang/*.cpp"]) + [
        "libclang/TestUtils.h",
    ],
    deps = [
        "//clang:c-bindings",
        "//llvm:Support",
        "//llvm:gtest",
        "//llvm:gtest_main",
    ],
)
