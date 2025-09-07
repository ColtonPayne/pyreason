"""Utility to expose pure-Python versions of numba-compiled interpretation functions.

The previous implementation bound to ``interpretation_fp`` directly.  This module
now provides :func:`get_interpretation_helpers` which can return helpers for either
``interpretation_fp`` or ``interpretation`` based on the supplied module name.
"""

from types import SimpleNamespace
import importlib
import pyreason.scripts.numba_wrapper.numba_types.label_type as label


def _py(func):
    """Return the underlying Python callable for numba compiled functions."""
    return getattr(func, "py_func", func)


def get_interpretation_helpers(module_name: str = "interpretation_fp"):
    """Return a namespace with helpers for the given interpretation module.

    Parameters
    ----------
    module_name:
        Either ``"interpretation_fp"`` or ``"interpretation"``.
    """
    interpretation = importlib.import_module(
        f"pyreason.scripts.interpretation.{module_name}"
    )

    ns = SimpleNamespace()
    ns.interpretation = interpretation
    ns.label = label

    ns.is_satisfied_edge = _py(interpretation.is_satisfied_edge)
    ns.is_satisfied_node = _py(interpretation.is_satisfied_node)
    ns.get_qualified_edge_groundings = _py(
        interpretation.get_qualified_edge_groundings
    )
    ns.get_qualified_node_groundings = _py(
        interpretation.get_qualified_node_groundings
    )
    ns.get_rule_node_clause_grounding = _py(
        interpretation.get_rule_node_clause_grounding
    )
    ns.get_rule_edge_clause_grounding = _py(
        interpretation.get_rule_edge_clause_grounding
    )
    ns.satisfies_threshold = _py(interpretation._satisfies_threshold)
    ns.check_node_grounding_threshold_satisfaction = _py(
        interpretation.check_node_grounding_threshold_satisfaction
    )
    ns.check_edge_grounding_threshold_satisfaction = _py(
        interpretation.check_edge_grounding_threshold_satisfaction
    )
    ns.refine_groundings = _py(interpretation.refine_groundings)
    ns.check_all_clause_satisfaction = _py(
        interpretation.check_all_clause_satisfaction
    )
    ns.add_node = _py(interpretation._add_node)
    ns.add_edge = _py(interpretation._add_edge)
    ns.ground_rule = _py(interpretation._ground_rule)
    ns.update_rule_trace = _py(interpretation._update_rule_trace)
    ns.are_satisfied_node = _py(interpretation.are_satisfied_node)
    ns.are_satisfied_edge = _py(interpretation.are_satisfied_edge)
    ns.is_satisfied_node_comparison = _py(
        interpretation.is_satisfied_node_comparison
    )
    ns.is_satisfied_edge_comparison = _py(
        interpretation.is_satisfied_edge_comparison
    )
    ns.check_consistent_node = _py(interpretation.check_consistent_node)
    ns.check_consistent_edge = _py(interpretation.check_consistent_edge)
    ns.resolve_inconsistency_node = _py(
        interpretation.resolve_inconsistency_node
    )
    ns.resolve_inconsistency_edge = _py(
        interpretation.resolve_inconsistency_edge
    )
    if hasattr(interpretation, "_add_node_to_interpretation"):
        ns.add_node_to_interpretation = _py(
            interpretation._add_node_to_interpretation
        )
    if hasattr(interpretation, "_add_edge_to_interpretation"):
        ns.add_edge_to_interpretation = _py(
            interpretation._add_edge_to_interpretation
        )
    ns.add_edges = _py(interpretation._add_edges)
    ns.delete_edge = _py(interpretation._delete_edge)
    ns.delete_node = _py(interpretation._delete_node)
    ns.float_to_str = _py(interpretation.float_to_str)
    ns.str_to_float = _py(interpretation.str_to_float)
    ns.str_to_int = _py(interpretation.str_to_int)
    ns.annotate = _py(interpretation.annotate)
    ns.reason = _py(interpretation.Interpretation.reason)

    class FakeLabel:
        def __init__(self, value):
            self.value = value

        def __hash__(self):
            return hash(self.value)

        def __eq__(self, other):
            return isinstance(other, FakeLabel) and self.value == other.value

        def __repr__(self):
            return f"FakeLabel({self.value!r})"

    ns.FakeLabel = FakeLabel
    return ns


# Provide default exports for backward compatibility with existing tests
_default = get_interpretation_helpers("interpretation_fp")
for _name in dir(_default):
    if not _name.startswith("_"):
        globals()[_name] = getattr(_default, _name)
