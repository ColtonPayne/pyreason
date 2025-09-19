import os
import sys

# Ensure JIT is enabled for this test directory
if "NUMBA_DISABLE_JIT" in os.environ:
    del os.environ["NUMBA_DISABLE_JIT"]

# Clear any cached numba modules to reset JIT configuration
numba_modules = [name for name in sys.modules.keys() if name.startswith('numba')]
for module_name in numba_modules:
    if module_name in sys.modules:
        del sys.modules[module_name]

# Clear any cached pyreason modules that might have numba dependencies
pyreason_modules = [name for name in sys.modules.keys() if name.startswith('pyreason')]
for module_name in pyreason_modules:
    if module_name in sys.modules:
        del sys.modules[module_name]

import numba
numba.config.DISABLE_JIT = False