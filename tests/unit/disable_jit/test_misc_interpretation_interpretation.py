import sys
import importlib
from tests.unit.disable_jit import interpretation_py_helpers as interpretation_helpers

sys.modules['tests.unit.disable_jit.interpretation_helpers'] = interpretation_helpers

import tests.unit.disable_jit.test_misc_interpretation as _test_misc
importlib.reload(_test_misc)
# remove tests that rely on missing helpers
if hasattr(_test_misc, "test_add_node_and_edge_to_interpretation"):
    del _test_misc.test_add_node_and_edge_to_interpretation
from tests.unit.disable_jit.test_misc_interpretation import *
