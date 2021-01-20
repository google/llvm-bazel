#!/bin/bash

# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

# Walks commits in the llvm-project submodule at SUBMODULE_DIR (default
# "third_party/llvm-project") between the current state (exclusive) and the tip
# of the $BRANCH (inclusive, default "main") on the remote and calls the
# specified command.

set -e
set -o pipefail

BRANCH="${BRANCH:-main}"
ROOT_DIR="$(git rev-parse --show-toplevel)"
SUBMODULE_DIR="${ROOT_DIR?}/third_party/llvm-project"

pushd "${SUBMODULE_DIR?}"
START="$(git rev-parse HEAD)"
# For help debugging https://github.com/actions/checkout/issues/363
git remote -v
git checkout "${BRANCH?}"
git pull --ff-only origin "${BRANCH?}"

if [[ "$(git rev-parse "${BRANCH?}")" == "${START?}" ]]; then
  echo "Current HEAD is already up to date with ${BRANCH?}"
  popd
  exit 0
fi

readarray -t commits < <(git rev-list --reverse --ancestry-path "${START?}..${BRANCH?}")
if [[ ${#commits[@]} == 0 ]]; then
  echo "Failed to find path between current HEAD and ${BRANCH?}"
  popd
  exit 1
fi
popd

for commit in "${commits[@]?}"; do
  pushd "${SUBMODULE_DIR?}"
  git checkout "${commit?}"
  popd
  "$@";
done

git submodule update
