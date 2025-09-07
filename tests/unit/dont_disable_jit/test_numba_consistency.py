import numba
import pyreason.scripts.interpretation.interpretation as interpretation
import pyreason.scripts.numba_wrapper.numba_types.label_type as label


def test_satisfies_threshold_consistency():
    """_satisfies_threshold should match between JIT and pure Python."""
    thresh = ('greater_equal', ('number', 'total'), 4)
    jit_res = interpretation._satisfies_threshold(10, 5, thresh)
    py_res = interpretation._satisfies_threshold.py_func(10, 5, thresh)
    assert jit_res == py_res


def test_get_rule_node_clause_grounding_consistency():
    """get_rule_node_clause_grounding outputs should match between JIT and Python."""
    node_type = numba.types.string
    nodes = numba.typed.List(['n1', 'n2', 'n3'])
    groundings = numba.typed.Dict.empty(key_type=node_type, value_type=interpretation.list_of_nodes)
    predicate_map = numba.typed.Dict.empty(key_type=label.label_type, value_type=interpretation.list_of_nodes)
    l = label.Label('L')
    predicate_map[l] = numba.typed.List(['n1', 'n2'])

    jit_res = interpretation.get_rule_node_clause_grounding('X', groundings, predicate_map, l, nodes)
    py_res = interpretation.get_rule_node_clause_grounding.py_func('X', groundings, predicate_map, l, nodes)
    assert list(jit_res) == list(py_res)


def test_get_rule_edge_clause_grounding_consistency():
    """get_rule_edge_clause_grounding outputs should match between JIT and Python."""
    node_type = numba.types.string
    edge_type = numba.types.UniTuple(numba.types.string, 2)
    nodes = numba.typed.List(['n1', 'n2'])
    edges = numba.typed.List([('n1', 'n2'), ('n2', 'n1')])

    neighbors = numba.typed.Dict.empty(key_type=node_type, value_type=interpretation.list_of_nodes)
    neighbors['n1'] = numba.typed.List(['n2'])
    neighbors['n2'] = numba.typed.List(['n1'])
    reverse_neighbors = numba.typed.Dict.empty(key_type=node_type, value_type=interpretation.list_of_nodes)
    reverse_neighbors['n1'] = numba.typed.List(['n2'])
    reverse_neighbors['n2'] = numba.typed.List(['n1'])

    groundings = numba.typed.Dict.empty(key_type=node_type, value_type=interpretation.list_of_nodes)
    groundings_edges = numba.typed.Dict.empty(key_type=edge_type, value_type=interpretation.list_of_edges)
    predicate_map = numba.typed.Dict.empty(key_type=label.label_type, value_type=interpretation.list_of_edges)
    l = label.Label('L')

    jit_res = interpretation.get_rule_edge_clause_grounding('X', 'Y', groundings, groundings_edges,
                                                            neighbors, reverse_neighbors, predicate_map, l, edges)
    py_res = interpretation.get_rule_edge_clause_grounding.py_func('X', 'Y', groundings, groundings_edges,
                                                                    neighbors, reverse_neighbors, predicate_map, l, edges)
    assert list(jit_res) == list(py_res)
import numpy as np
import pyreason.scripts.numba_wrapper.numba_types.world_type as world
import pyreason.scripts.numba_wrapper.numba_types.interval_type as interval


