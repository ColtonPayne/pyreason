# import the logicIntegratedClassifier class

import torch
import torch.nn as nn
import networkx as nx
import numpy as np
import random
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from pyreason.scripts.learning.classification.classifier import LogicIntegratedClassifier
from pyreason.scripts.facts.fact import Fact
from pyreason.scripts.learning.utils.model_interface import ModelInterfaceOptions
from pyreason.scripts.rules.rule import Rule
from pyreason.pyreason import _Settings as Settings, reason, reset_settings, get_rule_trace, add_fact, add_rule, load_graph

# seed_value = 41
seed_value = 42
random.seed(seed_value)
np.random.seed(seed_value)
torch.manual_seed(seed_value)


# --- Part 1: Fraud Detector Model Integration ---

# Create a dummy PyTorch model for transaction fraud detection.
# Each transaction is represented by 5 features and is classified into "fraud" or "legitimate".
model = nn.Linear(5, 2)
class_names = ["fraud", "legitimate"]

# Create a dummy transaction feature vector.
transaction_features = torch.rand(1, 5)

# Define integration options
# Only probabilities above 0.5 are considered for adjustment.
interface_options = ModelInterfaceOptions(
    threshold=0.5,         # Only process probabilities above 0.5
    set_lower_bound=True,  # For high confidence, adjust the lower bound.
    set_upper_bound=False, # Keep the upper bound unchanged.
    snap_value=1.0         # Use 1.0 as the snap value.
)

# Wrap the model using LogicIntegratedClassifier
fraud_detector = LogicIntegratedClassifier(
    model,
    class_names,
    identifier="fraud_detector",
    interface_options=interface_options
)

# Run the model to obtain logits, probabilities, and generated PyReason facts.
logits, probabilities, classifier_facts = fraud_detector(transaction_features)

print("=== Fraud Detector Output ===")
print("Logits:", logits)
print("Probabilities:", probabilities)
print("\nGenerated Classifier Facts:")
for fact in classifier_facts:
    print(fact)

# Add the classifier-generated facts.
for fact in classifier_facts:
    add_fact(fact)

# --- Part 2: Create and Load a Networkx Graph representing an account knowledge base ---

# Create a networkx graph representing a network of accounts.
G = nx.DiGraph()
# Add account nodes.
G.add_node("AccountA", account=1)
G.add_node("AccountB", account=1)
G.add_node("AccountC", account=1)
# Add edges with an attribute "relationship" set to "associated".
G.add_edge("AccountA", "AccountB", associated=1)
G.add_edge("AccountB", "AccountC", associated=1)
load_graph(G)

# --- Part 3: Set Up Context and Reasoning Environment ---

# Add additional contextual information:
# 1. A fact indicating the transaction comes from a suspicious location. This could come from a separate fraud detection system.
add_fact(Fact("suspicious_location(AccountA)", "transaction_fact"))

# Define a rule: if the fraud detector flags a transaction as fraud and the transaction info is suspicious,
# then mark the associated account (AccountA) as requiring investigation.
add_rule(Rule("requires_investigation(acc) <- account(acc), fraud(fraud_detector), suspicious_location(acc)", "investigation_rule"))

# Define a propagation rule:
# If an account requires investigation and is connected (via the "associated" relationship) to another account,
# then the connected account is also flagged for investigation.
add_rule(Rule("requires_investigation(y) <- requires_investigation(x), associated(x,y)", "propagation_rule"))

# --- Part 4: Run the Reasoning Engine ---

# Reset settings before running reasoning
reset_settings()

# Run the reasoning engine to allow the investigation flag to propagate through the network.
Settings.atom_trace = True
interpretation = reason()

trace = get_rule_trace(interpretation)
print(f"RULE TRACE: \n\n{trace[0]}\n")
