#!/bin/bash

# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

# Updates for the current LLVM commit and creates a tag.
#  1. Creates a new commit for the
#  2. Tags the HEAD commit with the matching LLVM commit.

set -e
set -o pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"

LLVM_COMMIT="$(${ROOT_DIR?}/scripts/get_llvm_commit.sh)"
SHORT_COMMIT="$(echo ${LLVM_COMMIT?} | cut -c -12)"

git commit -am "Integrate LLVM at llvm/llvm-project@${SHORT_COMMIT?}"

"${ROOT_DIR?}/scripts/tag_rev.sh"
