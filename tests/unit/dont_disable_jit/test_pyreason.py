"""
Practical unit tests for pyreason.py focusing on public API and testable functions.
Complements functional tests with focused unit testing of individual components.
"""

import pytest
import unittest.mock as mock
import tempfile
import os
import networkx as nx

# Import the module under test
import pyreason as pr
from pyreason.scripts.facts.fact import Fact
from pyreason.scripts.rules.rule import Rule
from pyreason.scripts.query.query import Query
import pyreason.scripts.numba_wrapper.numba_types.interval_type as interval


class TestSettingsClass:
    """Test the Settings class - this is fully testable via public API"""

    def setup_method(self):
        """Reset settings before each test"""
        pr.reset_settings()

    def test_settings_defaults(self):
        """Test all default property values"""
        s = pr.settings
        assert s.verbose is True
        assert s.output_to_file is False
        assert s.output_file_name == 'pyreason_output'
        assert s.graph_attribute_parsing is True
        assert s.abort_on_inconsistency is False
        assert s.memory_profile is False
        assert s.reverse_digraph is False
        assert s.atom_trace is False
        assert s.save_graph_attributes_to_trace is False
        assert s.canonical is False  # Deprecated, uses persistent
        assert s.persistent is False
        assert s.inconsistency_check is True
        assert s.static_graph_facts is True
        assert s.store_interpretation_changes is True
        assert s.parallel_computing is False
        assert s.update_mode == 'intersection'
        assert s.allow_ground_rules is False
        assert s.fp_version is False

    def test_reset_settings(self):
        """Test settings reset functionality"""
        s = pr.settings
        # Change some settings
        s.verbose = False
        s.memory_profile = True
        s.update_mode = 'override'

        # Reset and verify defaults restored
        pr.reset_settings()
        assert s.verbose is True
        assert s.memory_profile is False
        assert s.update_mode == 'intersection'

    @pytest.mark.parametrize("property_name", [
        'verbose', 'output_to_file', 'graph_attribute_parsing',
        'abort_on_inconsistency', 'memory_profile', 'reverse_digraph',
        'atom_trace', 'save_graph_attributes_to_trace', 'canonical',
        'persistent', 'inconsistency_check', 'static_graph_facts',
        'store_interpretation_changes', 'parallel_computing',
        'allow_ground_rules', 'fp_version'
    ])
    def test_boolean_setters_valid(self, property_name):
        """Test all boolean setters with valid inputs"""
        s = pr.settings

        # Test setting to True
        setattr(s, property_name, True)
        assert getattr(s, property_name) is True

        # Test setting to False
        setattr(s, property_name, False)
        assert getattr(s, property_name) is False

    @pytest.mark.parametrize("property_name", [
        'verbose', 'output_to_file', 'graph_attribute_parsing',
        'abort_on_inconsistency', 'memory_profile', 'reverse_digraph',
        'atom_trace', 'save_graph_attributes_to_trace', 'canonical',
        'persistent', 'inconsistency_check', 'static_graph_facts',
        'store_interpretation_changes', 'parallel_computing',
        'allow_ground_rules', 'fp_version'
    ])
    def test_boolean_setters_invalid_type(self, property_name):
        """Test all boolean setters with invalid inputs raise TypeError"""
        s = pr.settings

        with pytest.raises(TypeError, match='value has to be a bool'):
            setattr(s, property_name, "not_a_bool")
        with pytest.raises(TypeError, match='value has to be a bool'):
            setattr(s, property_name, 123)

    def test_string_setters_valid(self):
        """Test string setters with valid inputs"""
        s = pr.settings

        # Test output_file_name
        s.output_file_name = "test_output"
        assert s.output_file_name == "test_output"

        # Test update_mode
        s.update_mode = "override"
        assert s.update_mode == "override"

    def test_string_setters_invalid_type(self):
        """Test string setters with invalid inputs raise TypeError"""
        s = pr.settings

        with pytest.raises(TypeError, match='file_name has to be a string'):
            s.output_file_name = 123

        with pytest.raises(TypeError, match='value has to be a str'):
            s.update_mode = True

    def test_canonical_persistent_aliasing(self):
        """Test that canonical setter affects persistent property (deprecated feature)"""
        s = pr.settings

        s.canonical = True
        assert s.persistent is True
        assert s.canonical is True

        s.canonical = False
        assert s.persistent is False
        assert s.canonical is False


