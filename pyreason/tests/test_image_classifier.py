# import the logicIntegratedClassifier class

from pathlib import Path
import torch
import torch.nn as nn
import networkx as nx
import numpy as np
import random
import sys
import os
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import torch.nn.functional as F
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from pyreason.scripts.learning.classification.classifier import LogicIntegratedClassifier
from pyreason.scripts.facts.fact import Fact
from pyreason.scripts.learning.utils.model_interface import ModelInterfaceOptions
from pyreason.scripts.rules.rule import Rule
from pyreason.pyreason import _Settings as Settings, reason, reset_settings, get_rule_trace, add_fact, add_rule, load_graph, save_rule_trace


# Step 1: Load a pre-trained model and image processor from Hugging Face
model_name = "google/vit-base-patch16-224"  # Vision Transformer model
processor = AutoImageProcessor.from_pretrained(model_name)
model = AutoModelForImageClassification.from_pretrained(model_name)

G = nx.DiGraph()
## Make a complete graph between all the nodes
load_graph(G)

# Step 2: Load and preprocess images from the directory
image_dir = "/Users/coltonpayne/pyreason/examples/image_classifier_two/images"
image_paths = list(Path(image_dir).glob("*.jpeg"))  # Get all .jpeg files in the directory
image_list = []
allowed_labels = ['goldfish', 'tiger shark', 'hammerhead', 'great white shark', 'tench']

# Get the index-to-label mapping from the model config
id2label = model.config.id2label

# Get the indices of the allowed labels, stripping everything after the comma
allowed_indices = [
    i for i, label in id2label.items()
    if label.split(",")[0].strip().lower() in [name.lower() for name in allowed_labels]
]

# Add Rules to the knowlege base
add_rule(Rule("is_fish(x) <-0 goldfish(x)", "is_fish_rule"))
add_rule(Rule("is_fish(x) <-0 tench(x)", "is_fish_rule"))
add_rule(Rule("is_shark(x) <-0 tigershark(x)", "is_shark_rule"))
add_rule(Rule("is_shark(x) <-0 hammerhead(x)", "is_shark_rule"))
add_rule(Rule("is_shark(x) <-0 greatwhiteshark(x)", "is_shark_rule"))
add_rule(Rule("is_scary(x) <-0 is_shark(x)", "is_scary_rule"))
add_rule(Rule("likes_to_eat(y,x) <-0 is_shark(y), is_fish(x)", "likes_to_eat_rule"))



for image_path in image_paths:
    print(f"Processing Image: {image_path.name}")
    image = Image.open(image_path)
    inputs = processor(images=image, return_tensors="pt")

    interface_options = ModelInterfaceOptions(
        threshold=0.5,       # Only process probabilities above 0.5
        set_lower_bound=True,  # For high confidence, adjust the lower bound.
        set_upper_bound=False, # Keep the upper bound unchanged.
        snap_value=1.0      # Use 1.0 as the snap value.
    )


    classifier_name = image_path.name.split(".")[0]
    # We use dynamic variable names to create a unique classifier for each image
    # There's a better way to do this probably
    globals()[classifier_name] = LogicIntegratedClassifier(
        model,
        allowed_labels,
        identifier=classifier_name,
        interface_options=interface_options
    )

    # print("Top Probs: ", filtered_probs)
    logits, probabilities, classifier_facts = globals()[classifier_name](inputs, limit_classification_output_classes=True)
    #logits, probabilities, classifier_facts = fish_classifier(inputs, output=logits, probabilities=top_probs)
    #logits, probabilities, classifier_facts = fish_classifier(inputs)
    #logits, probabilities, classifier_facts = fish_classifier(**inputs)

    print("=== Fish Classifier Output ===")
    #print("Probabilities:", probabilities)
    print("\nGenerated Classifier Facts:")
    for fact in classifier_facts:
        print(fact)

    for fact in classifier_facts:
        add_fact(fact)

    print("Done processing image ", image_path.name)

# --- Part 4: Run the Reasoning Engine ---

# Reset settings before running reasoning
reset_settings()

# Run the reasoning engine to allow the investigation flag to propagate hat through the network.
Settings.atom_trace = True
interpretation = reason()

trace = get_rule_trace(interpretation)
print(f"RULE TRACE: \n\n{trace[0]}\n")


# First, make the knowlege base with all the hardcoded rules
# Get the inputs, turn the images into FACTS in pyreason.  This completes our knowlege base
# Then, run the inferences

# TODO:
# Re-write with non-grounded rules
# Try to make a more general version of the LogicIntegratedClassifier that can load in a huggingface model and a set of classes
# Ask Dyuman about how to connect all the edges of a graph within the LogicIntegratedClassifier