# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

load("//llvm:template_rule.bzl", "template_rule")
load("//llvm:tblgen.bzl", "gentbl")

package(
    default_visibility = ["//visibility:public"],
    licenses = ["notice"],
)

exports_files(["LICENSE.TXT"])

llvm_host_triple = "x86_64-unknown-linux_gnu"

# FIXME: Would be nice to have a select here on the compiler so that we can use
# a more minimal list for Clang than we need for GCC. Currently this merges the
# two lists. However, that results in warning flags that aren't understood by
# the compiler. For GCC, this will only result in extra warning output when
# a warning or error occurs for some other reason. For Clang, we disable
# warning on unknown warning options.
llvm_copts = [
    "$(STACK_FRAME_UNLIMITED)",
    "-Wno-unused-parameter",
    "-Wno-comment",
    "-Wno-class-memaccess",
    "-Wno-maybe-uninitialized",
    "-Wno-misleading-indentation",
    "-Wno-unknown-warning-option",
]

llvm_targets = [
    "AArch64",
    "AMDGPU",
    "ARM",
    "BPF",
    "Hexagon",
    "Lanai",
    "NVPTX",
    "PowerPC",
    "RISCV",
    "Sparc",
    "WebAssembly",
    "X86",
]

template_rule(
    name = "targets_def_gen",
    src = "include/llvm/Config/Targets.def.in",
    out = "include/llvm/Config/Targets.def",
    substitutions = {
        "@LLVM_ENUM_TARGETS@": "\n".join(["LLVM_TARGET({})".format(t) for t in llvm_targets]),
    },
)

template_rule(
    name = "asm_printers_def_gen",
    src = "include/llvm/Config/AsmPrinters.def.in",
    out = "include/llvm/Config/AsmPrinters.def",
    substitutions = {
        "@LLVM_ENUM_ASM_PRINTERS@": "\n".join(["LLVM_ASM_PRINTER({})".format(t) for t in llvm_targets]),
    },
)

llvm_target_asm_parsers = [
    "AArch64",
    "AMDGPU",
    "ARM",
    "BPF",
    "Hexagon",
    "Lanai",
    "PowerPC",
    "RISCV",
    "Sparc",
    "WebAssembly",
    "X86",
]

template_rule(
    name = "asm_parsers_def_gen",
    src = "include/llvm/Config/AsmParsers.def.in",
    out = "include/llvm/Config/AsmParsers.def",
    substitutions = {
        "@LLVM_ENUM_ASM_PARSERS@": "\n".join(["LLVM_ASM_PARSER({})".format(t) for t in llvm_target_asm_parsers]),
    },
)

llvm_target_disassemblers = [
    "AArch64",
    "AMDGPU",
    "ARM",
    "BPF",
    "Hexagon",
    "Lanai",
    "PowerPC",
    "RISCV",
    "Sparc",
    "WebAssembly",
    "X86",
]

template_rule(
    name = "disassemblers_def_gen",
    src = "include/llvm/Config/Disassemblers.def.in",
    out = "include/llvm/Config/Disassemblers.def",
    substitutions = {
        "@LLVM_ENUM_DISASSEMBLERS@": "\n".join(["LLVM_DISASSEMBLER({})".format(t) for t in llvm_target_disassemblers]),
    },
)

# TODO: Need to replace this with something that actually extracts the git
# commit from the LLVM source (submodule or http_archive).
genrule(
    name = "version_info_gen",
    outs = ["include/llvm/Config/VersionInfo.h"],
    cmd = "echo \"#define LLVM_VERSION_INFO \\\"git\\\"\" > $@",
)

# These rules substitute fairly generic Linux and x86 flavored configs
# currently. We could extend it in-place with selects-style switching on
# platforms, or by extracting parts of the dictionary to be computed in with
# a separate starlark function where the config switching can be managed.
#
# TODO: Priority list of enhancements needed here:
# - Reflect `opt`, `dbg`, etc. features.
# - Basic port to Mac for convenience.
# - Extract into something cleaner based on Starlark.

template_rule(
    name = "llvm_config_h_gen",
    src = "include/llvm/Config/llvm-config.h.cmake",
    out = "include/llvm/Config/llvm-config.h",
    substitutions = {
        # Define if LLVM_ENABLE_DUMP is enabled
        "#cmakedefine LLVM_ENABLE_DUMP": "/* #undef LLVM_ENABLE_DUMP */",

        # Target triple LLVM will generate code for by default
        "#cmakedefine LLVM_DEFAULT_TARGET_TRIPLE \"${LLVM_DEFAULT_TARGET_TRIPLE}\"": "#define LLVM_DEFAULT_TARGET_TRIPLE \"x86_64-unknown-linux-gnu\"",

        # Define if threads enabled
        "#cmakedefine01 LLVM_ENABLE_THREADS": "#define LLVM_ENABLE_THREADS 1",

        # Has gcc/MSVC atomic intrinsics
        "#cmakedefine01 LLVM_HAS_ATOMICS": "#define LLVM_HAS_ATOMICS 1",

        # Host triple LLVM will be executed on
        "#cmakedefine LLVM_HOST_TRIPLE \"${LLVM_HOST_TRIPLE}\"": "#define LLVM_HOST_TRIPLE \"x86_64-unknown-linux-gnu\"",

        # LLVM architecture name for the native architecture, if available
        "#cmakedefine LLVM_NATIVE_ARCH ${LLVM_NATIVE_ARCH}": "#define LLVM_NATIVE_ARCH X86",

        # LLVM name for the native AsmParser init function, if available
        "#cmakedefine LLVM_NATIVE_ASMPARSER LLVMInitialize${LLVM_NATIVE_ARCH}AsmParser": "#define LLVM_NATIVE_ASMPARSER LLVMInitializeX86AsmParser",

        # LLVM name for the native AsmPrinter init function, if available
        "#cmakedefine LLVM_NATIVE_ASMPRINTER LLVMInitialize${LLVM_NATIVE_ARCH}AsmPrinter": "#define LLVM_NATIVE_ASMPRINTER LLVMInitializeX86AsmPrinter",

        # LLVM name for the native Disassembler init function, if available
        "#cmakedefine LLVM_NATIVE_DISASSEMBLER LLVMInitialize${LLVM_NATIVE_ARCH}Disassembler": "#define LLVM_NATIVE_DISASSEMBLER LLVMInitializeX86Disassembler",

        # LLVM name for the native Target init function, if available
        "#cmakedefine LLVM_NATIVE_TARGET LLVMInitialize${LLVM_NATIVE_ARCH}Target": "#define LLVM_NATIVE_TARGET LLVMInitializeX86Target",

        # LLVM name for the native TargetInfo init function, if available
        "#cmakedefine LLVM_NATIVE_TARGETINFO LLVMInitialize${LLVM_NATIVE_ARCH}TargetInfo": "#define LLVM_NATIVE_TARGETINFO LLVMInitializeX86TargetInfo",

        # LLVM name for the native target MC init function, if available
        "#cmakedefine LLVM_NATIVE_TARGETMC LLVMInitialize${LLVM_NATIVE_ARCH}TargetMC": "#define LLVM_NATIVE_TARGETMC LLVMInitializeX86TargetMC",

        # Define if this is Unixish platform
        "#cmakedefine LLVM_ON_UNIX ${LLVM_ON_UNIX}": "#define LLVM_ON_UNIX 1",

        # Define if we have the Intel JIT API runtime support library
        "#cmakedefine01 LLVM_USE_INTEL_JITEVENTS": "#define LLVM_USE_INTEL_JITEVENTS 0",

        # Define if we have the oprofile JIT-support library
        "#cmakedefine01 LLVM_USE_OPROFILE": "#define LLVM_USE_OPROFILE 0",

        # Define if we have the perf JIT-support library
        "#cmakedefine01 LLVM_USE_PERF": "#define LLVM_USE_PERF 0",

        # Major version of the LLVM API
        "#define LLVM_VERSION_MAJOR ${LLVM_VERSION_MAJOR}": "#define LLVM_VERSION_MAJOR 11",

        # Minor version of the LLVM API
        "#define LLVM_VERSION_MINOR ${LLVM_VERSION_MINOR}": "#define LLVM_VERSION_MINOR 0",

        # Patch version of the LLVM API
        "#define LLVM_VERSION_PATCH ${LLVM_VERSION_PATCH}": "#define LLVM_VERSION_PATCH 0",

        # LLVM version string
        "#define LLVM_VERSION_STRING \"${PACKAGE_VERSION}\"": "#define LLVM_VERSION_STRING \"11.0.0git\"",

        # Whether LLVM records statistics for use with GetStatistics(),
        # PrintStatistics() or PrintStatisticsJSON()
        "#cmakedefine01 LLVM_FORCE_ENABLE_STATS": "#define LLVM_FORCE_ENABLE_STATS 0",

        # Define if we have z3 and want to build it */
        "#cmakedefine LLVM_WITH_Z3 ${LLVM_WITH_Z3}": "/* #undef LLVM_WITH_Z3 */",

        # Define if LLVM was built with a dependency to the libtensorflow dynamic library */
        "#cmakedefine LLVM_HAVE_TF_API": "/* #undef LLVM_HAVE_TF_API */",

        # Define if LLVM was built with a dependency to the tensorflow compiler */
        "#cmakedefine LLVM_HAVE_TF_AOT": "/* #undef LLVM_HAVE_TF_AOT */",
    },
)

template_rule(
    name = "abi_breaking_h_gen",
    src = "include/llvm/Config/abi-breaking.h.cmake",
    out = "include/llvm/Config/abi-breaking.h",
    substitutions = {
        # Define to enable checks that alter the LLVM C++ ABI
        "#cmakedefine01 LLVM_ENABLE_ABI_BREAKING_CHECKS": "#define LLVM_ENABLE_ABI_BREAKING_CHECKS 0",

        # Define to enable reverse iteration of unordered llvm containers
        "#cmakedefine01 LLVM_ENABLE_REVERSE_ITERATION": "#define LLVM_ENABLE_REVERSE_ITERATION 0",
    },
)

