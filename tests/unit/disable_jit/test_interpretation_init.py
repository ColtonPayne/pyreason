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


@pytest.fixture
def shim_types(monkeypatch):
    class ListShim:
        def __call__(self, iterable=()):
            return list(iterable)

        def empty_list(self, *args, **kwargs):
            return []

    class DictShim:
        def empty(self, *args, **kwargs):
            return {}

    monkeypatch.setattr(interpretation.numba.typed, "List", ListShim())
    monkeypatch.setattr(interpretation.numba.typed, "Dict", DictShim())

    class World:
        def __init__(self, labels=None):
            self.world = {}

    monkeypatch.setattr(interpretation.world, "World", World)
    monkeypatch.setattr(interpretation.interval, "closed", lambda lo, up: (lo, up))


# ---- _init_reverse_neighbors tests ----

def test_init_reverse_neighbors_branches(shim_types):
    neighbors = {
        "n1": ["n2", "n2"],
        "n2": ["n3"],
        "n3": ["n2"],
        "n4": [],
    }
    rev = init_reverse_neighbors(neighbors)
    assert rev == {"n2": ["n1", "n3"], "n1": [], "n3": ["n2"], "n4": []}


def test_init_reverse_neighbors_empty(shim_types):
    assert init_reverse_neighbors({}) == {}


# ---- _init_interpretations_node tests ----

def test_init_interpretations_node_populates(shim_types):
    nodes = ["a", "b"]
    specific = {"L": ["a"], "M": []}
    interps, pmap = init_interpretations_node(nodes, specific)
    assert pmap["L"] == ["a"] and pmap["M"] == []
    if interpretation.__name__.endswith("interpretation"):
        assert set(interps.keys()) == {"a", "b"}
        assert interps["a"].world["L"] == (0.0, 1.0)
        assert interps["b"].world == {}
    else:
        assert set(interps.keys()) == {0}


def test_init_interpretations_node_empty(shim_types):
    interps, pmap = init_interpretations_node([], {})
    assert pmap == {}
    if interpretation.__name__.endswith("interpretation"):
        assert interps == {}
    else:
        assert interps == {0: {}}


# ---- _init_interpretations_edge tests ----

def test_init_interpretations_edge_populates(shim_types):
    edges = [("a", "b"), ("b", "c")]
    specific = {"L": [("a", "b")], "M": []}
    interps, pmap = init_interpretations_edge(edges, specific)
    assert pmap["L"] == [("a", "b")] and pmap["M"] == []
    if interpretation.__name__.endswith("interpretation"):
        assert set(interps.keys()) == set(edges)
        assert interps[("a", "b")].world["L"] == (0.0, 1.0)
        assert interps[("b", "c")].world == {}
    else:
        assert set(interps.keys()) == {0}


def test_init_interpretations_edge_empty(shim_types):
    interps, pmap = init_interpretations_edge([], {})
    assert pmap == {}
    if interpretation.__name__.endswith("interpretation"):
        assert interps == {}
    else:
        assert interps == {0: {}}
