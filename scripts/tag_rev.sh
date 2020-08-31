#!/bin/bash

# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

# Updates for the current LLVM commit and creates a tag.
#  1. Generates a new LLVM build file for the current LLVM commit.
#  2. If there are diffs (including if the current LLVM submocule change was not
#     committed), creates a new commit.
#  3. Tags the HEAD commit with the matching LLVM commit.

set -e
set -o pipefail

SUBMODULE_DIR="third_party/llvm-project"

if [[ -n "$(git status --porcelain)" ]]; then
    echo "Working directory not clean. Aborting"
    git status
    exit 1
fi

LLVM_COMMIT="$(git submodule status -- ${SUBMODULE_DIR?} | awk '{print $1}' | tr -d '+')"
SHORT_COMMIT="$(echo ${LLVM_COMMIT?} | cut -c -12)"

git tag -f "llvm-project-${LLVM_COMMIT?}"