template_rule(
    name = "config_h_gen",
    src = "include/llvm/Config/config.h.cmake",
    out = "include/llvm/Config/config.h",
    substitutions = {
        # Bug report URL.
        "#define BUG_REPORT_URL \"${BUG_REPORT_URL}\"": "#define BUG_REPORT_URL \"https://bugs.llvm.org/\"",

        # Define to 1 to enable backtraces, and to 0 otherwise.
        "#cmakedefine01 ENABLE_BACKTRACES": "#define ENABLE_BACKTRACES 1",

        # Define to 1 to enable crash overrides, and to 0 otherwise.
        "#cmakedefine01 ENABLE_CRASH_OVERRIDES": "#define ENABLE_CRASH_OVERRIDES 1",

        # Define to 1 to enable crash memory dumps, and to 0 otherwise.
        "#cmakedefine01 LLVM_ENABLE_CRASH_DUMPS": "#define LLVM_ENABLE_CRASH_DUMPS 0",

        # Define to 1 if you have the `backtrace' function.
        "#cmakedefine HAVE_BACKTRACE ${HAVE_BACKTRACE}": "#define HAVE_BACKTRACE TRUE",
        "#define BACKTRACE_HEADER <${BACKTRACE_HEADER}>": "#define BACKTRACE_HEADER <execinfo.h>",

        # Define to 1 if you have the <CrashReporterClient.h> header file.
        "#cmakedefine HAVE_CRASHREPORTERCLIENT_H": "/* #undef HAVE_CRASHREPORTERCLIENT_H */",

        # can use __crashreporter_info__
        "#cmakedefine01 HAVE_CRASHREPORTER_INFO": "#define HAVE_CRASHREPORTER_INFO 0",

        # Define to 1 if you have the declaration of `arc4random', and to 0 if you don't.
        "#cmakedefine01 HAVE_DECL_ARC4RANDOM": "#define HAVE_DECL_ARC4RANDOM 0",

        # Define to 1 if you have the declaration of `FE_ALL_EXCEPT', and to 0 if you don't.
        "#cmakedefine01 HAVE_DECL_FE_ALL_EXCEPT": "#define HAVE_DECL_FE_ALL_EXCEPT 1",

        # Define to 1 if you have the declaration of `FE_INEXACT', and to 0 if you don't.
        "#cmakedefine01 HAVE_DECL_FE_INEXACT": "#define HAVE_DECL_FE_INEXACT 1",

        # Define to 1 if you have the declaration of `strerror_s', and to 0 if you don't.
        "#cmakedefine01 HAVE_DECL_STRERROR_S": "#define HAVE_DECL_STRERROR_S 0",

        # Define to 1 if you have the DIA SDK installed, and to 0 if you don't.
        "#cmakedefine01 LLVM_ENABLE_DIA_SDK": "#define LLVM_ENABLE_DIA_SDK 0",

        # Define to 1 if you have the <dlfcn.h> header file.
        "#cmakedefine HAVE_DLFCN_H ${HAVE_DLFCN_H}": "#define HAVE_DLFCN_H 1",

        # Define if dlopen() is available on this platform.
        "#cmakedefine HAVE_DLOPEN ${HAVE_DLOPEN}": "#define HAVE_DLOPEN 1",

        # Define if dladdr() is available on this platform.
        "#cmakedefine HAVE_DLADDR ${HAVE_DLADDR}": "/* #undef HAVE_DLADDR */",

        # Define to 1 if you have the <errno.h> header file.
        "#cmakedefine HAVE_ERRNO_H ${HAVE_ERRNO_H}": "#define HAVE_ERRNO_H 1",

        # Define to 1 if you have the <fcntl.h> header file.
        "#cmakedefine HAVE_FCNTL_H ${HAVE_FCNTL_H}": "#define HAVE_FCNTL_H 1",

        # Define to 1 if you have the <fenv.h> header file.
        "#cmakedefine HAVE_FENV_H ${HAVE_FENV_H}": "#define HAVE_FENV_H 1",

        # Define if libffi is available on this platform.
        "#cmakedefine HAVE_FFI_CALL ${HAVE_FFI_CALL}": "/* #undef HAVE_FFI_CALL */",

        # Define to 1 if you have the <ffi/ffi.h> header file.
        "#cmakedefine HAVE_FFI_FFI_H ${HAVE_FFI_FFI_H}": "/* #undef HAVE_FFI_FFI_H */",

        # Define to 1 if you have the <ffi.h> header file.
        "#cmakedefine HAVE_FFI_H ${HAVE_FFI_H}": "/* #undef HAVE_FFI_H */",

        # Define to 1 if you have the `futimens' function.
        "#cmakedefine HAVE_FUTIMENS ${HAVE_FUTIMENS}": "#define HAVE_FUTIMENS 1",

        # Define to 1 if you have the `futimes' function.
        "#cmakedefine HAVE_FUTIMES ${HAVE_FUTIMES}": "#define HAVE_FUTIMES 1",

        # Define to 1 if you have the `getpagesize' function.
        "#cmakedefine HAVE_GETPAGESIZE ${HAVE_GETPAGESIZE}": "#define HAVE_GETPAGESIZE 1",

        # Define to 1 if you have the `getrlimit' function.
        "#cmakedefine HAVE_GETRLIMIT ${HAVE_GETRLIMIT}": "#define HAVE_GETRLIMIT 1",

        # Define to 1 if you have the `getrusage' function.
        "#cmakedefine HAVE_GETRUSAGE ${HAVE_GETRUSAGE}": "#define HAVE_GETRUSAGE 1",

        # Define to 1 if you have the `isatty' function.
        "#cmakedefine HAVE_ISATTY 1": "#define HAVE_ISATTY 1",

        # Define to 1 if you have the `edit' library (-ledit).
        "#cmakedefine HAVE_LIBEDIT ${HAVE_LIBEDIT}": "/* #undef HAVE_LIBEDIT */",

        # Define to 1 if you have the `pfm' library (-lpfm).
        "#cmakedefine HAVE_LIBPFM ${HAVE_LIBPFM}": "/* #undef HAVE_LIBPFM */",

        # Define to 1 if the `perf_branch_entry' struct has field cycles.
        "#cmakedefine LIBPFM_HAS_FIELD_CYCLES ${LIBPFM_HAS_FIELD_CYCLES}": "/* #undef LIBPFM_HAS_FIELD_CYCLES */",

        # Define to 1 if you have the `psapi' library (-lpsapi).
        "#cmakedefine HAVE_LIBPSAPI ${HAVE_LIBPSAPI}": "/* #undef HAVE_LIBPSAPI */",

        # Define to 1 if you have the `pthread' library (-lpthread).
        "#cmakedefine HAVE_LIBPTHREAD ${HAVE_LIBPTHREAD}": "#define HAVE_LIBPTHREAD 1",

        # Define to 1 if you have the `pthread_getname_np' function.
        "#cmakedefine HAVE_PTHREAD_GETNAME_NP ${HAVE_PTHREAD_GETNAME_NP}": "#define HAVE_PTHREAD_GETNAME_NP 1",

        # Define to 1 if you have the `pthread_setname_np' function.
        "#cmakedefine HAVE_PTHREAD_SETNAME_NP ${HAVE_PTHREAD_SETNAME_NP}": "#define HAVE_PTHREAD_SETNAME_NP 1",

        # Define to 1 if you have the `z' library (-lz).
        # FIXME: Enable this by detecting the system library.
        "#cmakedefine HAVE_LIBZ ${HAVE_LIBZ}": "/* #undef HAVE_LIBZ */",

        # Define to 1 if you have the <link.h> header file.
        "#cmakedefine HAVE_LINK_H ${HAVE_LINK_H}": "#define HAVE_LINK_H 1",

        # Define to 1 if you have the `lseek64' function.
        "#cmakedefine HAVE_LSEEK64 ${HAVE_LSEEK64}": "#define HAVE_LSEEK64 1",

        # Define to 1 if you have the <mach/mach.h> header file.
        "#cmakedefine HAVE_MACH_MACH_H ${HAVE_MACH_MACH_H}": "/* #undef HAVE_MACH_MACH_H */",

        # Define to 1 if you have the `mallctl' function.
        "#cmakedefine HAVE_MALLCTL ${HAVE_MALLCTL}": "/* #undef HAVE_MALLCTL */",

        # Define to 1 if you have the `mallinfo' function.
        "#cmakedefine HAVE_MALLINFO ${HAVE_MALLINFO}": "#define HAVE_MALLINFO 1",

        # Define to 1 if you have the <malloc/malloc.h> header file.
        "#cmakedefine HAVE_MALLOC_MALLOC_H ${HAVE_MALLOC_MALLOC_H}": "/* #undef HAVE_MALLOC_MALLOC_H */",

        # Define to 1 if you have the `malloc_zone_statistics' function.
        "#cmakedefine HAVE_MALLOC_ZONE_STATISTICS ${HAVE_MALLOC_ZONE_STATISTICS}": "/* #undef HAVE_MALLOC_ZONE_STATISTICS */",

        # Define to 1 if you have the `posix_fallocate' function.
        "#cmakedefine HAVE_POSIX_FALLOCATE ${HAVE_POSIX_FALLOCATE}": "#define HAVE_POSIX_FALLOCATE 1",

        # Define to 1 if you have the `posix_spawn' function.
        "#cmakedefine HAVE_POSIX_SPAWN ${HAVE_POSIX_SPAWN}": "#define HAVE_POSIX_SPAWN 1",

        # Define to 1 if you have the `pread' function.
        "#cmakedefine HAVE_PREAD ${HAVE_PREAD}": "#define HAVE_PREAD 1",

        # Have pthread_getspecific
        "#cmakedefine HAVE_PTHREAD_GETSPECIFIC ${HAVE_PTHREAD_GETSPECIFIC}": "#define HAVE_PTHREAD_GETSPECIFIC 1",

        # Define to 1 if you have the <pthread.h> header file.
        "#cmakedefine HAVE_PTHREAD_H ${HAVE_PTHREAD_H}": "#define HAVE_PTHREAD_H 1",

        # Have pthread_mutex_lock
        "#cmakedefine HAVE_PTHREAD_MUTEX_LOCK ${HAVE_PTHREAD_MUTEX_LOCK}": "#define HAVE_PTHREAD_MUTEX_LOCK 1",

        # Have pthread_rwlock_init
        "#cmakedefine HAVE_PTHREAD_RWLOCK_INIT ${HAVE_PTHREAD_RWLOCK_INIT}": "#define HAVE_PTHREAD_RWLOCK_INIT 1",

        # Define to 1 if you have the `sbrk' function.
        "#cmakedefine HAVE_SBRK ${HAVE_SBRK}": "#define HAVE_SBRK 1",

        # Define to 1 if you have the `setenv' function.
        "#cmakedefine HAVE_SETENV ${HAVE_SETENV}": "#define HAVE_SETENV 1",

        # Define to 1 if you have the `setrlimit' function.
        "#cmakedefine HAVE_SETRLIMIT ${HAVE_SETRLIMIT}": "#define HAVE_SETRLIMIT 1",

        # Define to 1 if you have the `sigaltstack' function.
        "#cmakedefine HAVE_SIGALTSTACK ${HAVE_SIGALTSTACK}": "#define HAVE_SIGALTSTACK 1",

        # Define to 1 if you have the <signal.h> header file.
        "#cmakedefine HAVE_SIGNAL_H ${HAVE_SIGNAL_H}": "#define HAVE_SIGNAL_H 1",

        # Define to 1 if you have the `strerror' function.
        "#cmakedefine HAVE_STRERROR ${HAVE_STRERROR}": "#define HAVE_STRERROR 1",

        # Define to 1 if you have the `strerror_r' function.
        "#cmakedefine HAVE_STRERROR_R ${HAVE_STRERROR_R}": "#define HAVE_STRERROR_R 1",

        # Define to 1 if you have the `sysconf' function.
        "#cmakedefine HAVE_SYSCONF ${HAVE_SYSCONF}": "#define HAVE_SYSCONF 1",

        # Define to 1 if you have the <sys/ioctl.h> header file.
        "#cmakedefine HAVE_SYS_IOCTL_H ${HAVE_SYS_IOCTL_H}": "#define HAVE_SYS_IOCTL_H 1",

        # Define to 1 if you have the <sys/mman.h> header file.
        "#cmakedefine HAVE_SYS_MMAN_H ${HAVE_SYS_MMAN_H}": "#define HAVE_SYS_MMAN_H 1",

        # Define to 1 if you have the <sys/param.h> header file.
        "#cmakedefine HAVE_SYS_PARAM_H ${HAVE_SYS_PARAM_H}": "#define HAVE_SYS_PARAM_H 1",

        # Define to 1 if you have the <sys/resource.h> header file.
        "#cmakedefine HAVE_SYS_RESOURCE_H ${HAVE_SYS_RESOURCE_H}": "#define HAVE_SYS_RESOURCE_H 1",

        # Define to 1 if you have the <sys/stat.h> header file.
        "#cmakedefine HAVE_SYS_STAT_H ${HAVE_SYS_STAT_H}": "#define HAVE_SYS_STAT_H 1",

        # Define to 1 if you have the <sys/time.h> header file.
        "#cmakedefine HAVE_SYS_TIME_H ${HAVE_SYS_TIME_H}": "#define HAVE_SYS_TIME_H 1",

        # Define to 1 if stat struct has st_mtimespec member .
        "#cmakedefine HAVE_STRUCT_STAT_ST_MTIMESPEC_TV_NSEC ${HAVE_STRUCT_STAT_ST_MTIMESPEC_TV_NSEC}": "/* #undef HAVE_STRUCT_STAT_ST_MTIMESPEC_TV_NSEC */",

        # Define to 1 if stat struct has st_mtim member.
        "#cmakedefine HAVE_STRUCT_STAT_ST_MTIM_TV_NSEC ${HAVE_STRUCT_STAT_ST_MTIM_TV_NSEC}": "#define HAVE_STRUCT_STAT_ST_MTIM_TV_NSEC 1",

        # Define to 1 if you have the <sys/types.h> header file.
        "#cmakedefine HAVE_SYS_TYPES_H ${HAVE_SYS_TYPES_H}": "#define HAVE_SYS_TYPES_H 1",

        # Define if the setupterm() function is supported this platform.
        # FIXME: Enable this correctly by detecting the system library if possible.
        "#cmakedefine HAVE_TERMINFO ${HAVE_TERMINFO}": "/* #undef HAVE_TERMINFO */",

        # Define if the xar_open() function is supported this platform.
        "#cmakedefine HAVE_LIBXAR ${HAVE_LIBXAR}": "/* #undef HAVE_LIBXAR */",

        # Define to 1 if you have the <termios.h> header file.
        "#cmakedefine HAVE_TERMIOS_H ${HAVE_TERMIOS_H}": "#define HAVE_TERMIOS_H 1",

        # Define to 1 if you have the <unistd.h> header file.
        "#cmakedefine HAVE_UNISTD_H ${HAVE_UNISTD_H}": "#define HAVE_UNISTD_H 1",

        # Define to 1 if you have the <valgrind/valgrind.h> header file.
        "#cmakedefine HAVE_VALGRIND_VALGRIND_H ${HAVE_VALGRIND_VALGRIND_H}": "/* #undef HAVE_VALGRIND_VALGRIND_H */",

        # Define to 1 if you have the <zlib.h> header file.
        # FIXME: Enable this by detecting the system library.
        "#cmakedefine HAVE_ZLIB_H ${HAVE_ZLIB_H}": "/* #undef HAVE_ZLIB_H */",

        # Have host's _alloca
        "#cmakedefine HAVE__ALLOCA ${HAVE__ALLOCA}": "/* #undef HAVE__ALLOCA */",

        # Define to 1 if you have the `_chsize_s' function.
        "#cmakedefine HAVE__CHSIZE_S ${HAVE__CHSIZE_S}": "/* #undef HAVE__CHSIZE_S */",

        # Define to 1 if you have the `_Unwind_Backtrace' function.
        "#cmakedefine HAVE__UNWIND_BACKTRACE ${HAVE__UNWIND_BACKTRACE}": "#define HAVE__UNWIND_BACKTRACE 1",

        # Have host's __alloca
        "#cmakedefine HAVE___ALLOCA ${HAVE___ALLOCA}": "/* #undef HAVE___ALLOCA */",

        # Have host's __ashldi3
        "#cmakedefine HAVE___ASHLDI3 ${HAVE___ASHLDI3}": "/* #undef HAVE___ASHLDI3 */",

        # Have host's __ashrdi3
        "#cmakedefine HAVE___ASHRDI3 ${HAVE___ASHRDI3}": "/* #undef HAVE___ASHRDI3 */",

        # Have host's __chkstk
        "#cmakedefine HAVE___CHKSTK ${HAVE___CHKSTK}": "/* #undef HAVE___CHKSTK */",

        # Have host's __chkstk_ms
        "#cmakedefine HAVE___CHKSTK_MS ${HAVE___CHKSTK_MS}": "/* #undef HAVE___CHKSTK_MS */",

        # Have host's __cmpdi2
        "#cmakedefine HAVE___CMPDI2 ${HAVE___CMPDI2}": "/* #undef HAVE___CMPDI2 */",

        # Have host's __divdi3
        "#cmakedefine HAVE___DIVDI3 ${HAVE___DIVDI3}": "/* #undef HAVE___DIVDI3 */",

        # Have host's __fixdfdi
        "#cmakedefine HAVE___FIXDFDI ${HAVE___FIXDFDI}": "/* #undef HAVE___FIXDFDI */",

        # Have host's __fixsfdi
        "#cmakedefine HAVE___FIXSFDI ${HAVE___FIXSFDI}": "/* #undef HAVE___FIXSFDI */",

        # Have host's __floatdidf
        "#cmakedefine HAVE___FLOATDIDF ${HAVE___FLOATDIDF}": "/* #undef HAVE___FLOATDIDF */",

        # Have host's __lshrdi3
        "#cmakedefine HAVE___LSHRDI3 ${HAVE___LSHRDI3}": "/* #undef HAVE___LSHRDI3 */",

        # Have host's __main
        "#cmakedefine HAVE___MAIN ${HAVE___MAIN}": "/* #undef HAVE___MAIN */",

        # Have host's __moddi3
        "#cmakedefine HAVE___MODDI3 ${HAVE___MODDI3}": "/* #undef HAVE___MODDI3 */",

        # Have host's __udivdi3
        "#cmakedefine HAVE___UDIVDI3 ${HAVE___UDIVDI3}": "/* #undef HAVE___UDIVDI3 */",

        # Have host's __umoddi3
        "#cmakedefine HAVE___UMODDI3 ${HAVE___UMODDI3}": "/* #undef HAVE___UMODDI3 */",

        # Have host's ___chkstk
        "#cmakedefine HAVE____CHKSTK ${HAVE____CHKSTK}": "/* #undef HAVE____CHKSTK */",

        # Have host's ___chkstk_ms
        "#cmakedefine HAVE____CHKSTK_MS ${HAVE____CHKSTK_MS}": "/* #undef HAVE____CHKSTK_MS */",

        # Linker version detected at compile time.
        "#cmakedefine HOST_LINK_VERSION \"${HOST_LINK_VERSION}\"": "/* #undef HOST_LINK_VERSION */",

        # Target triple LLVM will generate code for by default
        # Doesn't use `cmakedefine` because it is allowed to be empty.
        "#define LLVM_DEFAULT_TARGET_TRIPLE \"${LLVM_DEFAULT_TARGET_TRIPLE}\"": "#define LLVM_DEFAULT_TARGET_TRIPLE \"x86_64-unknown-linux-gnu\"",

        # Define if zlib compression is available
        # FIXME: Enable this by detecting the system library.
        "#cmakedefine01 LLVM_ENABLE_ZLIB": "/* #undef LLVM_ENABLE_ZLIB */",

        # Define if overriding target triple is enabled
        "#cmakedefine LLVM_TARGET_TRIPLE_ENV \"${LLVM_TARGET_TRIPLE_ENV}\"": "/* #undef LLVM_TARGET_TRIPLE_ENV */",

        # LLVM version information
        "#cmakedefine LLVM_VERSION_INFO \"${LLVM_VERSION_INFO}\"": "/* #undef LLVM_VERSION_INFO */",

        # Whether tools show host and target info when invoked with --version
        "#cmakedefine01 LLVM_VERSION_PRINTER_SHOW_HOST_TARGET_INFO": "#define LLVM_VERSION_PRINTER_SHOW_HOST_TARGET_INFO 1",

        # Define if libxml2 is supported on this platform.
        "#cmakedefine LLVM_LIBXML2_ENABLED ${LLVM_LIBXML2_ENABLED}": "/* #undef LLVM_LIBXML2_ENABLED */",

        # Define to the extension used for shared libraries, say, \".so\".
        "#cmakedefine LTDL_SHLIB_EXT \"${LTDL_SHLIB_EXT}\"": "#define LTDL_SHLIB_EXT \".so\"",

        # Define to the address where bug reports for this package should be sent.
        "#cmakedefine PACKAGE_BUGREPORT \"${PACKAGE_BUGREPORT}\"": "#define PACKAGE_BUGREPORT \"https://bugs.llvm.org/\"",

        # Define to the full name of this package.
        "#cmakedefine PACKAGE_NAME \"${PACKAGE_NAME}\"": "#define PACKAGE_NAME \"LLVM\"",

        # Define to the full name and version of this package.
        "#cmakedefine PACKAGE_STRING \"${PACKAGE_STRING}\"": "#define PACKAGE_STRING \"LLVM 11.0.0git\"",

        # Define to the version of this package.
        "#cmakedefine PACKAGE_VERSION \"${PACKAGE_VERSION}\"": "#define PACKAGE_VERSION \"11.0.0git\"",

        # Define to the vendor of this package.
        "#cmakedefine PACKAGE_VENDOR \"${PACKAGE_VENDOR}\"": "/* #undef PACKAGE_VENDOR */",

        # Define as the return type of signal handlers (`int' or `void').
        "#cmakedefine RETSIGTYPE ${RETSIGTYPE}": "#define RETSIGTYPE void",

        # Define if std::is_trivially_copyable is supported
        "#cmakedefine HAVE_STD_IS_TRIVIALLY_COPYABLE ${HAVE_STD_IS_TRIVIALLY_COPYABLE}": "#define HAVE_STD_IS_TRIVIALLY_COPYABLE 1",

        # Define to a function implementing stricmp
        "#cmakedefine stricmp ${stricmp}": "/* #undef stricmp */",

        # Define to a function implementing strdup
        "#cmakedefine strdup ${strdup}": "/* #undef strdup */",

        # Whether GlobalISel rule coverage is being collected
        "#cmakedefine01 LLVM_GISEL_COV_ENABLED": "#define LLVM_GISEL_COV_ENABLED 0",

        # Define if we have z3 and want to build it
        "#cmakedefine LLVM_WITH_Z3 ${LLVM_WITH_Z3}": "/* #undef LLVM_WITH_Z3 */",

        # Define to the default GlobalISel coverage file prefix
        "#cmakedefine LLVM_GISEL_COV_PREFIX \"${LLVM_GISEL_COV_PREFIX}\"": "/* #undef LLVM_GISEL_COV_PREFIX */",

        # Whether Timers signpost passes in Xcode Instruments
        "#cmakedefine01 LLVM_SUPPORT_XCODE_SIGNPOSTS": "#define LLVM_SUPPORT_XCODE_SIGNPOSTS 0",
    },
)

