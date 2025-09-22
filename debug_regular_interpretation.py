#!/usr/bin/env python3
"""
Debug script to investigate regular interpretation engine behavior
Focus on understanding why basic facts aren't being stored/queried correctly
"""

import pyreason as pr
import networkx as nx

def test_regular_basic_facts():
    """Test if regular version can handle basic facts without rules"""
    print("=== TESTING REGULAR VERSION - BASIC FACTS ONLY ===")

    pr.reset()
    pr.reset_rules()
    pr.reset_settings()
    pr.settings.fp_version = False
    pr.settings.verbose = True  # Enable verbose to see what's happening

    # Create simple graph
    graph = nx.DiGraph()
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    pr.load_graph(graph)

    # Add a simple dummy rule (since PyReason requires at least one rule)
    pr.add_rule(pr.Rule('dummy(x) <- dummy(x)', 'dummy_rule'))
    pr.add_fact(pr.Fact('connected(A, B)', 'fact1'))
    pr.add_fact(pr.Fact('connected(B, C)', 'fact2'))

    print("\nReasoning with facts only (minimal dummy rule):")
    interpretation = pr.reason(timesteps=1)

    # Query the basic facts
    result_ab = interpretation.query(pr.Query('connected(A, B)'))
    result_bc = interpretation.query(pr.Query('connected(B, C)'))

    print(f"\nResults - Facts Only:")
    print(f"  connected(A, B): {result_ab}")
    print(f"  connected(B, C): {result_bc}")

    return result_ab, result_bc

def test_regular_with_transitive_rule():
    """Test regular version with transitive rule"""
    print("\n=== TESTING REGULAR VERSION - WITH TRANSITIVE RULE ===")

    pr.reset()
    pr.reset_rules()
    pr.reset_settings()
    pr.settings.fp_version = False
    pr.settings.verbose = True

    # Create simple graph
    graph = nx.DiGraph()
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    pr.load_graph(graph)

    # Add transitive rule
    pr.add_rule(pr.Rule('connected(x, z) <-1 connected(x, y), connected(y, z)', 'transitive_rule', infer_edges=True))
    pr.add_fact(pr.Fact('connected(A, B)', 'fact1'))
    pr.add_fact(pr.Fact('connected(B, C)', 'fact2'))

    print("\nReasoning with transitive rule:")
    interpretation = pr.reason(timesteps=2)

    # Query all possible connections
    result_ab = interpretation.query(pr.Query('connected(A, B)'))
    result_bc = interpretation.query(pr.Query('connected(B, C)'))
    result_ac = interpretation.query(pr.Query('connected(A, C)'))

    print(f"\nResults - With Transitive Rule:")
    print(f"  connected(A, B): {result_ab}")
    print(f"  connected(B, C): {result_bc}")
    print(f"  connected(A, C): {result_ac}")

    return result_ab, result_bc, result_ac

def test_regular_without_infer_edges():
    """Test regular version without infer_edges=True"""
    print("\n=== TESTING REGULAR VERSION - WITHOUT infer_edges=True ===")

    pr.reset()
    pr.reset_rules()
    pr.reset_settings()
    pr.settings.fp_version = False
    pr.settings.verbose = False  # Less verbose for comparison

    # Create simple graph
    graph = nx.DiGraph()
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    pr.load_graph(graph)

    # Add transitive rule WITHOUT infer_edges=True
    pr.add_rule(pr.Rule('connected(x, z) <-1 connected(x, y), connected(y, z)', 'transitive_rule'))  # No infer_edges!
    pr.add_fact(pr.Fact('connected(A, B)', 'fact1'))
    pr.add_fact(pr.Fact('connected(B, C)', 'fact2'))

    print("\nReasoning WITHOUT infer_edges=True:")
    interpretation = pr.reason(timesteps=2)

    # Query all possible connections
    result_ab = interpretation.query(pr.Query('connected(A, B)'))
    result_bc = interpretation.query(pr.Query('connected(B, C)'))
    result_ac = interpretation.query(pr.Query('connected(A, C)'))

    print(f"\nResults - WITHOUT infer_edges:")
    print(f"  connected(A, B): {result_ab}")
    print(f"  connected(B, C): {result_bc}")
    print(f"  connected(A, C): {result_ac}")

    return result_ab, result_bc, result_ac

def test_regular_different_timesteps():
    """Test regular version queries at different timesteps"""
    print("\n=== TESTING REGULAR VERSION - DIFFERENT TIMESTEPS ===")

    pr.reset()
    pr.reset_rules()
    pr.reset_settings()
    pr.settings.fp_version = False
    pr.settings.verbose = False

    # Create simple graph
    graph = nx.DiGraph()
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    pr.load_graph(graph)

    # Add transitive rule
    pr.add_rule(pr.Rule('connected(x, z) <-1 connected(x, y), connected(y, z)', 'transitive_rule', infer_edges=True))
    pr.add_fact(pr.Fact('connected(A, B)', 'fact1'))
    pr.add_fact(pr.Fact('connected(B, C)', 'fact2'))

    interpretation = pr.reason(timesteps=2)

    print(f"\nQuerying at different timesteps:")
    for t in range(3):
        try:
            result_ab = interpretation.query(pr.Query('connected(A, B)'), t)
            result_bc = interpretation.query(pr.Query('connected(B, C)'), t)
            result_ac = interpretation.query(pr.Query('connected(A, C)'), t)
            print(f"  t={t}: A-B={result_ab}, B-C={result_bc}, A-C={result_ac}")
        except Exception as e:
            print(f"  t={t}: Error - {e}")

if __name__ == "__main__":
    print("INVESTIGATING REGULAR INTERPRETATION ENGINE")
    print("=" * 60)

    # Test 1: Basic facts only
    facts_ab, facts_bc = test_regular_basic_facts()

    # Test 2: With transitive rule and infer_edges=True
    rule_ab, rule_bc, rule_ac = test_regular_with_transitive_rule()

    # Test 3: Without infer_edges=True
    no_infer_ab, no_infer_bc, no_infer_ac = test_regular_without_infer_edges()

    # Test 4: Different timesteps
    test_regular_different_timesteps()

    print("\n" + "=" * 60)
    print("SUMMARY COMPARISON")
    print("=" * 60)
    print(f"{'Test Case':<25} {'A-B':<6} {'B-C':<6} {'A-C':<6}")
    print("-" * 50)
    print(f"{'Facts Only':<25} {str(facts_ab):<6} {str(facts_bc):<6} {'N/A':<6}")
    print(f"{'With infer_edges=True':<25} {str(rule_ab):<6} {str(rule_bc):<6} {str(rule_ac):<6}")
    print(f"{'Without infer_edges':<25} {str(no_infer_ab):<6} {str(no_infer_bc):<6} {str(no_infer_ac):<6}")

    if not facts_ab or not facts_bc:
        print("\n🔴 PROBLEM: Regular version can't even handle basic facts!")
    elif rule_ac:
        print("\n🟢 WORKING: Regular version successfully does transitive reasoning!")
    else:
        print("\n🟡 PARTIAL: Regular version handles facts but not transitive reasoning")