def _build_reason_args():
    node_type = interpretation.node_type
    edge_type = interpretation.edge_type
    node = 'n1'
    lbl = label.Label('L')

    interpretations_node = numba.typed.Dict.empty(key_type=node_type, value_type=world.world_type)
    labels_list = numba.typed.List([lbl])
    interpretations_node[node] = world.World(labels_list)
    interpretations_edge = numba.typed.Dict.empty(key_type=edge_type, value_type=world.world_type)

    predicate_map_node = numba.typed.Dict.empty(key_type=label.label_type, value_type=interpretation.list_of_nodes)
    predicate_map_edge = numba.typed.Dict.empty(key_type=label.label_type, value_type=interpretation.list_of_edges)

    tmax = 0
    prev_reasoning_data = numba.typed.List([0, 0])
    rules = numba.typed.List.empty_list(numba.types.int64)
    nodes = numba.typed.List([node])
    edges = numba.typed.List.empty_list(edge_type)

    neighbors = numba.typed.Dict.empty(key_type=node_type, value_type=interpretation.list_of_nodes)
    neighbors[node] = numba.typed.List.empty_list(node_type)
    reverse_neighbors = numba.typed.Dict.empty(key_type=node_type, value_type=interpretation.list_of_nodes)
    reverse_neighbors[node] = numba.typed.List.empty_list(node_type)

    rules_to_be_applied_node = numba.typed.List.empty_list(interpretation.rules_to_be_applied_node_type)
    rules_to_be_applied_edge = numba.typed.List.empty_list(interpretation.rules_to_be_applied_edge_type)
    edges_to_be_added_node_rule = numba.typed.List.empty_list(interpretation.edges_to_be_added_type)
    edges_to_be_added_edge_rule = numba.typed.List.empty_list(interpretation.edges_to_be_added_type)
    rules_to_be_applied_node_trace = numba.typed.List.empty_list(interpretation.rules_to_be_applied_trace_type)
    rules_to_be_applied_edge_trace = numba.typed.List.empty_list(interpretation.rules_to_be_applied_trace_type)

    facts_to_be_applied_node = numba.typed.List.empty_list(interpretation.facts_to_be_applied_node_type)
    bnd = interval.closed(0.2, 0.2)
    facts_to_be_applied_node.append((np.uint16(0), node, lbl, bnd, False, False))
    facts_to_be_applied_edge = numba.typed.List.empty_list(interpretation.facts_to_be_applied_edge_type)
    facts_to_be_applied_node_trace = numba.typed.List.empty_list(numba.types.string)
    facts_to_be_applied_edge_trace = numba.typed.List.empty_list(numba.types.string)

    ipl = numba.typed.List.empty_list(numba.types.UniTuple(label.label_type, 2))
    rule_trace_node = numba.typed.List.empty_list(
        numba.types.Tuple((numba.types.uint16, numba.types.uint16, node_type, label.label_type, interval.interval_type))
    )
    rule_trace_edge = numba.typed.List.empty_list(
        numba.types.Tuple((numba.types.uint16, numba.types.uint16, edge_type, label.label_type, interval.interval_type))
    )
    rule_trace_node_atoms = numba.typed.List.empty_list(
        numba.types.Tuple(
            (
                numba.types.ListType(numba.types.ListType(node_type)),
                numba.types.ListType(numba.types.ListType(edge_type)),
                interval.interval_type,
                numba.types.string,
            )
        )
    )
    rule_trace_edge_atoms = numba.typed.List.empty_list(
        numba.types.Tuple(
            (
                numba.types.ListType(numba.types.ListType(node_type)),
                numba.types.ListType(numba.types.ListType(edge_type)),
                interval.interval_type,
                numba.types.string,
            )
        )
    )

    reverse_graph = numba.typed.Dict.empty(key_type=node_type, value_type=interpretation.list_of_nodes)
    annotation_functions = numba.typed.List.empty_list(numba.types.pyobject)
    num_ga = numba.typed.List([0])

    args = [
        interpretations_node,
        interpretations_edge,
        predicate_map_node,
        predicate_map_edge,
        tmax,
        prev_reasoning_data,
        rules,
        nodes,
        edges,
        neighbors,
        reverse_neighbors,
        rules_to_be_applied_node,
        rules_to_be_applied_edge,
        edges_to_be_added_node_rule,
        edges_to_be_added_edge_rule,
        rules_to_be_applied_node_trace,
        rules_to_be_applied_edge_trace,
        facts_to_be_applied_node,
        facts_to_be_applied_edge,
        facts_to_be_applied_node_trace,
        facts_to_be_applied_edge_trace,
        ipl,
        rule_trace_node,
        rule_trace_edge,
        rule_trace_node_atoms,
        rule_trace_edge_atoms,
        reverse_graph,
        False,
        False,
        False,
        False,
        False,
        '',
        True,
        0,
        annotation_functions,
        'perfect_convergence',
        0.0,
        num_ga,
        False,
        False,
    ]
    return args, node, lbl


def test_reason_node_fact_consistency():
    args1, node, lbl = _build_reason_args()
    args2, _, _ = _build_reason_args()
    jit_res = interpretation.Interpretation.reason(*args1)
    py_res = interpretation.Interpretation.reason.py_func(*args2)
    assert jit_res == py_res
    assert args1[0][node].world[lbl] == args2[0][node].world[lbl]