cc_library(
    name = "config",
    hdrs = [
        "include/llvm/Config/VersionInfo.h",
        "include/llvm/Config/abi-breaking.h",
        "include/llvm/Config/llvm-config.h",
    ],
    copts = llvm_copts,
    includes = ["include"],
    textual_hdrs = [
        "include/llvm/Config/Targets.def",
        "include/llvm/Config/AsmPrinters.def",
        "include/llvm/Config/AsmParsers.def",
        "include/llvm/Config/Disassemblers.def",
        # Needed for include scanner to find execinfo.h
        "include/llvm/Config/config.h",
    ],
)

cc_library(
    name = "Demangle",
    srcs = glob([
        "lib/Demangle/*.cpp",
        "lib/Demangle/*.h",
    ]),
    hdrs = glob(["include/llvm/Demangle/*.h"]),
    copts = llvm_copts,
    deps = [":config"],
)

genrule(
    name = "generate_vcs_revision",
    outs = ["include/llvm/Support/VCSRevision.h"],
    cmd = "echo '#define LLVM_REVISION \"git\"' >> $@\n" +
          "echo '#undef LLVM_REPOSITORY' >> $@\n",
)

genrule(
    name = "generate_static_extension_registry",
    outs = ["include/llvm/Support/Extension.def"],
    cmd = "echo -e '// extension handlers' >> $@\n" +
          "echo -e '#undef HANDLE_EXTENSION' >> $@\n",
)

cc_library(
    name = "Support",
    srcs = glob([
        "lib/Support/*.c",
        "lib/Support/*.cpp",
        "lib/Support/*.h",
        "lib/Support/*.inc",
        "lib/Support/Unix/*.h",
        "lib/Support/Unix/*.inc",
    ]),
    hdrs = glob([
        "include/llvm/Support/*.h",
        "include/llvm/ADT/*.h",
    ]) + [
        "include/llvm/Support/VCSRevision.h",
        "include/llvm/Support/Extension.def",
        "include/llvm-c/Core.h",
        "include/llvm-c/DataTypes.h",
        "include/llvm-c/DisassemblerTypes.h",
        "include/llvm-c/Error.h",
        "include/llvm-c/ExternC.h",
        "include/llvm-c/ErrorHandling.h",
        "include/llvm-c/Support.h",
        "include/llvm-c/Types.h",
    ],
    copts = llvm_copts,
    includes = ["include"],
    linkopts = [
        "-pthread",
    ],
    textual_hdrs = glob([
        "include/llvm/Support/*.def",
    ]),
    deps = [
        ":Demangle",
        ":config",
    ],
)

cc_library(
    name = "LineEditor",
    srcs = glob([
        "lib/LineEditor/*.cpp",
        "lib/LineEditor/*.h",
    ]),
    hdrs = glob(["include/llvm/LineEditor/*.h"]),
    copts = llvm_copts,
    deps = [
        ":Support",
        ":config",
    ],
)

cc_library(
    name = "Option",
    srcs = glob([
        "lib/Option/*.cpp",
        "lib/Option/*.h",
    ]),
    hdrs = glob(["include/llvm/Option/*.h"]),
    copts = llvm_copts,
    linkopts = ["-ldl"],
    deps = [
        ":Support",
        ":config",
    ],
)

cc_library(
    name = "TableGen",
    srcs = glob([
        "lib/TableGen/*.cpp",
        "lib/TableGen/*.h",
    ]),
    hdrs = glob(["include/llvm/TableGen/*.h"]),
    copts = llvm_copts,
    deps = [
        ":Support",
        ":config",
    ],
)

# This exists to avoid circular dependencies.
cc_library(
    name = "ir_headers",
    hdrs = glob(
        [
            "include/llvm/*.h",
            "include/llvm/IR/*.h",
        ],
        exclude = [
            "include/llvm/LinkAllPasses.h",
        ],
    ) + [
        "include/llvm/IR/Value.def",
        "include/llvm-c/Comdat.h",
        "include/llvm-c/DebugInfo.h",
    ],
    copts = llvm_copts,
)

cc_library(
    name = "BinaryFormat",
    srcs = glob([
        "lib/BinaryFormat/*.cpp",
        "lib/BinaryFormat/*.def",
        "lib/BinaryFormat/*.h",
    ]),
    hdrs = glob([
        "include/llvm/BinaryFormat/*.h",
    ]),
    copts = llvm_copts,
    includes = ["include"],
    textual_hdrs = glob([
        "include/llvm/BinaryFormat/*.def",
        "include/llvm/BinaryFormat/ELFRelocs/*.def",
    ]),
    deps = [
        ":Support",
    ],
)

cc_library(
    name = "DebugInfo",
    hdrs = glob(["include/llvm/DebugInfo/*.h"]),
    copts = llvm_copts,
    deps = [
        ":Object",
        ":Support",
    ],
)

cc_library(
    name = "DebugInfoMSF",
    srcs = glob([
        "lib/DebugInfo/MSF/*.cpp",
        "lib/DebugInfo/MSF/*.h",
    ]),
    hdrs = glob(["include/llvm/DebugInfo/MSF/*.h"]),
    copts = llvm_copts,
    deps = [":Support"],
)

cc_library(
    name = "DebugInfoCodeView",
    srcs = glob([
        "lib/DebugInfo/CodeView/*.cpp",
        "lib/DebugInfo/CodeView/*.h",
    ]),
    hdrs = glob([
        "include/llvm/DebugInfo/CodeView/*.h",
    ]),
    copts = llvm_copts,
    textual_hdrs = glob([
        "include/llvm/DebugInfo/CodeView/*.def",
    ]),
    deps = [
        ":BinaryFormat",
        ":DebugInfoMSF",
        ":Support",
    ],
)

cc_library(
    name = "DebugInfoPDB",
    srcs = glob([
        "lib/DebugInfo/PDB/*.cpp",
        "lib/DebugInfo/PDB/*.h",
        "lib/DebugInfo/PDB/Native/*.cpp",
        "lib/DebugInfo/PDB/Native/*.h",
    ]),
    hdrs = glob([
        "include/llvm/DebugInfo/PDB/*.h",
        "include/llvm/DebugInfo/PDB/Native/*.h",
    ]),
    copts = llvm_copts,
    deps = [
        ":BinaryFormat",
        ":DebugInfo",
        ":DebugInfoCodeView",
        ":DebugInfoMSF",
        ":Object",
        ":Support",
        ":config",
    ],
)

cc_library(
    name = "MC",
    srcs = glob([
        "lib/MC/*.cpp",
        "lib/MC/*.h",
    ]),
    hdrs = glob([
        "include/llvm/MC/*.h",
        "include/llvm/MC/*.def",
        "include/llvm/MC/*.inc",
    ]),
    copts = llvm_copts,
    deps = [
        ":BinaryFormat",
        ":DebugInfoCodeView",
        ":Support",
        ":config",
        ":ir_headers",
    ],
)

cc_library(
    name = "DebugInfoDWARF",
    srcs = glob([
        "lib/DebugInfo/DWARF/*.cpp",
        "lib/DebugInfo/DWARF/*.h",
    ]),
    hdrs = glob(["include/llvm/DebugInfo/DWARF/*.h"]),
    copts = llvm_copts,
    deps = [
        ":BinaryFormat",
        ":DebugInfo",
        ":MC",
        ":Object",
        ":Support",
    ],
)

cc_library(
    name = "Symbolize",
    srcs = glob([
        "lib/DebugInfo/Symbolize/*.cpp",
        "lib/DebugInfo/Symbolize/*.h",
    ]),
    hdrs = glob(["include/llvm/DebugInfo/Symbolize/*.h"]),
    copts = llvm_copts,
    deps = [
        ":BinaryFormat",
        ":DebugInfo",
        ":DebugInfoDWARF",
        ":DebugInfoPDB",
        ":Demangle",
        ":Object",
        ":Support",
    ],
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
    copts = llvm_copts,
    deps = [
        ":MC",
        ":Support",
        ":TableGen",
        ":config",
    ],
)

cc_binary(
    name = "llvm-tblgen",
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":tblgen",
    ],
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
    name = "intrinsics_impl_gen",
    tbl_outs = [("-gen-intrinsic-impl", "include/llvm/IR/IntrinsicImpl.inc")],
    tblgen = ":llvm-tblgen",
    td_file = "include/llvm/IR/Intrinsics.td",
    td_srcs = glob([
        "include/llvm/CodeGen/*.td",
        "include/llvm/IR/Intrinsics*.td",
    ]),
)

llvm_target_intrinsics_list = [
    {
        "name": "AArch64",
        "intrinsic_prefix": "aarch64",
    },
    {
        "name": "AMDGPU",
        "intrinsic_prefix": "amdgcn",
    },
    {
        "name": "ARM",
        "intrinsic_prefix": "arm",
    },
    {
        "name": "BPF",
        "intrinsic_prefix": "bpf",
    },
    {
        "name": "Hexagon",
        "intrinsic_prefix": "hexagon",
    },
    {
        "name": "Mips",
        "intrinsic_prefix": "mips",
    },
    {
        "name": "NVPTX",
        "intrinsic_prefix": "nvvm",
    },
    {
        "name": "PowerPC",
        "intrinsic_prefix": "ppc",
    },
    {
        "name": "R600",
        "intrinsic_prefix": "r600",
    },
    {
        "name": "RISCV",
        "intrinsic_prefix": "riscv",
    },
    {
        "name": "S390",
        "intrinsic_prefix": "s390",
    },
    {
        "name": "WebAssembly",
        "intrinsic_prefix": "wasm",
    },
    {
        "name": "X86",
        "intrinsic_prefix": "x86",
    },
    {
        "name": "XCore",
        "intrinsic_prefix": "xcore",
    },
]

[[
    gentbl(
        name = "intrinsic_" + target["name"] + "_gen",
        tbl_outs = [(
            "-gen-intrinsic-enums -intrinsic-prefix=" + target["intrinsic_prefix"],
            "include/llvm/IR/Intrinsics" + target["name"] + ".h",
        )],
        tblgen = ":llvm-tblgen",
        td_file = "include/llvm/IR/Intrinsics.td",
        td_srcs = glob([
            "include/llvm/CodeGen/*.td",
            "include/llvm/IR/*.td",
        ]),
    ),
] for target in llvm_target_intrinsics_list]

gentbl(
    name = "attributes_gen",
    tbl_outs = [("-gen-attrs", "include/llvm/IR/Attributes.inc")],
    tblgen = ":llvm-tblgen",
    td_file = "include/llvm/IR/Attributes.td",
    td_srcs = ["include/llvm/IR/Attributes.td"],
)

