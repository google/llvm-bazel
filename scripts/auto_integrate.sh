#!/bin/bash

# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

# Walks commits in the LLVM submodule creating new commits for each update.

./scripts/traverse_llvm_revs.sh ./scripts/generate_build_and_tag.sh
