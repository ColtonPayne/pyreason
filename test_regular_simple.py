#!/usr/bin/env python3
"""
Simple test of regular interpretation after fix
"""

import pyreason as pr
import networkx as nx
import signal
import sys

def timeout_handler(signum, frame):
    print("TIMEOUT: Regular version is hanging!")
    sys.exit(1)

# Set timeout
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(10)  # 10 second timeout

try:
    print("Testing regular version with simple facts only...")

    pr.reset()
    pr.reset_rules()
    pr.reset_settings()
    pr.settings.fp_version = False
    pr.settings.verbose = False

    # Create simple graph
    graph = nx.DiGraph()
    graph.add_edge("A", "B")
    pr.load_graph(graph)

    # Add minimal rule and fact
    pr.add_rule(pr.Rule('dummy(x) <- dummy(x)', 'dummy_rule'))
    pr.add_fact(pr.Fact('connected(A, B)', 'fact1'))

    print("About to call pr.reason()...")
    interpretation = pr.reason(timesteps=1)
    print("pr.reason() completed successfully!")

    result = interpretation.query(pr.Query('connected(A, B)'))
    print(f"Query result: {result}")

    signal.alarm(0)  # Cancel timeout
    print("✅ Regular version works with simple case")

except Exception as e:
    signal.alarm(0)
    print(f"❌ Regular version failed: {e}")