cc_library(
    name = "BitstreamReader",
    srcs = glob([
        "lib/Bitstream/Reader/*.cpp",
        "lib/Bitstream/Reader/*.h",
    ]),
    hdrs = [
        "include/llvm/Bitstream/BitCodes.h",
        "include/llvm/Bitstream/BitstreamReader.h",
    ],
    copts = llvm_copts,
    deps = [
        ":Support",
    ],
)

cc_library(
    name = "BitstreamWriter",
    srcs = glob([
        "lib/Bitstream/Writer/*.h",
    ]),
    hdrs = [
        "include/llvm/Bitstream/BitCodes.h",
        "include/llvm/Bitstream/BitstreamWriter.h",
    ],
    copts = llvm_copts,
    deps = [
        ":Support",
    ],
)

cc_library(
    name = "Remarks",
    srcs = glob(
        [
            "lib/Remarks/*.cpp",
            "lib/Remarks/*.h",
        ],
        exclude = ["lib/Remarks/RemarkLinker.cpp"],
    ),
    hdrs = glob(
        [
            "include/llvm/Remarks/*.h",
        ],
        exclude = ["include/llvm/Remarks/RemarkLinker.h"],
    ) + [
        "include/llvm-c/Remarks.h",
    ],
    copts = llvm_copts,
    deps = [
        ":BitstreamReader",
        ":BitstreamWriter",
        ":Support",
    ],
)

cc_library(
    name = "remark_linker",
    srcs = ["lib/Remarks/RemarkLinker.cpp"],
    hdrs = ["include/llvm/Remarks/RemarkLinker.h"],
    copts = llvm_copts,
    deps = [
        ":Object",
        ":Support",
    ],
)

cc_library(
    name = "Core",
    srcs = glob([
        "lib/IR/*.cpp",
        "lib/IR/*.h",
    ]),
    hdrs = glob(
        [
            "include/llvm/*.h",
            "include/llvm/IR/*.h",
        ],
        exclude = [
            "include/llvm/LinkAllPasses.h",
        ],
    ) + [
        "include/llvm-c/Comdat.h",
        "include/llvm-c/DebugInfo.h",
    ] + ["include/llvm/IR/Intrinsics" + target["name"] + ".h" for target in llvm_target_intrinsics_list],
    copts = llvm_copts,
    textual_hdrs = glob(["include/llvm/IR/*.def"]),
    deps = [
        ":BinaryFormat",
        ":Remarks",
        ":Support",
        ":attributes_gen",
        ":config",
        ":intrinsic_enums_gen",
        ":intrinsics_impl_gen",
    ],
)

cc_library(
    name = "BitReader",
    srcs = glob([
        "lib/Bitcode/Reader/*.cpp",
        "lib/Bitcode/Reader/*.h",
    ]),
    hdrs = [
        "include/llvm-c/BitReader.h",
        "include/llvm/Bitcode/BitcodeAnalyzer.h",
        "include/llvm/Bitcode/BitcodeCommon.h",
        "include/llvm/Bitcode/BitcodeReader.h",
        "include/llvm/Bitcode/LLVMBitCodes.h",
    ],
    copts = llvm_copts,
    deps = [
        ":BitstreamReader",
        ":Core",
        ":Support",
        ":config",
    ],
)

cc_library(
    name = "MCParser",
    srcs = glob([
        "lib/MC/MCParser/*.cpp",
        "lib/MC/MCParser/*.h",
    ]),
    hdrs = glob(["include/llvm/MC/MCParser/*.h"]),
    copts = llvm_copts,
    deps = [
        ":BinaryFormat",
        ":MC",
        ":Support",
        ":config",
    ],
)

cc_library(
    name = "TextAPI",
    srcs = glob([
        "lib/TextAPI/**/*.cpp",
    ]),
    hdrs = glob([
        "include/llvm/TextAPI/**/*.h",
        "include/llvm/TextAPI/**/*.def",
        "lib/TextAPI/MachO/*.h",
    ]),
    copts = llvm_copts,
    deps = [
        ":BinaryFormat",
        ":Support",
        ":config",
    ],
)

cc_library(
    name = "Object",
    srcs = glob([
        "lib/Object/*.cpp",
        "lib/Object/*.h",
    ]),
    hdrs = glob([
        "include/llvm/Object/*.h",
    ]) + [
        "include/llvm-c/Object.h",
    ],
    copts = llvm_copts,
    deps = [
        ":BinaryFormat",
        ":BitReader",
        ":Core",
        ":MC",
        ":MCParser",
        ":Support",
        ":TextAPI",
        ":config",
    ],
)

cc_library(
    name = "ObjectYAML",
    srcs = glob([
        "lib/ObjectYAML/*.cpp",
        "lib/ObjectYAML/*.h",
    ]),
    hdrs = glob(["include/llvm/ObjectYAML/*.h"]),
    copts = llvm_copts,
    deps = [
        ":BinaryFormat",
        ":DebugInfoCodeView",
        ":Object",
        ":Support",
    ],
)

cc_library(
    name = "ProfileData",
    srcs = glob([
        "lib/ProfileData/*.cpp",
        "lib/ProfileData/*.h",
    ]),
    hdrs = glob([
        "include/llvm/ProfileData/*.h",
        "include/llvm/ProfileData/*.inc",
    ]),
    copts = llvm_copts,
    deps = [
        ":Core",
        ":Support",
        ":config",
    ],
)

cc_library(
    name = "Coverage",
    srcs = glob([
        "lib/ProfileData/Coverage/*.cpp",
        "lib/ProfileData/Coverage/*.h",
    ]),
    hdrs = glob(["include/llvm/ProfileData/Coverage/*.h"]),
    copts = llvm_copts,
    deps = [
        ":Object",
        ":ProfileData",
        ":Support",
    ],
)

cc_library(
    name = "Analysis",
    srcs = glob(
        [
            "lib/Analysis/*.cpp",
            "lib/Analysis/*.h",
            "lib/Analysis/*.def",
        ],
        exclude = [
            # TODO: Add these files to the build.
            "lib/Analysis/MLInlineAdvisor.cpp",
            "lib/Analysis/ReleaseModeModelRunner.cpp",
            "lib/Analysis/TFUtils.cpp",
        ],
    ),
    hdrs = glob(
        [
            "include/llvm/Analysis/*.h",
            "include/llvm/Analysis/Utils/*.h",
        ],
        exclude = [
            # TODO: Add this file to the build.
            "include/llvm/Analysis/Utils/TFUtils.h",
        ],
    ) + [
        "include/llvm-c/Analysis.h",
        "include/llvm-c/Initialization.h",
    ],
    copts = llvm_copts,
    textual_hdrs = glob([
        "include/llvm/Analysis/*.def",
    ]),
    deps = [
        ":BinaryFormat",
        ":Core",
        ":Object",
        ":ProfileData",
        ":Support",
        ":config",
    ],
)

cc_library(
    name = "BitWriter",
    srcs = glob([
        "lib/Bitcode/Writer/*.cpp",
        "lib/Bitcode/Writer/*.h",
    ]),
    hdrs = [
        "include/llvm-c/BitWriter.h",
        "include/llvm/Bitcode/BitcodeCommon.h",
        "include/llvm/Bitcode/BitcodeWriter.h",
        "include/llvm/Bitcode/BitcodeWriterPass.h",
        "include/llvm/Bitcode/LLVMBitCodes.h",
    ],
    copts = llvm_copts,
    deps = [
        ":Analysis",
        ":BitstreamWriter",
        ":Core",
        ":MC",
        ":Object",
        ":Support",
        ":config",
    ],
)

cc_library(
    name = "Target",
    srcs = glob([
        "lib/Target/*.cpp",
        "lib/Target/*.h",
    ]),
    hdrs = glob([
        "include/llvm/Target/*.h",
    ]) + [
        "include/llvm-c/Target.h",
        "include/llvm-c/TargetMachine.h",
    ],
    copts = llvm_copts,
    deps = [
        ":Analysis",
        ":BinaryFormat",
        ":Core",
        ":MC",
        ":Support",
        ":config",
    ],
)

cc_library(
    name = "TransformUtils",
    srcs = glob([
        "lib/Transforms/Utils/*.cpp",
        "lib/Transforms/Utils/*.h",
    ]),
    hdrs = glob(["include/llvm/Transforms/Utils/*.h"]) + [
        "include/llvm/Transforms/Utils.h",
        "include/llvm-c/Transforms/Utils.h",
    ],
    copts = llvm_copts,
    deps = [
        ":Analysis",
        ":BinaryFormat",
        ":BitWriter",
        ":Core",
        ":Support",
        ":Target",
        ":config",
    ],
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
    ]) + [
        "include/llvm/TableGen/SearchableTable.td",
    ],
)

cc_library(
    name = "InstCombine",
    srcs = glob([
        "lib/Transforms/InstCombine/*.cpp",
        "lib/Transforms/InstCombine/*.h",
    ]),
    hdrs = glob(["include/llvm/Transforms/InstCombine/*.h"]) + [
        "include/llvm-c/Transforms/InstCombine.h",
    ],
    copts = llvm_copts,
    deps = [
        ":Analysis",
        ":Core",
        ":InstCombineTableGen",
        ":Support",
        ":Target",
        ":TransformUtils",
        ":config",
    ],
)

cc_library(
    name = "AggressiveInstCombine",
    srcs = glob([
        "lib/Transforms/AggressiveInstCombine/*.cpp",
        "lib/Transforms/AggressiveInstCombine/*.h",
    ]),
    hdrs = [
        "include/llvm-c/Transforms/AggressiveInstCombine.h",
        "include/llvm/Transforms/AggressiveInstCombine/AggressiveInstCombine.h",
    ],
    copts = llvm_copts,
    deps = [
        ":Analysis",
        ":Core",
        ":Support",
        ":TransformUtils",
    ],
)

cc_library(
    name = "Instrumentation",
    srcs = glob([
        "lib/Transforms/Instrumentation/*.cpp",
        "lib/Transforms/Instrumentation/*.h",
        "lib/Transforms/Instrumentation/*.inc",
    ]),
    hdrs = glob(["include/llvm/Transforms/Instrumentation/*.h"]) + [
        "include/llvm/Transforms/Instrumentation.h",
    ],
    copts = llvm_copts,
    deps = [
        ":Analysis",
        ":BinaryFormat",
        ":Core",
        ":MC",
        ":ProfileData",
        ":Support",
        ":TransformUtils",
        ":config",
    ],
)

cc_library(
    name = "ObjCARC",
    srcs = glob([
        "lib/Transforms/ObjCARC/*.cpp",
        "lib/Transforms/ObjCARC/*.h",
    ]),
    hdrs = ["include/llvm/Transforms/ObjCARC.h"],
    copts = llvm_copts,
    deps = [
        ":Analysis",
        ":Core",
        ":Support",
        ":Target",
        ":TransformUtils",
        ":config",
    ],
)

cc_library(
    name = "Scalar",
    srcs = glob([
        "lib/Transforms/Scalar/*.cpp",
        "lib/Transforms/Scalar/*.h",
    ]),
    hdrs = glob(["include/llvm/Transforms/Scalar/*.h"]) + [
        "include/llvm-c/Transforms/Scalar.h",
        "include/llvm/Transforms/Scalar.h",
    ],
    copts = llvm_copts,
    deps = [
        ":AggressiveInstCombine",
        ":Analysis",
        ":Core",
        ":InstCombine",
        ":ProfileData",
        ":Support",
        ":Target",
        ":TransformUtils",
        ":config",
    ],
)

cc_library(
    name = "Vectorize",
    srcs = glob([
        "lib/Transforms/Vectorize/*.cpp",
        "lib/Transforms/Vectorize/*.h",
    ]),
    hdrs = glob([
        "include/llvm/Transforms/Vectorize/*.h",
    ]) + [
        "include/llvm-c/Transforms/Vectorize.h",
        "include/llvm/Transforms/Vectorize.h",
    ],
    copts = llvm_copts,
    deps = [
        ":Analysis",
        ":Core",
        ":Support",
        ":Target",
        ":TransformUtils",
        ":config",
    ],
)

filegroup(
    name = "omp_td_files",
    srcs = glob([
        "include/llvm/Frontend/OpenMP/*.td",
        "include/llvm/Frontend/Directive/*.td",
    ]),
)

gentbl(
    name = "omp_gen",
    library = False,
    tbl_outs = [("--gen-directive-decl", "include/llvm/Frontend/OpenMP/OMP.h.inc")],
    tblgen = ":llvm-tblgen",
    td_file = "include/llvm/Frontend/OpenMP/OMP.td",
    td_srcs = [":omp_td_files"],
)

gentbl(
    name = "omp_gen_impl",
    library = False,
    tbl_outs = [
        ("--gen-directive-gen", "include/llvm/Frontend/OpenMP/OMP.cpp.inc"),
        ("--gen-directive-impl", "lib/Frontend/OpenMP/OMP.cpp"),
    ],
    tblgen = ":llvm-tblgen",
    td_file = "include/llvm/Frontend/OpenMP/OMP.td",
    td_srcs = [":omp_td_files"],
)

cc_library(
    name = "FrontendOpenMP",
    srcs = glob([
        "lib/Frontend/OpenMP/*.cpp",
    ]) + [
        "include/llvm/Frontend/OpenMP/OMP.cpp.inc",
        "lib/Frontend/OpenMP/OMP.cpp",
    ],
    hdrs = glob([
        "include/llvm/Frontend/OpenMP/*.h",
        "include/llvm/Frontend/OpenMP/OMP/*.h",
        "include/llvm/Frontend/*.h",
    ]) + ["include/llvm/Frontend/OpenMP/OMP.h.inc"],
    copts = llvm_copts,
    textual_hdrs = glob([
        "include/llvm/Frontend/OpenMP/*.def",
    ]),
    deps = [
        ":Analysis",
        ":Core",
        ":Support",
        ":TransformUtils",
    ],
)

cc_library(
    name = "AsmParser",
    srcs = glob([
        "lib/AsmParser/*.cpp",
        "lib/AsmParser/*.h",
    ]),
    hdrs = [
        "include/llvm/AsmParser/Parser.h",
        "include/llvm/AsmParser/SlotMapping.h",
    ],
    copts = llvm_copts,
    deps = [
        ":BinaryFormat",
        ":Core",
        ":Support",
    ],
)

cc_library(
    name = "IRReader",
    srcs = glob([
        "lib/IRReader/*.cpp",
        "lib/IRReader/*.h",
    ]),
    hdrs = glob([
        "include/llvm/IRReader/*.h",
    ]) + [
        "include/llvm-c/IRReader.h",
    ],
    copts = llvm_copts,
    deps = [
        ":AsmParser",
        ":BitReader",
        ":Core",
        ":Support",
        ":config",
    ],
)

