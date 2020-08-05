// This file is licensed under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

#include "mlir/InitAllDialects.h"
#include "mlir/InitAllPasses.h"

namespace mlir {
// This target is a convenient dependency for users to auto-initialize MLIR
// internals.
static bool auto_init = []() {
  registerAllDialects();
  registerAllPasses();

  return true;
}();

} // namespace mlir