class TestStateManagementFunctions:
    """Test state management functions - testable via public API"""

    def setup_method(self):
        """Reset state before each test"""
        pr.reset()
        pr.reset_settings()

    def test_reset_function(self):
        """Test reset function clears state properly"""
        # Add some state
        pr.add_rule(Rule('test(x) <- test2(x)', 'test_rule'))
        pr.add_fact(Fact('test(node1)', 'test_fact'))

        # Verify state exists
        assert pr.get_rules() is not None

        # Reset and verify cleared
        pr.reset()
        assert pr.get_rules() is None

    def test_reset_rules_function(self):
        """Test reset_rules function"""
        # Add rules
        pr.add_rule(Rule('test(x) <- test2(x)', 'test_rule'))
        assert pr.get_rules() is not None

        # Reset rules only
        pr.reset_rules()
        assert pr.get_rules() is None

    def test_get_rules_initially_none(self):
        """Test get_rules returns None initially"""
        pr.reset()
        assert pr.get_rules() is None

    def test_get_rules_after_adding(self):
        """Test get_rules returns rules after adding them"""
        pr.reset()
        rule = Rule('test(x) <- test2(x)', 'test_rule')
        pr.add_rule(rule)

        rules = pr.get_rules()
        assert rules is not None
        assert len(rules) == 1


