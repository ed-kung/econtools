"""
Test script: econtools.entities (Person, Good, Country, Firm, City) and their
round trip through GenericProblem params -> parquet -> rebuilt problem.

Run from the repo root:
    python tests/test_entities.py
"""

import os
import sys
import tempfile

import numpy as np

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(TESTS_DIR), "src"))

from econtools.entities import City, Country, Firm, Good, Person
from econtools.problems import generate
from econtools.problems.base import GenericProblem


def test_load_and_tags():
    for cls in (Person, Good, Country, Firm, City):
        assert len(cls.rows()) > 0, cls
    foods = Good.keys(tags="food")
    assert "pizza" in foods and "widget" not in foods
    assert set(Firm.keys(tags="car-lot")) == {"Stan's Used Car Rentals", "Bob's Car Emporium", "Kenny's Car Lot"}
    assert Good.keys(tags=["food", "market"]) == []


def test_sample():
    rng = np.random.default_rng(0)
    for _ in range(200):
        people = Person.sample(rng, 3)
        assert isinstance(people, tuple) and len(set(p.name for p in people)) == 3
    one = Person.sample(rng)
    assert isinstance(one, Person)

    a = Good.sample(np.random.default_rng(42), 2, tags="market")
    b = Good.sample(np.random.default_rng(42), 2, tags="market")
    assert a == b, "same seed must give the same draw"

    first = Person.sample(rng)
    for _ in range(100):
        assert Person.sample(rng, exclude=[first]).name != first.name
        assert Person.sample(rng, exclude=[first.name]).name != first.name

    n_cars = len(Firm.rows(tags="car-lot"))
    try:
        Firm.sample(rng, n_cars + 1, tags="car-lot")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_good_scales():
    rng = np.random.default_rng(1)
    seen = set()
    for _ in range(300):
        g = Good.sample(rng, tags="market")
        ps, qs = Good.scales(g.singular)
        assert g.pscale in ps and g.qscale in qs, g
        if g.singular == "corn":
            seen.add(g.pscale)
    assert seen == {1, 2, 5, 10}, seen
    assert Good.get("coffee").pscale == 5 and Good.get("coffee").plural == "coffee"
    assert Good.get("widget").pscale == Good.DEFAULT_PSCALES[0]
    assert Good.get("car").a == "a car" and Good.get("ice cream scoop").a == "an ice cream scoop"


def test_pronouns():
    jane = Person.get("Jane")
    assert (jane.subject, jane.object, jane.possessive, jane.possessive_pronoun, jane.reflexive) == \
        ("she", "her", "her", "hers", "herself")
    assert Person.get("Ferris").possessive == "his"
    assert Person("Sam", "they").reflexive == "themselves"
    assert f"{jane}" == "Jane"


class ToyProblem(GenericProblem):
    default_params = {
        "person": Person.get("Anna"),
        "goods": (Good.get("pizza"), Good.get("cake")),
        "rate": 1,
    }

    def build(self, rng):
        p = self.params
        self.add_setup(f"{p['person'].name} makes {p['goods'][0].plural} and {p['goods'][1].plural}.")

    @classmethod
    def candidate_params(cls, rng):
        for _ in range(20):
            yield {"person": Person.sample(rng), "goods": Good.sample(rng, 2, tags="market"),
                   "rate": int(rng.integers(1, 10))}


def test_parquet_round_trip():
    df = generate.generate(ToyProblem)
    originals = [ToyProblem(params=params, rng=np.random.default_rng(0)).params
                 for params in ToyProblem.candidate_params(np.random.default_rng(ToyProblem.seed))]
    with tempfile.TemporaryDirectory() as d:
        generate.save(df, ToyProblem, data_dir=d)
        loaded = generate.load_valid(ToyProblem, data_dir=d)
    assert len(loaded) == len(originals)
    for (_, row), orig in zip(loaded.iterrows(), originals):
        prob = ToyProblem(params=row.to_dict())
        assert isinstance(prob.params["person"], Person)
        assert isinstance(prob.params["goods"], tuple) and all(isinstance(g, Good) for g in prob.params["goods"])
        assert prob.params == orig, (prob.params, orig)
        assert type(prob.params["goods"][0].pscale) is int
    assert isinstance(ToyProblem().params["person"], Person)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
