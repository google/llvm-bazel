#!/bin/bash

# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

# Tags each commit between the specified commit and the current HEAD (exclusive
# and inclusive, respectively) with the corresponding LLVM commit from its
# submodule. Tags commits sequentially starting from the oldest, so if multiple
# commits correspond to the same LLVM submodule, the newest will end up with the
# tag.

set -e
set -o pipefail

START="${1?}"

ROOT_DIR="$(git rev-parse --show-toplevel)"

readarray -t commits < <(git rev-list --reverse --ancestry-path "${START?}..HEAD")
if [[ ${#commits[@]} == 0 ]]; then
  echo "Failed to find path between current HEAD and ${START?}"
  exit 1
fi

for commit in "${commits[@]?}"; do
  git checkout "${commit?}"
  git submodule update
  "${ROOT_DIR?}/scripts/tag_rev.sh"
done
