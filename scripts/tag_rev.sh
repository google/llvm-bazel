#!/bin/bash

# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

# Tags the current HEAD commit with the corresponding LLVM commit from its
# submodule.

set -e
set -o pipefail

if [[ -n "$(git status --porcelain)" ]]; then
    echo "Working directory not clean. Aborting"
    git status
    exit 1
fi

ROOT_DIR="$(git rev-parse --show-toplevel)"

LLVM_COMMIT="$(${ROOT_DIR?}/scripts/get_llvm_commit.sh)"

git tag -f "llvm-project-${LLVM_COMMIT?}"