cc_library(
    name = "Linker",
    srcs = glob([
        "lib/Linker/*.cpp",
        "lib/Linker/*.h",
    ]),
    hdrs = glob([
        "include/llvm/Linker/*.h",
    ]) + [
        "include/llvm-c/Linker.h",
    ],
    copts = llvm_copts,
    deps = [
        ":Core",
        ":Support",
        ":TransformUtils",
        ":config",
    ],
)

cc_library(
    name = "IPO",
    srcs = glob([
        "lib/Transforms/IPO/*.cpp",
        "lib/Transforms/IPO/*.h",
    ]),
    hdrs = glob([
        "include/llvm/Transforms/IPO/*.h",
    ]) + [
        "include/llvm-c/Transforms/IPO.h",
        "include/llvm-c/Transforms/PassManagerBuilder.h",
        "include/llvm/Transforms/IPO.h",
    ],
    copts = llvm_copts,
    deps = [
        ":AggressiveInstCombine",
        ":Analysis",
        ":BinaryFormat",
        ":BitReader",
        ":BitWriter",
        ":Core",
        ":FrontendOpenMP",
        ":IRReader",
        ":InstCombine",
        ":Instrumentation",
        ":Linker",
        ":ObjCARC",
        ":Object",
        ":ProfileData",
        ":Scalar",
        ":Support",
        ":Target",
        ":TransformUtils",
        ":Vectorize",
        ":config",
    ],
)

cc_library(
    name = "CFGuard",
    srcs = glob([
        "lib/Transforms/CFGuard/*.cpp",
        "lib/Transforms/CFGuard/*.h",
    ]),
    hdrs = ["include/llvm/Transforms/CFGuard.h"],
    copts = llvm_copts,
    deps = [
        ":Core",
        ":Support",
        ":config",
    ],
)

cc_library(
    name = "Coroutines",
    srcs = glob([
        "lib/Transforms/Coroutines/*.cpp",
        "lib/Transforms/Coroutines/*.h",
    ]),
    hdrs = [
        "include/llvm-c/Transforms/Coroutines.h",
        "include/llvm/Transforms/Coroutines.h",
        "include/llvm/Transforms/Coroutines/CoroCleanup.h",
        "include/llvm/Transforms/Coroutines/CoroEarly.h",
        "include/llvm/Transforms/Coroutines/CoroElide.h",
        "include/llvm/Transforms/Coroutines/CoroSplit.h",
    ],
    copts = llvm_copts,
    deps = [
        ":Analysis",
        ":Core",
        ":IPO",
        ":Scalar",
        ":Support",
        ":TransformUtils",
        ":config",
    ],
)

# Meta-target for clients which depend on all of the transforms libraries.
cc_library(
    name = "common_transforms",
    deps = [
        ":AggressiveInstCombine",
        ":CFGuard",
        ":Coroutines",
        ":IPO",
        ":InstCombine",
        ":Instrumentation",
        ":ObjCARC",
        ":Scalar",
        ":Vectorize",
    ],
)

cc_library(
    name = "asm_printer_defs",
    copts = llvm_copts,
    textual_hdrs = glob(["lib/CodeGen/AsmPrinter/*.def"]),
)

cc_library(
    name = "CodeGen",
    srcs = glob(
        [
            "lib/CodeGen/**/*.cpp",
            "lib/CodeGen/**/*.h",
            "lib/CodeGen/SelectionDAG/*.cpp",
            "lib/CodeGen/SelectionDAG/*.h",
        ],
    ),
    hdrs = [
        "include/llvm/LinkAllPasses.h",
    ] + glob(
        [
            "include/llvm/CodeGen/**/*.h",
        ],
    ),
    copts = llvm_copts,
    textual_hdrs = glob([
        "include/llvm/CodeGen/**/*.def",
        "include/llvm/CodeGen/**/*.inc",
    ]),
    deps = [
        ":Analysis",
        ":AsmParser",
        ":BinaryFormat",
        ":BitReader",
        ":BitWriter",
        ":Core",
        ":DebugInfoCodeView",
        ":DebugInfoDWARF",
        ":IPO",
        ":MC",
        ":MCParser",
        ":ProfileData",
        ":Remarks",
        ":Scalar",
        ":Support",
        ":Target",
        ":TransformUtils",
        ":asm_printer_defs",
        ":config",
    ],
)

cc_library(
    name = "MCDisassembler",
    srcs = glob([
        "lib/MC/MCDisassembler/*.cpp",
        "lib/MC/MCDisassembler/*.h",
    ]),
    hdrs = glob([
        "include/llvm/MC/MCDisassembler/*.h",
    ]) + [
        "include/llvm-c/Disassembler.h",
    ],
    copts = llvm_copts,
    deps = [
        ":MC",
        ":Support",
        ":config",
    ],
)

