import importlib.util
import pathlib

# Load filter_ruleset without importing the full pyreason package
SPEC_PATH = pathlib.Path(__file__).resolve().parents[1] / "pyreason" / "scripts" / "utils" / "filter_ruleset.py"
_spec = importlib.util.spec_from_file_location("filter_ruleset", SPEC_PATH)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
filter_ruleset = _module.filter_ruleset


class DummyRule:
    def __init__(self, name, target, clauses):
        self._name = name
        self._target = target
        self._clauses = clauses

    def get_rule_name(self):
        return self._name

    def get_target(self):
        return self._target

    def get_clauses(self):
        return self._clauses


class DummyQuery:
    def __init__(self, predicate):
        self._predicate = predicate

    def get_predicate(self):
        return self._predicate


def test_filter_ruleset_handles_cycles():
    """Rules with circular dependencies should not cause infinite recursion."""
    r1 = DummyRule('r1', 'a', [(None, 'b')])
    r2 = DummyRule('r2', 'b', [(None, 'a')])

    filtered = filter_ruleset([DummyQuery('a')], [r1, r2])
    assert {r.get_rule_name() for r in filtered} == {'r1', 'r2'}
