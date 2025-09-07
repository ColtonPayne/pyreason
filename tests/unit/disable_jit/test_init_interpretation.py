import pytest
from tests.unit.disable_jit.interpretation_helpers import get_interpretation_helpers

# Preload defaults so decorators resolve
_default = get_interpretation_helpers("interpretation_fp")
for _name in dir(_default):
    if not _name.startswith("_"):
        globals()[_name] = getattr(_default, _name)


@pytest.fixture(params=["interpretation_fp", "interpretation"], autouse=True)
def helpers_fixture(request):
    h = get_interpretation_helpers(request.param)
    g = globals()
    for name in dir(h):
        if not name.startswith("_"):
            g[name] = getattr(h, name)
    yield


def test_init_reverse_neighbors_branch_coverage():
    neighbors = {0: [2], 1: [2], 2: []}
    reverse = init_reverse_neighbors(neighbors)
    rev_py = {k: list(v) for k, v in reverse.items()}
    assert rev_py == {2: [0, 1], 0: [], 1: []}


def test_init_interpretations_node(monkeypatch):
    nodes = ["A", "B"]
    lbl = label.Label("L")
    if interpretation.__name__.endswith("interpretation"):
        monkeypatch.setattr(interpretation.interval, "closed", lambda lo, up: (lo, up))
    interpretations, predicate_map = init_interpretations_node(nodes, {lbl: ["A"]})
    pm_py = {k.get_value(): list(v) for k, v in predicate_map.items()}
    assert pm_py == {"L": ["A"]}
    if interpretation.__name__.endswith("interpretation_fp"):
        assert list(interpretations.keys()) == [0]
    else:
        assert set(interpretations.keys()) == set(nodes)
        assert lbl in interpretations["A"].world
        assert lbl not in interpretations["B"].world


def test_init_interpretations_edge(monkeypatch):
    edges = [("A", "B"), ("B", "C")]
    lbl = label.Label("L")
    if interpretation.__name__.endswith("interpretation"):
        monkeypatch.setattr(interpretation.interval, "closed", lambda lo, up: (lo, up))
    interpretations, predicate_map = init_interpretations_edge(edges, {lbl: [("A", "B")]})
    pm_py = {k.get_value(): list(v) for k, v in predicate_map.items()}
    assert pm_py == {"L": [("A", "B")]}
    if interpretation.__name__.endswith("interpretation_fp"):
        assert list(interpretations.keys()) == [0]
    else:
        assert set(interpretations.keys()) == set(edges)
        assert lbl in interpretations[("A", "B")].world
        assert lbl not in interpretations[("B", "C")].world
