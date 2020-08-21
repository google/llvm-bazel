#!/bin/bash

# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

# Creates a fake merge between the specified branches where the current state of
# the second parent (default "main") overrides the state of the first parent
# (default the current branch).

FIRST_PARENT="${1:-$(git rev-parse --abbrev-ref HEAD)}"
SECOND_PARENT="${2:-main}"

git checkout "${FIRST_PARENT?}"
git reset --hard \
  "$(git commit-tree ${SECOND_PARENT?}^{tree} -p ${FIRST_PARENT?} -p ${SECOND_PARENT?} -m "Merge from ${SECOND_PARENT?}")"
