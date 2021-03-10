#!/bin/bash

# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

# Returns the current submodule revision used for LLVM.

set -e
set -o pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
SUBMODULE_DIR="${ROOT_DIR?}/third_party/llvm-project"
git submodule status -- ${SUBMODULE_DIR?} | awk '{print $1}' | tr -d '+-'