llvm_target_list = [
    {
        "name": "AArch64",
        "short_name": "AArch64",
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
        "name": "ARM",
        "short_name": "ARM",
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
        "name": "AMDGPU",
        "short_name": "AMDGPU",
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
            ":r600_target_gen",
        ],
    },
    {
        "name": "BPF",
        "short_name": "BPF",
        "tbl_outs": [
            ("-gen-asm-writer", "lib/Target/BPF/BPFGenAsmWriter.inc"),
            ("-gen-asm-matcher", "lib/Target/BPF/BPFGenAsmMatcher.inc"),
            ("-gen-callingconv", "lib/Target/BPF/BPFGenCallingConv.inc"),
            ("-gen-dag-isel", "lib/Target/BPF/BPFGenDAGISel.inc"),
            ("-gen-disassembler", "lib/Target/BPF/BPFGenDisassemblerTables.inc"),
            ("-gen-emitter", "lib/Target/BPF/BPFGenMCCodeEmitter.inc"),
            ("-gen-instr-info", "lib/Target/BPF/BPFGenInstrInfo.inc"),
            ("-gen-register-info", "lib/Target/BPF/BPFGenRegisterInfo.inc"),
            ("-gen-subtarget", "lib/Target/BPF/BPFGenSubtargetInfo.inc"),
        ],
    },
    {
        "name": "Hexagon",
        "short_name": "Hexagon",
        "tbl_outs": [
            ("-gen-asm-matcher", "lib/Target/Hexagon/HexagonGenAsmMatcher.inc"),
            ("-gen-asm-writer", "lib/Target/Hexagon/HexagonGenAsmWriter.inc"),
            ("-gen-callingconv", "lib/Target/Hexagon/HexagonGenCallingConv.inc"),
            ("-gen-dag-isel", "lib/Target/Hexagon/HexagonGenDAGISel.inc"),
            ("-gen-dfa-packetizer", "lib/Target/Hexagon/HexagonGenDFAPacketizer.inc"),
            ("-gen-disassembler", "lib/Target/Hexagon/HexagonGenDisassemblerTables.inc"),
            ("-gen-instr-info", "lib/Target/Hexagon/HexagonGenInstrInfo.inc"),
            ("-gen-emitter", "lib/Target/Hexagon/HexagonGenMCCodeEmitter.inc"),
            ("-gen-register-info", "lib/Target/Hexagon/HexagonGenRegisterInfo.inc"),
            ("-gen-subtarget", "lib/Target/Hexagon/HexagonGenSubtargetInfo.inc"),
        ],
    },
    {
        "name": "Lanai",
        "short_name": "Lanai",
        "tbl_outs": [
            ("-gen-asm-matcher", "lib/Target/Lanai/LanaiGenAsmMatcher.inc"),
            ("-gen-asm-writer", "lib/Target/Lanai/LanaiGenAsmWriter.inc"),
            ("-gen-callingconv", "lib/Target/Lanai/LanaiGenCallingConv.inc"),
            ("-gen-dag-isel", "lib/Target/Lanai/LanaiGenDAGISel.inc"),
            ("-gen-disassembler", "lib/Target/Lanai/LanaiGenDisassemblerTables.inc"),
            ("-gen-emitter", "lib/Target/Lanai/LanaiGenMCCodeEmitter.inc"),
            ("-gen-instr-info", "lib/Target/Lanai/LanaiGenInstrInfo.inc"),
            ("-gen-register-info", "lib/Target/Lanai/LanaiGenRegisterInfo.inc"),
            ("-gen-subtarget", "lib/Target/Lanai/LanaiGenSubtargetInfo.inc"),
        ],
    },
    {
        "name": "NVPTX",
        "short_name": "NVPTX",
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
        "short_name": "PPC",
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
        "name": "Sparc",
        "short_name": "Sparc",
        "tbl_outs": [
            ("-gen-asm-writer", "lib/Target/Sparc/SparcGenAsmWriter.inc"),
            ("-gen-asm-matcher", "lib/Target/Sparc/SparcGenAsmMatcher.inc"),
            ("-gen-emitter", "lib/Target/Sparc/SparcGenMCCodeEmitter.inc"),
            ("-gen-register-info", "lib/Target/Sparc/SparcGenRegisterInfo.inc"),
            ("-gen-instr-info", "lib/Target/Sparc/SparcGenInstrInfo.inc"),
            ("-gen-dag-isel", "lib/Target/Sparc/SparcGenDAGISel.inc"),
            ("-gen-callingconv", "lib/Target/Sparc/SparcGenCallingConv.inc"),
            ("-gen-subtarget", "lib/Target/Sparc/SparcGenSubtargetInfo.inc"),
            ("-gen-disassembler", "lib/Target/Sparc/SparcGenDisassemblerTables.inc"),
        ],
    },
    {
        "name": "RISCV",
        "short_name": "RISCV",
        "tbl_outs": [
            ("-gen-asm-matcher", "lib/Target/RISCV/RISCVGenAsmMatcher.inc"),
            ("-gen-asm-writer", "lib/Target/RISCV/RISCVGenAsmWriter.inc"),
            ("-gen-compress-inst-emitter", "lib/Target/RISCV/RISCVGenCompressInstEmitter.inc"),
            ("-gen-dag-isel", "lib/Target/RISCV/RISCVGenDAGISel.inc"),
            ("-gen-disassembler", "lib/Target/RISCV/RISCVGenDisassemblerTables.inc"),
            ("-gen-global-isel", "lib/Target/RISCV/RISCVGenGlobalISel.inc"),
            ("-gen-instr-info", "lib/Target/RISCV/RISCVGenInstrInfo.inc"),
            ("-gen-emitter", "lib/Target/RISCV/RISCVGenMCCodeEmitter.inc"),
            ("-gen-pseudo-lowering", "lib/Target/RISCV/RISCVGenMCPseudoLowering.inc"),
            ("-gen-register-bank", "lib/Target/RISCV/RISCVGenRegisterBank.inc"),
            ("-gen-register-info", "lib/Target/RISCV/RISCVGenRegisterInfo.inc"),
            ("-gen-subtarget", "lib/Target/RISCV/RISCVGenSubtargetInfo.inc"),
            ("-gen-searchable-tables", "lib/Target/RISCV/RISCVGenSystemOperands.inc"),
        ],
    },
    {
        "name": "WebAssembly",
        "short_name": "WebAssembly",
        "tbl_outs": [
            ("-gen-disassembler", "lib/Target/WebAssembly/WebAssemblyGenDisassemblerTables.inc"),
            ("-gen-asm-writer", "lib/Target/WebAssembly/WebAssemblyGenAsmWriter.inc"),
            ("-gen-instr-info", "lib/Target/WebAssembly/WebAssemblyGenInstrInfo.inc"),
            ("-gen-dag-isel", "lib/Target/WebAssembly/WebAssemblyGenDAGISel.inc"),
            ("-gen-fast-isel", "lib/Target/WebAssembly/WebAssemblyGenFastISel.inc"),
            ("-gen-emitter", "lib/Target/WebAssembly/WebAssemblyGenMCCodeEmitter.inc"),
            ("-gen-register-info", "lib/Target/WebAssembly/WebAssemblyGenRegisterInfo.inc"),
            ("-gen-subtarget", "lib/Target/WebAssembly/WebAssemblyGenSubtargetInfo.inc"),
            ("-gen-asm-matcher", "lib/Target/WebAssembly/WebAssemblyGenAsmMatcher.inc"),
        ],
    },
    {
        "name": "X86",
        "short_name": "X86",
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

cc_library(
    name = "x86_target_layering_problem_hdrs",
    textual_hdrs = ["lib/Target/X86/X86InstrInfo.h"],
)

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

[[
    [gentbl(
        name = target["name"] + "CommonTableGen",
        tbl_outs = target["tbl_outs"],
        tblgen = ":llvm-tblgen",
        td_file = "lib/Target/" + target["name"] + "/" + target["short_name"] + ".td",
        td_srcs = [
            ":common_target_td_sources",
        ] + glob([
            "lib/Target/" + target["name"] + "/*.td",
        ]),
        deps = target.get("tbl_deps", []),
    )],
    [cc_library(
        name = target["name"] + "Info",
        srcs = ["lib/Target/" + target["name"] + "/TargetInfo/" + target["name"] + "TargetInfo.cpp"],
        hdrs = glob(["lib/Target/" + target["name"] + "/TargetInfo/*.h"]),
        copts = llvm_copts,
        deps = [
            ":" + target["name"] + "CommonTableGen",
            ":Support",
            ":Target",
        ],
    )],
    # We cannot separate the `Utils` and `MCTargetDesc` sublibraries of
    # a number of targets due to criss crossing inclusion of headers.
    [cc_library(
        name = target["name"] + "UtilsAndDesc",
        srcs = glob([
            "lib/Target/" + target["name"] + "/MCTargetDesc/*.cpp",
            "lib/Target/" + target["name"] + "/Utils/*.cpp",
            "lib/Target/" + target["name"] + "/*.h",
        ]),
        hdrs = glob([
            "lib/Target/" + target["name"] + "/MCTargetDesc/*.h",
            "lib/Target/" + target["name"] + "/Utils/*.h",
        ]),
        copts = llvm_copts,
        textual_hdrs = glob([
            "lib/Target/" + target["name"] + "/*.def",
            "lib/Target/" + target["name"] + "/*.inc",
        ]),
        deps = [
            ":BinaryFormat",
            # Depending on `:CodeGen` headers in this library is almost
            # certainly a layering problem in numerous targets.
            ":CodeGen",
            ":DebugInfoCodeView",
            ":MC",
            ":MCDisassembler",
            ":Support",
            ":Target",
            ":config",
            ":" + target["name"] + "CommonTableGen",
            ":" + target["name"] + "Info",
        ],
    )],
    [cc_library(
        name = target["name"] + "CodeGen",
        srcs = glob([
            "lib/Target/" + target["name"] + "/GISel/*.cpp",
            "lib/Target/" + target["name"] + "/GISel/*.h",
            "lib/Target/" + target["name"] + "/*.cpp",
            "lib/Target/" + target["name"] + "/*.h",
        ]),
        hdrs = ["lib/Target/" + target["name"] + "/" + target["short_name"] + ".h"],
        copts = llvm_copts,
        textual_hdrs = glob([
            "lib/Target/" + target["name"] + "/*.def",
            "lib/Target/" + target["name"] + "/*.inc",
        ]),
        deps = [
            ":Analysis",
            ":BinaryFormat",
            ":CFGuard",
            ":CodeGen",
            ":Core",
            ":IPO",
            ":MC",
            ":ProfileData",
            ":Scalar",
            ":Support",
            ":Target",
            ":TransformUtils",
            ":Vectorize",
            ":config",
            ":" + target["name"] + "CommonTableGen",
            ":" + target["name"] + "Info",
            ":" + target["name"] + "UtilsAndDesc",
        ],
    )],
    [cc_library(
        name = target["name"] + "AsmParser",
        srcs = glob([
            "lib/Target/" + target["name"] + "/AsmParser/*.cpp",
            "lib/Target/" + target["name"] + "/AsmParser/*.h",
        ]),
        copts = llvm_copts,
        deps = [
            ":BinaryFormat",
            ":MC",
            ":MCParser",
            ":Support",
            ":Target",
            ":" + target["name"] + "CodeGen",
            ":" + target["name"] + "CommonTableGen",
            ":" + target["name"] + "UtilsAndDesc",
        ],
    )],
    [cc_library(
        name = target["name"] + "Disassembler",
        srcs = glob([
            "lib/Target/" + target["name"] + "/Disassembler/*.cpp",
            "lib/Target/" + target["name"] + "/Disassembler/*.c",
            "lib/Target/" + target["name"] + "/Disassembler/*.h",
        ]),
        copts = llvm_copts,
        deps = [
            ":CodeGen",
            ":Core",
            ":MC",
            ":MCDisassembler",
            ":Support",
            ":Target",
            ":" + target["name"] + "CodeGen",
            ":" + target["name"] + "CommonTableGen",
            ":" + target["name"] + "UtilsAndDesc",
        ],
    )],
] for target in llvm_target_list]

cc_library(
    name = "AllTargetsCodeGens",
    copts = llvm_copts,
    deps = [
        target["name"] + "CodeGen"
        for target in llvm_target_list
    ],
)

cc_library(
    name = "AllTargetsAsmParsers",
    copts = llvm_copts,
    deps = [
        target["name"] + "AsmParser"
        for target in llvm_target_list
    ],
)

cc_library(
    name = "AllTargetsDisassemblers",
    copts = llvm_copts,
    deps = [
        target["name"] + "Disassembler"
        for target in llvm_target_list
    ],
)

cc_library(
    name = "pass_registry_def",
    copts = llvm_copts,
    textual_hdrs = ["lib/Passes/PassRegistry.def"],
)

cc_library(
    name = "MLPolicies",
    srcs = glob([
        "lib/Analysis/ML/*.cpp",
        "lib/Analysis/ML/*.h",
    ]),
    hdrs = glob([
        "include/llvm/Analysis/ML/*.h",
    ]),
    copts = llvm_copts,
    deps = [
        ":Analysis",
        ":Core",
        ":Support",
    ],
)

cc_library(
    name = "Passes",
    srcs = glob([
        "lib/Passes/*.cpp",
        "lib/Passes/*.h",
    ]),
    hdrs = glob(["include/llvm/Passes/*.h"]),
    copts = llvm_copts,
    deps = [
        ":Analysis",
        ":CodeGen",
        ":Core",
        ":Coroutines",
        ":MLPolicies",
        ":Support",
        ":Target",
        ":TransformUtils",
        ":common_transforms",
        ":config",
        ":pass_registry_def",
    ],
)

cc_library(
    name = "LTO",
    srcs = glob([
        "lib/LTO/*.cpp",
        "lib/LTO/*.h",
    ]),
    hdrs = glob([
        "include/llvm/LTO/*.h",
        "include/llvm/LTO/legacy/*.h",
    ]) + [
        "include/llvm-c/LinkTimeOptimizer.h",
        "include/llvm-c/lto.h",
    ],
    copts = llvm_copts,
    deps = [
        ":Analysis",
        ":BitReader",
        ":BitWriter",
        ":CodeGen",
        ":Core",
        ":IRReader",
        ":Linker",
        ":MC",
        ":MCParser",
        ":Object",
        ":Passes",
        ":Support",
        ":Target",
        ":TransformUtils",
        ":common_transforms",
        ":config",
    ],
)

cc_library(
    name = "ExecutionEngine",
    srcs = glob([
        "lib/ExecutionEngine/*.cpp",
        "lib/ExecutionEngine/*.h",
        "lib/ExecutionEngine/RuntimeDyld/*.cpp",
        "lib/ExecutionEngine/RuntimeDyld/*.h",
        "lib/ExecutionEngine/RuntimeDyld/Targets/*.cpp",
        "lib/ExecutionEngine/RuntimeDyld/Targets/*.h",
    ]),
    hdrs = glob(
        [
            "include/llvm/ExecutionEngine/*.h",
        ],
        exclude = [
            "include/llvm/ExecutionEngine/MCJIT*.h",
            "include/llvm/ExecutionEngine/OProfileWrapper.h",
        ],
    ) + [
        "include/llvm-c/ExecutionEngine.h",
    ],
    copts = llvm_copts,
    deps = [
        ":BinaryFormat",
        ":CodeGen",
        ":Core",
        ":DebugInfo",
        ":MC",
        ":MCDisassembler",
        ":Object",
        ":Passes",
        ":Support",
        ":Target",
        ":config",
    ],
)

cc_library(
    name = "Interpreter",
    srcs = glob([
        "lib/ExecutionEngine/Interpreter/*.cpp",
        "lib/ExecutionEngine/Interpreter/*.h",
    ]),
    hdrs = ["include/llvm/ExecutionEngine/Interpreter.h"],
    copts = llvm_copts,
    deps = [
        ":CodeGen",
        ":Core",
        ":ExecutionEngine",
        ":Support",
        ":Target",
        ":config",
    ],
)

cc_library(
    name = "JITLink",
    srcs = glob([
        "lib/ExecutionEngine/JITLink/*.cpp",
        "lib/ExecutionEngine/JITLink/*.h",
    ]),
    hdrs = glob([
        "include/llvm/ExecutionEngine/JITLink/*.h",
    ]),
    copts = llvm_copts,
    deps = [
        ":ExecutionEngine",
        ":Object",
        ":Support",
        ":config",
    ],
)

cc_library(
    name = "MCJIT",
    srcs = glob([
        "lib/ExecutionEngine/MCJIT/*.cpp",
        "lib/ExecutionEngine/MCJIT/*.h",
    ]),
    hdrs = glob(["include/llvm/ExecutionEngine/MCJIT*.h"]),
    copts = llvm_copts,
    deps = [
        ":CodeGen",
        ":Core",
        ":ExecutionEngine",
        ":MC",
        ":Object",
        ":Support",
        ":Target",
        ":config",
    ],
)

cc_library(
    name = "OrcJIT",
    srcs = glob([
        "lib/ExecutionEngine/Orc/*.cpp",
        "lib/ExecutionEngine/Orc/*.h",
        "lib/ExecutionEngine/Orc/RPC/*.cpp",
        "lib/ExecutionEngine/OrcError/*.cpp",
    ]),
    hdrs = glob([
        "include/llvm/ExecutionEngine/Orc/*.h",
        "include/llvm/ExecutionEngine/Orc/RPC/*.h",
    ]) + [
        "include/llvm-c/Orc.h",
        "include/llvm-c/OrcBindings.h",
    ],
    copts = llvm_copts,
    deps = [
        ":BitReader",
        ":BitWriter",
        ":Core",
        ":ExecutionEngine",
        ":JITLink",
        ":MC",
        ":Object",
        ":Support",
        ":Target",
        ":TransformUtils",
        ":config",
    ],
)

cc_library(
    name = "DWARFLinker",
    srcs = glob([
        "lib/DWARFLinker/*.cpp",
        "lib/DWARFLinker/*.h",
    ]),
    hdrs = glob(["include/llvm/DWARFLinker/*.h"]),
    copts = llvm_copts,
    deps = [
        ":CodeGen",
        ":DebugInfoDWARF",
        ":Support",
    ],
)

gentbl(
    name = "DllOptionsTableGen",
    tbl_outs = [(
        "-gen-opt-parser-defs",
        "lib/ToolDrivers/llvm-dlltool/Options.inc",
    )],
    tblgen = ":llvm-tblgen",
    td_file = "lib/ToolDrivers/llvm-dlltool/Options.td",
    td_srcs = ["include/llvm/Option/OptParser.td"],
)

cc_library(
    name = "DlltoolDriver",
    srcs = glob(["lib/ToolDrivers/llvm-dlltool/*.cpp"]),
    hdrs = glob(["include/llvm/ToolDrivers/llvm-dlltool/*.h"]),
    copts = llvm_copts,
    deps = [
        ":DllOptionsTableGen",
        ":Object",
        ":Option",
        ":Support",
    ],
)

gentbl(
    name = "LibOptionsTableGen",
    tbl_outs = [(
        "-gen-opt-parser-defs",
        "lib/ToolDrivers/llvm-lib/Options.inc",
    )],
    tblgen = ":llvm-tblgen",
    td_file = "lib/ToolDrivers/llvm-lib/Options.td",
    td_srcs = ["include/llvm/Option/OptParser.td"],
)

cc_library(
    name = "LibDriver",
    srcs = glob(["lib/ToolDrivers/llvm-lib/*.cpp"]),
    hdrs = glob(["include/llvm/ToolDrivers/llvm-lib/*.h"]),
    copts = llvm_copts,
    deps = [
        ":BinaryFormat",
        ":LibOptionsTableGen",
        ":Object",
        ":Option",
        ":Support",
    ],
)

cc_library(
    name = "InterfaceStub",
    srcs = glob([
        "lib/InterfaceStub/*.cpp",
        "lib/InterfaceStub/*.h",
    ]),
    hdrs = glob([
        "include/llvm/InterfaceStub/*.h",
    ]),
    copts = llvm_copts,
    deps = [
        ":Object",
        ":Support",
        ":config",
    ],
)

cc_library(
    name = "WindowsManifest",
    srcs = glob([
        "lib/WindowsManifest/*.cpp",
    ]),
    hdrs = glob([
        "include/llvm/WindowsManifest/*.h",
    ]),
    copts = llvm_copts,
    linkopts = [
        # Libxml2 is required to process Windows manifests. Without this,
        # lld uses Microsoft mt.exe instead, which is not cross-platform.
        "-lxml2",
    ],
    deps = [
        ":Support",
        ":config",
    ],
)

cc_library(
    name = "MCA",
    srcs = glob([
        "lib/MCA/**/*.cpp",
        "lib/MCA/**/*.h",
    ]),
    hdrs = glob([
        "include/llvm/MCA/**/*.h",
    ]),
    copts = llvm_copts,
    deps = [
        ":MC",
        ":MCDisassembler",
        ":Object",
        ":Support",
    ],
)

cc_library(
    name = "XRay",
    srcs = glob([
        "lib/XRay/*.cpp",
        "lib/XRay/*.h",
    ]),
    hdrs = glob(["include/llvm/XRay/*.h"]),
    copts = llvm_copts,
    deps = [
        ":Object",
        ":Support",
    ],
)

# FIXME: Add support for fetching and building libpfm4 and uncomment this.
#cc_library(
#    name = "llvm-exegesis-lib",
#    srcs = glob([
#        "tools/llvm-exegesis/lib/*.cpp",
#        "tools/llvm-exegesis/lib/X86/*.cpp",
#        "tools/llvm-exegesis/lib/X86/*.h",
#    ]),
#    hdrs = glob(["tools/llvm-exegesis/lib/*.h"]),
#    copts = llvm_copts + ["-DHAVE_LIBPFM=1"],
#    defines = ["LLVM_EXEGESIS_INITIALIZE_NATIVE_TARGET=InitializeX86ExegesisTarget"],
#    deps = [
#        ":AllTargetsAsmParsers",
#        ":AllTargetsCodeGens",
#        ":CodeGen",
#        ":Core",
#        ":ExecutionEngine",
#        ":MC",
#        ":MCDisassembler",
#        ":MCJIT",
#        ":Object",
#        ":ObjectYAML",
#        ":Support",
#        ":Target",
#        ":config",
#    ],
#)

################################################################################
# LLVM toolchain and development binaries

gentbl(
    name = "DsymutilTableGen",
    tbl_outs = [(
        "-gen-opt-parser-defs",
        "tools/dsymutil/Options.inc",
    )],
    tblgen = ":llvm-tblgen",
    td_file = "tools/dsymutil/Options.td",
    td_srcs = ["include/llvm/Option/OptParser.td"],
)

cc_binary(
    name = "dsymutil",
    srcs = glob([
        "tools/dsymutil/*.cpp",
        "tools/dsymutil/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AllTargetsCodeGens",
        ":BinaryFormat",
        ":CodeGen",
        ":DWARFLinker",
        ":DebugInfo",
        ":DebugInfoDWARF",
        ":DsymutilTableGen",
        ":MC",
        ":Object",
        ":Option",
        ":Support",
        ":Target",
        ":config",
        ":remark_linker",
    ],
)

cc_binary(
    name = "llc",
    srcs = glob([
        "tools/llc/*.cpp",
        "tools/llc/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AllTargetsAsmParsers",
        ":AllTargetsCodeGens",
        ":Analysis",
        ":AsmParser",
        ":BitReader",
        ":CodeGen",
        ":Core",
        ":IRReader",
        ":MC",
        ":Support",
        ":Target",
        ":TransformUtils",
    ],
)

cc_binary(
    name = "lli",
    srcs = glob([
        "tools/lli/*.cpp",
        "tools/lli/*.h",
    ]),
    copts = llvm_copts,
    # ll scripts rely on symbols from dependent
    # libraries being resolvable.
    linkopts = [
        "-Wl,--undefined=_ZTIi",
        "-Wl,--export-dynamic-symbol=_ZTIi",
        "-Wl,--export-dynamic-symbol=__cxa_begin_catch",
        "-Wl,--export-dynamic-symbol=__cxa_end_catch",
        "-Wl,--export-dynamic-symbol=__gxx_personality_v0",
        "-Wl,--export-dynamic-symbol=__cxa_allocate_exception",
        "-Wl,--export-dynamic-symbol=__cxa_throw",
    ],
    stamp = 0,
    deps = [
        ":AllTargetsAsmParsers",
        ":AllTargetsCodeGens",
        ":AsmParser",
        ":BitReader",
        ":CodeGen",
        ":Core",
        ":ExecutionEngine",
        ":IRReader",
        ":Instrumentation",
        ":Interpreter",
        ":MCJIT",
        ":Object",
        ":OrcJIT",
        ":Support",
        ":config",
    ],
)

cc_binary(
    name = "llvm-ar",
    srcs = glob([
        "tools/llvm-ar/*.cpp",
        "tools/llvm-ar/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AllTargetsAsmParsers",
        ":AllTargetsCodeGens",
        ":Core",
        ":DlltoolDriver",
        ":LibDriver",
        ":Object",
        ":Support",
    ],
)

# We need to run llvm-ar with different basenames to make it run with
# different behavior.
sh_binary(
    name = "llvm-dlltool",
    srcs = [":llvm-ar"],
)

sh_binary(
    name = "llvm-lib",
    srcs = [":llvm-ar"],
)

sh_binary(
    name = "llvm-ranlib",
    srcs = [":llvm-ar"],
)

cc_binary(
    name = "llvm-as",
    srcs = glob([
        "tools/llvm-as/*.cpp",
        "tools/llvm-as/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":Analysis",
        ":AsmParser",
        ":BitWriter",
        ":Core",
        ":Support",
    ],
)

cc_binary(
    name = "llvm-bcanalyzer",
    srcs = glob([
        "tools/llvm-bcanalyzer/*.cpp",
        "tools/llvm-bcanalyzer/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":BitReader",
        ":Support",
    ],
)

cc_binary(
    name = "llvm-cat",
    srcs = glob([
        "tools/llvm-cat/*.cpp",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":BitReader",
        ":BitWriter",
        ":Core",
        ":IRReader",
        ":Support",
    ],
)

cc_binary(
    name = "llvm-cfi-verify",
    srcs = glob([
        "tools/llvm-cfi-verify/*.cpp",
        "tools/llvm-cfi-verify/lib/*.cpp",
        "tools/llvm-cfi-verify/lib/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AllTargetsAsmParsers",
        ":AllTargetsCodeGens",
        ":AllTargetsDisassemblers",
        ":BinaryFormat",
        ":DebugInfoDWARF",
        ":MC",
        ":MCDisassembler",
        ":MCParser",
        ":Object",
        ":Support",
        ":Symbolize",
    ],
)

cc_binary(
    name = "llvm-cov",
    srcs = glob([
        "tools/llvm-cov/*.cpp",
        "tools/llvm-cov/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":Coverage",
        ":Instrumentation",
        ":Object",
        ":ProfileData",
        ":Support",
    ],
)

gentbl(
    name = "CvtResTableGen",
    tbl_outs = [(
        "-gen-opt-parser-defs",
        "tools/llvm-cvtres/Opts.inc",
    )],
    tblgen = ":llvm-tblgen",
    td_file = "tools/llvm-cvtres/Opts.td",
    td_srcs = ["include/llvm/Option/OptParser.td"],
)

cc_binary(
    name = "llvm-cvtres",
    srcs = glob([
        "tools/llvm-cvtres/*.cpp",
        "tools/llvm-cvtres/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":CvtResTableGen",
        ":Object",
        ":Option",
        ":Support",
    ],
)

cc_binary(
    name = "llvm-cxxdump",
    srcs = glob([
        "tools/llvm-cxxdump/*.cpp",
        "tools/llvm-cxxdump/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AllTargetsCodeGens",
        ":BitReader",
        ":Object",
        ":Support",
    ],
)

cc_binary(
    name = "llvm-cxxmap",
    srcs = glob([
        "tools/llvm-cxxmap/*.cpp",
        "tools/llvm-cxxmap/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":Support",
    ],
)

cc_binary(
    name = "llvm-cxxfilt",
    srcs = glob([
        "tools/llvm-cxxfilt/*.cpp",
        "tools/llvm-cxxfilt/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":Demangle",
        ":Support",
    ],
)

cc_binary(
    name = "llvm-dis",
    srcs = glob([
        "tools/llvm-dis/*.cpp",
        "tools/llvm-dis/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":Analysis",
        ":BitReader",
        ":Core",
        ":Support",
    ],
)

cc_binary(
    name = "llvm-dwarfdump",
    srcs = glob([
        "tools/llvm-dwarfdump/*.cpp",
        "tools/llvm-dwarfdump/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AllTargetsCodeGens",
        ":BinaryFormat",
        ":DebugInfo",
        ":DebugInfoDWARF",
        ":MC",
        ":Object",
        ":Support",
    ],
)

cc_binary(
    name = "llvm-dwp",
    srcs = glob([
        "tools/llvm-dwp/*.cpp",
        "tools/llvm-dwp/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AllTargetsCodeGens",
        ":DebugInfoDWARF",
        ":MC",
        ":Object",
        ":Support",
        ":Target",
    ],
)

cc_binary(
    name = "llvm-elfabi",
    srcs = glob([
        "tools/llvm-elfabi/*.cpp",
        "tools/llvm-elfabi/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":InterfaceStub",
        ":Object",
        ":Support",
        ":TextAPI",
    ],
)

# FIXME: Uncomment when the library builds.
#cc_binary(
#    name = "llvm-exegesis",
#    srcs = [
#        "tools/llvm-exegesis/llvm-exegesis.cpp",
#    ],
#    copts = llvm_copts + ["-DHAVE_LIBPFM=0"],
#    stamp = 0,
#    deps = [
#        ":AllTargetsAsmParsers",
#        ":AllTargetsCodeGens",
#        ":AllTargetsDisassemblers",
#        ":MC",
#        ":MCParser",
#        ":Object",
#        ":Support",
#        ":config",
#        ":llvm-exegesis-lib",
#    ],
#)

cc_binary(
    name = "llvm-extract",
    srcs = glob([
        "tools/llvm-extract/*.cpp",
        "tools/llvm-extract/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AsmParser",
        ":BitReader",
        ":BitWriter",
        ":Core",
        ":IPO",
        ":IRReader",
        ":Support",
    ],
)

cc_binary(
    name = "llvm-ifs",
    srcs = glob([
        "tools/llvm-ifs/*.cpp",
        "tools/llvm-ifs/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":ObjectYAML",
        ":Support",
        ":TextAPI",
    ],
)

cc_binary(
    name = "llvm-jitlink",
    srcs = glob([
        "tools/llvm-jitlink/*.cpp",
        "tools/llvm-jitlink/*.h",
    ]),
    copts = llvm_copts,
    # Make symbols from the standard library dynamically resolvable.
    linkopts = [
        "-Wl,--undefined=_ZTIi",
        "-Wl,--export-dynamic-symbol=_ZTIi",
        "-Wl,--export-dynamic-symbol=__cxa_begin_catch",
        "-Wl,--export-dynamic-symbol=__cxa_end_catch",
        "-Wl,--export-dynamic-symbol=__gxx_personality_v0",
        "-Wl,--export-dynamic-symbol=__cxa_allocate_exception",
        "-Wl,--export-dynamic-symbol=__cxa_throw",
    ],
    stamp = 0,
    deps = [
        ":AllTargetsAsmParsers",
        ":AllTargetsCodeGens",
        ":AllTargetsDisassemblers",
        ":AsmParser",
        ":BitReader",
        ":CodeGen",
        ":ExecutionEngine",
        ":MCJIT",
        ":Object",
        ":OrcJIT",
        ":Support",
        ":config",
    ],
)

cc_binary(
    name = "llvm-libtool-darwin",
    srcs = glob([
        "tools/llvm-libtool-darwin/*.cpp",
        "tools/llvm-libtool-darwin/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":BinaryFormat",
        ":Object",
        ":Support",
    ],
)

cc_binary(
    name = "llvm-link",
    srcs = glob([
        "tools/llvm-link/*.cpp",
        "tools/llvm-link/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AsmParser",
        ":BitReader",
        ":BitWriter",
        ":Core",
        ":IPO",
        ":IRReader",
        ":Linker",
        ":Object",
        ":Support",
        ":TransformUtils",
    ],
)

gentbl(
    name = "LipoOptsTableGen",
    tbl_outs = [(
        "-gen-opt-parser-defs",
        "tools/llvm-lipo/LipoOpts.inc",
    )],
    tblgen = ":llvm-tblgen",
    td_file = "tools/llvm-lipo/LipoOpts.td",
    td_srcs = ["include/llvm/Option/OptParser.td"],
)

cc_binary(
    name = "llvm-lipo",
    srcs = [
        "tools/llvm-lipo/llvm-lipo.cpp",
    ],
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":LipoOptsTableGen",
        ":Object",
        ":Option",
        ":Support",
    ],
)

cc_binary(
    name = "llvm-lto",
    srcs = glob([
        "tools/llvm-lto/*.cpp",
        "tools/llvm-lto/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AllTargetsAsmParsers",
        ":AllTargetsCodeGens",
        ":BitReader",
        ":BitWriter",
        ":CodeGen",
        ":Core",
        ":IRReader",
        ":LTO",
        ":Support",
        ":Target",
    ],
)

cc_binary(
    name = "llvm-lto2",
    srcs = glob([
        "tools/llvm-lto2/*.cpp",
        "tools/llvm-lto2/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AllTargetsAsmParsers",
        ":AllTargetsCodeGens",
        ":BitReader",
        ":CodeGen",
        ":Core",
        ":LTO",
        ":Support",
    ],
)

cc_binary(
    name = "llvm-mc",
    srcs = glob([
        "tools/llvm-mc/*.cpp",
        "tools/llvm-mc/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AllTargetsAsmParsers",
        ":AllTargetsCodeGens",
        ":AllTargetsDisassemblers",
        ":MC",
        ":MCDisassembler",
        ":MCParser",
        ":Object",
        ":Support",
    ],
)

cc_binary(
    name = "llvm-mca",
    srcs = glob([
        "tools/llvm-mca/*.cpp",
        "tools/llvm-mca/*.h",
        "tools/llvm-mca/Views/*.cpp",
        "tools/llvm-mca/Views/*.h",
    ]),
    copts = llvm_copts + ["-Iexternal/llvm-project/llvm/tools/llvm-mca"],
    stamp = 0,
    deps = [
        ":AllTargetsAsmParsers",
        ":AllTargetsCodeGens",
        ":AllTargetsDisassemblers",
        ":MC",
        ":MCA",
        ":MCParser",
        ":Support",
    ],
)

cc_binary(
    name = "llvm-ml",
    srcs = glob([
        "tools/llvm-ml/*.cpp",
        "tools/llvm-ml/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AllTargetsAsmParsers",
        ":AllTargetsCodeGens",
        ":AllTargetsDisassemblers",
        ":MC",
        ":MCParser",
        ":Support",
    ],
)

cc_binary(
    name = "llvm-modextract",
    srcs = glob([
        "tools/llvm-modextract/*.cpp",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":BitReader",
        ":BitWriter",
        ":IRReader",
        ":Support",
    ],
)

gentbl(
    name = "MtTableGen",
    tbl_outs = [(
        "-gen-opt-parser-defs",
        "tools/llvm-mt/Opts.inc",
    )],
    tblgen = ":llvm-tblgen",
    td_file = "tools/llvm-mt/Opts.td",
    td_srcs = ["include/llvm/Option/OptParser.td"],
)

cc_binary(
    name = "llvm-mt",
    srcs = glob([
        "tools/llvm-mt/*.cpp",
        "tools/llvm-mt/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":MtTableGen",
        ":Option",
        ":Support",
        ":WindowsManifest",
    ],
)

cc_binary(
    name = "llvm-nm",
    srcs = glob([
        "tools/llvm-nm/*.cpp",
        "tools/llvm-nm/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AllTargetsAsmParsers",
        ":AllTargetsCodeGens",
        ":BinaryFormat",
        ":BitReader",
        ":Core",
        ":Demangle",
        ":Object",
        ":Support",
    ],
)

gentbl(
    name = "llvm-objcopy-opts",
    tbl_outs = [(
        "-gen-opt-parser-defs",
        "tools/llvm-objcopy/ObjcopyOpts.inc",
    )],
    tblgen = ":llvm-tblgen",
    td_file = "tools/llvm-objcopy/ObjcopyOpts.td",
    td_srcs = [
        "include/llvm/Option/OptParser.td",
        "tools/llvm-objcopy/CommonOpts.td",
    ],
)

gentbl(
    name = "llvm-installnametool-opts",
    tbl_outs = [(
        "-gen-opt-parser-defs",
        "tools/llvm-objcopy/InstallNameToolOpts.inc",
    )],
    tblgen = ":llvm-tblgen",
    td_file = "tools/llvm-objcopy/InstallNameToolOpts.td",
    td_srcs = [
        "include/llvm/Option/OptParser.td",
        "tools/llvm-objcopy/CommonOpts.td",
    ],
)

gentbl(
    name = "llvm-strip-opts",
    tbl_outs = [(
        "-gen-opt-parser-defs",
        "tools/llvm-objcopy/StripOpts.inc",
    )],
    tblgen = ":llvm-tblgen",
    td_file = "tools/llvm-objcopy/StripOpts.td",
    td_srcs = [
        "include/llvm/Option/OptParser.td",
        "tools/llvm-objcopy/CommonOpts.td",
    ],
)

cc_binary(
    name = "llvm-objcopy",
    srcs = glob([
        "tools/llvm-objcopy/**/*.cpp",
        "tools/llvm-objcopy/**/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":BinaryFormat",
        ":MC",
        ":Object",
        ":ObjectYAML",
        ":Option",
        ":Support",
        ":Target",
        ":llvm-installnametool-opts",
        ":llvm-objcopy-opts",
        ":llvm-strip-opts",
    ],
)

sh_binary(
    name = "llvm-strip",
    srcs = [":llvm-objcopy"],
)

sh_binary(
    name = "llvm-install-name-tool",
    srcs = [":llvm-objcopy"],
)

cc_binary(
    name = "llvm-objdump",
    srcs = glob([
        "tools/llvm-objdump/*.cpp",
        "tools/llvm-objdump/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AllTargetsAsmParsers",
        ":AllTargetsCodeGens",
        ":AllTargetsDisassemblers",
        ":BinaryFormat",
        ":CodeGen",
        ":DebugInfo",
        ":DebugInfoDWARF",
        ":Demangle",
        ":MC",
        ":MCDisassembler",
        ":Object",
        ":Support",
        ":Symbolize",
        ":config",
    ],
)

cc_binary(
    name = "llvm-opt-report",
    srcs = glob([
        "tools/llvm-opt-report/*.cpp",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AllTargetsCodeGens",
        ":Demangle",
        ":Remarks",
        ":Support",
    ],
)

cc_binary(
    name = "llvm-pdbutil",
    srcs = glob([
        "tools/llvm-pdbutil/*.cpp",
        "tools/llvm-pdbutil/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":BinaryFormat",
        ":DebugInfoCodeView",
        ":DebugInfoMSF",
        ":DebugInfoPDB",
        ":Object",
        ":ObjectYAML",
        ":Support",
        ":config",
    ],
)

cc_binary(
    name = "llvm-profdata",
    srcs = glob([
        "tools/llvm-profdata/*.cpp",
        "tools/llvm-profdata/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":Core",
        ":ProfileData",
        ":Support",
    ],
)

gentbl(
    name = "RcTableGen",
    tbl_outs = [(
        "-gen-opt-parser-defs",
        "tools/llvm-rc/Opts.inc",
    )],
    tblgen = ":llvm-tblgen",
    td_file = "tools/llvm-rc/Opts.td",
    td_srcs = ["include/llvm/Option/OptParser.td"],
)

# Workaround inability to put `.def` files into `srcs` with a library.
cc_library(
    name = "llvm-rc-defs-lib",
    textual_hdrs = glob([
        "tools/llvm-rc/*.def",
    ]),
)

cc_binary(
    name = "llvm-rc",
    srcs = glob([
        "tools/llvm-rc/*.cpp",
        "tools/llvm-rc/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":Object",
        ":Option",
        ":RcTableGen",
        ":Support",
        ":llvm-rc-defs-lib",
    ],
)

cc_binary(
    name = "llvm-readobj",
    srcs = glob([
        "tools/llvm-readobj/*.cpp",
        "tools/llvm-readobj/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AllTargetsCodeGens",
        ":BinaryFormat",
        ":BitReader",
        ":DebugInfoCodeView",
        ":DebugInfoDWARF",
        ":Demangle",
        ":Object",
        ":Support",
    ],
)

# Create an 'llvm-readelf' named binary from the 'llvm-readobj' tool.
sh_binary(
    name = "llvm-readelf",
    srcs = [":llvm-readobj"],
)

cc_binary(
    name = "llvm-reduce",
    srcs = glob([
        "tools/llvm-reduce/**/*.cpp",
        "tools/llvm-reduce/**/*.h",
    ]),
    copts = llvm_copts,
    includes = ["tools/llvm-reduce"],
    stamp = 0,
    deps = [
        ":AllTargetsCodeGens",
        ":BitReader",
        ":Core",
    ],
)

cc_binary(
    name = "llvm-rtdyld",
    srcs = glob([
        "tools/llvm-rtdyld/*.cpp",
        "tools/llvm-rtdyld/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AllTargetsCodeGens",
        ":AllTargetsDisassemblers",
        ":DebugInfo",
        ":DebugInfoDWARF",
        ":ExecutionEngine",
        ":MC",
        ":MCDisassembler",
        ":Object",
        ":Support",
    ],
)

cc_binary(
    name = "llvm-size",
    srcs = glob([
        "tools/llvm-size/*.cpp",
        "tools/llvm-size/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":Object",
        ":Support",
    ],
)

cc_binary(
    name = "llvm-split",
    srcs = glob([
        "tools/llvm-split/*.cpp",
        "tools/llvm-split/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":BitWriter",
        ":Core",
        ":IRReader",
        ":Support",
        ":TransformUtils",
    ],
)

cc_binary(
    name = "llvm-strings",
    srcs = glob([
        "tools/llvm-strings/*.cpp",
        "tools/llvm-strings/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":Object",
        ":Support",
    ],
)

gentbl(
    name = "SymbolizerOptsTableGen",
    tbl_outs = [(
        "-gen-opt-parser-defs",
        "tools/llvm-symbolizer/Opts.inc",
    )],
    tblgen = ":llvm-tblgen",
    td_file = "tools/llvm-symbolizer/Opts.td",
    td_srcs = ["include/llvm/Option/OptParser.td"],
)

cc_binary(
    name = "llvm-symbolizer",
    srcs = glob([
        "tools/llvm-symbolizer/*.cpp",
        "tools/llvm-symbolizer/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":DebugInfoDWARF",
        ":DebugInfoPDB",
        ":Object",
        ":Option",
        ":Support",
        ":Symbolize",
        ":SymbolizerOptsTableGen",
    ],
)

sh_binary(
    name = "llvm-addr2line",
    srcs = [":llvm-symbolizer"],
)

cc_binary(
    name = "llvm-undname",
    srcs = glob([
        "tools/llvm-undname/*.cpp",
        "tools/llvm-undname/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":Demangle",
        ":Support",
    ],
)

cc_binary(
    name = "llvm-xray",
    srcs = glob([
        "tools/llvm-xray/*.cpp",
        "tools/llvm-xray/*.cc",
        "tools/llvm-xray/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":DebugInfoDWARF",
        ":Object",
        ":Support",
        ":Symbolize",
        ":XRay",
    ],
)

cc_binary(
    name = "opt",
    srcs = glob([
        "tools/opt/*.cpp",
        "tools/opt/*.h",
    ]),
    copts = llvm_copts,
    linkopts = ["-Wl,--export-dynamic"],
    stamp = 0,
    deps = [
        ":AllTargetsAsmParsers",
        ":AllTargetsCodeGens",
        ":Analysis",
        ":AsmParser",
        ":BitReader",
        ":BitWriter",
        ":CodeGen",
        ":Core",
        ":IRReader",
        ":MC",
        ":Passes",
        ":Support",
        ":Target",
        ":TransformUtils",
        ":common_transforms",
        ":config",
    ],
)

cc_binary(
    name = "sancov",
    srcs = glob([
        "tools/sancov/*.cpp",
        "tools/sancov/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AllTargetsCodeGens",
        ":AllTargetsDisassemblers",
        ":DebugInfoDWARF",
        ":DebugInfoPDB",
        ":MC",
        ":MCDisassembler",
        ":Object",
        ":Support",
        ":Symbolize",
    ],
)

cc_binary(
    name = "sanstats",
    srcs = glob([
        "tools/sanstats/*.cpp",
        "tools/sanstats/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":Support",
        ":Symbolize",
        ":TransformUtils",
    ],
)

cc_binary(
    name = "split-file",
    srcs = glob([
        "tools/split-file/*.cpp",
        "tools/split-file/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":Support",
    ],
)

################################################################################
# Begin testonly libraries

cc_library(
    name = "FuzzMutate",
    testonly = 1,
    srcs = glob(["lib/FuzzMutate/*.cpp"]),
    hdrs = glob(["include/llvm/FuzzMutate/*.h"]),
    copts = llvm_copts,
    includes = ["include"],
    deps = [
        ":Analysis",
        ":BitReader",
        ":BitWriter",
        ":Core",
        ":Scalar",
        ":Support",
    ],
)

cc_library(
    name = "gtest",
    testonly = 1,
    srcs = glob(
        [
            "utils/unittest/googletest/include/**/*.h",
            "utils/unittest/googletest/src/*.cc",
        ],
        exclude = [
            "utils/unittest/googletest/src/gtest-all.cc",
            "utils/unittest/googletest/include/gtest/gtest_pred_impl.h",
        ],
    ) + [
    ],
    hdrs = ["utils/unittest/googletest/include/gtest/gtest.h"],
    # TODO: the hard-coding of `external/llvm-project` path components here is
    # really unfortunate. It is essentially baking in an implementation detail
    # of how Bazel runs the compiler when compiling LLVM in the exact
    # configuration we use.
    copts = llvm_copts + ["-Iexternal/llvm-project/llvm/utils/unittest/googletest"],
    defines = [
        "GTEST_HAS_RTTI=0",
        "GTEST_USE_OWN_TR1_TUPLE",
        "__STDC_LIMIT_MACROS",
        "__STDC_CONSTANT_MACROS",
    ],
    includes = [
        "include",
        "utils/unittest/googletest/include",
    ],
    textual_hdrs = [
        "utils/unittest/googletest/include/gtest/gtest_pred_impl.h",
        "utils/unittest/googletest/src/gtest-internal-inl.h",
    ],
    deps = [":Support"],
)

cc_library(
    name = "gtest_main",
    testonly = 1,
    srcs = ["utils/unittest/UnitTestMain/TestMain.cpp"],
    copts = llvm_copts,
    deps = [
        ":Support",
        ":gmock",
        ":gtest",
    ],
)

cc_library(
    name = "gmock",
    testonly = 1,
    srcs = glob(
        [
            "utils/unittest/googlemock/include/**/*.h",
            "utils/unittest/googlemock/src/*.cc",
        ],
        exclude = ["utils/unittest/googlemock/src/gmock-all.cc"],
    ),
    hdrs = ["utils/unittest/googlemock/include/gmock/gmock.h"],
    # TODO: the hard-coding of `external/llvm-project` path components here is
    # really unfortunate. It is essentially baking in an implementation detail
    # of how Bazel runs the compiler when compiling LLVM in the exact
    # configuration we use.
    copts = llvm_copts + ["-Iexternal/llvm-project/llvm/utils/unittest/googlemock"],
    includes = [
        "include",
        "utils/unittest/googlemock/include",
    ],
    deps = [":gtest"],
)

cc_library(
    name = "TestingSupport",
    testonly = 1,
    srcs = glob([
        "lib/Testing/Support/*.cpp",
        "lib/Testing/Support/*.h",
    ]),
    hdrs = glob([
        "include/llvm/Testing/Support/*.h",
    ]),
    copts = llvm_copts,
    deps = [
        ":Support",
        ":config",
        ":gmock",
        ":gtest",
    ],
)

################################################################################
# Begin testonly binary utilities

cc_binary(
    name = "FileCheck",
    testonly = 1,
    srcs = glob([
        "utils/FileCheck/*.cpp",
        "utils/FileCheck/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [":Support"],
)

cc_binary(
    name = "bugpoint",
    srcs = glob([
        "tools/bugpoint/*.cpp",
        "tools/bugpoint/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AllTargetsAsmParsers",
        ":AllTargetsCodeGens",
        ":Analysis",
        ":AsmParser",
        ":BitReader",
        ":BitWriter",
        ":CodeGen",
        ":Core",
        ":IRReader",
        ":Linker",
        ":Passes",
        ":Support",
        ":TransformUtils",
        ":common_transforms",
        ":config",
    ],
)

cc_binary(
    name = "count",
    testonly = 1,
    srcs = glob([
        "utils/count/*.c",
        "utils/count/*.h",
    ]),
    stamp = 0,
)

cc_binary(
    name = "lli-child-target",
    testonly = 1,
    srcs = glob([
        "tools/lli/ChildTarget/*.cpp",
        "tools/lli/ChildTarget/*.h",
    ]) + [
        "tools/lli/RemoteJITUtils.h",
    ],
    copts = llvm_copts,
    # The tests load code into this binary that expect to see symbols
    # from libstdc++ such as __cxa_begin_catch and _ZTIi. The latter
    # isn't even used in the main binary, so we also need to force it
    # to be included.
    linkopts = [
        "-rdynamic",
        "-u_ZTIi",
    ],
    stamp = 0,
    deps = [
        ":OrcJIT",
        ":Support",
        ":attributes_gen",
        ":config",
        ":intrinsic_enums_gen",
    ],
)

cc_binary(
    name = "llvm-c-test",
    testonly = 1,
    srcs = glob([
        "tools/llvm-c-test/*.c",
        "tools/llvm-c-test/*.cpp",
        "tools/llvm-c-test/*.h",
    ]),
    # Note that we cannot use the general LLVM options here as we mix C and C++
    # code. However, we generally don't need to disable warnings here as
    # headers included here shouldn't trigger warnings.
    copts = [],
    stamp = 0,
    deps = [
        ":AllTargetsAsmParsers",
        ":AllTargetsCodeGens",
        ":AllTargetsDisassemblers",
        ":Analysis",
        ":BitReader",
        ":BitWriter",
        ":Core",
        ":ExecutionEngine",
        ":IPO",
        ":LTO",
        ":Linker",
        ":MCDisassembler",
        ":Object",
        ":OrcJIT",
        ":Scalar",
        ":Support",
        ":Target",
        ":Vectorize",
    ],
)

cc_binary(
    name = "llvm-diff",
    testonly = 1,
    srcs = glob([
        "tools/llvm-diff/*.cpp",
        "tools/llvm-diff/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AsmParser",
        ":BitReader",
        ":Core",
        ":IRReader",
        ":Support",
    ],
)

cc_binary(
    name = "llvm-isel-fuzzer",
    testonly = 1,
    srcs = glob([
        "tools/llvm-isel-fuzzer/*.cpp",
        "tools/llvm-isel-fuzzer/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AllTargetsAsmParsers",
        ":AllTargetsCodeGens",
        ":Analysis",
        ":BitReader",
        ":BitWriter",
        ":CodeGen",
        ":Core",
        ":FuzzMutate",
        ":IRReader",
        ":Support",
        ":Target",
    ],
)

# This is really a Python script, but call it sh_binary to ignore the hyphen in
# the path, which py_binary does not allow.
# Also, note: llvm-locstats expects llvm-dwarfdump to be in the same directory
# when executed.
sh_binary(
    name = "llvm-locstats",
    testonly = 1,
    srcs = glob([
        "utils/llvm-locstats/*.py",
    ]),
    # llvm-locstats is a thin wrapper around llvm-dwarfdump.
    data = [":llvm-dwarfdump"],
)

cc_binary(
    name = "not",
    testonly = 1,
    srcs = glob([
        "utils/not/*.cpp",
        "utils/not/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [":Support"],
)

cc_binary(
    name = "llvm-opt-fuzzer",
    testonly = 1,
    srcs = glob([
        "tools/llvm-opt-fuzzer/*.cpp",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AllTargetsCodeGens",
        ":Analysis",
        ":BitReader",
        ":BitWriter",
        ":CodeGen",
        ":Core",
        ":Coroutines",
        ":FuzzMutate",
        ":Passes",
        ":Support",
    ],
)

cc_binary(
    name = "obj2yaml",
    testonly = 1,
    srcs = glob([
        "tools/obj2yaml/*.cpp",
        "tools/obj2yaml/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":BinaryFormat",
        ":DebugInfoCodeView",
        ":DebugInfoDWARF",
        ":Object",
        ":ObjectYAML",
        ":Support",
    ],
)

cc_binary(
    name = "verify-uselistorder",
    srcs = glob([
        "tools/verify-uselistorder/*.cpp",
        "tools/verify-uselistorder/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":AsmParser",
        ":BitReader",
        ":BitWriter",
        ":Core",
        ":IRReader",
        ":Support",
    ],
)

cc_binary(
    name = "yaml2obj",
    testonly = 1,
    srcs = glob([
        "tools/yaml2obj/*.cpp",
        "tools/yaml2obj/*.h",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":BinaryFormat",
        ":DebugInfoCodeView",
        ":MC",
        ":Object",
        ":ObjectYAML",
        ":Support",
    ],
)

cc_binary(
    name = "yaml-bench",
    testonly = 1,
    srcs = glob([
        "utils/yaml-bench/*.cpp",
    ]),
    copts = llvm_copts,
    stamp = 0,
    deps = [
        ":Support",
    ],
)