class TestRuleManagement:
    """Test rule management functions"""

    def setup_method(self):
        """Reset state before each test"""
        pr.reset()

    def test_add_single_rule(self):
        """Test adding a single rule"""
        rule = Rule('test(x) <- test2(x)', 'test_rule')
        pr.add_rule(rule)

        rules = pr.get_rules()
        assert rules is not None
        assert len(rules) == 1
        assert rules[0].get_rule_name() == 'test_rule'

    def test_add_multiple_rules(self):
        """Test adding multiple rules"""
        rule1 = Rule('test1(x) <- test2(x)', 'rule1')
        rule2 = Rule('test3(x) <- test4(x)', 'rule2')

        pr.add_rule(rule1)
        pr.add_rule(rule2)

        rules = pr.get_rules()
        assert len(rules) == 2

    def test_add_rule_auto_naming(self):
        """Test rule auto-naming when name not provided"""
        rule = Rule('test(x) <- test2(x)')  # No name provided
        pr.add_rule(rule)

        rules = pr.get_rules()
        assert rules[0].get_rule_name() == 'rule_0'

    def test_add_rule_auto_naming_with_offset(self):
        """Test rule auto-naming considers existing rules"""
        # Add first rule with explicit name
        rule1 = Rule('test1(x) <- test2(x)', 'explicit_name')
        pr.add_rule(rule1)

        # Add second rule without name - should be rule_1
        rule2 = Rule('test3(x) <- test4(x)')
        pr.add_rule(rule2)

        rules = pr.get_rules()
        assert rules[1].get_rule_name() == 'rule_1'

    def test_add_rules_from_file(self):
        """Test adding rules from a text file"""
        # Create temporary file with rules
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("# This is a comment\n")
            f.write("\n")  # Empty line
            f.write("rule1(x) <- rule2(x)\n")
            f.write("rule3(x) <- rule4(x)\n")
            temp_path = f.name

        try:
            pr.add_rules_from_file(temp_path)

            rules = pr.get_rules()
            assert len(rules) == 2  # Should ignore comment and empty line
            assert rules[0].get_rule_name() == 'rule_0'
            assert rules[1].get_rule_name() == 'rule_1'
        finally:
            os.unlink(temp_path)

    def test_add_rules_from_file_with_infer_edges(self):
        """Test adding rules from file with infer_edges parameter"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("test_rule(x) <-1 other_rule(x)\n")  # Add threshold for valid rule
            temp_path = f.name

        try:
            pr.add_rules_from_file(temp_path, infer_edges=True)

            rules = pr.get_rules()
            assert len(rules) == 1
            # The infer_edges property is on the Rule wrapper, not the internal rule
            # We can't easily test this without accessing internals, so just verify it doesn't crash
        finally:
            os.unlink(temp_path)


class TestFactManagement:
    """Test fact management functions"""

    def setup_method(self):
        """Reset state before each test"""
        pr.reset()

    def test_add_node_fact(self):
        """Test adding a node fact"""
        fact = Fact('test(node1)', 'test_fact', 0, 1)
        pr.add_fact(fact)

        # Verify fact was added (we can't directly access internal state easily,
        # but we can verify no exceptions were raised and the fact object was modified)
        assert fact.name == 'test_fact'
        assert fact.type == 'node'

    def test_add_edge_fact(self):
        """Test adding an edge fact"""
        fact = Fact('test(node1, node2)', 'test_fact', 0, 1)
        pr.add_fact(fact)

        assert fact.name == 'test_fact'
        assert fact.type == 'edge'

    def test_add_fact_auto_naming(self):
        """Test fact auto-naming when name not provided"""
        fact = Fact('test(node1)')  # No name provided
        original_name = fact.name

        pr.add_fact(fact)

        # Name should be auto-generated if it was None
        if original_name is None:
            assert fact.name.startswith('fact_')

    def test_add_multiple_facts(self):
        """Test adding multiple facts"""
        fact1 = Fact('test1(node1)', 'fact1', 0, 1)
        fact2 = Fact('test2(node1, node2)', 'fact2', 0, 1)

        pr.add_fact(fact1)
        pr.add_fact(fact2)

        # Verify both facts maintain their properties
        assert fact1.name == 'fact1'
        assert fact2.name == 'fact2'


class TestGraphLoading:
    """Test graph loading functions"""

    def setup_method(self):
        """Reset state before each test"""
        pr.reset()
        pr.reset_settings()

    def test_load_empty_networkx_graph(self):
        """Test loading an empty NetworkX graph"""
        graph = nx.DiGraph()
        pr.load_graph(graph)

        # Should not raise exceptions
        # We can't easily verify internal state, but we can test it doesn't crash

    def test_load_simple_networkx_graph(self):
        """Test loading a simple NetworkX graph"""
        graph = nx.DiGraph()
        graph.add_edge("A", "B")
        graph.add_edge("B", "C")

        pr.load_graph(graph)
        # Should not raise exceptions

    def test_load_graph_with_attributes(self):
        """Test loading graph with node/edge attributes"""
        graph = nx.DiGraph()
        graph.add_node("A", label="person")
        graph.add_node("B", label="person")
        graph.add_edge("A", "B", relation="knows")

        pr.settings.graph_attribute_parsing = True
        pr.load_graph(graph)
        # Should not raise exceptions

    def test_load_graph_without_attribute_parsing(self):
        """Test loading graph with attribute parsing disabled"""
        graph = nx.DiGraph()
        graph.add_node("A", label="person")
        graph.add_edge("A", "B", relation="knows")

        pr.settings.graph_attribute_parsing = False
        pr.load_graph(graph)
        # Should not raise exceptions

    def test_load_graphml_file_not_found(self):
        """Test loading non-existent GraphML file raises appropriate error"""
        with pytest.raises((FileNotFoundError, OSError)):
            pr.load_graphml("non_existent_file.graphml")


class TestAnnotationFunctions:
    """Test annotation function management"""

    def test_add_annotation_function(self):
        """Test adding annotation function"""
        def test_function(annotations, weights):
            return sum(annotations)

        # Should not raise exceptions
        pr.add_annotation_function(test_function)


class TestIPLManagement:
    """Test IPL (Inconsistent Predicate List) management"""

    def setup_method(self):
        """Reset state before each test"""
        pr.reset()

    def test_add_inconsistent_predicate(self):
        """Test adding inconsistent predicate pair"""
        # Should not raise exceptions
        pr.add_inconsistent_predicate("pred1", "pred2")
        pr.add_inconsistent_predicate("pred3", "pred4")

    def test_load_ipl_file_not_found(self):
        """Test loading non-existent IPL file raises appropriate error"""
        with pytest.raises((FileNotFoundError, OSError)):
            pr.load_inconsistent_predicate_list("non_existent_ipl.yaml")


class TestOutputFunctions:
    """Test output and filtering functions - these have testable assertion logic"""

    def setup_method(self):
        """Reset settings before each test"""
        pr.reset_settings()

    def test_save_rule_trace_assertion_when_store_changes_false(self):
        """Test save_rule_trace raises assertion when store_interpretation_changes=False"""
        pr.settings.store_interpretation_changes = False

        with pytest.raises(AssertionError, match='store interpretation changes setting is off'):
            pr.save_rule_trace(mock.MagicMock(), './test/')

    def test_get_rule_trace_assertion_when_store_changes_false(self):
        """Test get_rule_trace raises assertion when store_interpretation_changes=False"""
        pr.settings.store_interpretation_changes = False

        with pytest.raises(AssertionError, match='store interpretation changes setting is off'):
            pr.get_rule_trace(mock.MagicMock())

    def test_filter_and_sort_nodes_assertion_when_store_changes_false(self):
        """Test filter_and_sort_nodes raises assertion when store_interpretation_changes=False"""
        pr.settings.store_interpretation_changes = False

        with pytest.raises(AssertionError, match='store interpretation changes setting is off'):
            pr.filter_and_sort_nodes(mock.MagicMock(), ['test'])

    def test_filter_and_sort_edges_assertion_when_store_changes_false(self):
        """Test filter_and_sort_edges raises assertion when store_interpretation_changes=False"""
        pr.settings.store_interpretation_changes = False

        with pytest.raises(AssertionError, match='store interpretation changes setting is off'):
            pr.filter_and_sort_edges(mock.MagicMock(), ['test'])


class TestTorchIntegration:
    """Test torch integration - check current state"""

    def test_torch_availability_check(self):
        """Test that torch integration state is consistent with torch availability"""
        try:
            import torch
            # If torch is available, LogicIntegratedClassifier should be available
            assert hasattr(pr, 'LogicIntegratedClassifier')
            assert hasattr(pr, 'ModelInterfaceOptions')
            # These might be None if torch import failed, but attributes should exist
        except ImportError:
            # If torch is not available, these should be None
            assert pr.LogicIntegratedClassifier is None
            assert pr.ModelInterfaceOptions is None


class TestReasoningValidation:
    """Test reasoning function validation and error conditions"""

    def setup_method(self):
        """Reset state before each test"""
        pr.reset()
        pr.reset_settings()

    def test_reason_without_rules_raises_exception(self):
        """Test that reasoning without rules raises an exception"""
        # Load a simple graph but no rules
        graph = nx.DiGraph()
        graph.add_edge("A", "B")
        pr.load_graph(graph)

        with pytest.raises(Exception, match='There are no rules'):
            pr.reason()

    # def test_reason_with_empty_graph_warning(self):
    #     """Test reasoning with no graph loads empty graph and warns"""
    #     pr.add_rule(Rule('test(x) <-1 test2(x)', 'test_rule'))

    #     with pytest.warns(UserWarning, match='Graph not loaded'):
    #         interpretation = pr.reason(timesteps=1)
    #         # Should complete without crashing


if __name__ == '__main__':
    pytest.main([__file__])